# modules/swagger_migration.py
import re

def migrate_swagger_annotations(content: str) -> str:
    # @ApiOperation -> @Operation (migrar antes de cambiar imports)
    def replace_api_op(match):
        args = match.group(1)

        # Quitar httpMethod y cualquier coma o espacio sobrante
        args = re.sub(r'\s*httpMethod\s*=\s*\"[^\"]*\"\s*,?', '', args)
        args = args.strip().strip(',')  # elimina comas residuales al inicio/final

        # Extraer summary y description (equivalentes a value y notes)
        summary_match = re.search(r'value\s*=\s*\"([^\"]*)\"', args)
        description_match = re.search(r'notes\s*=\s*\"([^\"]*)\"', args)

        summary = summary_match.group(1) if summary_match else None
        description = description_match.group(1) if description_match else None

        if summary and description:
            return f'@Operation(summary = "{summary}", description = "{description}")'
        elif summary:
            return f'@Operation(summary = "{summary}")'
        elif description:
            return f'@Operation(description = "{description}")'
        else:
            return '@Operation()'

    content = re.sub(r'@ApiOperation\s*\((.*?)\)', replace_api_op, content, flags=re.DOTALL)

    # Reemplazar imports
    content = content.replace('io.swagger.annotations.Api', 'io.swagger.v3.oas.annotations.tags.Tag')
    content = content.replace('io.swagger.annotations.ApiOperation', 'io.swagger.v3.oas.annotations.Operation')
    content = content.replace('io.swagger.annotations.ApiResponses', 'io.swagger.v3.oas.annotations.responses.ApiResponses')
    content = content.replace('io.swagger.annotations.ApiResponse', 'io.swagger.v3.oas.annotations.responses.ApiResponse')

    # Eliminar import comodín
    content = content.replace('import io.swagger.annotations.*;', '')
    
    # @Api -> @Tag
    def replace_api(match):
        args = match.group(1)
        name = ""
        desc = ""
        tag_match = re.search(r'tags\s*=\s*\{?\s*\"([^\"]+)\"\s*}?', args)
        if tag_match:
            name = tag_match.group(1)
        val_match = re.search(r'value\s*=\s*\"([^\"]+)\"', args)
        if val_match and not name:
            name = val_match.group(1)
        if val_match and name:
            desc = val_match.group(1)
        result = f'@Tag(name = "{name}"'
        if desc and desc != name:
            result += f', description = "{desc}"'
        return result + ')'

    content = re.sub(r'@Api\s*\(([^)]*)\)', replace_api, content)

    # @ApiResponse -> @ApiResponse (con responseCode y description)
    def replace_api_response(match):
        code = match.group(1)
        msg = match.group(2)
        return f'@ApiResponse(responseCode = "{code}", description = "{msg}")'

    content = re.sub(r'@ApiResponse\(\s*code\s*=\s*([0-9]+)\s*,\s*message\s*=\s*\"([^\"]+)\"\s*\)', replace_api_response, content)

    # Corrección defensiva por si queda algún @Operation con value= o notes=
    def fix_incorrect_operation(match):
        args = match.group(1)
        if 'summary =' in args or 'description =' in args:
            return f'@Operation({args})'
        summary_match = re.search(r'value\s*=\s*\"([^\"]*)\"', args)
        description_match = re.search(r'notes\s*=\s*\"([^\"]*)\"', args)
        summary = summary_match.group(1) if summary_match else None
        description = description_match.group(1) if description_match else None

        if summary and description:
            return f'@Operation(summary = "{summary}", description = "{description}")'
        elif summary:
            return f'@Operation(summary = "{summary}")'
        elif description:
            return f'@Operation(description = "{description}")'
        else:
            return '@Operation()'

    content = re.sub(r'@Operation\s*\((.*?)\)', fix_incorrect_operation, content, flags=re.DOTALL)

    return content

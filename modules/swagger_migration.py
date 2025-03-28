# modules/swagger_migration.py
import re
 
def migrate_swagger_annotations(content: str) -> str:
    # Reemplazar anotaciones Swagger 2 por OpenAPI 3
    content = content.replace('io.swagger.annotations.Api', 'io.swagger.v3.oas.annotations.tags.Tag')
    content = content.replace('io.swagger.annotations.ApiOperation', 'io.swagger.v3.oas.annotations.Operation')
    content = content.replace('io.swagger.annotations.ApiResponses', 'io.swagger.v3.oas.annotations.responses.ApiResponses')
    content = content.replace('io.swagger.annotations.ApiResponse', 'io.swagger.v3.oas.annotations.responses.ApiResponse')
 
    # @Api -> @Tag
    def replace_api(match):
        args = match.group(1)
        name = ""
        desc = ""
        tag_match = re.search(r'tags\s*=\s*\{?\s*"([^"]+)"\s*}?', args)
        if tag_match:
            name = tag_match.group(1)
        val_match = re.search(r'value\s*=\s*"([^"]+)"', args)
        if val_match and not name:
            name = val_match.group(1)
        if val_match and name:
            desc = val_match.group(1)
        result = f'@Tag(name = "{name}"'
        if desc and desc != name:
            result += f', description = "{desc}"'
        return result + ')'
 
    content = re.sub(r'@Api\s*\(([^)]*)\)', replace_api, content)
 
    # @ApiOperation -> @Operation
    def replace_api_op(match):
        args = match.group(1)
        args = re.sub(r'value\s*=', 'summary =', args)
        args = re.sub(r'notes\s*=', 'description =', args)
        args = re.sub(r'nickname\s*=', 'operationId =', args)
        return f'@Operation({args})'
 
    content = re.sub(r'@ApiOperation\(([^)]*)\)', replace_api_op, content)
 
    # @ApiResponse -> @ApiResponse (con responseCode y description)
    def replace_api_response(match):
        code = match.group(1)
        msg = match.group(2)
        return f'@ApiResponse(responseCode = "{code}", description = "{msg}")'
 
    content = re.sub(r'@ApiResponse\(\s*code\s*=\s*([0-9]+)\s*,\s*message\s*=\s*"([^"]+)"\s*\)', replace_api_response, content)
 
    return content
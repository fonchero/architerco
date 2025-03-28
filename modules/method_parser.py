# modules/method_parser.py
import re

def process_methods(content: str) -> str:
    method_pattern = re.compile(r'(public\s+Response\s+(\w+)\s*\((.*?)\)\s*\{)(.*?return\s+null;.*?)\}', re.DOTALL)

    def replace_method_body(match):
        full_signature = match.group(1)
        method_name = match.group(2)
        raw_params = match.group(3)
        _method_body = match.group(4)

        params = [p.strip() for p in raw_params.split(',') if p.strip()]
        query_params = []
        body_param = 'null'
        header_param = None
        context_param = '@Context HttpHeaders httpHeaders'
        cleaned_params = []

        for param in params:
            if '@QueryParam' in param:
                match_q = re.search(r'@QueryParam\("(.*?)"\)\s+.*\s+(\w+)', param)
                if match_q:
                    query_params.append((match_q.group(1), match_q.group(2)))
                cleaned_params.append(param)
            elif '@HeaderParam' in param:
                header_param = param
                cleaned_params.append(param)
            elif '@Context' not in param:
                parts = param.split()
                if len(parts) == 2:
                    body_param = parts[1]
                cleaned_params.append(param)

        # Añadir el parámetro de contexto solo si no está
        if not any('@Context' in p for p in cleaned_params):
            cleaned_params.append(context_param)

        # Reconstruir la firma del método sin errores
        full_signature = f"public Response {method_name}({', '.join(cleaned_params)})"

        # Generar cuerpo del método
        camel_call = f'        Object response = sendRequestToCamel("direct:{method_name}", {body_param}, httpHeaders, '
        if query_params:
            param_lines = ["        Map<String, String> params = Map.of(" + ", ".join(
                [f'\"{k}\", {v}' for k, v in query_params]) + ");"]
            camel_call += 'params);'
        else:
            param_lines = []
            camel_call += 'null);'

        return_stmt = '        return Response.ok(response).build();'
        new_body = '\n'.join(param_lines + [camel_call, return_stmt])
        return f'{full_signature} {{\n{new_body}\n    }}'

    content = method_pattern.sub(replace_method_body, content)
    return content

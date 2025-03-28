# modules/method_parser.py
import re
 
def process_methods(content: str) -> str:
    method_pattern = re.compile(r'(public\s+Response\s+(\w+)\s*\([^)]*\)\s*\{)', re.MULTILINE)
 
    def replace_method_body(match):
        full_sig = match.group(1)
        method_name = match.group(2)
 
        # Buscar el cuerpo del método desde el final de la firma
        start = match.end()
        brace_count = 1
        end = start
        while end < len(content):
            if content[end] == '{':
                brace_count += 1
            elif content[end] == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
            end += 1
 
        method_body = content[start:end]
 
        # Detectar parámetros
        param_match = re.search(r'\((.*?)\)', full_sig)
        params = param_match.group(1) if param_match else ''
        param_list = [p.strip() for p in params.split(',') if p.strip()]
        query_params = []
        body_param = 'null'
 
        for param in param_list:
            if '@QueryParam' in param:
                match_query = re.search(r'@QueryParam\("(.*?)"\)\s+.*\s+(\w+)', param)
                if match_query:
                    query_params.append((match_query.group(1), match_query.group(2)))
            elif '@Context' not in param and '@HeaderParam' not in param:
                # Asumimos que es el body
                parts = param.split()
                if len(parts) == 2:
                    body_param = parts[1]
 
        if query_params:
            lines = ['        Map<String, Object> params = new HashMap<>();']
            for key, var in query_params:
                lines.append(f'        params.put("{key}", {var});')
            lines.append(f'        return sendRequestToCamel("direct:{method_name}", {body_param}, httpHeaders, params);')
        else:
            lines = [f'        return sendRequestToCamel("direct:{method_name}", {body_param}, httpHeaders, Collections.emptyMap());']
 
        # Reemplazar todo el cuerpo del método
        return f'{full_sig}\n' + "\n".join(lines) + '\n    }'
 
    content = method_pattern.sub(replace_method_body, content)
 
    # Agregar método auxiliar si no existe
    if 'sendRequestToCamel' not in content:
        helper = '''
    private Response sendRequestToCamel(String endpointUri, Object body, HttpHeaders httpHeaders, Map<String, Object> params) {
        Map<String, Object> headers = new HashMap<>();
        if (httpHeaders != null) {
            for (String headerName : httpHeaders.getRequestHeaders().keySet()) {
                headers.put(headerName, httpHeaders.getHeaderString(headerName));
            }
        }
        if (params != null) {
            headers.putAll(params);
        }
        Object responseBody = producerTemplate.requestBodyAndHeaders(endpointUri, body, headers);
        if (responseBody instanceof Response) {
            return (Response) responseBody;
        } else if (responseBody != null) {
            return Response.ok(responseBody).build();
        } else {
            return Response.noContent().build();
        }
    }
'''
        # Insertarlo antes del cierre de la clase
        content = re.sub(r'(\n}\s*)$', helper + r'\1', content)
 
    return content
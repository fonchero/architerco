# camel_helper_inserter.py
import re

def ensure_camel_helper_method(content: str) -> str:
    if 'private Object sendRequestToCamel' in content:
        return content  # Ya existe

    # ======== 1. Asegurar imports necesarios ==========
    required_imports = [
        'import java.util.Map;',
        'import java.util.stream.Collectors;',
        'import com.fasterxml.jackson.databind.ObjectMapper;',
        'import com.fasterxml.jackson.core.JsonProcessingException;'
    ]

    existing_imports = re.findall(r'^import .*?;', content, re.MULTILINE)
    missing_imports = [imp for imp in required_imports if imp not in content]

    # Buscar el último import existente para insertar después de él
    if missing_imports:
        all_imports = list(re.finditer(r'^import .*?;', content, re.MULTILINE))
        if all_imports:
            last_import = all_imports[-1]
            insert_pos = last_import.end()
            content = content[:insert_pos] + '\n' + '\n'.join(missing_imports) + content[insert_pos:]
        else:
            # Si no hay imports, insertar después del package
            package_match = re.search(r'^(package .*?;)', content, re.MULTILINE)
            if package_match:
                insert_pos = package_match.end()
                content = content[:insert_pos] + '\n\n' + '\n'.join(missing_imports) + '\n' + content[insert_pos:]

    # ======== 2. Definir el método helper a insertar ==========
    helper_method = '''

    private Object sendRequestToCamel(String endpoint, Object body, HttpHeaders httpHeaders,
                                      Map<String, String> queryParams) {
        Map<String, Object> headers = httpHeaders.getRequestHeaders()
                .entrySet()
                .stream()
                .collect(Collectors.toMap(
                        Map.Entry::getKey,
                        e -> e.getValue().get(0)));

        if (queryParams != null) {
            queryParams.forEach((key, value) -> {
                if (value != null) {
                    headers.put(key, value);
                }
            });
        }

        Object response = producerTemplate.requestBodyAndHeaders(endpoint, body, headers);

        if (response instanceof String) {
            String responseString = (String) response;
            try {
                ObjectMapper objectMapper = new ObjectMapper();
                return objectMapper.readValue(responseString, Map.class);
            } catch (JsonProcessingException e) {
                System.err.println("⚠ Error al deserializar respuesta de Camel: " + e.getMessage());
            }
        }

        return response;
    }
'''

    # ======== 3. Insertar el helper antes de la última llave de cierre de clase ==========
    brace_stack = []
    for i, char in enumerate(content):
        if char == '{':
            brace_stack.append(i)
        elif char == '}':
            if brace_stack:
                start = brace_stack.pop()
                if not brace_stack:  # última llave de cierre de la clase
                    content = content[:i] + helper_method + '\n' + content[i:]
                    break

    return content
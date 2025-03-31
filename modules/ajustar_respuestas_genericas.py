import re

def ajustar_respuestas_genericas(content: str) -> str:
    if not content:
        return content

    # Detecta métodos con @annotations arriba, que retornen BaseResponse<...> y estén vacíos
    pattern = re.compile(
        r'(?:@\w+(?:\([^)]*\))?\s*)*'                              # Anotaciones múltiples (como @GET, @Path, etc.)
        r'(public\s+BaseResponse<\s*([\w<>]+)\s*>)\s+'             # Firma: public BaseResponse<T>
        r'(\w+)\s*\(([^)]*)\)\s*'                                  # Nombre y parámetros
        r'\{\s*return null;\s*\}',                                 # Cuerpo vacío
        re.MULTILINE
    )

    def add_httpheaders(params: str) -> str:
        if "HttpHeaders" in params:
            return params
        if not params.strip():
            return "@Context HttpHeaders httpHeaders"
        return params.strip() + ", @Context HttpHeaders httpHeaders"

    def build_body(return_type: str, method_name: str) -> str:
        camel_endpoint = method_name[0].lower() + method_name[1:]

        if return_type.startswith("List<") and return_type.endswith(">"):
            return (
                f'{return_type} data = sendRequestToCamel("direct:{camel_endpoint}", null, httpHeaders, null, new TypeReference<{return_type}>() {{}});\n'
                f'        BaseResponse<{return_type}> resultado = new BaseResponse<>();\n'
                f'        resultado.setData(data);\n'
                f'        resultado.setSuccess(true);\n'
                f'        resultado.setWarning(false);\n'
                f'        resultado.setMessage("OK");\n'
                f'        return resultado;'
            )
        else:
            return (
                f'{return_type} data = sendRequestToCamel("direct:{camel_endpoint}", null, httpHeaders, null, {return_type}.class);\n'
                f'        BaseResponse<{return_type}> resultado = new BaseResponse<>();\n'
                f'        resultado.setData(data);\n'
                f'        resultado.setSuccess(true);\n'
                f'        resultado.setWarning(false);\n'
                f'        resultado.setMessage("OK");\n'
                f'        return resultado;'
            )

    def replacer(match):
        full_decl = match.group(1)
        inner_type = match.group(2).strip()
        method_name = match.group(3).strip()
        params = match.group(4).strip()

        params = add_httpheaders(params)
        method_body = build_body(inner_type, method_name)

        return f"{full_decl} {method_name}({params}) {{\n        {method_body}\n    }}"

    return pattern.sub(replacer, content)

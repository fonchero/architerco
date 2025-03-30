# modules/ajustar_respuestas_genericas.py
import re

def reemplazar_metodos_genericos(content: str) -> str:
    # Solo procesa si hay retorno tipo BaseResponse o BaseProxyResponse
    if not re.search(r'public\s+(Base(Response|ProxyResponse)<.*?>)', content):
        return content

    # Regex para capturar métodos con return null y tipo BaseResponse o BaseProxyResponse
    patron_metodo = re.compile(
        r'(public\s+(Base(?:Proxy)?Response<[^>]+>)\s+(\w+)\s*\((.*?)\)\s*\{[^}]*?)return\s+null\s*;\s*\}',
        re.DOTALL
    )

    def reemplazar(match):
        tipo_retorno = match.group(2)
        nombre_metodo = match.group(3)
        parametros = match.group(4)

        # Separar los parámetros y detectar el de tipo body
        params = [p.strip() for p in parametros.split(',') if p.strip()]
        cleaned_params = []
        body_param = 'null'
        tiene_http_headers = any('@Context' in p and 'HttpHeaders' in p for p in params)

        for param in params:
            if '@Context' not in param:
                parts = param.split()
                if len(parts) == 2:
                    body_param = parts[1]
            cleaned_params.append(param)

        # Agregar @Context HttpHeaders httpHeaders si no está
        if not tiene_http_headers:
            cleaned_params.append('@Context HttpHeaders httpHeaders')

        # Reconstruir firma
        nueva_firma = f'public {tipo_retorno} {nombre_metodo}({", ".join(cleaned_params)}) {{'

        # Generar cuerpo
        cuerpo = f"""        Object response = sendRequestToCamel(\"direct:{nombre_metodo}\", {body_param}, httpHeaders, null);
        {tipo_retorno} resultado = new {tipo_retorno}();
        resultado.setData(response);
        resultado.setSuccess(true);
        resultado.setWarning(false);
        resultado.setMessage(\"OK\");
        return resultado;"""

        return f"{nueva_firma}\n{cuerpo}\n    }}"

    print(f"[DEBUG] Reemplazando métodos genéricos en clase con {len(patron_metodo.findall(content))} coincidencias.")
    return patron_metodo.sub(reemplazar, content)

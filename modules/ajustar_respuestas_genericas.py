# modules/ajustar_respuestas_genericas.py
import re

def reemplazar_metodos_genericos(content: str) -> str:
    if not re.search(r'public\s+(Base(Response|ProxyResponse)<.*?>)', content):
        return content

    patron_metodo = re.compile(
        r'(public\s+(Base(?:Proxy)?Response<([^>]+)>)\s+(\w+)\s*\((.*?)\)\s*\{[^}]*?)return\s+null\s*;\s*\}',
        re.DOTALL
    )

    def reemplazar(match):
        tipo_retorno_completo = match.group(2)
        tipo_generico = match.group(3)
        nombre_metodo = match.group(4)
        parametros = match.group(5)

        tipo_clase_base = tipo_retorno_completo.split('<')[0]

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

        if not tiene_http_headers:
            cleaned_params.append('@Context HttpHeaders httpHeaders')

        nueva_firma = f'public {tipo_retorno_completo} {nombre_metodo}({", ".join(cleaned_params)}) {{'

        cuerpo = f'''        {tipo_generico} data = sendRequestToCamel("direct:{nombre_metodo}", {body_param}, httpHeaders, null, {tipo_generico}.class);
        {tipo_retorno_completo} resultado = new {tipo_clase_base}<>();
        resultado.setData(data);
        resultado.setSuccess(true);
        resultado.setWarning(false);
        resultado.setMessage("OK");
        return resultado;'''

        return f"{nueva_firma}\n{cuerpo}\n    }}"

    matches = list(patron_metodo.finditer(content))
    print(f"[DEBUG] Reemplazando métodos genericos en clase con {len(matches)} coincidencias.")

    for match in reversed(matches):
        content = content[:match.start()] + reemplazar(match) + content[match.end():]

    return content

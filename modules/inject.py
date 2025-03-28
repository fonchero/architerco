# modules/inject.py
import re
 
def inject_producer_and_context(content: str) -> str:
    lines = content.splitlines()
 
    # Inyectar ProducerTemplate si no existe
    if 'ProducerTemplate' not in content:
        for i, line in enumerate(lines):
            if re.match(r'.*class\s+\w+\s*\{', line):
                indent = ' ' * (len(line) - len(line.lstrip()))
                lines.insert(i + 1, indent + '@Inject')
                lines.insert(i + 2, indent + 'ProducerTemplate producerTemplate;')
                lines.insert(i + 3, '')
                break
 
    # Agregar @Context HttpHeaders en métodos si no existe
    def add_httpheaders_to_signature(signature):
        if 'HttpHeaders' in signature:
            return signature  # ya lo tiene
        if signature.strip().endswith(')'):
            signature = signature.strip()[:-1] + ', @Context HttpHeaders httpHeaders)'
        return signature
 
    new_lines = []
    in_method = False
    for line in lines:
        if re.match(r'\s*public\s+Response\s+\w+\s*\(.*\).*', line):
            in_method = True
            new_lines.append(add_httpheaders_to_signature(line))
        else:
            new_lines.append(line)
 
    return '\n'.join(new_lines)
# modules/imports.py
def fix_imports(content: str) -> str:
    import_lines = set()
    other_lines = []
 
    for line in content.splitlines():
        if line.strip().startswith("import "):
            import_lines.add(line.strip())
        else:
            other_lines.append(line)
 
    # Reemplazo javax por jakarta
    updated_imports = set()
    for imp in import_lines:
        updated_imports.add(imp.replace("javax.", "jakarta."))
 
    # Imports necesarios para camel 4
    required_imports = {
        "import jakarta.ws.rs.core.Context;",
        "import jakarta.ws.rs.core.HttpHeaders;",
        "import jakarta.inject.Inject;",
        "import org.apache.camel.ProducerTemplate;",
        "import java.util.Map;",
        "import java.util.HashMap;",
        "import java.util.Collections;",
        "import com.fasterxml.jackson.databind.ObjectMapper;"
    }
 
    updated_imports.update(required_imports)
 
    # Eliminar duplicados y ordenar
    sorted_imports = sorted(updated_imports)
 
    # Reconstruir el contenido completo
    final_lines = []
    in_imports = False
    for line in content.splitlines():
        if line.strip().startswith("import "):
            if not in_imports:
                in_imports = True
                final_lines.extend(sorted_imports)
        elif not line.strip().startswith("import "):
            final_lines.append(line)
 
    return "\n".join(final_lines)
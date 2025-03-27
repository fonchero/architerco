import subprocess
import sys
from pathlib import Path
 
def ejecutar_para_todos(in_path, out_path, pom_template_path, global_props_path):
    in_path = Path(in_path).resolve()
    out_path = Path(out_path).resolve()
    pom_template_path = Path(pom_template_path).resolve()
    global_props_path = Path(global_props_path).resolve()
 
    if not in_path.exists() or not in_path.is_dir():
        print(f"[ERROR] La carpeta IN no existe o no es válida: {in_path}")
        return
 
    proyectos = [d for d in in_path.iterdir() if d.is_dir()]
    if not proyectos:
        print("[WARN] No hay subproyectos en la carpeta IN.")
        return
 
    for proyecto in proyectos:
        print(f"\n[INFO] Migrando proyecto: {proyecto.name}")
        comando = [
            "python", "migrar_proyecto_completo.py",
            str(proyecto),
            str(out_path),
            str(pom_template_path),
            str(global_props_path)
        ]
        try:
            resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
            print(resultado.stdout)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Falló la migración de {proyecto.name}")
            print(e.stderr)
 
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python migrar_todos_los_proyectos.py <carpeta_IN> <carpeta_OUT> <pom_template.xml> <application-global.properties>")
        sys.exit(1)
 
    carpeta_in = sys.argv[1]
    carpeta_out = sys.argv[2]
    pom_template = sys.argv[3]
    global_properties = sys.argv[4]
 
    ejecutar_para_todos(carpeta_in, carpeta_out, pom_template, global_properties)

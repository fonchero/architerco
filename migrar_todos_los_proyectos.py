import subprocess
import sys
import shutil
import os
import stat
from pathlib import Path

def eliminar_con_permisos(path):
    def onerror(func, path, exc_info):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            print(f"[ERROR] No se pudo eliminar {path}: {e}")

    for child in path.iterdir():
        try:
            if child.is_file() or child.is_symlink():
                child.unlink()
            elif child.is_dir():
                shutil.rmtree(child, onerror=onerror)
        except Exception as e:
            print(f"[ERROR] No se pudo eliminar {child}: {e}")

def ejecutar_para_todos(in_path, out_path, pom_template_path, global_props_path):
    in_path = Path(in_path).resolve()
    out_path = Path(out_path).resolve()
    pom_template_path = Path(pom_template_path).resolve()
    global_props_path = Path(global_props_path).resolve()

    if out_path.exists() and out_path.is_dir():
        print(f"[INFO] Limpiando carpeta de salida: {out_path}")
        eliminar_con_permisos(out_path)
    else:
        out_path.mkdir(parents=True, exist_ok=True)

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
            sys.executable, "-u", "migrar_proyecto_completo.py",
            str(proyecto),
            str(out_path),
            str(pom_template_path),
            str(global_props_path)
        ]
        try:
            proceso = subprocess.Popen(
                comando,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            for linea in proceso.stdout:
                print(linea, end='', flush=True)

            proceso.wait()
            if proceso.returncode != 0:
                print(f"[ERROR] La migración de {proyecto.name} terminó con error")
        except Exception as e:
            print(f"[ERROR] Excepción al migrar {proyecto.name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python migrar_todos_los_proyectos.py <carpeta_IN> <carpeta_OUT> <pom_template.xml> <application-global.properties>")
        sys.exit(1)

    carpeta_in = sys.argv[1]
    carpeta_out = sys.argv[2]
    pom_template = sys.argv[3]
    global_properties = sys.argv[4]

    ejecutar_para_todos(carpeta_in, carpeta_out, pom_template, global_properties)

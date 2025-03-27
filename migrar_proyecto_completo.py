import subprocess
import sys
from pathlib import Path
 
def ejecutar(nombre_script, argumentos):
    print(f"\n[STEP] Ejecutando: {nombre_script} {argumentos}")
    try:
        resultado = subprocess.run(
            ["python", nombre_script] + argumentos,
            check=True,
            capture_output=True,
            text=True
        )
        print(resultado.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error en {nombre_script}")
        print(e.stderr)
 
def obtener_nombre_directorio(path_str):
    return Path(path_str).resolve().name
 
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python migrar_proyecto_completo.py <IN> <OUT> <pom_template> <application-global.properties>")
        sys.exit(1)
 
    ruta_in = Path(sys.argv[1]).resolve()
    ruta_out_base = Path(sys.argv[2]).resolve()
    ruta_pom_template = Path(sys.argv[3]).resolve()
    ruta_global_properties = Path(sys.argv[4]).resolve()
 
    if not ruta_in.exists():
        print(f"[ERROR] Carpeta IN no existe: {ruta_in}")
        sys.exit(1)
 
    nombre_proyecto = obtener_nombre_directorio(ruta_in)
    ruta_out = ruta_out_base / nombre_proyecto
 
    # Paso 1: copiar proyecto original
    ejecutar("estructurar_proyecto_migrado.py", [str(ruta_in), str(ruta_out)])
 
    # Paso 2: migrar pom.xml
    ejecutar("migrar_pom.py", [str(ruta_out), str(ruta_pom_template)])
 
    # Paso 3: modificar imports y anotaciones
    ejecutar("migrar_clases_completas.py", [str(ruta_out)])
 
    # Paso 4: convertir blueprint si corresponde
    ejecutar("convertir_blueprint.py", [str(ruta_out)])
 
    # Paso 5: sobreescribir RootRouteBuilder
    ejecutar("ajustar_root_routebuilder.py", [str(ruta_out)])
 
    # Paso 5.5: sobreescribir LoggerTrace
    ejecutar("ajustar_logger_trace.py", [str(ruta_out)])

    # Paso 5.6: sobreescribir SingletonProperties
    ejecutar("ajustar_singleton_properties.py", [str(ruta_out)])

    # Paso 5.7: actualizar métodos consumer (header Authorization)
    ejecutar("ajustar_metodos_consumer.py", [str(ruta_out)])

    # Paso 5.8: ajustar @Path y anotaciones de servicios REST
    ejecutar("ajustar_services_path.py", [str(ruta_out)])
    
    # Paso 5.9: ajustar anotaciones en métodos de servicios REST
    ejecutar("ajustar_anotaciones_metodos_service.py", [str(ruta_out)])
    
    # Paso 5.9.1: ajustar MainRouteBuilder si existe
    ejecutar("ajustar_main_routebuilder.py", [str(ruta_out)])

    # Paso 5.10: actualizar expresiones ${property.*} a ${exchangeProperty.*}
    ejecutar("ajustar_property_expression.py", [str(ruta_out)])
 
    # Paso 6: generar Dockerfile actualizado
    ejecutar("generar_dockerfile.py", [str(ruta_out)])
 
    # Paso 7: crear application.properties desde archivo global
    ejecutar("ajustar_application_properties.py", [str(ruta_out), str(ruta_global_properties)])
 
    print(f"\n[OK] Migración completada para: {nombre_proyecto}")
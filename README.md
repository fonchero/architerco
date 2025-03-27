# 🔁 Migrador de Proyectos Fuse 2 a Quarkus 4

Este conjunto de scripts automatiza la migración de proyectos Apache Camel en Fuse 2 a una arquitectura moderna basada en Quarkus 4.

## 🧱 Estructura de Módulos

El orquestador principal es `migrar_proyecto_completo.py`, que realiza los siguientes pasos:

1. **estructurar_proyecto_migrado.py** – Copia y reestructura el proyecto base.
2. **migrar_pom.py** – Reemplaza y adapta el `pom.xml`.
3. **migrar_clases_completas.py** – Ajusta imports, anotaciones y expresiones antiguas de Camel 2.
4. **convertir_blueprint.py** – Convierte `blueprint.xml` a estructura compatible.
5. **ajustar_root_routebuilder.py** – Reemplaza la clase `RootRouteBuilder` con su versión modernizada.
6. **ajustar_logger_trace.py** – Reestructura `LoggerTrace` para el nuevo stack.
7. **ajustar_singleton_properties.py** – Simplifica la clase de propiedades para usar texto plano.
8. **ajustar_metodos_consumer_bean.py** – Ajusta llamadas HTTP externas según la nueva estructura.
9. **ajustar_services_path.py** – Ajusta anotaciones `@Path` y `@Tag` en clases expuestas.
10. **ajustar_anotaciones_metodos_service.py** – Reestructura anotaciones como `@Operation` y `@ApiResponse` en métodos.
11. **ajustar_main_routebuilder.py** – Garantiza que `MainRouteBuilder` tenga definido su `from(...)`.
12. **ajustar_expresion_log_error.py** – Actualiza `LOG_ERROR` para el nuevo contexto.
13. **generar_dockerfile.py** – Genera un Dockerfile con configuración de Quarkus.
14. **ajustar_application_properties.py** – Genera `application.properties` incluyendo variables específicas del proyecto.

---

## 📁 Para Migrar Todos los Proyectos

Usa:

```bash
python migrar_todos_los_proyectos.py IN OUT pom_template.xml application-global.properties

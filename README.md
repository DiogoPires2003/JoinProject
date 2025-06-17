## JoinProject

JoinProject es una aplicación web desarrollada con Django que permite la gestión y registro de datos de salud, facilitando el seguimiento de parámetros clínicos y la colaboración entre profesionales.

---

### 📋 Tabla de contenidos

1. [Descripción del sistema](#descripci%C3%B3n-del-sistema)
2. [Componentes del proyecto](#componentes-del-proyecto)
3. [Diagrama de Arquitectura](#diagrama-de-arquitectura)
4. [Instalación](#instalaci%C3%B3n)

   * [Prerequisitos](#prerequisitos)
   * [Instalación local](#instalaci%C3%B3n-local)
   * [Uso con Docker](#uso-con-docker)
5. [Uso de la aplicación](#uso-de-la-aplicaci%C3%B3n)
6. [Desarrollo y Contribución](#desarrollo-y-contribuci%C3%B3n)
7. [Miembros del Proyecto](#miembros-del-proyecto)
8. [Checklist de Documentación](#checklist-de-documentaci%C3%B3n)
9. [Licencia](#licencia)

---

### Descripción del sistema

JoinProject permite:

* Registrar y consultar datos de salud (presión arterial, frecuencia cardíaca, etc.).
* Generar informes y estadísticas básicas.
* Acceso basado en roles (médico, enfermero, administrador).

**Calidad documental** conforme a ISO/IEC 25000: claridad, completitud y consistencia garantizadas.

---

### Componentes del proyecto

* **betterHealth/**: Lógica principal de la aplicación (modelos, vistas, formularios).
* **healthApp/**: Funcionalidades adicionales y vistas específicas.
* **static/**: Archivos estáticos (CSS, JS, imágenes).
* **templates/**: Plantillas HTML de Django.
* **db.sqlite3**: Base de datos SQLite local.
* **Dockerfile & docker-compose.yml**: Configuración para contenerización.
* **manage.py**: Herramientas de gestión de Django.

---

### Diagrama de Arquitectura

```text
+----------------+     +---------------+      +-------------+
|                |     |               |      |             |
| Navegador WEB  +<--->+ Django Server +<---->+   SQLite    |
| (Front-end)    |     | (Back-end)    |      |  Database   |
|                |     |               |      |             |
+----------------+     +---------------+      +-------------+
```

---

### Instalación

#### Prerequisitos

* Python 3.8+ instalado
* pip
* Docker & Docker Compose (opcional)

#### Instalación local

```bash
# Clonar repositorio
git clone https://github.com/DiogoPires2003/JoinProject.git
cd JoinProject

# Instalar dependencias
echo "Creando entorno virtual..." && python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Migraciones y arranque
env/bin/python manage.py migrate
env/bin/python manage.py runserver
```

Visita `http://127.0.0.1:8000/` en tu navegador.

#### Uso con Docker

```bash
docker-compose build
docker-compose up
```

La aplicación estará disponible en `http://localhost:8000/`.

---

### Uso de la aplicación

1. **Registro de usuario:** Crear cuenta de médico, enfermero o administrador.
2. **Inicio de sesión:** Acceder con tus credenciales.
3. **Gestión de datos:** Añadir, editar o eliminar registros de salud.
4. **Generación de informes:** Exportar resúmenes en PDF (próxima versión).

---

### Desarrollo y Contribución

1. Crea una rama nueva para cada funcionalidad:

   ```bash
   git checkout -b feature/nombre-feature
   ```
2. Realiza cambios y añade tests:

   ```bash
   ```

env/bin/python manage.py test

3. Envía un Pull Request describiendo tu aporte.
4. Se ejecutará la pipeline de CI/CD que incluye tests, métricas y validación de complejidad.

### Miembros del Proyecto

- **Diogo Alves** - [DiogoPires2003](https://github.com/DiogoPires2003)
- **Oriol Farràs** - [Oriol-Farras](https://github.com/Oriol-Farras)
- **Hamza Boulhani** - [Jamshaa](https://github.com/Jamshaa)

---
### Checklist de Documentación

| Ítem                                 | Cumple | Comentarios                                    |
|--------------------------------------|--------|------------------------------------------------|
| Claridad                             | Sí     | Lenguaje accesible y directo                   |
| Estructura                           | Sí     | Secciones bien definidas y numeradas           |
| Completitud                          | Sí     | Incluye instalación, uso, desarrollo y diagrama |
| Consistencia                         | Sí     | Términos coherentes en todo el documento       |
| Trazabilidad                         | Sí     | Enlaces a secciones y referencias claras       |

---
### Licencia

Este proyecto está licenciado bajo la **MIT License**. Consulta el archivo LICENSE para más detalles.

```

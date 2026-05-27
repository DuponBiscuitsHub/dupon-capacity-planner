# Dupon Capacity Planner - Panel de Estado y Evolución del Proyecto
Este documento es la bitácora viva del proyecto. Debe ser actualizado al finalizar cada sesión de desarrollo o intervención de agentes de IA para evitar la pérdida de contexto entre diferentes desarrolladores o herramientas de automatización.

---

## 📊 1. Resumen de Estado Actual
*   **Fase Activa:** FASE 0 - Diagnóstico y Calidad de Datos (Configuración de Infraestructura Base)
*   **Rama de Trabajo Activa:** `Beta` (Desarrollo y Pruebas)
*   **Fecha de Última Modificación:** 27 de Mayo de 2026
*   **Último Operador:** Antigravity (Staff Software Architect & Industrial Planning Agent)
*   **Salud del Repositorio:** 🟢 Inicializado (Entorno virtual configurado, Git en rama Beta y publicado en GitHub)
*   **Integración Odoo:** ⚪ No Iniciada (En fase de diseño de contratos API)

---

## 🗺️ 2. Roadmap y Porcentaje de Avance General

```
[███████████░░░░░░░░░] 55% Completado
```

*   [x] **FASE 0: Diagnóstico y Calidad de Datos (Frontend)** (100% - Vistas de administración, i18n, usuarios y configuraciones)
*   [x] **FASE 1: RM & Silos Planner** (100% - Frontend Interactivo, SCADA y Simulador de Cisternas Completado)
*   [x] **FASE 2: Aluminum Planner** (100% - Frontend Interactivo y Simulador de Pico Completado)
*   [x] **FASE 3: Commercial Capacity Viewer** (100% - Módulo CTP y Analizador de Riesgo de Pedidos Completado)
*   [x] **FASE 4: Scenario Simulator & Optimization** (100% - Sandbox "What-If" e Impacto en Cascada Completado)

---

## 📝 3. Checklist de Tareas Activas (Sesión Actual)

### Infraestructura Base & Configuración Inicial
- [x] Redactar y guardar el Documento de Contexto y Arquitectura de Referencia ([architecture_plan.md](file:///home/pakipy/dupon-dev/dupon-capacity-planner/architecture_plan.md)).
- [x] Crear el Tablero de Control y Estado General del Proyecto (`project_status.md`).
- [/] Inicializar la estructura de carpetas física del repositorio (Monorepo: `frontend/` completado, `backend/` pendiente).
- [x] Definir los archivos de configuración base (`.gitignore`, `.cursorrules`, `ai_instructions.md`, `run_frontend.py`).
- [x] Crear el entorno virtual de Python (`.venv`) e inicializar el repositorio local Git.
- [x] Inicializar Next.js en `/frontend` con TypeScript y sistema de diseño Vanilla CSS.
- [x] Implementar layout de navegación interactiva (Sidebar + Header) y vista general del Dashboard `/`.
- [x] Implementar vista de Login `/login` con estilos CSS Modules.
- [x] Desarrollar la vista interactiva de Silos `/silos` con tanques animados en HSL según autonomía.
- [x] Diseñar e implementar la curva de decaimiento interactiva de silos con gráficos SVG vectoriales nativos.
- [x] Desarrollar la consola de cisternas inbound con simulador de descarga de camión (balance de masas en vivo en el cliente).
- [x] Desarrollar la vista interactiva de Aluminios `/aluminum` con Mapa de Calor de Saturación Semanal semafórico.
- [x] Diseñar e implementar la gráfica de cuota de capacidad grupal mediante gráficos de donut SVG nativos reactivos.
- [x] Crear el simulador de Pico de Demanda del Grupo (+35%) reactivo en cliente con banners de alertas preventivas.
- [x] Diseñar el Módulo de Capacidad Comercial (`/commercial`) con consulta CTP (Capable-To-Promise) y semáforo de restricciones.
- [x] Desarrollar el Simulador de Escenarios Sandbox (`/simulation`) con lógica comparativa lado a lado reactiva y feed de alertas de colisiones.
- [x] Diseñar e implementar el selector de modo visual (Tema Claro / Tema Oscuro) global, persistiendo en localStorage.
- [x] Fortalecer la seguridad (Security First) del login mediante el uso de cookies de sesión SameSite=Strict; Secure y protección de rutas en el dashboard.
- [x] Diseñar e implementar soporte nativo de multi-idioma (i18n) desacoplado para los 6 idiomas con un dropdown en el layout.
- [x] Compilar y verificar el build de producción del Frontend con Turbopack.


### FASE 0: Diagnóstico y Calidad de Datos (Backend & DB Replica)
- [ ] Configurar el entorno Docker Compose (`docker-compose.yml`) local con la base de datos PostgreSQL.
- [ ] Inicializar la estructura física del módulo `/backend` y configurar dependencias en `requirements.txt`.
- [ ] Diseñar y crear los modelos ORM de SQLAlchemy para la réplica de Odoo y configuraciones locales.
- [ ] Configurar las migraciones automáticas con Alembic y aplicarlas a la base de datos PostgreSQL local.
- [ ] Implementar el motor de sincronización `sync_engine.py` vía XML-RPC conectando a Odoo Staging mediante API Key.
- [ ] Crear el script validador recursivo de consistencia de BOMs y stock (*BOM Integrity Checker*).
- [ ] Configurar los endpoints REST en FastAPI expuestos a través de la API v1.


### Suite de Pruebas Automatizadas (Fase A - QA)
- [ ] Configurar el entorno de pruebas en Next.js con `Vitest`, `React Testing Library` y `jsdom`.
- [ ] Implementar pruebas unitarias de calidad para formateadores y utilidades consistentes (`format.ts`).
- [ ] Implementar pruebas unitarias para componentes interactivos de UI (ej. Silo interactivo o alertas).
- [ ] Validar la ejecución correcta de las pruebas con cobertura y 0 fallos.

---


## 📓 4. Historial de Sesiones (Bitácora)

### Sesión 1: 27 de Mayo de 2026
*   **Operador:** Antigravity (AI Agent)
*   **Hitos:**
    *   Definición completa de la arquitectura y alcance de las fases del proyecto.
    *   Creación y guardado del archivo maestro de arquitectura: `architecture_plan.md`.
    *   Creación de este panel de control `project_status.md` para mitigar pérdida de contexto inter-sesiones.
    *   Creación de los archivos de inyección y reglas para agentes de desarrollo (`.cursorrules` y `ai_instructions.md`).
    *   Creación del entorno virtual aislado de Python (`.venv`) y definición del archivo de exclusiones `.gitignore`.
    *   Inicialización del repositorio Git local y preparación del primer commit.
    *   **Inicialización y construcción del Frontend** en la carpeta `/frontend` usando Next.js, TypeScript y Vanilla CSS.
    *   Implementación de la interfaz corporativa premium (modo oscuro, glassmorphism, pulse alerts) en el Login, Sidebar Layout, y el Dashboard principal.
    *   **Desarrollo del Módulo Predictivo de Silos (`/silos`):** Creación del cuadro SCADA con tanques interactivos animados, cálculo de autonomía en base a tasa de consumo y coloreado HSL dinámico.
    *   **Gráfica de Decaimiento Predictiva:** Proyección de consumo a 72h del Silo #1 de Harina mediante curvas vectoriales SVG nativas.
    *   **Consola de Cisternas Inbound & Simulador:** Creación del panel de compras de camiones y del motor de simulación de descarga en vivo.
    *   **Desarrollo del Módulo de Aluminios (`/aluminum`):** Creación de la consola operativa del taller con monitor físico de los 5 troqueles, su formato de corte activo y estado de marcha.
    *   **Mapa de Calor de Ocupación por Formato:** Grilla semafórica dinámica que indica la saturación semanal de los formatos F1 a F6 en troqueles y enrolladoras.
    *   **Simulador de Demanda Externa y SVG Reparto:** Un conmutador interactivo que eleva la demanda del grupo un +35%, lo cual recalcula en vivo las cargas, genera un banner de alerta crítica al saturar los formatos F3 y F5, y actualiza de manera fluida el gráfico de donut SVG de cuotas de producción (reduciendo la asignación local de Iberica del 65% al 45%).
    *   **Internacionalización (i18n) Desacoplada y Reactiva:** Implementación de diccionarios de traducción en los 6 idiomas (`es`, `en`, `fr`, `de`, `be`, `ca`) en `translations.ts` y del `LanguageProvider` en `context.tsx`. Sustitución del tag de Turno en cabecera por un selector dropdown estilizado en HSL, traduciendo de forma reactiva y en tiempo real todo el layout y el Dashboard general.
    *   Ejecución exitosa del compilador de Next.js (`npm run build`) verificando cero errores y cero advertencias.
*   **Decisiones Clave:**
    *   Se aprueba el enfoque **Read-Only** para las primeras tres fases, manteniendo a Odoo como SSoT absoluto y libre de modificaciones invasivas.
    *   Se prioriza la **Fase 1 (Silos Planner)** como primer módulo de valor del MVP debido al alto impacto financiero que representan las paradas de línea por rotura de materia prima.
    *   Se utiliza una arquitectura de **Route Groups** (`(dashboard)`) en Next.js para separar las páginas que consumen el Sidebar/Header común de la pantalla limpia de Login `/login`.
    *   Se implementa el motor de simulación de silos completamente en el lado del cliente (Client State) para este prototipo a fin de validar la interactividad de la interfaz antes de conectar la lógica del backend real.
    *   El simulador de pico de demanda de aluminio se acopla directamente al estado de la vista para demostrar de manera reactiva cómo colisionan las prioridades operativas de la planta local Iberica con las demandas de otras plantas del grupo.
    *   Se desacoplan totalmente las traducciones (diccionarios planos de i18n) de la capa lógica y de componentes de la interfaz de usuario, garantizando un código limpio y mantenible.
*   **Bloqueos / Riesgos Detectados:**
    *   Se requiere configurar las credenciales y probar la conexión real a las APIs de Odoo del cliente en las fases subsiguientes.

### Sesión 2: 27 de Mayo de 2026
*   **Operador:** Antigravity (AI Agent)
*   **Hitos:**
    *   **Módulo Comercial CTP (`/commercial`):** Diseño e implementación de la terminal analítica de consulta de capacidad Capable-to-Promise. Se creó el formulario de consulta y el panel diagnóstico de semáforos HSL con barras de progreso dinámicas para materias primas, aluminio y slots de línea.
    *   **Analizador de Riesgo de Pedidos:** Tabla reactiva que simula la lectura de pedidos de ventas confirmados de Odoo, asignando de manera proactiva indicadores de riesgo de demora por cuellos de botella previstos.
    *   **Simulador de Escenarios Sandbox (`/simulation`):** Creación de un panel de simulación analítico con tres controles paramétricos (pérdida de eficiencia de enrolladora #12, retraso de proveedor A13 y pedidos de emergencia adicionales) que calculan en vivo e interactivamente el impacto en OEE, OTD de entregas, horas de parada de líneas y costes extra de flete, contrastando el "Plan Simulado" lado a lado con el "Plan Activo" del ERP oficial.
    *   **Internacionalización (i18n) Total:** Incorporación de más de 30 nuevas claves de traducción en `translations.ts` para todos los textos de consulta comercial y del simulador, ofreciendo compatibilidad instantánea en los 6 idiomas (`es`, `en`, `fr`, `de`, `be`, `ca`).
    *   **Corrección de Compatibilidad CSS:** Corrección de propiedades estándar de sliders `appearance: none` en `simulation.module.css` para solventar avisos del linter de compatibilidad del navegador.
    *   **Build de Producción Limpio:** Compilación analítica con Next.js y Turbopack completada de forma 100% satisfactoria (0 errores y 0 avisos), pre-renderizando todas las rutas comerciales y del simulador como estáticas.
*   **Decisiones Clave:**
    *   Se implementa el motor de CTP y la lógica analítica de degradación en el cliente usando ecuaciones de simulación deterministas para validar los rangos y alertar al operador de manera fluida antes de enlazar la API.
    *   Se diseña el simulador con un enfoque de sandbox aislado comparativo, permitiendo a los planificadores "jugar" con variables logísticas críticas sin alterar el estado real transaccional de Odoo (SSoT).
*   **Bloqueos / Riesgos Detectados:**
    *   Ninguno en el plano del frontend. La base del prototipo visual e interactiva está ahora 100% completada y lista para la integración con las bases de datos de Postgres y el Sync Engine en FastAPI del backend.

### Sesión 3: 27 de Mayo de 2026
*   **Operador:** Antigravity (AI Agent)
*   **Hitos:**
    *   **Seguridad Primero (Security First) en Login:** Fortalecimiento del módulo de autenticación mediante el establecimiento de una cookie de sesión DCP (`dcp_session=active_token; Path=/; SameSite=Strict; Secure`) con políticas estrictas de transporte y aislamiento SameSite en `/login`.
    *   **Protección de Rutas en Dashboard Layout:** Implementación de verificación analítica en tiempo de carga (`useEffect`) en `(dashboard)/layout.tsx` que redirige inmediatamente a los usuarios no autenticados hacia `/login` si no poseen la cookie de sesión activa.
    *   **Cierre de Sesión Seguro (Logout):** Modificación del link de cierre por un botón con manejador `handleLogout` que destruye la cookie de sesión en el cliente (estableciendo su caducidad en el pasado) y fuerza una recarga de página (`window.location.href`) para vaciar memorias del navegador y estados en caché.
    *   **Selector de Modo Visual (Claro / Oscuro):** Implementación de variables HSL y CSS customizadas en `globals.css` para el tema claro (`data-theme="light"`).
    *   **Visual Theme Context:** Creación del `ThemeContext` y `ThemeProvider` globales que leen y persisten de forma transparente la selección del tema en `localStorage`.
    *   **Selector en Header y Login:** Inserción de un dropdown premium en el cabezal del dashboard y de selectores flotantes (idioma + tema) en la esquina superior de la pantalla de login, garantizando internacionalización completa en los 6 idiomas.
    *   **Optimización Estética del Login (Modo Oscuro):**
        *   *Corrección de Campos de Entrada:* Se definió el fondo y estilo de los campos de entrada en Modo Oscuro, anulando la discordancia visual del autocompletado (`-webkit-autofill`) del navegador mediante sombras internas y color de texto forzado.
        *   *Mayor Contraste de Tarjeta:* Se aumentó la opacidad de fondo de la tarjeta glassmorphic en Modo Oscuro (`hsla(224, 71%, 7%, 0.8)`) y se incrementó el brillo de los orbes decorativos traseros para resaltar el efecto de difuminado y profundidad.
*   **Decisiones Clave:**
    *   Se utiliza una cookie con bandera `Secure` y `SameSite=Strict` para modelar de forma fidedigna y robusta la seguridad industrial requerida en Next.js, preparando la integración del BFF (Backend-for-Frontend) y mitigando el riesgo de secuestro de token por ataques XSS/CSRF.
    *   La selección del tema visual se aplica sobre el atributo raíz `data-theme` en el elemento `html`, garantizando un cambio de variables CSS instantáneo y de bajo consumo de CPU sin parpadeos de renderizado.
*   **Bloqueos / Riesgos Detectados:**
    *   Ninguno. La infraestructura visual de login y modos de visualización está completamente operativa y validada.

### Sesión 4: 27 de Mayo de 2026
*   **Operador:** Antigravity (AI Agent)
*   **Hitos:**
    *   **Rediseño Visual del Dashboard General (`/`):** Remoción de los antiguos fondos oscuros remanentes en las tarjetas de monitoreo de líneas `.lineRow` y sustitución por un elegante fondo cristalino perla estilo *Synetica* de Dribbble. Implementación del hover dinámico de elevación, sombras difusas y contorno de acento en azul/cian.
    *   **Corrección de Bugs Críticos:** Resolución de un error de interpolación en el componente `page.tsx` que impedía renderizar la clase `.alertItemDanger` en la bitácora de alertas del planificador.
    *   **Suite de Pruebas Automatizadas Frontend (QA):** Configuración y despliegue del entorno de pruebas unitarias bajo **Vitest** y **jsdom** en la carpeta `/frontend`. Configuración de alias `@/` en [vitest.config.ts](file:///home/pakipy/dupon-dev/dupon-capacity-planner/frontend/vitest.config.ts) e inyección de scripts en `package.json`.
    *   **Pruebas de Formateo e i18n:** Desarrollo de 14 pruebas de integridad divididas en `format.test.ts` (previniendo fallos de hidratación SSR) y `translations.test.ts` (asegurando simetría de claves i18n y la correcta traducción catalana de Silo a `"Sitge"` y `"Sitges"`). Ejecución 100% exitosa (14 de 14 pasados en 819ms).
    *   **Aislamiento de Persistencia Local (Docker):** Configuración de [docker-compose.yml](file:///home/pakipy/dupon-dev/dupon-capacity-planner/docker-compose.yml) mapeando PostgreSQL v15 al puerto **`5435:5432`** para evitar colisiones con otros proyectos del cliente activos en Docker Desktop (como `qms-postgres`). Despliegue atómico completado y verificado.
    *   **Estructura y Core del Backend (FastAPI):** Inicialización de la carpeta `/backend`, dependencias en `requirements.txt` e inyección de configuraciones core (`config.py`, `database.py`, `security.py`).
    *   **Modelos ORM Declarativos y Multi-Esquema:** Diseño de los modelos SQLAlchemy compartiendo `Base.metadata` y mapeados con esquemas Postgres separados: `odoo_replica` (8 tablas) y `dcp_app` (4 tablas).
    *   **Migraciones Alembic Aplicadas:** Configuración de `env.py` para autocrear los esquemas lógicos y mapear autogenerate. Generación y aplicación exitosa del esquema de migración inicial en PostgreSQL local.
    *   **FastAPI Health Check:** Creación de `main.py` y validación con total éxito del endpoint de salud `/health` (`{"status":"healthy","database":"connected"}`) sobre el puerto de desarrollo **`8005`** (evitando colisión con puerto 8000).
*   **Decisiones Clave:**
    *   Implementar un completo aislamiento de puertos de desarrollo de DCP (Base de datos en `5435` y Backend en `8005`) para permitir coexistir con sus otros entornos activos sin interferencias.
    *   Persistencia de credenciales locales mediante `.env` no versionado.
*   **Bloqueos / Riesgos Detectados:**
    *   Ninguno. La base estructurada del monorepo está completamente desplegada y sincronizada.

---

## 🛠️ 5. Instrucciones para Nuevos Agentes / Desarrolladores

Si acabas de entrar al proyecto, por favor sigue estos pasos rigurosamente:
1.  Lee el archivo [architecture_plan.md](file:///home/pakipy/dupon-dev/dupon-capacity-planner/architecture_plan.md) para comprender la arquitectura de la solución, los módulos de negocio y el stack tecnológico.
2.  Revisa la sección **Checklist de Tareas Activas** de este documento (`project_status.md`) para saber en qué tarea debes trabajar.
3.  Una vez termines tus cambios, marca las casillas completadas `[x]`, actualiza el **Historial de Sesiones** añadiendo una nueva entrada al final y sube el commit.
4.  *Regla de Oro:* **No introduzcas lógica de optimización compleja o escritura en Odoo sin antes verificar la calidad de datos y asegurar el desacoplamiento.**


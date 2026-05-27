# Dupon Capacity Planner
## Documento de Contexto, Arquitectura y Desarrollo de Sistema
**Versión:** 1.0.0  
**Fecha:** 27 de Mayo de 2026  
**Autor:** Staff Software Architect & Industrial Planning Expert  
**Estado:** Propuesta de Arquitectura de Referencia  

---

## 1. Visión del Proyecto

El **Dupon Capacity Planner (DCP)** es concebido como el "cerebro analítico externo" acoplado a Odoo. En entornos industriales de manufactura discreta y de proceso continuo como el de Dupon, los sistemas ERP tradicionales (como Odoo) sobresalen en el registro transaccional y administrativo (compras, inventarios, órdenes de producción, facturación), pero carecen de la capacidad de cómputo reactivo y simulación dinámica en tiempo real que exige un **APS (Advanced Planning System)**.

El DCP actúa como una capa desacoplada de inteligencia operacional que extrae el estado transaccional de Odoo y, mediante modelos matemáticos de balance de masas y algoritmos de optimización de restricciones de capacidad, proporciona visibilidad predictiva, capacidad de simulación "What-If" y heurísticas de optimización para la cadena de suministro. El sistema transiciona las decisiones de planificación desde una metodología reactiva basada en hojas de cálculo hacia una operativa proactiva gobernada por datos continuos.

---

## 2. Objetivos de Negocio

El éxito de la implantación del Dupon Capacity Planner se medirá en función del impacto directo en las operaciones y la cuenta de resultados (P&L):

*   **Reducción del Lead Time Total:** Reducir la variabilidad de entrega del producto final A17 mediante la sincronización del suministro del semielaborado de aluminio (A15/A16) y materias primas críticas.
*   **Garantía de Continuidad Operativa (Zero Stockouts):** Mitigar por completo las paradas de línea por rotura de stock de materias primas críticas (harina, azúcar, aceite de coco) mediante la predicción matemática del punto de ruptura con un margen mínimo de 72 horas.
*   **Optimización de Logística Inbound:** Minimizar los costes de transporte y demurrage recomendando ventanas óptimas (fecha y hora) para la descarga de camiones cisternas de materias primas, maximizando la capacidad útil de los silos sin provocar sobrefrenado.
*   **Incremento del OEE en Troquelado y Enrollado:** Optimizar el secuenciamiento en los 5 troqueles y 34 enrolladoras para reducir los tiempos de cambio de formato (setup times) y la saturación de cuellos de botella.
*   **Maximización de la Capacidad Comercial Vendible:** Habilitar un modelo CTP (*Capable-to-Promise*) fiable para el equipo comercial, identificando con precisión slots de capacidad libres para capturar demanda incremental sin comprometer las fechas de entrega de pedidos existentes.

---

## 3. Problemas que Resuelve

El DCP elimina los siguientes cuellos de botella sistémicos y organizacionales:

```
[Datos Odoo] ──(Desconexión Dinámica)──> [Silobolsas / Planta] ──> Decisión Reactiva
     │                                           ▲
     └───────> [Dupon Capacity Planner] ─────────┘ (Planificación Predictiva)
```

1.  **Desconexión entre el Inventario Estático y el Consumo Dinámico:** Odoo registra cuánto stock de harina/azúcar hay "ahora", pero no proyecta la curva de decaimiento en función de la velocidad real de las líneas de galleta activas, turnos de trabajo, rendimientos históricos y tasa de scrap por receta.
2.  **Ceguera en la Cadena del Aluminio (A13 ➔ A17):** El cuello de botella en los formatos de aluminio y la distribución de capacidad de troquelado/enrollado para plantas hermanas genera retrasos que Odoo no puede predecir al planificar con tiempos de espera estáticos (*lead times fijos*).
3.  **Incapacidad de Simular Escenarios Operativos:** Si un troquel crítico falla o si el proveedor de bobinas A13 retrasa una entrega 5 días, los planificadores actualmente no tienen forma de simular el impacto en cascada sobre los pedidos de clientes finales A17 si no es mediante simulaciones manuales propensas a errores.
4.  **Saturación Logística en Recepción de Materias Primas:** La falta de una ventana horaria predictiva de entrega provoca que coincidan múltiples camiones de harina en planta, superando la capacidad de recepción física o forzando esperas costosas.

---

## 4. Arquitectura de Alto Nivel

El sistema se diseña bajo un patrón de **Arquitectura Desacoplada de Lectura Optimizada**. Dado que el ERP Odoo es el *Single Source of Truth* (SSoT), el Capacity Planner no competirá por recursos de base de datos con el transaccional de Odoo. 

```
┌────────────────────────────────────────────────────────────────────────┐
│                              Nube (GCP)                                │
│                                                                        │
│  ┌───────────────┐        ┌──────────────┐         ┌────────────────┐  │
│  │ Odoo ERP      │        │ Cloud Run    │         │ Cloud Run      │  │
│  │               │        │              │         │                │  │
│  │ (SSoT)        │        │ Sync Engine  │         │ FastAPI Backend│  │
│  └───────┬───────┘        └──────┬───────┘         └──────┬─────────┘  │
│          │ XML-RPC               │  SQL Write             │  JSON API  │
│          │ / REST                ▼                        ▼            │
│          │                ┌──────────────┐         ┌────────────────┐  │
│          └───────────────>│ Cloud SQL    │────────>│ Next.js SPA    │  │
│                           │ (PostgreSQL) │  Read   │                │  │
│                           └──────────────┘         └────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

### Componentes Principales:
1.  **Odoo Sync Engine (FastAPI/Python Background Worker):** Servicio ligero encargado de sincronizar delta-changes desde Odoo de manera asíncrona hacia la base de datos del DCP. Utiliza llamadas paginadas y optimizadas para evitar degradar el rendimiento de Odoo.
2.  **DCP Database (Cloud SQL - PostgreSQL):** Base de datos relacional optimizada para lectura analítica. Almacena réplicas de las tablas críticas de Odoo (BOMs, rutas, stock, órdenes de producción, pedidos) y los datos de configuración específicos del planificador (capacidades de troqueles, silos, parámetros de simulación).
3.  **APS Engine & FastAPI Backend (Python):** El núcleo analítico. Contiene los motores de cálculo (Mass Balance Engine para silos y Constraint Programming / Heuristic Solver para aluminio). Expone una API REST limpia y documentada bajo OpenAPI/Swagger.
4.  **DCP Frontend (Next.js + TypeScript):** Interfaz de usuario rica y de alta densidad de información. Diseñada con un enfoque de consola de control industrial (tablas dinámicas, diagramas de Gantt interactivos, curvas de consumo de silos predictivas y paneles de simulación paramétrica).

---

## 5. Filosofía Técnica

*   **Odoo como Única Fuente de Verdad (SSoT):** Toda la información estructural y transaccional reside en Odoo. El DCP lee de Odoo y procesa localmente. Inicialmente, no escribe datos de vuelta para evitar riesgos transaccionales y facilitar una implementación rápida (Fases 0 a 3 en modo lectura).
*   **Diseño Cloud-Native y Serverless:** El backend y el frontend se empaquetan en contenedores Docker y se despliegan en **Google Cloud Run**. Esto garantiza alta disponibilidad, escalabilidad a cero cuando no se usa (reducción de costes de infraestructura) y despliegues atómicos sin fricción.
*   **Modularidad Estricta y Desacoplamiento (DDD):** El backend se estructura siguiendo principios de *Domain-Driven Design (DDD)* simplificado. El dominio de "Aluminios" y el de "Silos" son independientes en lógica de negocio, compartiendo únicamente la capa de infraestructura y datos base de Odoo a través de contratos e interfaces bien definidas.
*   **Simplicidad sobre Complejidad:** Se prioriza la legibilidad del código. Los motores de cálculo iniciales utilizarán ecuaciones algebraicas deterministas explícitas antes de delegar en motores de optimización matemática complejos (como solucionadores MILP o heurísticas avanzadas).
*   **Soporte Multicompañía Nativo (Multi-company):** Dado que el entorno Odoo opera con múltiples razones sociales/fábricas, el DCP es multicompañía por diseño. Toda transacción, stock, BOM o MO replicada se asocia a su respectivo `company_id`. El backend segmenta los cálculos por compañía y el frontend ofrece un selector global en el cabezal para conmutar el contexto operacional dinámicamente.
*   **Arquitectura de Internacionalización (i18n) desde el Origen:** El sistema provee soporte nativo para los seis idiomas definidos: **Español (es), Inglés (en), Francés (fr), Alemán (de), Belga (nl-be) y Catalán (ca)**. El Frontend implementa un `LanguageProvider` basado en contexto para conmutar diccionarios de traducción de forma instantánea sin penalizar la velocidad de renderizado.

---

## 6. Restricciones y Principios

Aplicamos de forma estricta el orden de precedencia establecido: **Seguridad > Correctitud > Simplicidad > Mantenibilidad > Elegancia > Optimización**.

1.  **Cero Modificaciones Críticas en Odoo:** No se instalarán módulos customizados pesados dentro de Odoo para el funcionamiento del planificador. Toda la lógica analítica se ejecuta fuera del ERP. Odoo solo expone sus APIs estándar (XML-RPC o REST nativa).
2.  **Seguridad Industrial y de Datos (Security by Design):**
    *   **Cifrado en Tránsito:** Toda comunicación entre el DCP y Odoo, y entre el DCP Backend y Frontend, se realiza bajo cifrado estricto TLS 1.3 (HTTPS / WSS).
    *   **Gestión de Secretos:** No se almacenan contraseñas en texto plano, tokens de Odoo ni secretos en el repositorio ni en archivos de entorno del contenedor. Se utiliza **GCP Secret Manager** para inyectar credenciales de base de datos y APIs en tiempo de ejecución.
    *   **Autenticación Robusta:** El Backend de FastAPI autentica las sesiones mediante tokens JWT (*JSON Web Tokens*) firmados con algoritmos asimétricos (RS256) o HMAC-SHA256 con claves rotativas de 256 bits.
    *   **Manejo Seguro de Cookies (Seguridad Web Obligatoria):** Las sesiones se gestionan mediante cookies de estado protegidas con las banderas **`HttpOnly`** (evitando robos por scripts XSS), **`Secure`** (restringiendo el envío solo sobre HTTPS) y **`SameSite=Strict`** (mitigando ataques de falsificación de peticiones en sitios cruzados o CSRF).
    *   **Validación y Sanitización en Fronteras:** Todo input recibido en los endpoints de FastAPI se valida estrictamente mediante esquemas **Pydantic** para bloquear cargas maliciosas. Las consultas a PostgreSQL se parametrizan obligatoriamente a través del ORM (SQLAlchemy) para erradicar cualquier vector de inyección SQL.
3.  **Control de Acceso Basado en Roles (RBAC):**
    El sistema restringe privilegios basándose en roles explícitos definidos en la base de datos de usuarios del DCP:
    *   `admin`: Control total del sistema, administración de credenciales de Odoo, y configuraciones del Sync Engine.
    *   `planner`: Acceso operativo a Silos y Aluminios, capacidad de crear simulaciones Sandbox y modificar eficiencias teóricas.
    *   `commercial`: Visibilidad exclusiva del Dashboard general e interfaz de consulta CTP (Capable-to-Promise) para verificar fechas factibles de entrega de ventas.
    *   `viewer`: Vista de lectura estricta de paneles y pantallas en planta (diseñado para monitores informativos).
4.  **Read-Only por Diseño Fases Iniciales:** Bajo ningún concepto el MVP realizará escrituras destructivas ni modificaciones directas en el inventario o producción de Odoo. Cualquier recomendación del planificador será ejecutada manualmente por el operador en Odoo, garantizando el control humano (*human-in-the-loop*).
5.  **Consistencia del Balance de Masas:** Los cálculos de consumo de silos deben respetar la ley de conservación de la materia, teniendo en cuenta factores de merma estocásticos parametrizables (scrap) y eficiencias reales por línea, evitando la subestimación de consumo.

---

## 7. Roadmap por Fases

El proyecto está diseñado para mitigar el riesgo de implantación mediante entregables de valor incremental:

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   FASE 0     │ ───> │    FASE 1    │ ───> │    FASE 2    │ ───> │    FASE 3    │ ───> │    FASE 4    │
│ Diagnóstico  │      │ RM & Silos   │      │ Aluminum     │      │ Commercial   │      │ Simulator &  │
│ Calidad Datos│      │ Planner      │      │ Planner      │      │ Cap. Viewer  │      │ Optimization │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
```

### Fase 0: Diagnóstico y Calidad de Datos (Semanas 1-4)
*   **Objetivo:** Validar la integridad de los datos de Odoo y establecer la infraestructura base.
*   **Entregables:** Pipeline de extracción de datos, auditoría automática de BOMs e inventarios en Odoo, base de datos Postgres inicial y esqueleto del backend/frontend.

### Fase 1: RM & Silos Planner (Semanas 5-10)
*   **Objetivo:** Visibilidad predictiva del consumo de harina, azúcar y aceite de coco.
*   **Entregables:** Dashboard de estado de silos, curvas predictivas de stockouts, recomendador automático de horarios de camiones cisternas.

### Fase 2: Aluminum Planner (Semanas 11-18)
*   **Objetivo:** Planificación de la transformación de aluminio (A13 ➔ A15/A16 ➔ A17).
*   **Entregables:** Módulo de capacidad para los 5 troqueles y 34 enrolladoras por formato, alertas de riesgo de ruptura de envoltorios y distribución de carga de planta Iberica vs otras plantas.

### Fase 3: Commercial Capacity Viewer (Semanas 19-24)
*   **Objetivo:** Visibilidad de capacidad comercial disponible para ventas.
*   **Entregables:** Módulo de consulta CTP (*Capable-to-Promise*) para comerciales con visualización de cuellos de botella por formato o materia prima.

### Fase 4: Scenario Simulator & Optimization (Semanas 25+)
*   **Objetivo:** Simulación interactiva "What-If" y optimización automática.
*   **Entregables:** Entorno de simulación de escenarios (caída de máquinas, picos de demanda, retraso de proveedores) y secuenciador optimizado mediante algoritmos heurísticos.

---

## 8. Descripción Detallada de cada Módulo

### 8.1. Módulo de Diagnóstico y Calidad de Datos (Fase 0)
Este módulo actúa como el guardián de la integridad de los datos del sistema. Si los datos en Odoo contienen errores (ej. BOMs desactualizadas, registros de stock desfasados), cualquier software de planificación fallará (*Garbage In, Garbage Out*).

*   **Funcionalidades:**
    *   **Data Quality Engine:** Validador de consistencia que detecta discrepancias en Odoo (ej. órdenes de producción activas sin materias primas asignadas, rutas con tiempo cero, falta de registros de stock en ubicaciones clave).
    *   **BOM Integrity Checker:** Analiza de forma recursiva las listas de materiales desde A17 hasta A13 buscando bucles infinitos, componentes huérfanos o desfases de rendimientos teóricos.
    *   **Sync Monitor:** Panel administrativo que muestra la latencia de la réplica de datos de Odoo y el estado de salud de las APIs.

### 8.2. RM & Silos Planner (Fase 1)
Previene la parada de las líneas de producción de galleta garantizando el flujo constante de materias primas pesadas (harina, azúcar, aceite de coco).

```
   ┌─────────────────────────────────────────────────────────────┐
   │                  Modelo de Balance de Masas                 │
   │                                                             │
   │  Consumo Predictivo = Σ ( L_activa * Velocidad_std *        │
   │                          Eficiencia_std * (1 + Scrap_est) ) │
   └──────────────────────────────┬──────────────────────────────┘
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │             Cálculo de Punto de Rotura (t_ruptura)          │
   │                                                             │
   │  Silo_Niveles(t) = Niveles_Actuales - ∫ Consumo(t) dt       │
   └──────────────────────────────┬──────────────────────────────┘
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                  Recomendación de Camión                    │
   │                                                             │
   │  Ventana Óptima = t_ruptura - Lead_Time_Logístico           │
   │  Volumen = Capacidad_Máx_Silo - Niveles(t_llegada)          │
   └─────────────────────────────────────────────────────────────┘
```

*   **Modelo de Balance de Masas Matemático:** El consumo predictivo de cada silo $S_i$ en el instante $t$ se calcula mediante la fórmula:
    $$Consumo_{S_i}(t) = \sum_{l \in L_{activas}(t)} (C_{prod(l)} \times V_{l} \times \eta_{l} \times (1 + \sigma_{prod(l)}))$$
    Donde:
    *   $L_{activas}(t)$: Líneas de galleta planificadas como activas en el instante $t$.
    *   $C_{prod(l)}$: Consumo unitario de la materia prima según la BOM del producto asignado a la línea $l$.
    *   $V_{l}$: Velocidad de la línea (unidades/hora).
    *   $\eta_{l}$: Eficiencia operativa esperada de la línea (basada en históricos de OEE).
    *   $\sigma_{prod(l)}$: Coeficiente de scrap/merma específico del producto y línea.
*   **Funcionalidades Clave:**
    *   **Curva Predictiva de Decaimiento:** Gráfica temporal que proyecta el volumen remanente en los silos (3 silos de harina de 25 t, 1 de azúcar de 30 t, 1 de aceite de coco) contra el tiempo de producción planificado.
    *   **Truck Scheduler Advisor:** Algoritmo heurístico que calcula la ventana óptima de entrega para los camiones cisterna. Recomienda el envío de manera que el camión pueda descargar en su totalidad (evitando que el camión tenga que regresar con carga parcial debido a falta de espacio físico en el silo) pero con un margen de seguridad de stock de 4 horas antes de la rotura técnica.

### 8.3. Aluminum Planner (Fase 2)
Gestiona la cadena interna de valor del aluminio para el envoltorio de la galleta (A13 ➔ A15 ➔ A16 ➔ A17).

```
   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
   │  Proveedor   │ ───> │ 5 Troqueles  │ ───> │34 Enrolladoras│───> │Galleta A17   │
   │  Bobina A13  │      │ Semielab A15 │      │ EnvoltorioA16│      │Prod. Final   │
   └──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
```

*   **Restricciones de Máquinas:**
    *   **Troquelado:** 5 troqueles físicos con restricciones de compatibilidad por formato (6 formatos principales). Los tiempos de cambio de formato (setup times) varían según la matriz a instalar.
    *   **Enrollado:** 34 enrolladoras con límites de velocidad, capacidad de bobinado y eficiencia de corte.
*   **Funcionalidades Clave:**
    *   **Multi-Plant Allocation Engine:** Controla y planifica la demanda interna de aluminio no solo para la planta local (Iberica) sino también para las demandas externas de otras plantas del grupo que consumen bobinas producidas localmente.
    *   **Format Saturation Heatmap:** Matriz de colores (Verde/Amarillo/Rojo) que identifica cuellos de botella proyectados en los troqueles por formato, alertando si la demanda de un formato específico supera la capacidad nominal agregada en la semana de planificación.
    *   **Rupture Risk Alert:** Alertas automáticas cuando el inventario proyectado de un sleeve específico (A16) cae por debajo del lead time de troquelado + enrollado necesario para reponerlo antes de su consumo programado en la línea de ensamble A17.

### 8.3. Commercial Capacity Viewer (Fase 3)
Transforma los datos complejos de planificación en una interfaz interactiva de consulta ágil para el equipo de ventas.

*   **Funcionalidades Clave:**
    *   **Capable-to-Promise (CTP) Engine:** A diferencia del simple *Available-to-Promise* (ATP), el motor CTP simula la inserción de un nuevo pedido en el plan de producción actual para verificar si:
        1.  Hay capacidad disponible en las líneas de ensamble.
        2.  Hay suficiente capacidad de troquelado y enrollado de aluminio para el formato requerido.
        3.  Las materias primas necesarias se encuentran en stock o pueden comprarse dentro del lead time estándar sin desplazar pedidos existentes.
    *   **Saturación por Formato/Producto:** Reporte visual que indica qué familias de productos están saturadas para los próximos meses, permitiendo al equipo comercial redirigir las campañas de venta hacia formatos con capacidad ociosa.
    *   **Order Delivery Risk Analyzer:** Panel que escanea de forma proactiva todos los pedidos de venta confirmados en Odoo y marca con bandera roja aquellos que tienen riesgo de retraso debido a un desabastecimiento de componentes o saturación en las fases previas.

### 8.4. Scenario Simulator & Optimization (Fase 4)
Proporciona la capacidad de jugar con el futuro y optimizar la toma de decisiones complejas mediante modelos avanzados.

*   **Simulador "What-If" Paramétrico:** Permite al planificador clonar el plan activo en un sandbox aislado y realizar modificaciones interactivas:
    *   *¿Qué pasa si la enrolladora #12 se detiene por mantenimiento preventivo 3 días?*
    *   *¿Qué pasa si entra un pedido de emergencia de 50.000 unidades de A17 formato F3 para el próximo martes?*
    *   *¿Qué pasa si el proveedor de A13 declara fuerza mayor y retrasa los despachos una semana?*
    El sistema recalcula instantáneamente todas las curvas de silos, la saturación de aluminios y el riesgo de entregas del resto de pedidos, mostrando una comparativa de costes e indicadores de servicio (OTD).
*   **Secuenciador y Optimizado de Producción (APS Engine):** Algoritmo heurístico de programación por restricciones (Constraint Programming) que lee las órdenes de fabricación pendientes y propone una secuencia de paso por troqueles y enrolladoras que minimiza los tiempos totales de cambio de formato (Setup Times) y maximiza el rendimiento global de la sección de aluminio.

---

## 9. Riesgos Técnicos y Mitigaciones

| Riesgo Técnico | Impacto | Probabilidad | Mitigación |
| :--- | :--- | :--- | :--- |
| **Latencia y saturación de API de Odoo:** Consultas concurrentes desde el planificador degradan la transaccionalidad de ventas y almacén en Odoo. | Alto | Alta | **Sync asíncrono desacoplado:** El DCP nunca consulta a Odoo en tiempo real para las vistas de usuario. El `Sync Engine` realiza volcados periódicos programados (ej. cada 15 min para datos volátiles, 1 vez al día para datos estáticos) hacia PostgreSQL, el cual sirve las consultas del Frontend. |
| **Complejidad combinatoria (NP-Hard) en Fase 4:** El secuenciamiento de 34 enrolladoras con cambios de formato puede provocar *timeout* del motor de optimización. | Medio | Alta | **Heurísticas acotadas y Greedy Algorithms:** No intentar resolver la optimización global óptima matemática de inmediato. Implementar metaheurísticas simplificadas (búsqueda tabú local, algoritmos genéticos limitados a 10 segundos de ejecución) para dar soluciones "suficientemente buenas" rápido. |
| **Inconsistencias de datos de inventario en Odoo:** Stock virtual en ERP no coincide con la realidad física (desfases en silos). | Alto | Alta | **Tolerancia y calibración manual:** El sistema permitirá a los planificadores realizar un "override" manual de inventario inicial de silos directamente en el DCP si detectan una desviación, notificando a Odoo para su corrección administrativa. |
| **Deriva en las tasas de scrap y OEE:** Los rendimientos reales en planta varían estacionalmente o por temperatura, alterando las predicciones del balance de masas de silos. | Medio | Media | **Modelos adaptativos sencillos:** El sistema calculará una media móvil indexada de la eficiencia real por máquina de los últimos 30 días para auto-ajustar los parámetros de velocidad y scrap dentro de las ecuaciones de balance de masas. |

---

## 10. Riesgos de Negocio y Mitigaciones

| Riesgo de Negocio | Impacto | Probabilidad | Mitigación |
| :--- | :--- | :--- | :--- |
| **Baja adopción por los planificadores:** Los usuarios abandonan la herramienta y regresan a sus archivos Excel locales históricos. | Crítico | Alta | **Diseño UX centrado en Planner:** Involucrar a los planificadores desde la Fase 0 en el diseño de las pantallas. El sistema debe permitir la exportación rápida a Excel y el diseño de la UI debe imitar el flujo mental de planificación de la fábrica. |
| **"Garbage In, Garbage Out":** Decisiones erróneas tomadas por el planificador debido a que las recetas (BOM) en Odoo tienen errores de formulación teórica. | Crítico | Media | **Fase 0 obligatoria de Data Quality:** Bloquear el avance de las fases si el reporte de calidad de datos de la Fase 0 muestra indicadores de salud de BOMs por debajo del 98%. |
| **Falta de alineación comercial-operaciones:** El equipo de ventas satura el sistema con consultas CTP ficticias distorsionando las prioridades reales de producción. | Bajo | Media | **Políticas de cuotas de simulación:** Separar claramente los entornos de simulación de ventas de la planificación real de producción, y establecer niveles de visibilidad limitados para el área comercial. |

---

## 11. Datos Necesarios desde Odoo

Para el correcto funcionamiento de los algoritmos de planificación del DCP, se requiere mapear y sincronizar de forma sistemática los siguientes modelos de datos de Odoo:

```
                  ┌──────────────────────────────────────────┐
                  │                 Odoo ERP                 │
                  └────────────────────┬─────────────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
  [Datos de Ventas]           [Datos de Producción]        [Datos de Inventario]
  - Pedidos de Venta (SO)     - Órdenes de Fabricación (MO) - Niveles de Stock Real
  - Fechas de Entrega         - Rutas de Trabajo           - Ubicaciones Físicas
  - Estado del Pedido         - Tiempos Estándar Setup     - Recepciones Pendientes (PO)
```

1.  **Datos Estáticos (Configuración y Estructura):**
    *   `mrp.bom` (Listas de Materiales): Componentes necesarios para A17, A16, A15 y ratios de consumo teórico.
    *   `mrp.bom.line`: Líneas de detalle de la BOM que vinculan materias primas y mermas estimadas.
    *   `mrp.workcenter` (Centros de Trabajo): Datos de los 5 troqueles y 34 enrolladoras (capacidad nominal, costes horario, eficiencias teóricas).
    *   `mrp.routing.workcenter` (Hojas de Ruta): Operaciones secuenciales necesarias para procesar el aluminio y ensamblar la galleta.
2.  **Datos Transaccionales Dinámicos:**
    *   `stock.quant` (Inventario Actual): Niveles de stock en tiempo real de harina, azúcar, aceite de coco, bobinas A13, aluminio semielaborado A15, mangas A16 y producto final A17, desglosado por ubicación física (*locations*).
    *   `mrp.production` (Órdenes de Fabricación - MOs): Órdenes planificadas, en progreso y confirmadas, incluyendo cantidades pedidas, fechas de inicio programadas y prioridad.
    *   `sale.order` y `sale.order.line` (Pedidos de Venta - SOs): Demandas de clientes finales para A17 con sus respectivas fechas comprometidas de entrega (*delivery dates*).
    *   `purchase.order` y `purchase.order.line` (Órdenes de Compra - POs): Entradas programadas de materias primas críticas (camiones de harina, azúcar, aceite de coco) y bobinas A13 con fechas de recepción estimadas del proveedor.

---

## 12. Qué NO hacer en las Primeras Fases

Para evitar la sobreingeniería y garantizar el éxito del proyecto, se definen estrictas exclusiones para las Fases 0, 1 y 2:

*   **NO implementar escritura automática en Odoo:** El sistema operará estrictamente en **modo lectura**. No creará órdenes de compra, no modificará las órdenes de producción existentes directamente en Odoo, ni cambiará estados de stock de forma automatizada.
*   **NO utilizar Inteligencia Artificial compleja para la secuenciación:** Evitar modelos de Deep Learning, redes neuronales o algoritmos genéticos altamente parametrizados de entrada. Un secuenciador heurístico determinista básico o programación lineal entera (MILP) bien acotada es infinitamente más fácil de depurar, predecible y suficiente para la escala inicial del negocio.
*   **NO conectar sensores de silos IoT directamente en esta capa:** La medición física de los silos por ultrasonido/radar debe consolidarse primero en un sistema SCADA/PLC local o en el propio Odoo. El planificador consumirá el dato consolidado del inventario de Odoo, evitando gestionar protocolos industriales en tiempo real (Modbus, OPC-UA) de forma directa en el backend web.
*   **NO crear un sistema de gestión multi-bodega complejo externo:** Toda la lógica de almacenes lógicos y físicos debe ser gobernada por las reglas de Odoo. El planificador solo consumirá la foto del inventario en las ubicaciones parametrizadas como "silos de producción" u "oficina de aluminio".

---

## 13. MVP Recomendado (Minimum Viable Product)

El MVP se centrará exclusivamente en resolver la mayor fuente de riesgo operativo actual de la planta: **La parada de líneas de galleta por rotura de stock en silos.**

### Alcance del MVP:
1.  **Fase 0 (Calidad de datos):** Conexión vía API asíncrona a Odoo para descargar estructuras BOM de A17 y niveles de stock de harina, azúcar y aceite de coco.
2.  **Fase 1 (Silos Planner):**
    *   Pantalla principal interactiva con el nivel actual de los 5 silos críticos.
    *   Algoritmo algebraico de balance de masas que proyecta el consumo dinámico a 7 días vista basado en las órdenes de producción programadas en Odoo.
    *   Generador automático de alertas de rotura técnica de stock (tiempo restante hasta vaciado).
    *   Generador automático de recomendaciones de entrega de camiones cisterna indicando: *Fecha recomendada, hora recomendada y cantidad máxima a descargar*.

### Justificación:
Este MVP tiene un coste de desarrollo bajo, un riesgo técnico mínimo, no requiere lógica de optimización compleja y aporta un retorno de inversión (ROI) inmediato al erradicar las paradas no programadas por falta de materias primas.

---

## 14. Posibles Evoluciones Futuras

Una vez estabilizado el sistema y completadas las 5 fases iniciales, el DCP podrá evolucionar en las siguientes direcciones:

1.  **Bucle Cerrado (Closed-Loop APS):** Habilitar el canal de escritura seguro hacia Odoo para permitir que el planificador pueda:
    *   Reprogramar directamente en Odoo las fechas de inicio de las Órdenes de Fabricación (MO) una vez optimizada la secuencia de aluminio.
    *   Generar solicitudes de compra automáticas (*purchase requisitions*) para bobinas de aluminio A13 cuando el planificador detecte riesgo de ruptura.
2.  **Integración Directa SCADA/IoT:** Conexión con los PLCs de pesaje de silos para comparar en tiempo real el consumo teórico proyectado contra el consumo físico real acumulado en cada turno de trabajo, permitiendo calibrar automáticamente la tasa de scrap de las fórmulas.
3.  **Planificación de Rutas Logísticas Outbound:** Sincronizar el plan de producción del producto terminado A17 con el despachador de camiones de reparto para clientes, garantizando la carga óptima de camiones de salida minimizando el inventario en tránsito en el almacén de producto terminado.

---

## 15. KPIs Importantes

El rendimiento del planificador y de la planta de producción se monitorizará mediante los siguientes indicadores clave de rendimiento (KPIs):

*   **Prediction Accuracy of Stockouts (PAS):** Precisión del modelo de predicción de rotura en silos a 72 horas vista (Objetivo: > 95%).
*   **Truck Scheduling Efficiency (TSE):** Porcentaje de camiones cisterna descargados en la ventana horaria recomendada sin generar demoras de transporte ni rechazos de descarga por silo lleno (Objetivo: > 98%).
*   **Plan Adherence (Adherencia al Plan):** Porcentaje de cumplimiento de la secuencia de producción de aluminio propuesta por el optimizador de enrollado y troquelado en planta (Objetivo: > 90%).
*   **Setup Time Reduction (STR):** Porcentaje de reducción del tiempo improductivo por cambio de formato en troqueles y enrolladoras gracias al secuenciamiento óptimo (Objetivo: -15% de horas de setup).
*   **Capable-to-Promise Precision (CTPP):** Desviación en días entre la fecha de entrega prometida al cliente mediante el simulador CTP y la fecha real de despacho final (Objetivo: < 1 día de varianza).

---

## 16. Ideas de Optimización Futura

Para la Fase 4 y evoluciones posteriores, proponemos las siguientes técnicas matemáticas avanzadas para resolver los cuellos de botella de aluminio:

*   **Mixed-Integer Linear Programming (MILP):** Para optimizar la asignación de bobinas primarias A13 a las combinaciones de formatos de corte de las enrolladoras. El modelo minimizará el desperdicio residual de aluminio (scrap por refilado lateral de bobina) sujeto a restricciones de demanda semanal.
*   **Algoritmos de Programación de Restricciones (Constraint Programming - CP):** Utilizar solucionadores industriales (como Google OR-Tools) para secuenciar dinámicamente las tareas en los 5 troqueles considerando penalizaciones por matriz de transición de cambio de formato. Esto evitará saltar aleatoriamente entre formatos incompatibles o costosos (ej. de formato muy ancho a muy estrecho sin pasar por transiciones óptimas).

---

## 17. Consideraciones de Escalabilidad

Para asegurar que el DCP responda velozmente a medida que aumenta el volumen de datos en Odoo o la cantidad de plantas que adopten la solución:

1.  **Caché Distribuida con Redis:** Almacenar en caché las respuestas de consultas pesadas de capacidad comercial de solo lectura que no cambian con frecuencia durante el día.
2.  **Indexación Avanzada en PostgreSQL:** Crear índices relacionales compuestos y optimizados sobre claves foráneas temporales (como combinación de `product_id`, `workcenter_id` y ventanas de tiempo) para acelerar los cálculos de agregación analítica de la base de datos de réplica.
3.  **Procesamiento Asíncrono de Simulaciones:** Las simulaciones "What-If" comerciales complejas que requieran recalcular la ruta completa de producción no bloquearán el hilo del servidor web FastAPI. Se ejecutarán en background mediante colas de tareas asíncronas (**Celery** o **Google Cloud Tasks**) notificando los resultados al cliente mediante WebSockets o Server-Sent Events (SSE).

---

## 18. Ideas de IA Futuras

Líneas de investigación aplicada una vez consolidadas las fases operativas básicas:

*   **Machine Learning Predictivo para OEE y Scrap:** Entrenar modelos de regresión lineal avanzada o Gradient Boosting (XGBoost) para estimar de forma dinámica la tasa de scrap de aluminio y el rendimiento de las enrolladoras en función de variables de contexto: *Temperatura de planta, humedad relativa ambiental (que afecta el comportamiento del papel/aluminio), lote específico del proveedor de bobinas A13 e históricos de operarios asignados al turno*.
*   **Interface Conversacional (NLP Llama/GPT con RAG):** Integrar un asistente de lenguaje natural conectado a la base de datos del planificador (mediante técnicas de generación recuperada o RAG) que permita a los directores de planta realizar consultas en lenguaje natural:
    *   *¿Cuál es el principal cuello de botella que arriesga el pedido del cliente X para la próxima semana?*
    *   *Recomiéndame una acción rápida para liberar capacidad en el troquel F3.*

---

## 19. Diagrama Textual de Arquitectura

El siguiente diagrama Mermaid visualiza la arquitectura física y lógica, detallando la separación de responsabilidades y el flujo de la información desde Odoo hasta la interfaz de usuario:

```mermaid
graph TB
    subgraph Odoo ERP (Single Source of Truth)
        OdooDB[(Odoo PostgreSQL)]
        OdooAPI[Odoo API Standard: XML-RPC / REST]
        OdooDB --> OdooAPI
    end

    subgraph GCP Cloud Run - Sync Engine
        SyncWorker[Background Sync Engine: FastAPI / Celery]
    end

    subgraph GCP Cloud SQL - Base de Datos DCP
        DCP_DB[(DCP PostgreSQL DB)]
    end

    subgraph GCP Cloud Run - Núcleo Analítico & API
        subgraph FastAPI Backend
            APIRouter[API Router - REST]
            
            subgraph Motores Analíticos
                MassBalance[Silos Mass Balance Engine]
                ConstraintSolver[Aluminum Capacity Solver]
                CTPEngine[CTP / Sales Engine]
            end
            
            APIRouter --> MassBalance
            APIRouter --> ConstraintSolver
            APIRouter --> CTPEngine
        end
    end

    subgraph Client Browser
        NextJSApp[Next.js SPA: React / TypeScript / Tailwind-CSS]
    end

    OdooAPI -->|1. Extracción asíncrona Delta| SyncWorker
    SyncWorker -->|2. Escritura de datos limpios| DCP_DB
    
    DCP_DB -->|3. Lectura de estado y configuraciones| APIRouter
    MassBalance -.-> DCP_DB
    ConstraintSolver -.-> DCP_DB
    
    APIRouter -->|4. JSON API over HTTPS| NextJSApp
    NextJSApp -->|5. Petición de Simulación / Consulta CTP| APIRouter
```

---

## 20. Estructura Sugerida del Repositorio

Para soportar un desarrollo modular, limpio e independiente del frontend y backend, se propone una estructura de monorepo gestionada y limpia:

```
dupon-capacity-planner/
├── .github/
│   └── workflows/              # CI/CD pipelines para Google Cloud Run
├── backend/                    # Proyecto FastAPI (Python 3.11+)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # Punto de entrada de la aplicación FastAPI
│   │   ├── core/               # Configuraciones del sistema, seguridad y base de datos
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/             # Esquemas SQLAlchemy (ORM) de la DB réplica
│   │   │   ├── base.py
│   │   │   ├── odoo_replica.py # Tablas replicadas de Odoo
│   │   │   └── planner.py      # Datos de configuración del planificador
│   │   ├── schemas/            # Validadores Pydantic para APIs e Ingestion
│   │   │   ├── silos.py
│   │   │   ├── aluminum.py
│   │   │   └── commercial.py
│   │   ├── services/           # Lógica analítica pura (Motores Matemáticos)
│   │   │   ├── mass_balance.py # Algoritmo de balance de masas de silos
│   │   │   ├── solver.py       # Optimizador/Programador de restricciones
│   │   │   └── sync_engine.py  # Conectores y lógica de sincronización con Odoo
│   │   └── api/                # Controladores de endpoints REST
│   │       ├── v1/
│   │       │   ├── silos.py
│   │       │   ├── aluminum.py
│   │       │   └── commercial.py
│   │       └── router.py
│   ├── tests/                  # Pruebas unitarias e integración de los motores
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Aplicación Next.js SPA (TypeScript)
│   ├── src/
│   │   ├── app/                # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx        # Dashboard global
│   │   │   ├── silos/          # Vistas del Planificador de Silos
│   │   │   ├── aluminum/       # Vistas de Troqueles y Enrollado
│   │   │   └── commercial/     # Consola de capacidad de Ventas
│   │   ├── components/         # Componentes UI reutilizables
│   │   │   ├── ui/             # Botones, selectores, modales dinámicos
│   │   │   ├── silos-chart.tsx # Gráfico de decaimiento dinámico de silos
│   │   │   └── gantt-chart.tsx # Gantt interactivo para troqueles
│   │   ├── hooks/              # Custom React Hooks para llamadas API
│   │   ├── services/           # Clientes de API REST (Axios / Fetch)
│   │   │   └── api.ts
│   │   └── types/              # Definiciones TypeScript compartidas
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml          # Orquestación de desarrollo local (Postgres + Backend + Frontend)
└── README.md
```

---

## 21. Plan de Pruebas y Validación (Testing Strategy)

Para asegurar la robustez, correctitud y mantenibilidad a largo plazo del **Dupon Capacity Planner (DCP)**, se establece una estrategia de pruebas automatizadas de tres niveles en el Frontend y el Backend.

### A. Estrategia de Pruebas para el Frontend (Next.js & TypeScript)

El frontend contiene lógica matemática interactiva en el cliente (como el decaimiento de silos, cálculo de OEE en simulaciones y slots comerciales CTP) que debe validarse ante cualquier cambio de diseño.

1. **Suite de Pruebas Unitarias y de Componentes:**
   * **Tecnología:** `Vitest` + `React Testing Library` + `jsdom`.
   * **Enfoque:**
     * **Unit Tests:** Validar que las utilidades y formateadores puros (ej. `formatNumber` en `utils/format.ts`) se comporten exactamente igual independientemente de la configuración regional o el entorno de SSR.
     * **Component Tests:** Verificar la reactividad y renderizado de componentes críticos (ej. que la animación del tanque interactivo de harina aplique correctamente los colores HSL e inyecte los porcentajes correctos).
   * **Comando de Ejecución:** `npm run test` y `npm run test:watch`.

2. **Suite de Pruebas E2E (Extremo a Extremo):**
   * **Tecnología:** `Playwright`.
   * **Enfoque:** Validar flujos de interacción de extremo a extremo, tales como la redirección forzada del Login, la persistencia del selector de idioma `i18n` en el layout, y la simulación interactiva CTP.

---

### B. Estrategia de Pruebas para el Backend (FastAPI & Python)

El backend resolverá los cálculos matemáticos de balance de masa y la sincronización en tiempo real con Odoo ERP.

1. **Suite de Pruebas Unitarias:**
   * **Tecnología:** `pytest`.
   * **Enfoque:**
     * Validar el balance de masa de silos en `services/mass_balance.py`.
     * Validar el motor de restricciones de troqueles y enrolladoras en `services/solver.py`.
2. **Suite de Pruebas de Integración y Mocking:**
   * **Tecnología:** `pytest-asyncio` + `httpx` + `SQLAlchemy` (base de datos en Docker de pruebas con rollbacks).
   * **Enfoque:**
     * Mockear llamadas XML-RPC/REST de Odoo (`sync_engine.py`) para verificar la consistencia de datos de stock y BOM.
     * Validar endpoints REST de la API local (`api/v1/silos`, etc.) para ratificar que las respuestas JSON y los códigos de estado HTTP coincidan con el contrato esperado.

---

## 22. Infraestructura de Desarrollo Local (Docker Compose & DB)

Para agilizar el desarrollo local y garantizar el aislamiento de datos, se establece el uso de contenedores Docker para la persistencia del Capacity Planner.

### A. Orquestación Local (PostgreSQL en Docker)
* **Archivo de Configuración:** `docker-compose.yml` en la raíz del repositorio.
* **Detalle del Contenedor:**
  * **Servicio:** `dcp_db`
  * **Motor:** `postgres:15-alpine` (Ligero, seguro y de alta disponibilidad).
  * **Persistencia:** Volumen nombrado `dcp_postgres_data` mapeado a `/var/lib/postgresql/data`.
  * **Puerto de Exposición:** `5432:5432` en localhost.

### B. Conectividad Segura con Odoo Staging (API Keys)
El sistema consumirá las APIs tradicionales XML-RPC del staging oficial del cliente mediante el uso de tokens/API keys.
* **Gestión de Entorno:** Un archivo `.env` en `/backend` (basado en `.env.example`) contendrá los secretos de conexión. Este archivo local queda estrictamente excluido del repositorio Git (`.gitignore`).
* **Variables de Entorno Clave:**
  * `DATABASE_URL`: Conexión JDBC/SQLAlchemy a la réplica PostgreSQL.
  * `ODOO_URL`: URL del entorno Odoo Staging del cliente.
  * `ODOO_DB`: Nombre del esquema Odoo.
  * `ODOO_USER`: Email o usuario autenticado.
  * `ODOO_API_KEY`: API Key o password de sincronización.
  * `SYNC_INTERVAL_MINUTES`: Intervalo de sincronización dinámica (Fijado en **30 minutos**).

---

*Fin del Documento de Contexto y Arquitectura.*



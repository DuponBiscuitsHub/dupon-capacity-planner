# INSTRUCCIONES CRÍTICAS PARA AGENTES DE IA (AI Agent Instructions)
Este archivo contiene las directrices de obligatorio cumplimiento para cualquier agente de inteligencia artificial (LLM, Copilot, Cursor, etc.) que asista en el desarrollo de este proyecto.

---

## 🚨 REGLA DE ORO (MANDATORIA)
> [!IMPORTANT]
> Antes de proponer o escribir cualquier línea de código, modificar un archivo existente o instalar dependencias, **DEBES LEER COMPLETAMENTE** los siguientes dos archivos ubicados en la raíz:
> 1. [architecture_plan.md](file:///home/pakipy/dupon-dev/dupon-capacity-planner/architecture_plan.md) - Arquitectura, stack tecnológico, límites del diseño y roadmap.
> 2. [project_status.md](file:///home/pakipy/dupon-dev/dupon-capacity-planner/project_status.md) - Estado de avance, checklist de tareas activas y bitácora de sesiones.

---

## 🛠️ DIRECTRICES TÉCNICAS Y DE ARQUITECTURA
Si eres una IA trabajando en este repositorio, debes adherirte estrictamente a los siguientes principios de diseño:

1.  **Odoo como Single Source of Truth (SSoT):** No almacenes datos maestros que deban residir en Odoo. El planificador inicialmente opera en **modo lectura**. Bajo ningún concepto realices escrituras destructivas o modificaciones en Odoo en las Fases 0, 1 y 2.
2.  **Modularidad Estricta:** El sistema se organiza de forma desacoplada. Backend en Python (`FastAPI`) y Frontend en `Next.js` con TypeScript. No mezcles lógica de negocio del módulo de Silos con el de Aluminios.
3.  **Simplicidad Primero:** Evita la sobreingeniería. Prioriza algoritmos deterministas claros y balance de masas algebraico antes de proponer optimizadores matemáticos complejos.
4.  **Idioma de Desarrollo:** La documentación, comentarios de código y respuestas al usuario deben ser redactados en **Español**, manteniendo un tono altamente técnico y profesional.
5.  **Internacionalización Mandatoria (i18n):** Cada vez que agregues, edites o modifiques textos, etiquetas, botones o títulos visuales en la interfaz del Frontend, **BETA prohibido hardcodear cadenas**. DEBES añadir la entrada correspondiente con su clave en el diccionario desacoplado `/frontend/src/app/i18n/translations.ts` conteniendo traducciones válidas para los 6 idiomas requeridos (`es`, `en`, `fr`, `de`, `be`, `ca`).

---

## 🔄 PROTOCOLO DE CIERRE DE SESIÓN
Antes de finalizar tu turno o dar una tarea por completada, **DEBES actualizar el archivo `project_status.md`**:
*   Marca como completadas `[x]` las tareas de la checklist en las que hayas trabajado.
*   Añade una nueva entrada en la sección **📓 4. Historial de Sesiones (Bitácora)** detallando la fecha actual, tu nombre de agente, los hitos logrados, decisiones clave adoptadas y cualquier bloqueo o riesgo detectado.

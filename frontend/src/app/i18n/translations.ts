/* translations.ts — DCP Raw Material Planner i18n
 * ES, CA, EN. Claves mínimas del scope actual.
 * Añadir claves aquí antes de usarlas en componentes.
 */

export type LanguageType = "es" | "ca" | "en";

export interface TranslationDictionary {
  [key: string]: Record<LanguageType, string>;
}

export const translations: TranslationDictionary = {
  // ── Locale (BCP-47) — used by toLocaleString() calls ───────────────────────
  _locale: {
    es: "es-ES",
    ca: "ca-ES",
    en: "en-GB",
  },

  // ── Line type ────────────────────────────────────────────────────────────
  lineTypeRotary: {
    es: "Rotativa",
    ca: "Rotativa",
    en: "Rotary",
  },
  lineTypeLinear: {
    es: "Lineal",
    ca: "Lineal",
    en: "Linear",
  },
  configColType: {
    es: "Tipo",
    ca: "Tipus",
    en: "Type",
  },

  // ── Nav ─────────────────────────────────────────────────────────────────────
  navDashboard: {
    es: "Inicio",
    ca: "Inici",
    en: "Home",
  },
  navSilos: {
    es: "Silos & Entregas",
    ca: "Sitges & Lliuraments",
    en: "Silos & Deliveries",
  },
  navConfig: {
    es: "Configuración",
    ca: "Configuració",
    en: "Configuration",
  },
  navLogout: {
    es: "Cerrar Sesión",
    ca: "Tancar Sessió",
    en: "Sign Out",
  },

  // ── Titles ───────────────────────────────────────────────────────────────────
  titleDashboard: {
    es: "Vista General — Primera Materia",
    ca: "Vista General — Primera Matèria",
    en: "Overview — Raw Materials",
  },
  titleSilos: {
    es: "Silos y Planificación de Entregas",
    ca: "Sitges i Planificació de Lliuraments",
    en: "Silos & Delivery Planning",
  },
  titleConfig: {
    es: "Configuración del Sistema",
    ca: "Configuració del Sistema",
    en: "System Configuration",
  },

  // ── Silos page ───────────────────────────────────────────────────────────────
  silosTitle: {
    es: "Estado de Silos",
    ca: "Estat de Sitges",
    en: "Silo Status",
  },
  silosFill: {
    es: "Nivel",
    ca: "Nivell",
    en: "Fill",
  },
  silosCapacity: {
    es: "Capacidad",
    ca: "Capacitat",
    en: "Capacity",
  },
  silosStock: {
    es: "Stock actual",
    ca: "Estoc actual",
    en: "Current stock",
  },
  silosStatus: {
    es: "Estado",
    ca: "Estat",
    en: "Status",
  },
  silosStatusOk: {
    es: "OK",
    ca: "OK",
    en: "OK",
  },
  silosStatusWarning: {
    es: "Atención",
    ca: "Atenció",
    en: "Warning",
  },
  silosStatusCritical: {
    es: "Crítico",
    ca: "Crític",
    en: "Critical",
  },
  silosStatusUnknown: {
    es: "Sin datos",
    ca: "Sense dades",
    en: "No data",
  },

  // ── Deliveries ───────────────────────────────────────────────────────────────
  deliveriesTitle: {
    es: "Sugerencias de Entrega",
    ca: "Suggeriments de Lliurament",
    en: "Delivery Suggestions",
  },
  deliveriesRecalculate: {
    es: "Recalcular Entregas",
    ca: "Recalcular Lliuraments",
    en: "Recalculate Deliveries",
  },
  deliveriesRecalculating: {
    es: "Calculando...",
    ca: "Calculant...",
    en: "Calculating...",
  },
  deliveriesColDate: {
    es: "Fecha Sugerida",
    ca: "Data Suggerida",
    en: "Suggested Date",
  },
  deliveriesColQty: {
    es: "Cantidad (kg)",
    ca: "Quantitat (kg)",
    en: "Quantity (kg)",
  },
  deliveriesColStatus: {
    es: "Estado",
    ca: "Estat",
    en: "Status",
  },
  deliveriesColPO: {
    es: "PO Odoo",
    ca: "PO Odoo",
    en: "Odoo PO",
  },
  deliveriesStatusDraft: {
    es: "⚪ Borrador",
    ca: "⚪ Esborrany",
    en: "⚪ Draft",
  },
  deliveriesStatusPoPending: {
    es: "🟡 PO Pendiente",
    ca: "🟡 PO Pendent",
    en: "🟡 PO Pending",
  },
  deliveriesStatusConfirmed: {
    es: "✅ Confirmada",
    ca: "✅ Confirmada",
    en: "✅ Confirmed",
  },
  deliveriesStatusDelivered: {
    es: "📦 Entregada",
    ca: "📦 Lliurada",
    en: "📦 Delivered",
  },
  deliveriesEmpty: {
    es: "No hay sugerencias activas. Pulsa Recalcular para generarlas.",
    ca: "No hi ha suggeriments actius. Prem Recalcular per generar-los.",
    en: "No active suggestions. Press Recalculate to generate them.",
  },
  deliveriesConfirmedLocked: {
    es: "🔒 Bloqueada — PO confirmada en Odoo",
    ca: "🔒 Bloquejada — PO confirmada a Odoo",
    en: "🔒 Locked — PO confirmed in Odoo",
  },

  // ── Config ───────────────────────────────────────────────────────────────────
  configLines: {
    es: "Capacidad por Línea",
    ca: "Capacitat per Línia",
    en: "Line Capacity",
  },
  configSilos: {
    es: "Configuración de Silos",
    ca: "Configuració de Sitges",
    en: "Silo Configuration",
  },
  configUsers: {
    es: "Usuarios",
    ca: "Usuaris",
    en: "Users",
  },
  configSave: {
    es: "Guardar",
    ca: "Desar",
    en: "Save",
  },
  configCancel: {
    es: "Cancelar",
    ca: "Cancel·lar",
    en: "Cancel",
  },
  configEdit: {
    es: "Editar",
    ca: "Editar",
    en: "Edit",
  },
  configLineActive: {
    es: "Produciendo",
    ca: "Produint",
    en: "Active",
  },
  configLineIdle: {
    es: "Parada",
    ca: "Aturada",
    en: "Idle",
  },
  configKgH: {
    es: "kg/h teórico",
    ca: "kg/h teòric",
    en: "Theoretical kg/h",
  },
  configSafetyStock: {
    es: "Stock de seguridad (kg)",
    ca: "Estoc de seguretat (kg)",
    en: "Safety stock (kg)",
  },

  // ── Users ────────────────────────────────────────────────────────────────────
  usersCreate: {
    es: "Crear Usuario",
    ca: "Crear Usuari",
    en: "Create User",
  },
  usersUsername: {
    es: "Usuario",
    ca: "Usuari",
    en: "Username",
  },
  usersPassword: {
    es: "Contraseña",
    ca: "Contrasenya",
    en: "Password",
  },
  usersRole: {
    es: "Rol",
    ca: "Rol",
    en: "Role",
  },
  usersRoleIt: {
    es: "IT (Admin)",
    ca: "IT (Admin)",
    en: "IT (Admin)",
  },
  usersRoleUser: {
    es: "Planificador",
    ca: "Planificador",
    en: "Planner",
  },
  usersDeactivate: {
    es: "Desactivar",
    ca: "Desactivar",
    en: "Deactivate",
  },
  usersActive: {
    es: "Activo",
    ca: "Actiu",
    en: "Active",
  },
  usersInactive: {
    es: "Inactivo",
    ca: "Inactiu",
    en: "Inactive",
  },

  // ── Sync ─────────────────────────────────────────────────────────────────────
  syncRun: {
    es: "Sincronizar con Odoo",
    ca: "Sincronitzar amb Odoo",
    en: "Sync with Odoo",
  },
  syncRunning: {
    es: "Sincronizando...",
    ca: "Sincronitzant...",
    en: "Syncing...",
  },
  syncLastSync: {
    es: "Último sync",
    ca: "Últim sync",
    en: "Last sync",
  },
  syncOk: {
    es: "Conectado",
    ca: "Connectat",
    en: "Connected",
  },
  syncError: {
    es: "Error de sync",
    ca: "Error de sync",
    en: "Sync error",
  },

  // ── Login ────────────────────────────────────────────────────────────────────
  loginTitle: {
    es: "Acceso Operaciones",
    ca: "Accés Operacions",
    en: "Operations Login",
  },
  loginUserLabel: {
    es: "Usuario",
    ca: "Usuari",
    en: "Username",
  },
  loginPassLabel: {
    es: "Contraseña",
    ca: "Contrasenya",
    en: "Password",
  },
  loginBtn: {
    es: "Entrar",
    ca: "Entrar",
    en: "Sign In",
  },
  loginError: {
    es: "Usuario o contraseña incorrectos.",
    ca: "Usuari o contrasenya incorrectes.",
    en: "Invalid username or password.",
  },
  loginFooter: {
    es: "DCP Raw Material Planner © 2026 · Dupon Biscuits",
    ca: "DCP Raw Material Planner © 2026 · Dupon Biscuits",
    en: "DCP Raw Material Planner © 2026 · Dupon Biscuits",
  },

  // ── Errors / Generic ─────────────────────────────────────────────────────────
  errorLoading: {
    es: "Error al cargar los datos.",
    ca: "Error en carregar les dades.",
    en: "Error loading data.",
  },
  loading: {
    es: "Cargando...",
    ca: "Carregant...",
    en: "Loading...",
  },
  noData: {
    es: "Sin datos",
    ca: "Sense dades",
    en: "No data",
  },

  // ── Dashboard gauge ───────────────────────────────────────────────────────────
  dashNoDelivery: {
    es: "Sin entrega planificada",
    ca: "Sense lliurament planificat",
    en: "No planned delivery",
  },
  dashToday: {
    es: "Hoy",
    ca: "Avui",
    en: "Today",
  },
  dashTomorrow: {
    es: "Mañana",
    ca: "Demà",
    en: "Tomorrow",
  },
  dashAlertCritical: {
    es: "Stock crítico (< 20%)",
    ca: "Estoc crític (< 20%)",
    en: "Critical stock (< 20%)",
  },
  dashAlertLow: {
    es: "Stock bajo (20–40%)",
    ca: "Estoc baix (20–40%)",
    en: "Low stock (20–40%)",
  },
  dashStatOk: {
    es: "Silos OK",
    ca: "Sitges OK",
    en: "Silos OK",
  },
  dashStatLow: {
    es: "Silos bajos",
    ca: "Sitges baixos",
    en: "Low silos",
  },
  dashStatCritical: {
    es: "Silos críticos",
    ca: "Sitges crítics",
    en: "Critical silos",
  },
  dashStatDeliveries: {
    es: "Entregas pendientes",
    ca: "Lliuraments pendents",
    en: "Pending deliveries",
  },

  // ── Chart projection ──────────────────────────────────────────────────────
  chartTitle: {
    es: "Proyección de Stock — 14 días",
    ca: "Projecció d'Estoc — 14 dies",
    en: "Stock Projection — 14 days",
  },
  chartStock: {
    es: "Stock (t)",
    ca: "Estoc (t)",
    en: "Stock (t)",
  },
  chartCapacity: {
    es: "Capacidad",
    ca: "Capacitat",
    en: "Capacity",
  },
  chartSafety: {
    es: "Safety Stock",
    ca: "Safety Stock",
    en: "Safety Stock",
  },
  chartNoData: {
    es: "Sin datos de proyección",
    ca: "Sense dades de projecció",
    en: "No projection data",
  },

  // ── Silos page ───────────────────────────────────────────────────────────────
  silosDeliveryPlanning: {
    es: "Planificación de Entregas",
    ca: "Planificació de Lliuraments",
    en: "Delivery Planning",
  },
  silosNextDays: {
    es: "Próximos {n} días",
    ca: "Propers {n} dies",
    en: "Next {n} days",
  },
  silosFilterAll: {
    es: "Todos",
    ca: "Tots",
    en: "All",
  },
  silosNoPO: {
    es: "Sin PO",
    ca: "Sense PO",
    en: "No PO",
  },
  silosSyncing: {
    es: "Sincronizando…",
    ca: "Sincronitzant…",
    en: "Syncing…",
  },
  silosRecalculating: {
    es: "Recalculando…",
    ca: "Recalculant…",
    en: "Recalculating…",
  },
  silosSyncDone: {
    es: "✓ Listo",
    ca: "✓ Llest",
    en: "✓ Done",
  },
  silosSyncError: {
    es: "⚠ Error",
    ca: "⚠ Error",
    en: "⚠ Error",
  },
  silosSyncBtn: {
    es: "🔄 Sync Odoo",
    ca: "🔄 Sync Odoo",
    en: "🔄 Sync Odoo",
  },
  silosSyncNever: {
    es: "Sin sincronizar",
    ca: "Sense sincronitzar",
    en: "Not synced",
  },
  silosSyncJustNow: {
    es: "< 1 min",
    ca: "< 1 min",
    en: "< 1 min",
  },
  syncOverlayTitle: {
    es: "Sincronizando con Odoo",
    ca: "Sincronitzant amb Odoo",
    en: "Syncing with Odoo",
  },
  syncOverlayStepSync: {
    es: "Importando stock y pedidos de compra…",
    ca: "Important estoc i comandes de compra…",
    en: "Importing stock and purchase orders…",
  },
  syncOverlayStepRecalc: {
    es: "Calculando ventanas de entrega…",
    ca: "Calculant finestres d'entrega…",
    en: "Calculating delivery windows…",
  },
  syncOverlayErrTitle: {
    es: "No se puede conectar con Odoo",
    ca: "No es pot connectar amb Odoo",
    en: "Cannot connect to Odoo",
  },
  syncOverlayErrHint: {
    es: "Comprueba la conexión o inténtalo de nuevo más tarde.",
    ca: "Comprova la connexió o torna-ho a intentar més tard.",
    en: "Check your connection or try again later.",
  },

  // ── Odoo Status Dot ─────────────────────────────────────────────────────────
  odooStatusConnected: {
    es: "Odoo: conectado ({ms}ms)",
    ca: "Odoo: connectat ({ms}ms)",
    en: "Odoo: connected ({ms}ms)",
  },
  odooStatusDisconnected: {
    es: "Odoo: sin conexión",
    ca: "Odoo: sense connexió",
    en: "Odoo: disconnected",
  },
  odooStatusMock: {
    es: "Odoo: modo simulación",
    ca: "Odoo: mode simulació",
    en: "Odoo: mock mode",
  },
  odooStatusChecking: {
    es: "Verificando conexión…",
    ca: "Verificant connexió…",
    en: "Checking connection…",
  },

  silosDeliveryStatusDraft: {
    es: "Borrador",
    ca: "Esborrany",
    en: "Draft",
  },
  silosDeliveryStatusPending: {
    es: "PO Pendiente",
    ca: "PO Pendent",
    en: "PO Pending",
  },
  silosDeliveryStatusConfirmed: {
    es: "Confirmado",
    ca: "Confirmat",
    en: "Confirmed",
  },
  silosDeliveryStatusDelivered: {
    es: "Entregado",
    ca: "Lliurat",
    en: "Delivered",
  },

  // ── Delivery Planning Table ─────────────────────────────────────────────────
  planTitle: {
    es: "Planificación de Entregas",
    ca: "Planificació de Lliuraments",
    en: "Delivery Planning",
  },
  planColMaterial: {
    es: "Material",
    ca: "Material",
    en: "Material",
  },
  planColPO: {
    es: "PO Odoo",
    ca: "PO Odoo",
    en: "PO Odoo",
  },
  planColQty: {
    es: "Cantidad",
    ca: "Quantitat",
    en: "Quantity",
  },
  planColPODate: {
    es: "Fecha PO",
    ca: "Data PO",
    en: "PO Date",
  },
  planColAppDate: {
    es: "Fecha Sugerida",
    ca: "Data Suggerida",
    en: "Suggested Date",
  },
  planUseSuggested: {
    es: "Usar propuesta",
    ca: "Usar proposta",
    en: "Use suggested",
  },
  planNoSuggested: {
    es: "Sin fecha propuesta",
    ca: "Sense data proposta",
    en: "No suggested date",
  },
  planColState: {
    es: "Estado",
    ca: "Estat",
    en: "State",
  },
  planColAction: {
    es: "Acción",
    ca: "Acció",
    en: "Action",
  },
  planNoPO: {
    es: "Sin PO",
    ca: "Sense PO",
    en: "No PO",
  },
  planStateDraft: {
    es: "Borrador",
    ca: "Esborrany",
    en: "Draft",
  },
  planStateSent: {
    es: "Enviada",
    ca: "Enviada",
    en: "Sent",
  },
  planStatePurchase: {
    es: "Confirmada",
    ca: "Confirmada",
    en: "Confirmed",
  },
  planStateDone: {
    es: "Recibida",
    ca: "Rebuda",
    en: "Received",
  },
  planBtnSendToOdoo: {
    es: "Enviar a Odoo",
    ca: "Enviar a Odoo",
    en: "Send to Odoo",
  },
  planBtnEditDate: {
    es: "Editar fecha",
    ca: "Editar data",
    en: "Edit date",
  },
  planWarningConfirmed: {
    es: "Esta PO ya fue confirmada al proveedor. ¿Seguro que quieres cambiar la fecha de entrega?",
    ca: "Aquesta PO ja ha estat confirmada al proveïdor. Segur que vols canviar la data de lliurament?",
    en: "This PO has already been confirmed with the supplier. Are you sure you want to change the delivery date?",
  },
  planBlockedDone: {
    es: "PO ya recibida — no se puede modificar",
    ca: "PO ja rebuda — no es pot modificar",
    en: "PO already received — cannot modify",
  },
  planConfirmSend: {
    es: "Confirmar",
    ca: "Confirmar",
    en: "Confirm",
  },
  planCancel: {
    es: "Cancelar",
    ca: "Cancel·lar",
    en: "Cancel",
  },
  planUpdated: {
    es: "Fecha actualizada correctamente",
    ca: "Data actualitzada correctament",
    en: "Date updated successfully",
  },
  planForecast: {
    es: "Horizonte",
    ca: "Horitzó",
    en: "Forecast",
  },
  planDays: {
    es: "{n} días",
    ca: "{n} dies",
    en: "{n} days",
  },

  // ── Config tabs ───────────────────────────────────────────────────────────────
  configTabLines: {
    es: "Líneas de galleta",
    ca: "Línies de galeta",
    en: "Cookie lines",
  },
  configTabSilos: {
    es: "Silos",
    ca: "Sitges",
    en: "Silos",
  },
  configTabUsers: {
    es: "Usuarios",
    ca: "Usuaris",
    en: "Users",
  },
  configTabRecipes: {
    es: "Recetas (kg/día)",
    ca: "Receptes (kg/dia)",
    en: "Recipes (kg/day)",
  },
  configTabLineFormats: {
    es: "Líneas ↔ Formatos",
    ca: "Línies ↔ Formats",
    en: "Lines ↔ Formats",
  },

  // ── Config lines tab ──────────────────────────────────────────────────────────
  configLinesDesc: {
    es: "Capacidad teórica de cada línea de galleta en kg/h. Afecta directamente al cálculo de entregas.",
    ca: "Capacitat teòrica de cada línia de galeta en kg/h. Afecta directament al càlcul de lliuraments.",
    en: "Theoretical capacity of each cookie line in kg/h. Directly affects delivery calculations.",
  },
  configColLine: {
    es: "Línea",
    ca: "Línia",
    en: "Line",
  },
  configColStatus: {
    es: "Estado",
    ca: "Estat",
    en: "Status",
  },
  configColKgH: {
    es: "Consumo (kg/h)",
    ca: "Consum (kg/h)",
    en: "Consumption (kg/h)",
  },

  // ── Config silos tab ──────────────────────────────────────────────────────────
  configSilosDesc: {
    es: "Capacidad y stock de seguridad de cada silo. El stock de seguridad define cuándo se genera una alerta crítica.",
    ca: "Capacitat i estoc de seguretat de cada sitja. L'estoc de seguretat defineix quan es genera una alerta crítica.",
    en: "Capacity and safety stock for each silo. Safety stock defines when a critical alert is triggered.",
  },
  configColCode: {
    es: "Código",
    ca: "Codi",
    en: "Code",
  },
  configColMaterial: {
    es: "Material",
    ca: "Material",
    en: "Material",
  },
  configColCapacity: {
    es: "Capacidad (kg)",
    ca: "Capacitat (kg)",
    en: "Capacity (kg)",
  },
  configColSafety: {
    es: "Stock seguridad (kg)",
    ca: "Estoc seguretat (kg)",
    en: "Safety stock (kg)",
  },

  // ── Config users tab ──────────────────────────────────────────────────────────
  usersCreateTitle: {
    es: "Crear usuario",
    ca: "Crear usuari",
    en: "Create user",
  },
  usersPlaceholderUser: {
    es: "Usuario",
    ca: "Usuari",
    en: "Username",
  },
  usersPlaceholderPass: {
    es: "Contraseña (mín. 8)",
    ca: "Contrasenya (mín. 8)",
    en: "Password (min. 8)",
  },
  usersCreating: {
    es: "Creando...",
    ca: "Creant...",
    en: "Creating...",
  },
  usersCreate2: {
    es: "Crear",
    ca: "Crear",
    en: "Create",
  },
  configColUser: {
    es: "Usuario",
    ca: "Usuari",
    en: "User",
  },
  configColRole: {
    es: "Rol",
    ca: "Rol",
    en: "Role",
  },

  // ── Config recipes tab ────────────────────────────────────────────────────────
  configRecipesTitle: {
    es: "Consumos de referencia (kg/día por máquina)",
    ca: "Consums de referència (kg/dia per màquina)",
    en: "Reference consumption (kg/day per machine)",
  },
  configRecipesHint: {
    es: "Datos del Excel CON · Clic en valor para editar (IT)",
    ca: "Dades de l'Excel CON · Clic en valor per editar (IT)",
    en: "Excel CON data · Click value to edit (IT)",
  },
  configColFormat: {
    es: "Formato",
    ca: "Format",
    en: "Format",
  },

  // ── Config line-formats tab ───────────────────────────────────────────────────
  configLineFormatsTitle: {
    es: "Líneas ↔ Formatos",
    ca: "Línies ↔ Formats",
    en: "Lines ↔ Formats",
  },
  configLineFormatsHint: {
    es: "Qué formatos puede producir cada línea y nº de máquinas",
    ca: "Quins formats pot produir cada línia i nº de màquines",
    en: "Which formats each line can produce and number of machines",
  },
  configColMachines: {
    es: "Máquinas",
    ca: "Màquines",
    en: "Machines",
  },

  // ── Generic actions ───────────────────────────────────────────────────────────
  actionSave: {
    es: "Guardar",
    ca: "Desar",
    en: "Save",
  },
  actionCancel: {
    es: "Cancelar",
    ca: "Cancel·lar",
    en: "Cancel",
  },
  actionEdit: {
    es: "Editar",
    ca: "Editar",
    en: "Edit",
  },
  actionDeactivate: {
    es: "Desactivar",
    ca: "Desactivar",
    en: "Deactivate",
  },
  actionSaving: {
    es: "...",
    ca: "...",
    en: "...",
  },

  // ── Status labels ─────────────────────────────────────────────────────────────
  statusActive: {
    es: "Activo",
    ca: "Actiu",
    en: "Active",
  },
  statusInactive: {
    es: "Inactivo",
    ca: "Inactiu",
    en: "Inactive",
  },
  statusProducing: {
    es: "Produciendo",
    ca: "Produint",
    en: "Producing",
  },
  statusIdle: {
    es: "Parada",
    ca: "Aturada",
    en: "Idle",
  },
  statusProducingBullet: {
    es: "● Produciendo",
    ca: "● Produint",
    en: "● Producing",
  },
  statusIdleBullet: {
    es: "○ Parada",
    ca: "○ Aturada",
    en: "○ Idle",
  },

  // ── Material labels (silo gauges & filters) ───────────────────────────────
  matHarina: {
    es: "HARINA",
    ca: "FARINA",
    en: "FLOUR",
  },
  matAzucar: {
    es: "AZÚCAR",
    ca: "SUCRE",
    en: "SUGAR",
  },
  matAceite: {
    es: "ACEITE COCO",
    ca: "OLI DE COCO",
    en: "COCONUT OIL",
  },
  matHarinaLong: {
    es: "🌾 Harina",
    ca: "🌾 Farina",
    en: "🌾 Flour",
  },
  matAzucarLong: {
    es: "🍚 Azúcar",
    ca: "🍚 Sucre",
    en: "🍚 Sugar",
  },
  matAceiteLong: {
    es: "🫙 Aceite Coco",
    ca: "🫙 Oli de Coco",
    en: "🫙 Coconut Oil",
  },

  // ── Silo status unknown ────────────────────────────────────────────────────
  siloStatusUnknown: {
    es: "Sin datos",
    ca: "Sense dades",
    en: "No data",
  },
  siloSafetyStock: {
    es: "Stock de seguridad",
    ca: "Estoc de seguretat",
    en: "Safety stock",
  },
};

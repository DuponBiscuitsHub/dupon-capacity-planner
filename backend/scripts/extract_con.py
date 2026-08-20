"""
extract_con.py — Extrae consumos de la hoja CON del Excel Apro-PM 2026.ods

La hoja CON (shape 28×14) tiene esta estructura:
  Col 0    → nombre ingrediente
  Fila 14  → nombres de formato (col 1–13)
  Filas 16-27 → valores kg/turno de 8h, 1 máquina (ya normalizados)

Cálculo: kg_per_day = kg_turno_8h × 3 turnos

Columnas identificadas (fila 14):
  1: STANDARD        → STD_R_110
  2: STD S.S         → STD_R_SS
  3: HASS 110        → HAAS_110
  4: HASS 98         → HAAS_98          (col 4 = HASS 98, col 5 era 0/vacío)
  5: 0.0/NaN         → (HAAS_98 SS — no existe formato DCP separado)
  6: Mini 75 s.s.    → MINI_75_SS
  7: Mini 75 oli     → MINI_75_OLI
  8: Mini 90 s.s.    → MINI_90_SS
  9: Mini 90         → MINI_90
  10: Imperial       → IMPERIAL
  11: Mini 82        → (sin asignar — no en scope)
  12: Mini 82 Oreo   → HAAS_98_OREO     (HAAS 98 con cacao = OREO)
  13: B.C.           → SPECIAL
"""
import pandas as pd

ODS_PATH = "Apro-PM 2026.ods"

# Col idx → format_code DCP  (los None se ignoran)
COL_TO_FORMAT = {
    1:  "STD_R_110",
    2:  "STD_R_SS",
    3:  "HAAS_110",
    4:  "HAAS_98",
    6:  "MINI_75_SS",
    7:  "MINI_75_OLI",
    8:  "MINI_90_SS",
    9:  "MINI_90",
    10: "IMPERIAL",
    # col 11 Mini 82 → sin formato DCP
    12: "HAAS_98_OREO",
    13: "SPECIAL",
}

# Nombre en col 0 → material_type DCP  (fila 16-27)
MATERIAL_MAP = {
    "Farina":     "harina",
    "Sucre":      "azucar",
    "Oli":        "aceite",
    "Lecit.":     "lecitina",
    "Sal":        "sal",
    "Carbonat":   "carbonat",
    "Caramelina": "caramelina",
    "Maltitex":   "maltitol",
    "Capcol":     "colorante",
    "Cacao":      "cacao",
    "OLI bany":   "oli_bany",
}

MATERIALS_ORDER = [
    "harina", "azucar", "aceite", "lecitina", "sal",
    "carbonat", "caramelina", "maltitol", "cacao", "colorante", "oli_bany",
]

FORMATS_ALL = [
    "STD_R_110", "STD_R_SS", "HAAS_110", "HAAS_98", "HAAS_98_OREO",
    "HAAS_110_OREO", "MINI_75_SS", "MINI_75_OLI", "MINI_90_SS", "MINI_90",
    "IMPERIAL", "SPECIAL", "SPECIAL_SS",
]

def safe_int(val) -> int:
    try:
        return int(round(float(val)))
    except (TypeError, ValueError):
        return 0

df = pd.read_excel(ODS_PATH, sheet_name="CON", engine="odf", header=None)

# Extraer datos fila 16-27 (0-indexed)
result: dict[str, dict[str, int]] = {}
for row_idx in range(16, min(28, len(df))):
    mat_cell = df.iloc[row_idx, 0]
    mat_name = str(mat_cell).strip() if mat_cell is not None and str(mat_cell) != "nan" else ""
    if mat_name not in MATERIAL_MAP:
        continue
    mt = MATERIAL_MAP[mat_name]
    for col_idx, fc in COL_TO_FORMAT.items():
        kg_turno = safe_int(df.iloc[row_idx, col_idx])
        kg_24h = kg_turno * 3   # 3 turnos de 8h = 24h
        result.setdefault(fc, {})[mt] = kg_24h

# HAAS_110_OREO no está en CON → mismos valores que HAAS_110 pero con cacao de HAAS_98_OREO
# (mismo horno que HAAS_110 + variante oreo → mismos consumos base)
haas110 = result.get("HAAS_110", {})
haas98_oreo = result.get("HAAS_98_OREO", {})
result["HAAS_110_OREO"] = {**haas110, "cacao": haas98_oreo.get("cacao", 0)}

# SPECIAL_SS: mismo que SPECIAL pero sin azúcar, con maltitol (igual que STD_R_SS vs STD_R_110)
special = result.get("SPECIAL", {})
result["SPECIAL_SS"] = {
    **special,
    "azucar":   0,
    "maltitol": special.get("maltitol", 0) if special.get("maltitol", 0) > 0
                else result.get("STD_R_SS", {}).get("maltitol", 0),
}

# Imprimir resultado como CON_DATA para seed_config.py
print("CON_DATA = [")
for fc in FORMATS_ALL:
    fdata = result.get(fc, {})
    for mt in MATERIALS_ORDER:
        v = fdata.get(mt, 0)
        print(f'    ("{fc:<16}", "{mt:<12}",  {v:>5}),')
    print()
print("]")
print()
print("# Valores extraídos de la hoja CON de Apro-PM 2026.ods")
print("# kg/día por 1 máquina (3 turnos × 8h = 24h)")
import pandas as pd

ODS_PATH = "Apro-PM 2026.ods"

# Mapa: nombre en CON → formato DCP
FORMAT_MAP = {
    "STANDARD":      "STD_R_110",
    "STD S.S":       "STD_R_SS",
    "HASS 110":      "HAAS_110",
    "HASS 98":       "HAAS_98",
    "Mini 75 s.s.":  "MINI_75_SS",
    "Mini 75 oli":   "MINI_75_OLI",
    "Mini 90 s.s.":  "MINI_90_SS",
    "Mini 90":       "MINI_90",
    "Imperial":      "IMPERIAL",
    "B.C.":          "SPECIAL",         # Barquillo Cilíndrico = SPECIAL
}

# Mapa: nombre en CON → material_type DCP
MATERIAL_MAP = {
    "Farina":    "harina",
    "Sucre":     "azucar",
    "Oli":       "aceite",
    "Lecit.":    "lecitina",
    "Sal":       "sal",
    "Carbonat":  "carbonat",
    "Caramelina":"caramelina",
    "Maltitex":  "maltitol",
    "Capcol":    "colorante",
    "Cacao":     "cacao",
    "OLI bany":  "oli_bany",
}

def safe_int(val) -> int:
    try:
        v = float(val)
        return int(round(v))
    except (TypeError, ValueError):
        return 0

df = pd.read_excel(ODS_PATH, sheet_name="CON", engine="odf", header=None)

# Fila 14 (idx=14) tiene los nombres de formato
header_row = df.iloc[14, :].tolist()

# Fila 13 (idx=13) tiene la cantidad de máquinas por columna
maq_row = df.iloc[13, :].tolist()

# Localizar columnas de cada formato
col_map: dict[str, int] = {}     # format_code → col index
maq_map: dict[str, float] = {}   # format_code → num machines
for col_idx, cell in enumerate(header_row):
    name = str(cell).strip() if cell is not None else ""
    if name in FORMAT_MAP:
        fc = FORMAT_MAP[name]
        col_map[fc] = col_idx
        maq_map[fc] = max(safe_int(maq_row[col_idx]), 1)

# Extraer filas de materiales (fila 16 en adelante hasta que se acaben)
# Columna 0 = nombre ingrediente
result: dict[str, dict[str, int]] = {}

for row_idx in range(16, 30):
    mat_name = str(df.iloc[row_idx, 0]).strip() if df.iloc[row_idx, 0] is not None else ""
    if mat_name not in MATERIAL_MAP:
        continue
    mt = MATERIAL_MAP[mat_name]
    for fc, col_idx in col_map.items():
        kg_turno_total = safe_int(df.iloc[row_idx, col_idx])
        n_maq = maq_map[fc]
        # kg por 1 máquina, 3 turnos (=24h)
        kg_1maq_24h = int(round((kg_turno_total / n_maq) * 3))
        result.setdefault(fc, {})[mt] = kg_1maq_24h

# Imprimir resultado ordenado por formato y material
MATERIALS_ORDER = ["harina", "azucar", "aceite", "lecitina", "sal",
                   "carbonat", "caramelina", "maltitol", "cacao",
                   "colorante", "oli_bany"]

print("# ── CON data extraído del Excel Apro-PM 2026.ods ──")
print("# formato | material | kg/día/maq")
print()
for fc in sorted(col_map.keys()):
    for mt in MATERIALS_ORDER:
        v = result.get(fc, {}).get(mt, 0)
        print(f'    ("{fc:<16}", "{mt:<12}",  {v:>5}),')
    print()

print()
print("# Máquinas por formato en el Excel:")
for fc, n in sorted(maq_map.items()):
    print(f"#  {fc:<16}: {n} maq")

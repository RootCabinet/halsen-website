import streamlit as st
import pandas as pd
import numpy as np
import math
import base64
import os

# --- PAGE SETUP & BRAND THEME ---
st.set_page_config(
    page_title="HALSEN | Estimador de Maquila y Enchapado (Interno)",
    page_icon="🪵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Logo SVG
def load_logo():
    paths = [
        "static/images/logo.svg",
        "../../static/images/logo.svg",
        "/home/rootcabinet/tech-projects/halsen-website/static/images/logo.svg"
    ]
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
    return None

def render_logo():
    svg_data = load_logo()
    if svg_data:
        # Base64 encode to ensure clean cross-browser rendering in Streamlit
        b64 = base64.b64encode(svg_data.encode('utf-8')).decode('utf-8')
        src = f"data:image/svg+xml;base64,{b64}"
        st.write(
            f'<div style="text-align: center; margin-bottom: 1.5rem;">'
            f'<img src="{src}" style="max-height: 80px; width: auto;" alt="Halsen Logo" />'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown("<h1 style='text-align: center; color: #8a1c2c; margin-bottom: 1.5rem;'>🪵 HALSEN</h1>", unsafe_allow_html=True)

# Custom CSS for Solid Dark Mode & Branding (Eliminates all light flashes and white backgrounds)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Force deep dark theme across ALL possible container levels */
html, body, 
[data-testid="stAppViewContainer"], 
[data-testid="stHeader"], 
[data-testid="stMain"], 
.main, 
[data-testid="stMainSpaceBlock"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stBlock"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: #121316 !important;
    color: #e0e0e0 !important;
}

/* Force dark background for expanded content containers and dialogs */
div[data-testid="stForm"], div[data-testid="stExpander"], div[role="dialog"] {
    background-color: #1e2025 !important;
    border: 1px solid #2d2e33 !important;
    border-radius: 8px !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #ffffff !important;
}

/* Sidebar configuration panel styling - Solid Dark Slate */
[data-testid="stSidebar"] {
    background-color: #1a1b1e !important;
    border-right: 1px solid #2d2e33 !important;
}

/* Overriding sidebar labels and text to bright white/gray */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h5,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h6,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div.stMarkdown p,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] span {
    color: #e0e0e0 !important;
}

/* Inputs styling */
input, select, textarea {
    color: #ffffff !important;
    background-color: #2b2d30 !important;
    border: 1px solid #3d3e42 !important;
    border-radius: 4px !important;
}

[data-testid="stSidebar"] input, [data-testid="stSidebar"] select {
    color: #ffffff !important;
    background-color: #2b2d30 !important;
    border: 1px solid #3d3e42 !important;
}

/* Redefine buttons to Halsen Burgundy */
div.stButton > button {
    background-color: #8a1c2c !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
}

div.stButton > button:hover {
    background-color: #a32236 !important;
    color: white !important;
    transform: translateY(-1px) !important;
}

/* Custom styled metric containers */
.metric-card {
    background-color: #1e2025;
    border: 1px solid #2d2e33;
    border-radius: 8px;
    padding: 1.25rem;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    height: 100%;
}
.metric-val {
    font-size: 1.85rem;
    font-weight: 800;
    color: #ec5b70; /* Brighter accent red for dark mode contrast */
    margin: 0.25rem 0;
}
.metric-lbl {
    font-size: 0.75rem;
    color: #aaaaaa;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.metric-desc {
    font-size: 0.75rem;
    color: #888888;
    margin-top: 0.2rem;
}

/* Fix warning/success/info containers for dark mode */
[data-testid="stNotification"] {
    background-color: #2b2d30 !important;
}
</style>
""", unsafe_allow_html=True)


# --- DATA CLEANING & PARSING ENGINE ---

def clean_boolean_column(series):
    """Converts 1/0, True/False, Yes/No, Sí/No to clean boolean types"""
    def parse_val(val):
        if pd.isnull(val):
            return False
        val_str = str(val).strip().lower()
        if val_str in ['1', '1.0', 'true', 'sí', 'si', 'yes', 'y', 'x', 's']:
            return True
        return False
    return series.apply(parse_val)

def clean_numeric_column(series, default_val=0):
    """Converts series to integers cleanly, handling errors"""
    return pd.to_numeric(series, errors='coerce').fillna(default_val).round().astype(int)

def clean_float_column(series, default_val=0.0):
    """Converts series to floats cleanly up to 2 decimal places, handling errors"""
    return pd.to_numeric(series, errors='coerce').fillna(default_val).round(2).astype(float)

def clean_string_column(series, default_val="Pieza"):
    """Converts series to strings cleanly"""
    return series.fillna(default_val).astype(str).str.strip()

def safe_int(val_str, default=100):
    """Safely converts input text values to integers to bypass numeric slider hijacking"""
    try:
        if not val_str:
            return default
        return int(float(str(val_str).strip()))
    except (ValueError, AttributeError):
        return default

def safe_float(val_str, default=100.0):
    """Safely converts input text values to floats to bypass numeric slider hijacking"""
    try:
        if not val_str:
            return default
        return round(float(str(val_str).strip()), 2)
    except (ValueError, AttributeError):
        return default

def auto_detect_columns(df):
    """Automatically detects standard cutlist column names from input DataFrame"""
    cols = list(df.columns)
    mapping = {
        "Label": "",
        "Length (mm)": "",
        "Width (mm)": "",
        "Quantity": "",
        "L1_Edge": "",
        "L2_Edge": "",
        "W1_Edge": "",
        "W2_Edge": "",
        "Thickness (mm)": ""
    }
    
    for col in cols:
        col_lower = col.lower().strip().replace("_", " ").replace("-", " ")
        
        # Label/Piece Name
        if col_lower in ["label", "label", "nombre", "pieza", "piezas", "nombre pieza", "nombre de pieza", "description", "descripcion", "part", "part name", "name"]:
            mapping["Label"] = col
        # Length
        elif col_lower in ["length (mm)", "largo (mm)", "length", "largo", "largos", "l", "longitud", "len", "length mm", "largo mm"]:
            mapping["Length (mm)"] = col
        # Width
        elif col_lower in ["width (mm)", "ancho (mm)", "width", "ancho", "anchos", "w", "a", "anchura", "wid", "width mm", "ancho mm"]:
            mapping["Width (mm)"] = col
        # Quantity
        elif col_lower in ["quantity", "cantidad", "cant", "qty", "c", "piezas_cant", "quantity pcs", "piezas cant", "pzas"]:
            mapping["Quantity"] = col
        # L1 Edge
        elif col_lower in ["l1 edge", "l1_edge", "l1", "canto l1", "canto_l1", "largo 1", "largo_1", "largo1", "canto largo1"]:
            mapping["L1_Edge"] = col
        # L2 Edge
        elif col_lower in ["l2 edge", "l2_edge", "l2", "canto l2", "canto_l2", "largo 2", "largo_2", "largo2", "canto largo2"]:
            mapping["L2_Edge"] = col
        # W1 Edge / A1 Edge
        elif col_lower in ["w1 edge", "w1_edge", "w1", "a1", "a1 edge", "a1_edge", "canto a1", "canto_a1", "ancho 1", "ancho_1", "ancho1", "canto ancho1"]:
            mapping["W1_Edge"] = col
        # W2 Edge / A2 Edge
        elif col_lower in ["w2 edge", "w2_edge", "w2", "a2", "a2 edge", "a2_edge", "canto a2", "canto_a2", "ancho 2", "ancho_2", "ancho2", "canto ancho2"]:
            mapping["W2_Edge"] = col
        # Thickness / Espesor
        elif col_lower in ["thickness (mm)", "espesor (mm)", "thickness", "espesor", "espesores", "t", "thickness mm", "espesor mm"]:
            mapping["Thickness (mm)"] = col

    return mapping


# --- WORKSHOP CALCULATIONS ENGINE ---

def run_workshop_calculations(df, settings):
    """
    Computes precise workshop metrics based on physical constraints:
    - Usable sheet boundary: 10mm margins on all 4 sides -> 1200x2420 usable area
    - Piece spacing padding: 8mm between all cut pieces -> padding (L+8)*(W+8)
    - Woodgrain waste multipliers: 25% with grain, 10% without
    - Edgebanding overcut buffer: +50.8mm (2 inches) per edge enchapado
    - Edgebanding machine startup buffer: +3000mm (3m) per project
    - Machine cutting rate: 4500 mm/min effective with G00 fast-traverse overhead (30%)
    - CAM programming block: $75 MXN per 3 sheets
    """
    # Configuration inputs
    feed_rate = settings.get("feed_rate", 6000)
    efficiency = settings.get("efficiency", 0.75)
    effective_feed_rate = feed_rate * efficiency  # 4500 mm/min default
    g00_multiplier = settings.get("g00_multiplier", 0.30)
    cnc_minute_rate = settings.get("cnc_minute_rate", 10.00)
    cam_fee_per_block = settings.get("cam_fee_per_block", 75.00)
    has_grain = settings.get("has_grain", False)
    edgeband_meter_rate = settings.get("edgeband_meter_rate", 11.50)
    
    # Grid nesting boundaries
    nesting_gap = 8  # Space between pieces is 8mm
    usable_width = 1200  # 1220 - 20 (10mm margin each side)
    usable_length = 2420  # 2440 - 20 (10mm margin each side)
    usable_sheet_area = usable_width * usable_length  # 2,904,000 mm²
    
    waste_multiplier = 0.25 if has_grain else 0.10
    
    total_cut_length_all_items = 0
    total_banded_length_all_items = 0
    total_net_area_required = 0
    total_pieces_count = 0
    
    detailed_rows = []
    
    for idx, row in df.iterrows():
        # Clean inputs
        length = float(row.get("Length (mm)", 500.0))
        width = float(row.get("Width (mm)", 300.0))
        qty = int(row.get("Quantity", 1))
        label = str(row.get("Label", f"Pieza {idx+1}"))
        
        l1 = bool(row.get("L1_Edge", False))
        l2 = bool(row.get("L2_Edge", False))
        w1 = bool(row.get("W1_Edge", False))
        w2 = bool(row.get("W2_Edge", False))
        
        if qty <= 0:
            continue
            
        piece_perimeter = 2 * (length + width)
        total_cut_length_all_items += (piece_perimeter * qty)
        total_pieces_count += qty
        
        # Usable area calculation with bit spacing
        buffered_area = (length + nesting_gap) * (width + nesting_gap)
        total_net_area_required += (buffered_area * qty)
        
        # Edgebanding calculations with +50.8mm calibration overcut per enchapado
        piece_banded_length = 0
        l1_m = (length + 50.8) if l1 else 0
        l2_m = (length + 50.8) if l2 else 0
        w1_m = (width + 50.8) if w1 else 0
        w2_m = (width + 50.8) if w2 else 0
        
        piece_banded_length = l1_m + l2_m + w1_m + w2_m
        total_banded_length_all_items += (piece_banded_length * qty)
        
        detailed_rows.append({
            "Label": label,
            "Dimensiones": f"{length} × {width} mm",
            "Cant.": qty,
            "Corte Crudo (m)": (piece_perimeter * qty) / 1000,
            "Cantos Solicitados": f"{'L1 ' if l1 else ''}{'L2 ' if l2 else ''}{'A1 ' if w1 else ''}{'A2 ' if w2 else ''}".strip() or "Ninguno",
            "Canto Enchapado (m)": (piece_banded_length * qty) / 1000,
            "Área con Bit (m²)": (buffered_area * qty) / 1_000_000
        })

    # Sheets required applying nesting waste multiplier
    factored_area = total_net_area_required * (1 + waste_multiplier)
    total_project_sheets = math.ceil(factored_area / usable_sheet_area) if total_net_area_required > 0 else 0
    if total_project_sheets == 0 and total_net_area_required > 0:
        total_project_sheets = 1
        
    # Router CNC times
    net_cutting_time_minutes = (total_cut_length_all_items / effective_feed_rate) if effective_feed_rate > 0 else 0.0
    g00_overhead_minutes = net_cutting_time_minutes * g00_multiplier
    sheet_change_overhead = (total_project_sheets - 1) * 4.0 if total_project_sheets > 1 else 0.0
    
    # CNC machine setup run: 10 mins overhead
    total_machine_runtime_minutes = (10.0 + net_cutting_time_minutes + g00_overhead_minutes + sheet_change_overhead) if total_pieces_count > 0 else 0.0
    
    # Financial breakdowns
    cnc_execution_cost = total_machine_runtime_minutes * cnc_minute_rate
    cam_programming_blocks = math.ceil(total_project_sheets / 3.0)
    total_cam_fee = (cam_programming_blocks * cam_fee_per_block) if total_pieces_count > 0 else 0.0
    total_cnc_service_cost = cnc_execution_cost + total_cam_fee
    
    # Total linear edgebanding meterage incorporates machine startup calibration reserve (3m)
    total_project_edgebanding_meters = (total_banded_length_all_items + 3000) / 1000 if total_banded_length_all_items > 0 else 0.0
    edgebanding_cost = total_project_edgebanding_meters * edgeband_meter_rate
    
    subtotal_estimated = total_cnc_service_cost + edgebanding_cost
    
    # Heuristic nesting efficiency
    nesting_efficiency = 0.0
    if total_project_sheets > 0:
        nesting_efficiency = (total_net_area_required / (total_project_sheets * usable_sheet_area)) * 100
        # Clamps matching physical floor standards
        if nesting_efficiency > 92: nesting_efficiency = 92.0
        if nesting_efficiency < 45: nesting_efficiency = 45.0
        
    efficiency_label = "Excelente" if nesting_efficiency > 80 else "Buena" if nesting_efficiency > 65 else "Aceptable"
    
    return {
        "total_pieces": total_pieces_count,
        "total_cut_length_m": total_cut_length_all_items / 1000,
        "total_sheets": total_project_sheets,
        "machine_runtime_mins": total_machine_runtime_minutes,
        "cnc_execution_cost": cnc_execution_cost,
        "cam_fee": total_cam_fee,
        "total_cnc_cost": total_cnc_service_cost,
        "edgeband_meters": total_project_edgebanding_meters,
        "edgeband_cost": edgebanding_cost,
        "subtotal": subtotal_estimated,
        "nesting_efficiency": nesting_efficiency,
        "efficiency_label": efficiency_label,
        "detailed_df": pd.DataFrame(detailed_rows) if detailed_rows else pd.DataFrame()
    }


# --- INITIAL SESSION STATE SETUP ---

if 'cutlist' not in st.session_state:
    # Set default standard reference row
    st.session_state.cutlist = pd.DataFrame([{
        "Label": "Lateral Izquierdo",
        "Length (mm)": 720,
        "Width (mm)": 560,
        "Quantity": 2,
        "L1_Edge": True,
        "L2_Edge": False,
        "W1_Edge": True,
        "W2_Edge": False
    }, {
        "Label": "Techo/Piso Gabinete",
        "Length (mm)": 564,
        "Width (mm)": 560,
        "Quantity": 2,
        "L1_Edge": False,
        "L2_Edge": False,
        "W1_Edge": True,
        "W2_Edge": False
    }, {
        "Label": "Entrepaño Ajustable",
        "Length (mm)": 562,
        "Width (mm)": 540,
        "Quantity": 3,
        "L1_Edge": False,
        "L2_Edge": False,
        "W1_Edge": True,
        "W2_Edge": False
    }])

if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None

if 'board_thickness' not in st.session_state:
    st.session_state.board_thickness = 15.0


# --- SIDEBAR: WORKSHOP SETTINGS PANEL ---

with st.sidebar:
    render_logo()
    st.markdown("<h3 style='text-align: center; color: #ffffff; margin-top: -1rem; margin-bottom: 1.5rem; font-size: 1.1rem;'>🔧 Parámetros de Simulación</h3>", unsafe_allow_html=True)
    
    st.markdown("##### 🌲 Características del Tablero")
    # Flexible thickness selection supporting standard values and custom decimals
    thickness_options = [15.0, 16.0, 18.0, 25.0, 28.0, 36.0, "Otro..."]
    default_thickness = float(st.session_state.board_thickness)
    if default_thickness in thickness_options[:-1]:
        default_index = thickness_options.index(default_thickness)
    else:
        default_index = 6 # "Otro..."
        
    thickness_sel = st.selectbox("Espesor de placa", thickness_options, index=default_index, 
                                 format_func=lambda x: f"{x} mm" if isinstance(x, (int, float)) else str(x))
    
    if thickness_sel == "Otro...":
        thickness = st.number_input("Especifica espesor (mm)", min_value=1.0, max_value=100.0, 
                                    value=default_thickness if default_thickness not in thickness_options[:-1] else 15.0, 
                                    step=0.01)
    else:
        thickness = float(thickness_sel)
    
    st.session_state.board_thickness = thickness
    has_grain = st.checkbox("¿Tiene Veta de Madera? (Woodgrain)", value=False, 
                            help="Si se activa, el algoritmo de nesting NO rotará las piezas para mantener el flujo visual de la veta. Esto incrementa el desperdicio estimado al 25%.")
    
    st.markdown("---")
    st.markdown("##### ⚡ Parámetros del Router CNC")
    feed_rate = st.number_input("Velocidad de avance (mm/min)", min_value=1000, max_value=15000, value=6000, step=500,
                                help="Velocidad programada de corte en línea recta.")
    efficiency = st.slider("Eficiencia de Maquinado (%)", min_value=50, max_value=100, value=75, step=5,
                           help="Compensa frenados en esquinas y curvas. 75% es el estándar industrial.") / 100.0
    g00_multiplier = st.slider("Overhead de Movimiento Rápido (%)", min_value=10, max_value=50, value=30, step=5,
                               help="Overhead agregado para simular tiempos de posicionamiento sin corte (G00).") / 100.0
    
    st.markdown("---")
    st.markdown("##### 💵 Tarifas de Maquila (MXN)")
    cnc_minute_rate = st.number_input("Costo por minuto de Router CNC", min_value=1.0, max_value=50.0, value=10.0, step=0.5)
    cam_fee_per_block = st.number_input("Costo de Nesting (cada 3 hojas)", min_value=0.0, max_value=500.0, value=75.0, step=5.0)
    edgeband_meter_rate = st.number_input("Costo de Enchapado por metro lineal", min_value=1.0, max_value=100.0, value=11.50, step=0.5)

    # Compile settings dictionary
    settings = {
        "feed_rate": feed_rate,
        "efficiency": efficiency,
        "g00_multiplier": g00_multiplier,
        "cnc_minute_rate": cnc_minute_rate,
        "cam_fee_per_block": cam_fee_per_block,
        "has_grain": has_grain,
        "thickness": thickness,
        "edgeband_meter_rate": edgeband_meter_rate
    }


# --- MAIN PANEL ---

st.markdown("<h2 style='color: #8a1c2c; margin-top: -1rem;'>🪵 Estimador Standalone de Maquila Halsen</h2>", unsafe_allow_html=True)
st.markdown("Carga y analiza listas de corte de tus clientes de forma local para validar los costos y optimizaciones.", unsafe_allow_html=True)

# 1. Loading files block
col_upload, col_controls = st.columns([3, 1])

with col_upload:
    uploaded_file = st.file_uploader("Sube un archivo de lista de corte (CSV o Excel .xlsx)", type=["csv", "xlsx"])

with col_controls:
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    if st.button("🧹 Limpiar Todo y Restablecer"):
        st.session_state.cutlist = pd.DataFrame([{
            "Label": "Pieza",
            "Length (mm)": 500,
            "Width (mm)": 300,
            "Quantity": 1,
            "L1_Edge": False,
            "L2_Edge": False,
            "W1_Edge": False,
            "W2_Edge": False
        }])
        st.session_state.uploaded_file_name = None
        st.rerun()

# Process uploaded file if present
if uploaded_file is not None and uploaded_file.name != st.session_state.uploaded_file_name:
    try:
        # Read format with flexible delimiter detection
        if uploaded_file.name.endswith(".csv"):
            bytes_data = uploaded_file.read(2048)
            uploaded_file.seek(0)  # Reset pointer
            import csv
            try:
                dialect = csv.Sniffer().sniff(bytes_data.decode('utf-8-sig', errors='ignore'))
                sep = dialect.delimiter
            except Exception:
                # Fallback separator detection
                sample = bytes_data.decode('utf-8-sig', errors='ignore')
                if sample.count(';') > sample.count(','):
                    sep = ';'
                else:
                    sep = ','
            df_raw = pd.read_csv(uploaded_file, sep=sep)
        else:
            df_raw = pd.read_excel(uploaded_file)
            
        st.success(f"✅ Archivo '{uploaded_file.name}' cargado con éxito ({len(df_raw)} filas detectadas).")
        
        # Map columns
        detected_mapping = auto_detect_columns(df_raw)
        # Thickness column is optional for manual mapping warnings
        missing_cols = [k for k, v in detected_mapping.items() if not v and k != "Thickness (mm)"]
        
        if missing_cols:
            st.info("🔧 Se detectaron encabezados de columna personalizados en tu archivo. Confirma el mapeo de columnas abajo:")
            cols_grid = st.columns(4)
            mapped_selections = {}
            
            fields = list(detected_mapping.keys())
            for i, field in enumerate(fields):
                grid_col = cols_grid[i % 4]
                with grid_col:
                    default_idx = 0
                    col_list = ["-- No asignada --"] + list(df_raw.columns)
                    if detected_mapping[field] in df_raw.columns:
                        default_idx = col_list.index(detected_mapping[field])
                        
                    selected_col = st.selectbox(
                        f"Campo: {field}", 
                        col_list, 
                        index=default_idx,
                        key=f"select_map_{field}"
                    )
                    mapped_selections[field] = selected_col if selected_col != "-- No asignada --" else None
        else:
            mapped_selections = detected_mapping
            
        if st.button("📥 Importar Lista de Corte Mapeada", key="confirm_import"):
            cleaned_rows = []
            for idx, row in df_raw.iterrows():
                label_col = mapped_selections.get("Label")
                label = clean_string_column(pd.Series([row[label_col]]))[0] if label_col else f"Pieza {idx+1}"
                
                l_col = mapped_selections.get("Length (mm)")
                length = clean_float_column(pd.Series([row[l_col]]), default_val=500.0)[0] if l_col else 500.0
                
                w_col = mapped_selections.get("Width (mm)")
                width = clean_float_column(pd.Series([row[w_col]]), default_val=300.0)[0] if w_col else 300.0
                
                q_col = mapped_selections.get("Quantity")
                qty = clean_numeric_column(pd.Series([row[q_col]]), default_val=1)[0] if q_col else 1
                
                l1_col = mapped_selections.get("L1_Edge")
                l1 = clean_boolean_column(pd.Series([row[l1_col]]))[0] if l1_col else False
                
                l2_col = mapped_selections.get("L2_Edge")
                l2 = clean_boolean_column(pd.Series([row[l2_col]]))[0] if l2_col else False
                
                w1_col = mapped_selections.get("W1_Edge")
                w1 = clean_boolean_column(pd.Series([row[w1_col]]))[0] if w1_col else False
                
                w2_col = mapped_selections.get("W2_Edge")
                w2 = clean_boolean_column(pd.Series([row[w2_col]]))[0] if w2_col else False
                
                cleaned_rows.append({
                    "Label": label,
                    "Length (mm)": length,
                    "Width (mm)": width,
                    "Quantity": qty,
                    "L1_Edge": l1,
                    "L2_Edge": l2,
                    "W1_Edge": w1,
                    "W2_Edge": w2
                })
            
            # Auto-detect thickness from CSV if present and update st.session_state.board_thickness
            t_col = mapped_selections.get("Thickness (mm)")
            if t_col:
                try:
                    thicknesses = clean_float_column(df_raw[t_col], default_val=15.0)
                    if not thicknesses.empty:
                        mode_thickness = float(thicknesses.mode().iloc[0])
                        st.session_state.board_thickness = mode_thickness
                except Exception:
                    pass
            
            st.session_state.cutlist = pd.DataFrame(cleaned_rows)
            st.session_state.uploaded_file_name = uploaded_file.name
            st.success("🎉 Lista de corte importada exitosamente al editor.")
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error procesando el archivo: {str(e)}.")


# --- PART ADMINISTRATION CONTROLS (FORM-BASED WITH FLAWLESS TABBING) ---

st.markdown("---")
st.markdown("### ✏️ Administrar Piezas de la Lista")
st.caption("Usa estos controles para agregar o modificar piezas de forma fluida. Soporta saltos rápidos con la tecla <TAB> y activar casillas con <Space> sin perder el foco.")

col_add, col_edit = st.columns(2)

with col_add:
    with st.form("quick_add_form", clear_on_submit=True):
        st.markdown("##### ➕ Agregar Nueva Pieza")
        
        add_name = st.text_input("Nombre de Pieza", value="Lateral", key="form_label")
        col_dim1, col_dim2, col_qty = st.columns(3)
        with col_dim1:
            add_length_str = st.text_input("Largo (mm)", value="720", key="add_length_str_key")
        with col_dim2:
            add_width_str = st.text_input("Ancho (mm)", value="560", key="add_width_str_key")
        with col_qty:
            add_qty_str = st.text_input("Cantidad", value="2", key="add_qty_str_key")
            
        st.markdown("<p style='font-size:0.85rem; font-weight:bold; margin-bottom: 0px;'>Enchapado de Cantos para esta pieza:</p>", unsafe_allow_html=True)
        col_edges1, col_edges2 = st.columns(2)
        with col_edges1:
            add_l1 = st.checkbox("Canto Largo 1 (L1)", value=False)
            add_l2 = st.checkbox("Canto Largo 2 (L2)", value=False)
        with col_edges2:
            add_w1 = st.checkbox("Canto Ancho 1 (A1)", value=False)
            add_w2 = st.checkbox("Canto Ancho 2 (A2)", value=False)
            
        add_submitted = st.form_submit_button("➕ Añadir a la Lista")
        
        if add_submitted:
            new_row = {
                "Label": add_name if add_name else "Pieza Nueva",
                "Length (mm)": safe_float(add_length_str, 500.0),
                "Width (mm)": safe_float(add_width_str, 300.0),
                "Quantity": safe_int(add_qty_str, 1),
                "L1_Edge": bool(add_l1),
                "L2_Edge": bool(add_l2),
                "W1_Edge": bool(add_w1),
                "W2_Edge": bool(add_w2)
            }
            st.session_state.cutlist = pd.concat([st.session_state.cutlist, pd.DataFrame([new_row])], ignore_index=True)
            st.toast(f"✅ Pieza '{add_name}' añadida.")
            st.rerun()

with col_edit:
    if len(st.session_state.cutlist) > 0:
        # Generate item choices mapping
        options_list = []
        for idx, row in st.session_state.cutlist.iterrows():
            options_list.append((idx, f"#{idx+1}: {row['Label']} ({row['Length (mm)']}x{row['Width (mm)']}) × {row['Quantity']} pza(s)"))
            
        selected_option = st.selectbox(
            "✏️ Selecciona una pieza para editar o eliminar:",
            options_list,
            format_func=lambda x: x[1]
        )
        
        if selected_option is not None:
            sel_idx = selected_option[0]
            current_piece = st.session_state.cutlist.iloc[sel_idx]
            
            # Setup a sub-form populated with current piece's data using text inputs for flawless tabbing
            with st.form(f"edit_form_{sel_idx}", clear_on_submit=False):
                st.markdown(f"##### Modificar Pieza #{sel_idx+1}")
                
                edit_name = st.text_input("Nombre de Pieza", value=str(current_piece["Label"]))
                col_edim1, col_edim2, col_eqty = st.columns(3)
                with col_edim1:
                    edit_length_str = st.text_input("Largo (mm)", value=str(current_piece["Length (mm)"]))
                with col_edim2:
                    edit_width_str = st.text_input("Ancho (mm)", value=str(current_piece["Width (mm)"]))
                with col_eqty:
                    edit_qty_str = st.text_input("Cantidad", value=str(current_piece["Quantity"]))
                    
                st.markdown("<p style='font-size:0.85rem; font-weight:bold; margin-bottom: 0px;'>Enchapado de Cantos para esta pieza:</p>", unsafe_allow_html=True)
                col_eedges1, col_eedges2 = st.columns(2)
                with col_eedges1:
                    edit_l1 = st.checkbox("Canto Largo 1 (L1)", value=bool(current_piece["L1_Edge"]))
                    edit_l2 = st.checkbox("Canto Largo 2 (L2)", value=bool(current_piece["L2_Edge"]))
                with col_eedges2:
                    edit_w1 = st.checkbox("Canto Ancho 1 (A1)", value=bool(current_piece["W1_Edge"]))
                    edit_w2 = st.checkbox("Canto Ancho 2 (A2)", value=bool(current_piece["W2_Edge"]))
                    
                col_eb1, col_eb2 = st.columns(2)
                with col_eb1:
                    edit_submitted = st.form_submit_button("💾 Guardar Cambios")
                with col_eb2:
                    delete_submitted = st.form_submit_button("❌ Eliminar esta Pieza")
                    
                if edit_submitted:
                    st.session_state.cutlist.at[sel_idx, "Label"] = edit_name if edit_name else "Pieza"
                    st.session_state.cutlist.at[sel_idx, "Length (mm)"] = safe_float(edit_length_str, 500.0)
                    st.session_state.cutlist.at[sel_idx, "Width (mm)"] = safe_float(edit_width_str, 300.0)
                    st.session_state.cutlist.at[sel_idx, "Quantity"] = safe_int(edit_qty_str, 1)
                    st.session_state.cutlist.at[sel_idx, "L1_Edge"] = bool(edit_l1)
                    st.session_state.cutlist.at[sel_idx, "L2_Edge"] = bool(edit_l2)
                    st.session_state.cutlist.at[sel_idx, "W1_Edge"] = bool(edit_w1)
                    st.session_state.cutlist.at[sel_idx, "W2_Edge"] = bool(edit_w2)
                    
                    st.toast(f"✅ Cambios guardados para Pieza #{sel_idx+1}.")
                    st.rerun()
                    
                if delete_submitted:
                    st.session_state.cutlist = st.session_state.cutlist.drop(sel_idx).reset_index(drop=True)
                    st.toast("❌ Pieza eliminada de la lista.")
                    st.rerun()
    else:
        st.info("La lista está vacía. Agrega una pieza con el formulario de la izquierda.")


# --- DYNAMIC LIST PREVIEW (READ ONLY & RELIABLE) ---

st.markdown("---")
st.markdown("### 📋 Vista Previa de la Lista de Corte")
st.caption("Esta es la tabla actual de tu estimación (en formato estándar de lectura para evitar bloqueos del cursor).")

# Render as read-only standard st.dataframe for beautiful, reliable grid previewing
st.dataframe(
    st.session_state.cutlist,
    use_container_width=True,
    column_config={
        "Label": st.column_config.TextColumn("Nombre Pieza"),
        "Length (mm)": st.column_config.NumberColumn("Largo (mm)"),
        "Width (mm)": st.column_config.NumberColumn("Ancho (mm)"),
        "Quantity": st.column_config.NumberColumn("Cantidad"),
        "L1_Edge": st.column_config.CheckboxColumn("Canto L1"),
        "L2_Edge": st.column_config.CheckboxColumn("Canto L2"),
        "W1_Edge": st.column_config.CheckboxColumn("Canto A1"),
        "W2_Edge": st.column_config.CheckboxColumn("Canto A2")
    }
)


# --- RUN CALCULATIONS ON THE ENTIRE LIST ---
results = run_workshop_calculations(st.session_state.cutlist, settings)


# --- DISPLAY METRICS GRID ---

st.markdown("---")
st.markdown("<h3 style='color: #ffffff; margin-bottom: 1rem;'>📊 Métricas Calculadas del Proyecto</h3>", unsafe_allow_html=True)

# Build beautiful 4-column metric cards layout (identical to the website's metrics results)
m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Tableros Necesarios</div>
        <div class="metric-val">{results['total_sheets']} Hojas</div>
        <div class="metric-desc">Eficiencia: <b>{results['nesting_efficiency']:.1f}%</b> ({results['efficiency_label']})</div>
    </div>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Router CNC</div>
        <div class="metric-val">{results['machine_runtime_mins']:.1f} min</div>
        <div class="metric-desc">Corte crudo: {results['total_cut_length_m']:.2f} m. Costo: <b>${results['total_cnc_cost']:,.2f} MXN</b></div>
    </div>
    """, unsafe_allow_html=True)

with m_col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-lbl">Cubrecanto Requerido</div>
        <div class="metric-val">{results['edgeband_meters']:.2f} m</div>
        <div class="metric-desc">Incluye reservas (+50.8mm por lado y +3m). Costo: <b>${results['edgeband_cost']:,.2f} MXN</b></div>
    </div>
    """, unsafe_allow_html=True)

with m_col4:
    st.markdown(f"""
    <div class="metric-card" style="border: 2px solid #8a1c2c; background-color: #1e1215;">
        <div class="metric-lbl" style="color: #ec5b70;">Subtotal Estimado</div>
        <div class="metric-val" style="font-size: 2rem; color: #ec5b70;">${results['subtotal']:,.2f}*</div>
        <div class="metric-desc" style="color: #888888;">Precio en MXN antes de IVA. Incluye despiece.</div>
    </div>
    """, unsafe_allow_html=True)


# --- EXPORT & DETAILED EXPANSER CONTROLS ---

st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
col_down1, col_down2 = st.columns([2, 1])

with col_down1:
    st.markdown("##### 📥 Exportar Lista")
    st.caption("Guarda esta lista de corte modificada de vuelta en el formato CSV nativo compatible con Halsen.")
    
    # Prepare standard export format supporting decimals and including thickness
    export_rows = []
    for idx, row in st.session_state.cutlist.iterrows():
        export_rows.append({
            "Label": row.get("Label", f"Pieza {idx+1}"),
            "Length (mm)": round(float(row.get("Length (mm)", 500.0)), 2),
            "Width (mm)": round(float(row.get("Width (mm)", 300.0)), 2),
            "Quantity": int(row.get("Quantity", 1)),
            "L1_Edge": 1 if row.get("L1_Edge", False) else 0,
            "L2_Edge": 1 if row.get("L2_Edge", False) else 0,
            "W1_Edge": 1 if row.get("W1_Edge", False) else 0,
            "W2_Edge": 1 if row.get("W2_Edge", False) else 0,
            "Thickness (mm)": round(float(settings['thickness']), 2)
        })
    export_df = pd.DataFrame(export_rows)
    csv_data = export_df.to_csv(index=False, encoding='utf-8-sig')
    
    # Format the current date as requested: YYYY-MM-DD:HH:mm
    import datetime
    current_date_str = datetime.datetime.now().strftime("%Y-%m-%d:%H:%M")
    export_filename = f"{current_date_str}_HALSEN_Cutlist.csv"
    
    st.download_button(
        label="📥 Descargar Lista de Corte en CSV",
        data=csv_data,
        file_name=export_filename,
        mime="text/csv"
    )

# --- COLLAPSIBLE WORKSHOP BREAKDOWN ---
st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
with st.expander("🔍 Ver Desglose de Cálculo Técnico", expanded=False):
    if not results['detailed_df'].empty:
        st.markdown("##### Métricas de Precisión por Pieza")
        st.dataframe(
            results['detailed_df'],
            use_container_width=True,
            column_config={
                "Corte Crudo (m)": st.column_config.NumberColumn(format="%.2f m"),
                "Canto Enchapado (m)": st.column_config.NumberColumn(format="%.2f m"),
                "Área con Bit (m²)": st.column_config.NumberColumn(format="%.4f m²")
            }
        )
    else:
        st.warning("La lista de piezas está vacía.")

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 0.8rem; color: #666666;'>HALSEN ENCODED CORTEXIA | Soluciones de Precisión Industrial | Puebla, Cholula, Chipilo, México.</p>", unsafe_allow_html=True)

# HALSEN | Estimador de Maquila de Corte CNC y Enchapado

Esta es una aplicación de escritorio interactiva desarrollada en **Python** utilizando **Streamlit**. Está diseñada para uso interno en el taller de Halsen para procesar listas de despiece de clientes (en formato CSV o Excel), calcular de forma precisa las métricas del taller, y generar cotizaciones y resúmenes estructurados listos para enviar por WhatsApp.

---

## Características de la Versión 1

1. **Importación Inteligente:**
   - Soporte para archivos `.csv` y `.xlsx` (Excel).
   - **Mapeo Inteligente de Columnas:** Si el cliente envía un archivo con encabezados personalizados (ej. `L`, `A`, `Cant`, `Tapacanto`), la aplicación detecta automáticamente las columnas y permite mapearlas visualmente mediante selectores interactivos.

2. **Editor de Tabla Interactivo:**
   - Una vez cargada la lista, puedes editar nombres, dimensiones, cantidades o cantos directamente en pantalla.
   - Posibilidad de agregar o eliminar filas en tiempo real.

3. **Cálculos de Maquila Reales:**
   - **Nesting Real:** Margen de hoja de $10\text{ mm}$ y separación entre piezas de $8\text{ mm}$ (Bit de Router CNC).
   - **Soporte para Veta (Woodgrain):** Ajuste de coeficiente de desperdicio ($25\%$ con veta, $10\%$ sin veta).
   - **Desglose de Cantos:** Reserva de calibración de $+50.8\text{ mm}$ ($2\text{ pulgadas}$) por lado enchapado y un buffer inicial del proyecto de $+3\text{ metros}$ para el purgado de la enchapadora.
   - **Tiempo de Máquina CNC Real:** Basado en velocidad de avance de $6000\text{ mm/min}$ a un $75\%$ de eficiencia ($4500\text{ mm/min}$ efectivo), más un $30\%$ de overhead por trayectorias rápidas (G00) y $4.0\text{ minutos}$ de recambio de hoja.

4. **Branding Consistente:**
   - Diseñado con la identidad visual oficial de Halsen (Borgoña `#8a1c2c`, Carbón `#333333`, Verde Menta `#2e7d32`, y fondo cálido).
   - Integración del logotipo vectorial oficial (SVG).

5. **Copiar Cotización a WhatsApp:**
   - Formateador de texto que genera un resumen limpio para enviar al cliente por WhatsApp con un solo clic.

---

## Requisitos de Instalación

1. Asegúrate de tener Python 3.8 o superior instalado en tu equipo.
2. Abre tu terminal o consola en esta carpeta y crea un entorno virtual (recomendado):

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Linux/macOS:
source venv/bin/activate
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1
```

3. Instala las dependencias necesarias:

```bash
pip install -r requirements.txt
```

---

## Cómo Ejecutar la Aplicación

Para iniciar el servidor local de Streamlit y abrir la interfaz gráfica en tu navegador, ejecuta:

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador web en la dirección: `http://localhost:8501`.

---

## Estructura de Columnas Sugerida

Para importaciones rápidas sin necesidad de mapeo manual, utiliza el siguiente formato de encabezados:

| Label | Length (mm) | Width (mm) | Quantity | L1_Edge | L2_Edge | W1_Edge | W2_Edge |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| Lateral | 720 | 560 | 2 | 1 | 0 | 1 | 0 |
| Techo | 564 | 560 | 2 | 0 | 0 | 1 | 0 |

*(Los cantos admiten `1` o `0`, o valores lógicos `TRUE`/`FALSE`).*

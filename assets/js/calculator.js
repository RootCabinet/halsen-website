  function bindRowListeners(row) {
    const inputs = row.querySelectorAll('input');
    inputs.forEach(input => {
      input.addEventListener('input', executeWorkshopCalculations);
    });
  }

  function addRow() {
    const tbody = document.getElementById('table-body');
    const rows = tbody.querySelectorAll('.item-row');
    const newIdx = rows.length + 1;
    
    const tr = document.createElement('tr');
    tr.className = 'item-row';
    tr.innerHTML = `
      <td class="item-index">#${newIdx}</td>
      <td><input type="text" class="form-input piece_name" value="Pieza Nueva" style="padding: 0.4rem; width: 100%;"></td>
      <td><input type="number" class="table-input-number length_mm" value="500" min="10" max="2400"></td>
      <td><input type="number" class="table-input-number width_mm" value="300" min="10" max="1200"></td>
      <td><input type="number" class="table-input-number quantity" value="1" min="1"></td>
      <td>
        <div class="edgebanding-checkboxes">
          <label class="edge-box" title="Largo 1">
            <input type="checkbox" class="edge_l1">
            <span>L1</span>
          </label>
          <label class="edge-box" title="Largo 2">
            <input type="checkbox" class="edge_l2">
            <span>L2</span>
          </label>
          <label class="edge-box" title="Ancho 1">
            <input type="checkbox" class="edge_a1">
            <span>A1</span>
          </label>
          <label class="edge-box" title="Ancho 2">
            <input type="checkbox" class="edge_a2">
            <span>A2</span>
          </label>
        </div>
      </td>
      <td><button type="button" class="btn-remove-row" onclick="removeRow(this)" style="color:#d9534f; border:none; background:none; cursor:pointer; font-weight:bold; font-size:1.1rem; padding: 0 4px;">❌</button></td>
    `;
    
    tbody.appendChild(tr);
    bindRowListeners(tr);
    executeWorkshopCalculations();
    
    // Focus the first numerical input (length)
    const lenInput = tr.querySelector('.length_mm');
    if (lenInput) {
      lenInput.focus();
      lenInput.select();
    }
  }

  function removeRow(button) {
    const tbody = document.getElementById('table-body');
    const row = button.closest('tr');
    if (tbody.querySelectorAll('.item-row').length > 1) {
      row.remove();
      updateIndexes();
      executeWorkshopCalculations();
    } else {
      alert("La lista debe contener al menos una pieza.");
    }
  }

  function updateIndexes() {
    const rows = document.querySelectorAll('.item-row');
    rows.forEach((row, idx) => {
      row.querySelector('.item-index').innerText = `#${idx + 1}`;
    });
  }

  function clearCutlist() {
    const tbody = document.getElementById('table-body');
    const rows = tbody.querySelectorAll('.item-row');
    
    for (let i = 1; i < rows.length; i++) {
      rows[i].remove();
    }
    
    const firstRow = rows[0];
    firstRow.querySelector('.piece_name').value = "Lateral Izquierdo Gabinete";
    firstRow.querySelector('.length_mm').value = "720";
    firstRow.querySelector('.width_mm').value = "560";
    firstRow.querySelector('.quantity').value = "2";
    firstRow.querySelector('.edge_l1').checked = true;
    firstRow.querySelector('.edge_l2').checked = false;
    firstRow.querySelector('.edge_a1').checked = true;
    firstRow.querySelector('.edge_a2').checked = false;
    
    updateIndexes();
    executeWorkshopCalculations();
  }

  function executeWorkshopCalculations() {
    const rows = document.querySelectorAll('.item-row');
    
    const FEED_RATE = 6000;
    const EFFICIENCY = 0.75;
    const EFFECTIVE_FEED_RATE = FEED_RATE * EFFICIENCY; // 4500 mm/min
    const G00_OVERHEAD_MULTIPLIER = 0.30; 
    
    const CNC_MINUTE_RATE = 10.00;
    const CAM_FEE_PER_BLOCK = 75.00;
    let hasGrain = document.getElementById('has-grain') ? document.getElementById('has-grain').checked : false;
    let thickness = 18; // Defaulting to 18mm
    
    const NESTING_GAP = hasGrain ? 12 : 8; // Adjust margin slightly bigger for grain
    const USABLE_SHEET_AREA = 1200 * 2420; 
    
    const INITIAL_SETUP_TIME = 10.0;
    const SHEET_CHANGE_INTERVAL = 4.0;

    const wasteMultiplier = hasGrain ? 0.25 : 0.10;

    let edgebandMeterRate = 11.50; // Default edgebanding service rate per meter
    let hasAnyBanding = true; // Always evaluate lengths, cost applies if > 0

    let totalCutLengthAllItems = 0;
    let totalBandedLengthAllItems = 0;
    let totalNetAreaRequired = 0;
    let totalPiecesCount = 0;

    let csvRows = [["Largo", "Ancho", "Cantidad", "Espesor", "Canto_L1", "Canto_L2", "Canto_A1", "Canto_A2", "Nombre"]];

    for (let i = 0; i < rows.length; i++) {
        let row = rows[i];
        let name = row.querySelector('.piece_name').value || `Pieza ${i+1}`;
        let lengthInput = row.querySelector('.length_mm');
        let widthInput = row.querySelector('.width_mm');
        let qtyInput = row.querySelector('.quantity');
        
        let length = parseInt(lengthInput.value) || 0;
        let width = parseInt(widthInput.value) || 0;
        let qty = parseInt(qtyInput.value) || 0;

        // Visual validation feedback/handling
        if (length > 2400) {
          lengthInput.style.borderColor = "#ef4444";
        } else {
          lengthInput.style.borderColor = "";
        }
        
        if (width > 1200) {
          widthInput.style.borderColor = "#ef4444";
        } else {
          widthInput.style.borderColor = "";
        }

        let l1 = row.querySelector('.edge_l1').checked;
        let l2 = row.querySelector('.edge_l2').checked;
        let a1 = row.querySelector('.edge_a1').checked;
        let a2 = row.querySelector('.edge_a2').checked;

        let piecePerimeter = 2 * (length + width);
        totalCutLengthAllItems += (piecePerimeter * qty);
        totalPiecesCount += qty;

        let bufferedArea = (length + NESTING_GAP) * (width + NESTING_GAP);
        totalNetAreaRequired += (bufferedArea * qty);

        let pieceBandedLength = 0;
        if (hasAnyBanding) {
          if (l1) pieceBandedLength += (length + 50.8);
          if (l2) pieceBandedLength += (length + 50.8);
          if (a1) pieceBandedLength += (width + 50.8);
          if (a2) pieceBandedLength += (width + 50.8);
        }
        totalBandedLengthAllItems += (pieceBandedLength * qty);

        csvRows.push([length, width, qty, thickness, l1?1:0, l2?1:0, a1?1:0, a2?1:0, name]);
    }

    let factoredArea = totalNetAreaRequired * (1 + wasteMultiplier);
    let totalProjectSheets = Math.ceil(factoredArea / USABLE_SHEET_AREA);
    if (totalProjectSheets === 0 && totalNetAreaRequired > 0) totalProjectSheets = 1;

    let netCuttingTimeMinutes = totalCutLengthAllItems / EFFECTIVE_FEED_RATE;
    let g00OverheadMinutes = netCuttingTimeMinutes * G00_OVERHEAD_MULTIPLIER;
    let sheetChangeOverhead = totalProjectSheets > 1 ? (totalProjectSheets - 1) * SHEET_CHANGE_INTERVAL : 0;
    
    let totalMachineRuntimeMinutes = totalPiecesCount > 0 ? (INITIAL_SETUP_TIME + netCuttingTimeMinutes + g00OverheadMinutes + sheetChangeOverhead) : 0;
    let cncExecutionCost = totalMachineRuntimeMinutes * CNC_MINUTE_RATE;

    let camProgrammingBlocks = Math.ceil(totalProjectSheets / 3);
    let totalCamFee = totalPiecesCount > 0 ? (camProgrammingBlocks * CAM_FEE_PER_BLOCK) : 0;
    
    let totalCncServiceCost = cncExecutionCost + totalCamFee;
    let totalProjectEdgebandingMeters = (hasAnyBanding && totalBandedLengthAllItems > 0) ? (totalBandedLengthAllItems + 3000) / 1000 : 0;
    let edgebandingCost = totalProjectEdgebandingMeters * edgebandMeterRate;

    let subtotalEstimated = totalCncServiceCost + edgebandingCost;
    
    // Heuristic nesting efficiency (simulated, based on grain and area ratio)
    let nestingEfficiency = 0;
    if (totalProjectSheets > 0) {
      nestingEfficiency = (totalNetAreaRequired / (totalProjectSheets * USABLE_SHEET_AREA)) * 100;
      // Clamp values between realistic ranges
      if (nestingEfficiency > 92) nestingEfficiency = 92;
      if (nestingEfficiency < 45) nestingEfficiency = 45;
    }
    let efficiencyLabel = nestingEfficiency > 80 ? "Excelente" : nestingEfficiency > 65 ? "Buena" : "Aceptable";

    // Update UI elements
    document.getElementById('res-total-pieces').innerText = `${totalPiecesCount} pza(s)`;
    document.getElementById('res-cut-length').innerText = `${(totalCutLengthAllItems / 1000).toFixed(2)} m`;
    document.getElementById('res-edge-meters').innerText = `${totalProjectEdgebandingMeters.toFixed(2)} m`;
    
    // Format currency to MXN
    const formatter = new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    });
    document.getElementById('res-subtotal').innerText = `${formatter.format(subtotalEstimated)}*`;

    // Configure CSV Button link content
    let csvContent = "data:text/csv;charset=utf-8,\uFEFF" + csvRows.map(e => e.join(",")).join("\n");
    let downloadBtn = document.getElementById('csv-download-btn');
    if (downloadBtn) {
      downloadBtn.setAttribute("href", encodeURI(csvContent));
      downloadBtn.setAttribute("download", `halsen_lista_corte_${thickness}mm.csv`);
    }
  }

  function sendQuoteRequest() {
    let pieces = document.getElementById('res-total-pieces').innerText;
    let cutLength = document.getElementById('res-cut-length').innerText;
    let edgeMeters = document.getElementById('res-edge-meters').innerText;
    let subtotal = document.getElementById('res-subtotal').innerText;
    
    let text = `Hola Halsen, me gustaría solicitar una cotización formal de maquila.\n\n*Resumen de Estimación:*\n- Piezas: ${pieces}\n- Corte Crudo: ${cutLength}\n- Cubrecanto: ${edgeMeters}\n- Subtotal Estimado: ${subtotal}\n\n*Nota:* Tengo el archivo CSV descargado para enviarles y revisar los detalles del proyecto. Mi nombre es: `;
    
    let encodedText = encodeURIComponent(text);
    let whatsappUrl = `https://wa.me/522229211335?text=${encodedText}`;
    
    window.open(whatsappUrl, '_blank');
  }

  document.addEventListener('DOMContentLoaded', () => {
    // Bind listeners to initial rows
    const rows = document.querySelectorAll('.item-row');
    rows.forEach(row => {
      bindRowListeners(row);
    });
    
    // Bind global selections
    let hasGrainEl = document.getElementById('has-grain');
    if (hasGrainEl) {
      hasGrainEl.addEventListener('change', executeWorkshopCalculations);
    }
    
    // Event delegation on table body to handle TAB key down inside the last input of the last row
    const tableElement = document.querySelector('.cutlist-table');
    if (tableElement) {
      tableElement.addEventListener('keydown', function(event) {
        if (event.key === 'Tab' && !event.shiftKey) {
          const activeEl = document.activeElement;
          const row = activeEl.closest('tr');
          if (!row) return;
          
          const tbody = document.getElementById('table-body');
          const allRows = tbody.querySelectorAll('.item-row');
          const isLastRow = row === allRows[allRows.length - 1];
          
          const isLastField = activeEl.classList.contains('edge_a2');
          
          if (isLastRow && isLastField) {
            event.preventDefault(); // Stop default focus escape from table
            addRow();
          }
        }
      });
    }

    // Run initial calculations
    executeWorkshopCalculations();
  });
/* =========================================================
   StockMate – JavaScript principal
   ========================================================= */

// ----- Toggle sidebar -----
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar       = document.getElementById('sidebar');

if (sidebarToggle && sidebar) {
  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
  });
}

// ----- Polling de alertas de stock (Observer en el frontend) -----
// Consulta /api/alerts cada 30 segundos y actualiza el panel de alertas.

const alertBell    = document.getElementById('alertBell');
const alertCount   = document.getElementById('alertCount');
const alertsList   = document.getElementById('alertsList');
const markAllBtn   = document.getElementById('markAllRead');

let lastAlertCount = 0;

async function fetchAlerts() {
  try {
    const res  = await fetch('/api/alerts');
    if (!res.ok) return;
    const data = await res.json();

    // Actualizar badge
    if (data.count > 0) {
      alertCount.textContent = data.count;
      alertCount.classList.remove('d-none');
      if (data.count > lastAlertCount) {
        alertCount.classList.add('pulse');
        setTimeout(() => alertCount.classList.remove('pulse'), 500);
      }
    } else {
      alertCount.classList.add('d-none');
    }
    lastAlertCount = data.count;

    // Renderizar lista en el panel
    if (alertsList) {
      if (data.alerts.length === 0) {
        alertsList.innerHTML = `
          <div class="text-center text-muted py-4">
            <i class="bi bi-check-circle text-success fs-3 d-block mb-2"></i>
            Sin alertas pendientes
          </div>`;
      } else {
        alertsList.innerHTML = data.alerts.map(a => `
          <div class="list-group-item px-3 py-2" id="alert-${a.id}">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <div class="fw-semibold">${escapeHtml(a.product)}</div>
                <div class="text-muted small">
                  Stock: <strong class="text-danger">${a.quantity}</strong> / Min: ${a.min_stock}
                  &nbsp;·&nbsp; ${a.created_at}
                </div>
              </div>
              <button class="btn btn-sm btn-link text-muted p-0 ms-2"
                      onclick="markRead(${a.id})" title="Marcar como leida">
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
          </div>`).join('');
      }
    }
  } catch (e) {
    // Silencioso: no interrumpir la experiencia si falla el polling
  }
}

async function markRead(alertId) {
  await fetch(`/api/alerts/${alertId}/read`, { method: 'POST' });
  const el = document.getElementById(`alert-${alertId}`);
  if (el) el.remove();
  fetchAlerts();
}

if (markAllBtn) {
  markAllBtn.addEventListener('click', async () => {
    await fetch('/api/alerts/read-all', { method: 'POST' });
    fetchAlerts();
  });
}

// Solo pollear si el usuario esta autenticado (sidebar existe)
if (sidebar) {
  fetchAlerts();
  setInterval(fetchAlerts, 30_000);
}

// ----- Utilidad: escapar HTML para prevenir XSS -----
function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// ----- Auto-dismiss flash messages despues de 5 segundos -----
document.querySelectorAll('.alert.alert-dismissible').forEach(alert => {
  setTimeout(() => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
    if (bsAlert) bsAlert.close();
  }, 5000);
});

// ----- Confirmacion generica para formularios de eliminacion -----
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    if (!confirm(el.dataset.confirm)) e.preventDefault();
  });
});

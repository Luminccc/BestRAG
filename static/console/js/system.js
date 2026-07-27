/**
 * System Dashboard — 状态面板 + 全链路验证
 */
async function loadSystemStatus() {
  try {
    var data = await API.get('/validation/status');
    renderStatus(data);
  } catch (e) {
    console.error('Status error:', e);
  }
}

function renderStatus(data) {
  var d = data.details || {};
  setStatusCell(0, data.core === 'ok');
  setStatusCell(1, d.embedding && d.embedding.status === 'ok');
  setStatusCell(2, d.vectorstore && d.vectorstore.status === 'ok');
  setStatusCell(3, data.retrieval === 'ok');
  setStatusCell(4, d.llm && d.llm.status === 'ok' ? true : (d.llm && d.llm.status === 'no_key' ? 'warn' : false));
  setStatusCell(5, data.generation === 'ok');
}

function setStatusCell(idx, ok) {
  var cells = document.querySelectorAll('#status-grid .status-item .value');
  if (!cells[idx]) return;
  var cls = ok === true ? 'status-ok' : (ok === 'warn' ? 'status-warn' : (ok === false ? 'status-err' : 'status-unknown'));
  var txt = ok === true ? '✅ OK' : (ok === 'warn' ? '⚠️ No Key' : (ok === false ? '❌ Error' : '⚪ Unknown'));
  cells[idx].className = 'value ' + cls;
  cells[idx].textContent = txt;
}

// ── Full Validation ──
document.addEventListener('DOMContentLoaded', function() {
  var refreshBtn = $id('btn-refresh-status');
  if (refreshBtn) refreshBtn.addEventListener('click', loadSystemStatus);

  var runBtn = $id('btn-run-validation');
  if (runBtn) {
    runBtn.addEventListener('click', async function() {
      setHTML('validation-result', '<span class="warn">Running full validation...</span>');
      try {
        var report = await API.post('/validation/run', {});
        renderFullValidation(report);
      } catch (e) {
        setHTML('validation-result', '<span class="err">Error: ' + escapeHtml(e.message) + '</span>');
      }
    });
  }
});

function renderFullValidation(report) {
  var s = report.summary || {};
  setHTML('validation-summary',
    '<div style="display:flex;gap:16px;font-size:.8rem;margin-bottom:8px;">' +
    '<span class="ok">✅ PASS: ' + (s.pass || 0) + '</span>' +
    '<span class="err">❌ FAIL: ' + (s.fail || 0) + '</span>' +
    '<span class="warn">⏭ SKIP: ' + (s.skip || 0) + '</span>' +
    '<span style="color:var(--text-muted)">Total: ' + (s.total || 0) + '</span>' +
    '</div>'
  );
  var checks = report.checks || [];
  var rows = checks.map(function(c) {
    var icon = c.status === 'PASS' ? '✅' : (c.status === 'SKIP' ? '⏭' : '❌');
    var color = c.status === 'PASS' ? 'ok' : (c.status === 'SKIP' ? 'warn' : 'err');
    return '<tr><td>' + icon + '</td><td class="' + color + '">' + escapeHtml(c.name) +
      '</td><td class="' + color + '">' + c.status + '</td><td>' + escapeHtml(c.message || '-') +
      '</td><td>' + (c.latency || 0) + 'ms</td></tr>';
  }).join('');
  setHTML('validation-result',
    '<table class="data-table"><thead><tr><th></th><th>Check</th><th>Status</th><th>Message</th><th>Latency</th></tr></thead><tbody>' + rows + '</tbody></table>'
  );
}

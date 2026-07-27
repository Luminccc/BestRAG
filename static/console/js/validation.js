/**
 * Validation Scenario — KB / QA / RAG E2E 场景验证
 */
document.addEventListener('DOMContentLoaded', function() {
  var btns = document.querySelectorAll('.scenario-btn');
  btns.forEach(function(b) {
    b.addEventListener('click', function() {
      var scenario = b.dataset.scenario;
      runScenario(scenario, b);
    });
  });
});

async function runScenario(name, btn) {
  // 标记按钮状态
  var origText = btn.textContent;
  btn.textContent = '⏳ Running...';
  btn.disabled = true;

  var endpoints = {
    'knowledge-base': '/validation/scenario/knowledge-base',
    'qa': '/validation/scenario/qa',
    'rag-e2e': '/validation/scenario/rag-e2e',
  };

  try {
    var data = await API.post(endpoints[name], {});
    renderScenarioResult(data);
    toast(name + ' scenario complete: ' + data.status);
  } catch (e) {
    setHTML('scenario-result', '<span class="err">Error: ' + escapeHtml(e.message) + '</span>');
    toast(e.message, 'error');
  } finally {
    btn.textContent = origText;
    btn.disabled = false;
  }
}

function renderScenarioResult(data) {
  var ok = data.status === 'PASS';
  var icon = ok ? '✅' : '❌';
  var color = ok ? 'ok' : 'err';

  var checksHtml = (data.checks || []).map(function(c) {
    var ci = c.status === 'PASS' ? '✅' : (c.status === 'SKIP' ? '⏭' : '❌');
    var cc = c.status === 'PASS' ? 'ok' : (c.status === 'SKIP' ? 'warn' : 'err');
    return '<tr><td>' + ci + '</td><td class="' + cc + '">' + escapeHtml(c.name) +
      '</td><td class="' + cc + '">' + c.status + '</td><td>' + escapeHtml(c.message || '-') +
      '</td><td>' + (c.latency || 0) + 'ms</td></tr>';
  }).join('');

  var detailsHtml = Object.entries(data.details || {}).map(function(e) {
    return '<span style="color:var(--text-muted)">' + escapeHtml(e[0]) + ':</span> ' + escapeHtml(String(e[1]));
  }).join(' | ');

  setHTML('scenario-result',
    '<div class="result-box">' +
    '<span class="' + color + '">' + icon + ' Scenario: ' + escapeHtml(data.name) +
    ' | Status: <b>' + data.status + '</b> | Duration: ' + (data.duration != null ? data.duration.toFixed(3) + 's' : '-') + '</span>\n' +
    (detailsHtml ? '\n' + detailsHtml + '\n' : '') +
    '</div>' +
    '<table class="data-table" style="margin-top:8px;"><thead><tr><th></th><th>Step</th><th>Status</th><th>Message</th><th>Latency</th></tr></thead><tbody>' + checksHtml + '</tbody></table>'
  );
}

/**
 * BestRAG Console — App Shell
 * Tab 切换 + Toast 通知 + API 工具
 */
const API = {
  async get(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error(r.status + ' ' + (await r.text()).slice(0, 100));
    return r.json();
  },
  async post(url, body) {
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!r.ok) throw new Error(r.status + ' ' + (await r.text()).slice(0, 100));
    return r.json();
  },
};

function toast(msg, type) {
  var el = document.createElement('div');
  el.className = 'toast toast-' + (type || 'success');
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(function() { el.remove(); }, 3000);
}

function setHTML(id, html) {
  var el = typeof id === 'string' ? document.getElementById(id) : id;
  if (el) el.innerHTML = html;
}

function setText(id, text) {
  var el = typeof id === 'string' ? document.getElementById(id) : id;
  if (el) el.textContent = text;
}

function $id(id) { return document.getElementById(id); }

function escapeHtml(s) {
  if (!s) return '';
  var d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

// Tab 切换
document.addEventListener('DOMContentLoaded', function() {
  var tabs = document.querySelectorAll('#tabs .tab');
  tabs.forEach(function(t) {
    t.addEventListener('click', function() {
      tabs.forEach(function(x) { x.classList.remove('active'); });
      t.classList.add('active');
      var panelId = t.dataset.panel;
      document.querySelectorAll('.panel').forEach(function(p) { p.classList.remove('active'); });
      var panel = document.getElementById('panel-' + panelId);
      if (panel) panel.classList.add('active');
    });
  });
  // 初始加载 System Status + Knowledge Status
  loadSystemStatus();
  loadKnowledgeStatus();
});

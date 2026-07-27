/**
 * Knowledge Base Console — 文档摄入 + 状态查看
 */
async function loadKnowledgeStatus() {
  try {
    var data = await API.get('/knowledge/status');
    renderKBStatus(data);
  } catch (e) {
    console.error('KB status error:', e);
  }
}

function renderKBStatus(data) {
  var cells = document.querySelectorAll('#kb-stats .status-item .value');
  if (cells[0]) cells[0].textContent = data.total_documents != null ? data.total_documents : '-';
  if (cells[1]) cells[1].textContent = data.total_chunks != null ? data.total_chunks : '-';
  if (cells[2]) {
    var vs = data.vectorstore || 'unknown';
    cells[2].textContent = vs === 'connected' ? '✅ ' + vs : '⚪ ' + vs;
    cells[2].className = 'value ' + (vs === 'connected' ? 'status-ok' : 'status-unknown');
  }
}

document.addEventListener('DOMContentLoaded', function() {
  var ingestBtn = $id('btn-kb-ingest');
  if (ingestBtn) {
    ingestBtn.addEventListener('click', async function() {
      var fp = $id('kb-filepath').value.trim();
      var strategy = $id('kb-strategy').value;
      if (!fp) { toast('请输入文件路径', 'error'); return; }
      setHTML('kb-ingest-result', '<span class="warn">Ingesting...</span>');
      try {
        var data = await API.post('/knowledge/ingest', { file_path: fp, strategy: strategy });
        if (data.success) {
          setHTML('kb-ingest-result',
            '<div class="result-box"><span class="ok">✅ Ingest 成功</span>\n' +
            'Document ID: ' + escapeHtml(data.document_id) + '\n' +
            'Chunks: ' + data.chunk_count + '\n' +
            'Message: ' + escapeHtml(data.message) + '</div>'
          );
          toast('Ingest 成功: ' + data.chunk_count + ' chunks');
          loadKnowledgeStatus();
        } else {
          setHTML('kb-ingest-result',
            '<div class="result-box"><span class="err">❌ Ingest 失败</span>\n' + escapeHtml(data.message) + '</div>'
          );
          toast('Ingest 失败: ' + data.message, 'error');
        }
      } catch (e) {
        setHTML('kb-ingest-result', '<span class="err">Error: ' + escapeHtml(e.message) + '</span>');
        toast(e.message, 'error');
      }
    });
  }

  var statusBtn = $id('btn-kb-status');
  if (statusBtn) statusBtn.addEventListener('click', loadKnowledgeStatus);
});

/**
 * Retrieval Debug — 检索过程诊断
 */
document.addEventListener('DOMContentLoaded', function() {
  var btn = $id('btn-ret-debug');
  var input = $id('ret-query');
  if (btn) btn.addEventListener('click', doRetrievalDebug);
  if (input) input.addEventListener('keydown', function(e) { if (e.key === 'Enter') doRetrievalDebug(); });
});

async function doRetrievalDebug() {
  var query = $id('ret-query').value.trim();
  if (!query) { toast('请输入查询文本', 'error'); return; }

  setHTML('ret-debug-result', '<span class="warn"><span class="spinner"></span> 诊断中...</span>');
  try {
    var data = await API.post('/validation/debug/retrieval', { query: query });
    renderRetrievalDebug(data);
  } catch (e) {
    setHTML('ret-debug-result', '<span class="err">Error: ' + escapeHtml(e.message) + '</span>');
  }
}

function renderRetrievalDebug(data) {
  var d = data.details || {};
  var html = ['<div class="result-box">'];
  html.push('<span style="color:var(--cyan)">Query:</span> ' + escapeHtml(data.query));
  html.push('<span style="color:var(--text-muted)">Latency:</span> ' + (data.latency_ms || 0) + 'ms');
  html.push('<span style="color:var(--text-muted)">Sections:</span> ' + (data.sections || []).join(', '));
  html.push('');

  // Retrieval results
  var ret = d.retrieval;
  if (ret) {
    html.push('<span style="color:var(--green)">── Retrieval ──</span>');
    if (ret.error) {
      html.push('<span class="err">Error: ' + escapeHtml(ret.error) + '</span>');
    } else {
      html.push('Count: ' + (ret.result_count || 0) + ' | Latency: ' + (ret.latency_ms || 0) + 'ms');
      var results = ret.results || [];
      results.forEach(function(r, i) {
        html.push('  #' + (i + 1) + ' [' + (r.score != null ? r.score.toFixed(4) : '-') + '] ' + escapeHtml((r.content_preview || '').slice(0, 100)));
      });
    }
  }

  // Rerank results
  var rerank = d.rerank;
  if (rerank) {
    html.push('');
    html.push('<span style="color:var(--green)">── Rerank ──</span>');
    if (rerank.error) {
      html.push('<span class="warn">Error: ' + escapeHtml(rerank.error) + '</span>');
    } else {
      html.push('Input: ' + (rerank.input_count || 0) + ' → Output: ' + (rerank.output_count || 0) + ' | Latency: ' + (rerank.latency_ms || 0) + 'ms');
      var rr = rerank.results || [];
      rr.forEach(function(r, i) {
        html.push('  #' + (i + 1) + ' [' + (r.score != null ? r.score.toFixed(4) : '-') + '] ' + escapeHtml((r.content_preview || '').slice(0, 100)));
      });
    }
  }

  html.push('</div>');
  setHTML('ret-debug-result', html.join('\n'));
}

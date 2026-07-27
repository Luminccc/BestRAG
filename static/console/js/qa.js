/**
 * QA Playground — RAG 问答交互
 */
document.addEventListener('DOMContentLoaded', function() {
  var sendBtn = $id('btn-qa-ask');
  var input = $id('qa-query');

  if (sendBtn) {
    sendBtn.addEventListener('click', doQA);
  }
  if (input) {
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') doQA();
    });
  }
});

async function doQA() {
  var query = $id('qa-query').value.trim();
  var topk = parseInt($id('qa-topk').value) || 5;
  if (!query) { toast('请输入问题', 'error'); return; }

  setHTML('qa-answer', '<span class="warn"><span class="spinner"></span> 思考中...</span>');
  setHTML('qa-sources', '');
  setText('qa-source-count', '0');
  setText('qa-ret-time', '-');
  setText('qa-gen-time', '-');
  setText('qa-total-time', '-');

  try {
    var data = await API.post('/qa/ask', { query: query, top_k: topk });
    renderQAResult(data);
  } catch (e) {
    setHTML('qa-answer', '<span class="err">Error: ' + escapeHtml(e.message) + '</span>');
    toast(e.message, 'error');
  }
}

function renderQAResult(data) {
  setHTML('qa-answer', escapeHtml(data.answer || '(无回答)'));
  setText('qa-ret-time', data.retrieval_time != null ? data.retrieval_time : '-');
  setText('qa-gen-time', data.generation_time != null ? data.generation_time : '-');
  setText('qa-total-time', data.total_time != null ? data.total_time : '-');

  var sources = data.sources || [];
  setText('qa-source-count', sources.length);

  if (sources.length === 0) {
    setHTML('qa-sources', '<div class="result-box">无检索结果</div>');
    return;
  }

  var html = sources.map(function(s, i) {
    return '<div class="source-item">' +
      '<div class="src-header"><span class="src-id">#' + (i + 1) + ' ' + escapeHtml((s.chunk_id || '').slice(0, 16)) +
      '</span><span class="src-score">score: ' + (s.score != null ? s.score.toFixed(4) : '-') + '</span></div>' +
      '<div class="src-content">' + escapeHtml((s.content || '').slice(0, 300)) + '</div>' +
      '</div>';
  }).join('');
  setHTML('qa-sources', html);
}

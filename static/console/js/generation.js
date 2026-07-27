/**
 * Generation Debug — 生成过程诊断
 */
document.addEventListener('DOMContentLoaded', function() {
  var btn = $id('btn-gen-debug');
  var input = $id('gen-query');
  if (btn) btn.addEventListener('click', doGenerationDebug);
  if (input) input.addEventListener('keydown', function(e) { if (e.key === 'Enter') doGenerationDebug(); });
});

async function doGenerationDebug() {
  var query = $id('gen-query').value.trim();
  if (!query) { toast('请输入查询文本', 'error'); return; }

  setHTML('gen-debug-result', '<span class="warn"><span class="spinner"></span> 诊断中...</span>');
  try {
    var data = await API.post('/validation/debug/generation', { query: query });
    renderGenerationDebug(data);
  } catch (e) {
    setHTML('gen-debug-result', '<span class="err">Error: ' + escapeHtml(e.message) + '</span>');
  }
}

function renderGenerationDebug(data) {
  var d = data.details || {};
  var html = ['<div class="result-box">'];
  html.push('<span style="color:var(--cyan)">Query:</span> ' + escapeHtml(data.query));
  html.push('<span style="color:var(--text-muted)">Latency:</span> ' + (data.latency_ms || 0) + 'ms');
  html.push('<span style="color:var(--text-muted)">Sections:</span> ' + (data.sections || []).join(', '));

  // Context
  var ctx = d.context;
  if (ctx) {
    html.push('');
    html.push('<span style="color:var(--green)">── Context ──</span>');
    html.push('Chunks: ' + (ctx.chunk_count || 0) + ' | Total chars: ' + (ctx.total_chars || 0) + ' | Latency: ' + (ctx.latency_ms || 0) + 'ms');
    html.push('<span style="color:var(--text-muted)">Preview:</span>');
    html.push(escapeHtml((ctx.preview || '').slice(0, 400)));
  }

  // Prompt
  var prompt = d.prompt;
  if (prompt) {
    html.push('');
    html.push('<span style="color:var(--green)">── Prompt ──</span>');
    html.push('System: ' + escapeHtml((prompt.system_prompt || '').slice(0, 150)));
    html.push('Query: ' + escapeHtml(prompt.query || ''));
    html.push('Context length: ' + (prompt.context_length || 0) + ' chars');
    html.push('Estimated total: ' + (prompt.estimated_total_chars || 0) + ' chars');
  }

  // Generation
  var gen = d.generation;
  if (gen) {
    html.push('');
    html.push('<span style="color:var(--green)">── LLM ──</span>');
    if (gen.error) {
      html.push('<span class="err">Error: ' + escapeHtml(gen.error) + '</span>');
    } else {
      html.push('Model: ' + escapeHtml(gen.model || 'unknown'));
      html.push('Answer length: ' + (gen.answer_length || 0) + ' chars');
      html.push('Latency: ' + (gen.latency_ms || 0) + 'ms');
      html.push('Estimated tokens: ~' + (gen.estimated_tokens || 0));
      html.push('');
      html.push('<span style="color:var(--text-muted)">Answer Preview:</span>');
      html.push(escapeHtml((gen.answer_preview || '').slice(0, 500)));
    }
  }

  if (d.error) {
    html.push('');
    html.push('<span class="err">Error: ' + escapeHtml(d.error) + '</span>');
  }

  html.push('</div>');
  setHTML('gen-debug-result', html.join('\n'));
}

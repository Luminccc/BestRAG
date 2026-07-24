/**
 * Developer Validation Center — API 调用与页面交互逻辑。
 *
 * 职责：
 *   - 调用 Ingress API 上传文件
 *   - 调用 Validation API 执行验证
 *   - 渲染 ValidationReport 结果
 *
 * 禁止：
 *   - 不包含任何业务逻辑（解析/清洗/嵌入等）
 */

// ==================== 状态 ====================

const state = {
  filePath: "",
  uploadInfo: null,
};

// ==================== DOM 引用 ====================

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// ==================== 上传区域 ====================

function initUpload() {
  const dropZone = $("#upload-zone");
  const fileInput = $("#file-input");
  const pathInput = $("#path-input");
  const usePathBtn = $("#use-path-btn");
  const uploadInfo = $("#upload-info");

  // 拖拽上传
  dropZone.addEventListener("click", () => fileInput.click());
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  });
  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
  });
  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    if (e.dataTransfer.files.length) uploadFile(e.dataTransfer.files[0]);
  });
  fileInput.addEventListener("change", () => {
    if (fileInput.files.length) uploadFile(fileInput.files[0]);
  });

  // 手动路径
  pathInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") useManualPath();
  });
  usePathBtn.addEventListener("click", useManualPath);

  async function uploadFile(file) {
    setStatus("upload-status", "正在上传...", "text-yellow-400");
    const form = new FormData();
    form.append("file", file);

    try {
      const resp = await fetch("/ingress/upload", { method: "POST", body: form });
      const data = await resp.json();
      if (!resp.ok) {
        setStatus("upload-status", `上传失败: ${data.detail || "未知错误"}`, "text-red-400");
        return;
      }
      state.uploadInfo = data;
      state.filePath = data.path;
      renderUploadInfo(data);
      setStatus("upload-status", `✅ 上传成功: ${data.filename}`, "text-emerald-400");
      setStatus("validate-status", `待验证文件: ${data.path}`, "text-gray-400");
      $("#current-path").textContent = data.path;
      $("#current-path").classList.remove("hidden");
    } catch (err) {
      setStatus("upload-status", `上传失败: ${err.message}`, "text-red-400");
    }
  }

  function useManualPath() {
    const path = pathInput.value.trim();
    if (!path) {
      setStatus("upload-status", "请输入文件路径", "text-yellow-400");
      return;
    }
    state.filePath = path;
    state.uploadInfo = null;
    $("#current-path").textContent = path;
    $("#current-path").classList.remove("hidden");
    uploadInfo.classList.add("hidden");
    setStatus("upload-status", `已设置路径: ${path}`, "text-gray-400");
    setStatus("validate-status", `待验证文件: ${path}`, "text-gray-400");
    renderPlaceholderPath(path);
  }

  function renderPlaceholderPath(path) {
    uploadInfo.classList.remove("hidden");
    uploadInfo.innerHTML = `
      <div class="flex items-center gap-3 text-sm text-gray-400 bg-gray-900/40 rounded-xl px-4 py-3 border border-gray-800">
        <span>📁</span>
        <span class="font-mono truncate">${path}</span>
        <span class="ml-auto text-gray-500">手动输入</span>
      </div>`;
  }

  function renderUploadInfo(data) {
    uploadInfo.classList.remove("hidden");
    uploadInfo.innerHTML = `
      <div class="bg-gray-900/40 border border-gray-800 rounded-xl p-4 text-sm">
        <div class="flex items-center gap-3 mb-3">
          <span class="text-2xl">${iconFor(data.filename)}</span>
          <span class="text-gray-100 font-semibold truncate">${data.filename}</span>
          <span class="ml-auto text-xs bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full">已上传</span>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
          ${kv("ID", data.id?.slice(0, 8) + "...")}
          ${kv("类型", data.mime)}
          ${kv("大小", humanSize(data.size))}
          ${kv("来源", data.source)}
        </div>
        <div class="mt-2 pt-2 border-t border-gray-800 text-xs text-gray-500 font-mono truncate" title="${data.path}">
          📍 ${data.path}
        </div>
      </div>`;
  }
}

// ==================== 验证操作 ====================

function initActions() {
  $("#validate-btn").addEventListener("click", validateDocument);
  $("#regression-btn").addEventListener("click", runRegression);
  $("#cleaner-btn").addEventListener("click", validateCleaner);
  $("#chunker-btn").addEventListener("click", validateChunker);
  $("#transformer-btn").addEventListener("click", validateTransformer);
  $("#pipeline-btn").addEventListener("click", validatePipeline);

  async function validateDocument() {
    const path = state.filePath;
    if (!path) {
      setStatus("validate-status", "请先上传文件或输入文件路径", "text-yellow-400");
      return;
    }
    setStatus("validate-status", `正在验证: ${path}`, "text-yellow-400");
    showLoading();

    try {
      const resp = await fetch("/validation/document", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_path: path }),
      });
      const report = await resp.json();
      hideLoading();
      renderSingleResult(report);
      setStatus("validate-status", "验证完成", "text-emerald-400");
    } catch (err) {
      hideLoading();
      setStatus("validate-status", `验证失败: ${err.message}`, "text-red-400");
    }
  }

  async function runRegression() {
    setStatus("validate-status", "正在执行全量回归验证...", "text-yellow-400");
    showLoading();

    try {
      const resp = await fetch("/validation/document/all", { method: "POST" });
      const reports = await resp.json();
      hideLoading();
      renderRegressionResults(reports);
      setStatus("validate-status", `回归完成: ${reports.length} 项`, "text-emerald-400");
    } catch (err) {
      hideLoading();
      setStatus("validate-status", `回归失败: ${err.message}`, "text-red-400");
    }
  }

  async function validateCleaner() {
    const path = state.filePath;
    if (!path) {
      setStatus("cleaner-status", "请先上传文件或输入文件路径", "text-yellow-400");
      return;
    }
    setStatus("cleaner-status", `正在清洗: ${path}`, "text-yellow-400");
    showCleanerLoading();

    try {
      const resp = await fetch("/validation/processor/cleaner", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_path: path }),
      });
      const report = await resp.json();
      hideCleanerLoading();
      renderCleanerResult(report);
      setStatus("cleaner-status", "清洗验证完成", "text-emerald-400");
    } catch (err) {
      hideCleanerLoading();
      setStatus("cleaner-status", `清洗验证失败: ${err.message}`, "text-red-400");
    }
  }

  async function validateChunker() {
    const path = state.filePath;
    if (!path) {
      setStatus("chunker-status", "请先上传文件或输入文件路径", "text-yellow-400");
      return;
    }
    const strategy = $("#strategy-select")?.value || "recursive";
    setStatus("chunker-status", `正在切分 [${strategy}]: ${path}`, "text-yellow-400");
    showChunkerLoading();

    try {
      const resp = await fetch("/validation/processor/chunk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_path: path, strategy: strategy }),
      });
      const report = await resp.json();
      hideChunkerLoading();
      renderChunkerResult(report);
      setStatus("chunker-status", `切分验证完成 [${strategy}]`, "text-emerald-400");
    } catch (err) {
      hideChunkerLoading();
      setStatus("chunker-status", `切分验证失败: ${err.message}`, "text-red-400");
    }
  }

  async function validateTransformer() {
    var path = state.filePath;
    if (!path) {
      setStatus("transformer-status", "请先上传文件或输入文件路径", "text-yellow-400");
      return;
    }
    setStatus("transformer-status", "正在转换: " + path, "text-yellow-400");
    showTransformerLoading();
    try {
      var resp = await fetch("/validation/processor/transformer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_path: path }),
      });
      var report = await resp.json();
      hideTransformerLoading();
      renderTransformerResult(report);
      setStatus("transformer-status", "转换验证完成", "text-emerald-400");
    } catch (err) {
      hideTransformerLoading();
      setStatus("transformer-status", "转换验证失败: " + err.message, "text-red-400");
    }
  }

  async function validatePipeline() {
    var path = state.filePath;
    if (!path) {
      setStatus("pipeline-status", "请先上传文件或输入文件路径", "text-yellow-400");
      return;
    }
    var sel = document.getElementById("pipeline-strategy");
    var strategy = sel ? sel.value : "recursive";
    setStatus("pipeline-status", "Pipeline: [" + strategy + "] " + path, "text-yellow-400");
    var ld = document.getElementById("pipeline-loading");
    if (ld) ld.classList.remove("hidden");
    try {
      var resp = await fetch("/validation/processor/pipeline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_path: path, strategy: strategy }),
      });
      var report = await resp.json();
      if (ld) ld.classList.add("hidden");
      renderPipelineResult(report);
      setStatus("pipeline-status", "管线验证完成 [" + strategy + "]", "text-emerald-400");
    } catch (err) {
      if (ld) ld.classList.add("hidden");
      setStatus("pipeline-status", "管线验证失败: " + err.message, "text-red-400");
    }
  }
}

// ==================== 结果渲染 ====================

function renderSingleResult(report) {
  const container = $("#result-area");
  $("#result-empty").classList.add("hidden");
  const isSuccess = report.status === "success";
  container.innerHTML = `
    <div class="bg-gray-900/60 border ${isSuccess ? "border-gray-800" : "border-red-900/50"} rounded-2xl p-6 toast-in">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-3">
          <span class="text-2xl">${isSuccess ? "✅" : "❌"}</span>
          <span class="text-lg font-semibold ${isSuccess ? "text-gray-100" : "text-red-400"}">
            Document Validation ${isSuccess ? "Success" : "Failed"}
          </span>
        </div>
        <span class="text-xs text-gray-500">${report.duration_ms}ms</span>
      </div>

      ${!isSuccess && report.message ? `
        <div class="mb-4 px-4 py-2 bg-red-500/10 border border-red-900/30 rounded-lg text-sm text-red-400">
          ${escapeHtml(report.message)}
        </div>` : ""}

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        ${kv("Module", report.module)}
        ${kv("Status", report.status)}
        ${kv("Parser", report.details?.parser || "-")}
        ${kv("Doc ID", report.details?.document_id?.slice(0, 8) + "..." || "-")}
        ${kv("Content", report.details?.content_length != null ? humanSize(report.details.content_length) : "-")}
        ${kv("File Type", report.details?.file_type || "-")}
        ${kv("Filename", report.details?.filename || "-")}
        ${kv("Duration", report.duration_ms + "ms")}
      </div>
    </div>`;
}

function renderRegressionResults(reports) {
  const container = $("#result-area");
  $("#result-empty").classList.add("hidden");
  const total = reports.length;
  const passed = reports.filter((r) => r.status === "success").length;
  const failed = total - passed;

  let rows = reports
    .map((r) => {
      const tc = r.details?.test_case || "?";
      const isOk = r.status === "success";
      return `
        <tr class="border-b border-gray-800/50 text-sm hover:bg-gray-800/20">
          <td class="py-2 px-3">${isOk ? "✅" : "❌"}</td>
          <td class="py-2 px-3 font-mono">${tc}</td>
          <td class="py-2 px-3">
            <span class="${isOk ? "text-emerald-400" : "text-red-400"}">${r.status}</span>
          </td>
          <td class="py-2 px-3 text-gray-400">${r.details?.parser || r.details?.expected_error || "-"}</td>
          <td class="py-2 px-3 text-gray-500 text-right">${r.duration_ms}ms</td>
        </tr>
        ${!isOk && r.message ? `
        <tr class="border-b border-gray-800/50">
          <td colspan="5" class="py-1 px-3 text-xs text-red-400/80 pl-10">${escapeHtml(r.message)}</td>
        </tr>` : ""}`;
    })
    .join("");

  container.innerHTML = `
    <div class="bg-gray-900/60 border border-gray-800 rounded-2xl p-6 toast-in">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-3">
          <span class="text-2xl">📊</span>
          <span class="text-lg font-semibold text-gray-100">Full Regression Report</span>
        </div>
        <div class="flex gap-4 text-xs">
          <span class="text-emerald-400">${passed} passed</span>
          ${failed > 0 ? `<span class="text-red-400">${failed} failed</span>` : ""}
          <span class="text-gray-500">${total} total</span>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead>
            <tr class="text-gray-500 border-b border-gray-800">
              <th class="text-left py-2 px-3 font-medium"></th>
              <th class="text-left py-2 px-3 font-medium">Case</th>
              <th class="text-left py-2 px-3 font-medium">Status</th>
              <th class="text-left py-2 px-3 font-medium">Parser / Error</th>
              <th class="text-right py-2 px-3 font-medium">Duration</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    </div>`;
}

function renderCleanerResult(report) {
  const container = $("#result-area");
  $("#result-empty").classList.add("hidden");
  const isSuccess = report.status === "success";
  const details = report.details || {};
  const origLen = details.original_length || 0;
  const cleanLen = details.cleaned_length || 0;
  const reduction = origLen - cleanLen;

  container.innerHTML = `
    <div class="bg-gray-900/60 border ${isSuccess ? "border-gray-800" : "border-red-900/50"} rounded-2xl p-6 toast-in">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-3">
          <span class="text-2xl">${isSuccess ? "✅" : "❌"}</span>
          <span class="text-lg font-semibold ${isSuccess ? "text-gray-100" : "text-red-400"}">
            Cleaner Validation ${isSuccess ? "Success" : "Failed"}
          </span>
        </div>
        <span class="text-xs text-gray-500">${report.duration_ms}ms</span>
      </div>

      ${!isSuccess && report.message ? `
        <div class="mb-4 px-4 py-2 bg-red-500/10 border border-red-900/30 rounded-lg text-sm text-red-400">
          ${escapeHtml(report.message)}
        </div>` : ""}

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
        ${kv("Module", report.module)}
        ${kv("Status", report.status)}
        ${kv("Doc ID", details.document_id?.slice(0, 8) + "..." || "-")}
        ${kv("Duration", report.duration_ms + "ms")}
        ${kv("Original", origLen > 0 ? `${origLen} chars` : "-")}
        ${kv("Cleaned", cleanLen > 0 ? `${cleanLen} chars` : "-")}
        ${kv("Reduction", reduction > 0 ? `${reduction} chars` : (reduction < 0 ? `+${Math.abs(reduction)} chars` : "0"))}
        ${kv("Metadata", `cleaned=${details.original_length != null}`)}
      </div>
    </div>`;
}

function renderChunkerResult(report) {
  var container = document.getElementById('result-area');
  var empty = document.getElementById('result-empty');
  if (empty) empty.classList.add('hidden');
  var isSuccess = report.status === 'success';
  var details = report.details || {};
  container.innerHTML = '<div class="bg-gray-900/60 border ' + (isSuccess ? 'border-gray-800' : 'border-red-900/50') + ' rounded-2xl p-6 toast-in">'
    + '<div class="flex items-center justify-between mb-4">'
    + '<div class="flex items-center gap-3">'
    + '<span class="text-2xl">' + (isSuccess ? '✅' : '❌') + '</span>'
    + '<span class="text-lg font-semibold ' + (isSuccess ? 'text-gray-100' : 'text-red-400') + '">Chunker Validation ' + (isSuccess ? 'Success' : 'Failed') + '</span>'
    + '</div>'
    + '<span class="text-xs text-gray-500">' + report.duration_ms + 'ms</span>'
    + '</div>'
    + (!isSuccess && report.message ? '<div class="mb-4 px-4 py-2 bg-red-500/10 border border-red-900/30 rounded-lg text-sm text-red-400">' + escapeHtml(report.message) + '</div>' : '')
    + '<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">'
    + kv('Module', report.module)
    + kv('Status', report.status)
    + kv('Strategy', details.strategy || '-')
    + kv('Duration', report.duration_ms + 'ms')
    + kv('Chunks', details.chunk_count != null ? details.chunk_count : '-')
    + kv('Avg Length', details.avg_length != null ? details.avg_length + ' chars' : '-')
    + kv('Max Length', details.max_length != null ? details.max_length + ' chars' : '-')
    + kv('Doc ID', (details.document_id || '').slice(0, 8) + '...')
    + '</div></div>';
}


function renderTransformerResult(report) {
  var el = document.getElementById("result-area");
  var empty = document.getElementById("result-empty");
  if (empty) empty.classList.add("hidden");
  var ok = report.status === "success";
  var d = report.details || {};
  el.innerHTML = '<div class="bg-gray-900/60 border ' + (ok ? 'border-gray-800' : 'border-red-900/50') + ' rounded-2xl p-6 toast-in">'
    + '<div class="flex items-center justify-between mb-4">'
    + '<span class="text-2xl">' + (ok ? '✅' : '❌') + '</span>'
    + '<span class="text-lg font-semibold ' + (ok ? 'text-gray-100' : 'text-red-400') + '">Transformer Validation ' + (ok ? 'Success' : 'Failed') + '</span>'
    + '<span class="text-xs text-gray-500">' + report.duration_ms + 'ms</span>'
    + '</div>'
    + (!ok && report.message ? '<div class="mb-4 px-4 py-2 bg-red-500/10 border border-red-900/30 rounded-lg text-sm text-red-400">' + escapeHtml(report.message) + '</div>' : '')
    + '<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">'
    + kv('Module', report.module)
    + kv('Status', report.status)
    + kv('Doc ID', (d.document_id || '').slice(0, 8) + '...')
    + kv('Duration', report.duration_ms + 'ms')
    + kv('Source File', d.source_file || '-')
    + kv('File Type', d.file_type || '-')
    + kv('Created', d.created_time ? d.created_time.slice(0, 10) : '-')
    + kv('Extra Fields', 'source_file, document_id')
    + '</div></div>';
}


function renderPipelineResult(report) {
  var area = document.getElementById("result-area");
  var empty = document.getElementById("result-empty");
  if (empty) empty.classList.add("hidden");
  var ok = report.status === "success";
  var d = report.details || {};
  var s = "<div class=\"bg-gray-900/60 border " + (ok ? "border-gray-800" : "border-red-900/50") + " rounded-2xl p-6 toast-in\">"
    + "<div class=\"flex items-center justify-between mb-4\">"
    + "<span class=\"text-2xl\">" + (ok ? "\u2705" : "\u274c") + "</span>"
    + "<span class=\"text-lg font-semibold " + (ok ? "text-gray-100" : "text-red-400") + "\">Pipeline " + (ok ? "Success" : "Failed") + "</span>"
    + "<span class=\"text-xs text-gray-500\">" + report.duration_ms + "ms</span></div>"
    + (!ok && report.message ? "<div class=\"mb-4 px-4 py-2 bg-red-500/10 border border-red-900/30 rounded-lg text-sm text-red-400\">" + escapeHtml(report.message) + "</div>" : "")
    + "<div class=\"grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs\">"
    + kv("Module", report.module)
    + kv("Status", report.status)
    + kv("Strategy", d.strategy || "-")
    + kv("Duration", report.duration_ms + "ms")
    + kv("Chunks", d.chunk_count != null ? d.chunk_count : "-")
    + kv("Avg Length", d.avg_chunk_length != null ? d.avg_chunk_length + " chars" : "-")
    + kv("Cleaner", d.cleaner_applied ? "applied" : "-")
    + kv("Transformer", d.transformer_applied ? "applied" : "-")
    + "</div></div>";
  area.innerHTML = s;
}

// ==================== 工具函数 ====================

function setStatus(id, msg, cls) {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = msg;
    el.className = `text-xs ${cls || "text-gray-400"}`;
  }
}

function showLoading() {
  const el = $("#loading");
  if (el) el.classList.remove("hidden");
}

function hideLoading() {
  const el = $("#loading");
  if (el) el.classList.add("hidden");
}

function showCleanerLoading() {
  const el = $("#cleaner-loading");
  if (el) el.classList.remove("hidden");
}

function hideCleanerLoading() {
  const el = $("#cleaner-loading");
  if (el) el.classList.add("hidden");
}

function showChunkerLoading() {
  const el = $("#chunker-loading");
  if (el) el.classList.remove("hidden");
}

function hideChunkerLoading() {
  const el = $("#chunker-loading");
  if (el) el.classList.add("hidden");
}

function showTransformerLoading() {
  var el = document.getElementById("transformer-loading");
  if (el) el.classList.remove("hidden");
}
function hideTransformerLoading() {
  var el = document.getElementById("transformer-loading");
  if (el) el.classList.add("hidden");
}


function kv(label, val) {
  return `<div class="bg-gray-950/60 rounded-lg px-3 py-2">
    <span class="text-gray-500 block">${label}</span>
    <span class="text-gray-200 font-mono block truncate mt-0.5">${val || "-"}</span>
  </div>`;
}

function humanSize(n) {
  if (n == null) return "-";
  for (const u of ["B", "KB", "MB", "GB"]) {
    if (n < 1024) return `${n.toFixed(1)} ${u}`;
    n /= 1024;
  }
  return `${n.toFixed(1)} TB`;
}

function iconFor(name) {
  const ext = name?.split(".").pop()?.toLowerCase();
  const map = {
    pdf: "📄", doc: "📝", docx: "📝", xls: "📊", xlsx: "📊",
    ppt: "📽️", pptx: "📽️", md: "📋", txt: "📃",
    json: "📦", xml: "📦", csv: "📊",
    png: "🖼️", jpg: "🖼️", jpeg: "🖼️", gif: "🖼️", svg: "🖼️",
    mp4: "🎬", mp3: "🎵", zip: "📦", rar: "📦",
    py: "🐍", js: "📜", ts: "📜",
  };
  return map[ext] || "📎";
}

function escapeHtml(text) {
  if (!text) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ==================== 启动 ====================

document.addEventListener("DOMContentLoaded", () => {
  initUpload();
  initActions();
});

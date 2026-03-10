const SAMPLE_LOG = `[2026-03-08 12:00:00] INFO: Application started
[2026-03-08 12:01:00] ERROR: Database timeout
[2026-03-08 12:02:00] WARNING: Disk usage high
[2026-03-08 12:03:00] ERROR: Database timeout
malformed line that should be skipped`;

const elements = {
  analyzeButton: document.getElementById("analyze-button"),
  browseFile: document.getElementById("browse-file"),
  clearButton: document.getElementById("clear-button"),
  containsFilter: document.getElementById("contains-filter"),
  copyJsonButton: document.getElementById("copy-json-button"),
  dropZone: document.getElementById("drop-zone"),
  entriesTable: document.getElementById("entries-table"),
  fileInput: document.getElementById("file-input"),
  fileName: document.getElementById("file-name"),
  jsonPreview: document.getElementById("json-preview"),
  levelBreakdown: document.getElementById("level-breakdown"),
  levelFilter: document.getElementById("level-filter"),
  loadSample: document.getElementById("load-sample"),
  logInput: document.getElementById("log-input"),
  sinceFilter: document.getElementById("since-filter"),
  statusMessage: document.getElementById("status-message"),
  summaryCards: document.getElementById("summary-cards"),
  topMessages: document.getElementById("top-messages"),
  untilFilter: document.getElementById("until-filter"),
};

function renderSummaryCards(summary) {
  const cards = [
    ["Files", summary.files_scanned],
    ["Lines", summary.total_lines],
    ["Parsed", summary.parsed_lines],
    ["Skipped", summary.skipped_lines],
    ["Matches", summary.matching_entries],
  ];

  elements.summaryCards.innerHTML = cards
    .map(
      ([label, value]) => `
        <article class="summary-card">
          <span>${label}</span>
          <strong>${value}</strong>
        </article>`,
    )
    .join("");
}

function renderLevelBreakdown(summary) {
  const entries = Object.entries(summary.counts_by_level);
  if (!entries.length) {
    elements.levelBreakdown.innerHTML = "<p>No matching levels.</p>";
    return;
  }

  const maxCount = Math.max(...entries.map(([, count]) => count));
  elements.levelBreakdown.innerHTML = entries
    .map(
      ([level, count]) => `
        <div class="level-row">
          <strong>${level}</strong>
          <div class="level-bar">
            <div class="level-fill" style="width: ${(count / maxCount) * 100}%"></div>
          </div>
          <span>${count}</span>
        </div>`,
    )
    .join("");
}

function renderTopMessages(summary) {
  if (!summary.top_messages.length) {
    elements.topMessages.innerHTML = "<p>No repeated messages.</p>";
    return;
  }

  elements.topMessages.innerHTML = summary.top_messages
    .map(
      (item) => `
        <div class="message-row">
          <span class="pill">${item.count}</span>
          <div>${item.message}</div>
        </div>`,
    )
    .join("");
}

function renderEntries(entries) {
  if (!entries.length) {
    elements.entriesTable.innerHTML =
      '<tr><td colspan="3">No matching entries for the current filters.</td></tr>';
    return;
  }

  elements.entriesTable.innerHTML = entries
    .map(
      (entry) => `
        <tr>
          <td>${entry.timestamp}</td>
          <td><span class="level-tag">${entry.level}</span></td>
          <td>${entry.message}</td>
        </tr>`,
    )
    .join("");
}

function render(summary, entries) {
  renderSummaryCards(summary);
  renderLevelBreakdown(summary);
  renderTopMessages(summary);
  renderEntries(entries);
  elements.jsonPreview.textContent = JSON.stringify(summary, null, 2);
}

function setStatus(message, isError = false) {
  elements.statusMessage.textContent = message;
  elements.statusMessage.style.color = isError ? "#8c2f39" : "";
}

async function analyzeCurrentInput() {
  const text = elements.logInput.value.trim();
  if (!text) {
    throw new Error("Paste log text or upload a file before analyzing.");
  }

  const selectedLevel = elements.levelFilter.value;
  const response = await fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      text,
      levels: selectedLevel ? [selectedLevel] : [],
      contains: elements.containsFilter.value.trim() || null,
      since: elements.sinceFilter.value.trim() || null,
      until: elements.untilFilter.value.trim() || null,
      top_messages: 5,
    }),
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Analysis failed.");
  }

  render(payload.summary, payload.entries);
  setStatus(`Analyzed ${payload.summary.parsed_lines} parsed lines.`);
}

function clearAll() {
  elements.logInput.value = "";
  elements.containsFilter.value = "";
  elements.levelFilter.value = "";
  elements.sinceFilter.value = "";
  elements.untilFilter.value = "";
  elements.fileInput.value = "";
  elements.fileName.textContent = "No file selected";
  render(
    {
      files_scanned: 0,
      total_lines: 0,
      parsed_lines: 0,
      skipped_lines: 0,
      matching_entries: 0,
      counts_by_level: {},
      first_timestamp: null,
      last_timestamp: null,
      top_messages: [],
      levels_present: [],
    },
    [],
  );
  setStatus("Cleared.");
}

async function copyJsonPreview() {
  try {
    await navigator.clipboard.writeText(elements.jsonPreview.textContent);
    setStatus("Copied JSON summary.");
  } catch {
    setStatus("Clipboard copy failed in this browser.", true);
  }
}

function populateWithSample() {
  elements.logInput.value = SAMPLE_LOG;
  elements.fileName.textContent = "Sample log loaded";
  analyzeCurrentInput().catch((error) => setStatus(error.message, true));
}

function handleFile(file) {
  if (!file) {
    return;
  }

  const reader = new FileReader();
  reader.onload = () => {
    elements.logInput.value = String(reader.result || "");
    elements.fileName.textContent = file.name;
    setStatus(`Loaded ${file.name}.`);
  };
  reader.onerror = () => setStatus("Could not read the selected file.", true);
  reader.readAsText(file);
}

function bindEvents() {
  elements.analyzeButton.addEventListener("click", () => {
    analyzeCurrentInput().catch((error) => {
      setStatus(error.message, true);
    });
  });

  elements.clearButton.addEventListener("click", clearAll);
  elements.copyJsonButton.addEventListener("click", copyJsonPreview);
  elements.loadSample.addEventListener("click", populateWithSample);
  elements.browseFile.addEventListener("click", () => elements.fileInput.click());
  elements.fileInput.addEventListener("change", (event) => {
    handleFile(event.target.files?.[0]);
  });

  ["dragenter", "dragover"].forEach((eventName) => {
    elements.dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      elements.dropZone.classList.add("is-active");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    elements.dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      if (eventName === "drop") {
        handleFile(event.dataTransfer?.files?.[0]);
      }
      elements.dropZone.classList.remove("is-active");
    });
  });
}

clearAll();
bindEvents();

const statusEl = document.getElementById("status-text");
const contentEl = document.getElementById("report-content");
const dateInput = document.getElementById("date-input");
const loadBtn = document.getElementById("load-btn");

// 默认把日期设置成今天（YYYY-MM-DD）
(function setToday() {
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, "0");
  const dd = String(today.getDate()).padStart(2, "0");
  dateInput.value = `${yyyy}-${mm}-${dd}`;
})();

// 加载报告
async function loadReportFromS3(dateStr) {
  statusEl.textContent = `Loading report for ${dateStr}...`;
  loadBtn.disabled = true;

  const key = `${dateStr}.md`;
  const bucketUrl =
    "https://cloud-incident-reports-scott.s3.amazonaws.com/daily-reports";
  const fileUrl = `${bucketUrl}/${key}`;

  try {
    const res = await fetch(fileUrl);

    if (!res.ok) {
      contentEl.textContent = `No report found for ${dateStr}.`;
      statusEl.textContent = "Report not found.";
      renderParsedReport(null); // 清空卡片 / 表格
      loadBtn.disabled = false;
      return;
    }

    const text = await res.text();
    contentEl.textContent = text; // 原始 markdown
    statusEl.textContent = "Report loaded.";
    renderParsedReport(text); // ← 新增：渲染卡片和表格
  } catch (err) {
    console.error(err);
    contentEl.textContent = "Error loading report.";
    statusEl.textContent = "Failed to load report.";
    renderParsedReport(null);
  } finally {
    loadBtn.disabled = false;
  }
}

loadBtn.addEventListener("click", () => {
  const dateStr = dateInput.value;
  if (!dateStr) {
    statusEl.textContent = "Please select a date.";
    return;
  }
  loadReportFromS3(dateStr);
});

function parseMarkdownReport(md) {
  if (!md) return null;

  const lines = md.split("\n");
  const data = {
    date: null,
    summary: {},
    byEvent: [],
    byRemediation: [],
    incidents: [],
  };

  // 标题行
  const titleLine = lines.find((l) =>
    l.startsWith("# Daily Cloud Incident Report")
  );
  if (titleLine) {
    const idx = titleLine.lastIndexOf("-");
    if (idx !== -1) {
      data.date = titleLine.slice(idx + 1).trim();
    }
  }

  const findSection = (label) =>
    lines.findIndex((l) => l.trim().toLowerCase() === label.toLowerCase());

  const summaryIdx = findSection("**Summary**");
  const byEventIdx = findSection("**By event type**");
  const byRemIdx = findSection("**By remediation type**");
  const incidentIdx = lines.findIndex((l) =>
    l.trim().startsWith("## Incident Details")
  );

  // Summary 部分
  if (summaryIdx !== -1) {
    let i = summaryIdx + 1;
    while (i < lines.length && lines[i].trim().startsWith("-")) {
      const line = lines[i].trim().slice(1).trim(); // 去掉 "- "
      const [k, v] = line.split(":");
      if (k && v !== undefined) {
        const key = k.trim().toLowerCase(); // "total incidents"
        const num = parseInt(v, 10);
        data.summary[key] = isNaN(num) ? v.trim() : num;
      }
      i++;
    }
  }

  // By event type
  if (byEventIdx !== -1) {
    let i = byEventIdx + 1;
    while (i < lines.length && lines[i].trim().startsWith("-")) {
      const line = lines[i].trim().slice(1).trim(); // "- EC2_HIGH_CPU: 1"
      const [name, count] = line.split(":");
      if (name && count !== undefined) {
        data.byEvent.push({
          name: name.trim(),
          count: parseInt(count, 10) || 0,
        });
      }
      i++;
    }
  }

  // By remediation type
  if (byRemIdx !== -1) {
    let i = byRemIdx + 1;
    while (i < lines.length && lines[i].trim().startsWith("-")) {
      const line = lines[i].trim().slice(1).trim();
      const [name, count] = line.split(":");
      if (name && count !== undefined) {
        data.byRemediation.push({
          name: name.trim(),
          count: parseInt(count, 10) || 0,
        });
      }
      i++;
    }
  }

  // Incident Details 表格
  if (incidentIdx !== -1) {
    // 找到第一行以 | 开头的 header
    let i = incidentIdx;
    while (i < lines.length && !lines[i].trim().startsWith("|")) i++;
    const headerLine = lines[i] || "";
    const separatorLine = lines[i + 1] || "";
    if (headerLine && separatorLine && headerLine.includes("|")) {
      const headers = headerLine
        .split("|")
        .map((s) => s.trim())
        .filter(Boolean);

      i = i + 2; // 跳过 header 和 separator
      while (i < lines.length && lines[i].trim().startsWith("|")) {
        const rowCells = lines[i]
          .split("|")
          .map((s) => s.trim())
          .filter(Boolean);
        if (rowCells.length === headers.length) {
          const obj = {};
          headers.forEach((h, idx) => {
            obj[h] = rowCells[idx];
          });
          data.incidents.push(obj);
        }
        i++;
      }
    }
  }

  return data;
}

function renderParsedReport(md) {
  const summaryRoot = document.getElementById("summary-cards");
  const breakdownRoot = document.getElementById("breakdown-cards");
  const tbody = document.querySelector("#incident-table tbody");

  if (!summaryRoot || !breakdownRoot || !tbody) return;

  summaryRoot.innerHTML = "";
  breakdownRoot.innerHTML = "";
  tbody.innerHTML =
    '<tr class="placeholder-row"><td colspan="6">No report loaded.</td></tr>';

  if (!md) return;

  const data = parseMarkdownReport(md);
  if (!data) return;

  // ----- Summary cards -----
  const s = data.summary;

  const createSummaryCard = (label, value, hint) => {
    const div = document.createElement("div");
    div.className = "summary-card";
    div.innerHTML = `
      <div class="summary-card-label">${label}</div>
      <div class="summary-card-value">${value ?? "–"}</div>
      ${
        hint
          ? `<div class="summary-card-hint">${hint}</div>`
          : '<div class="summary-card-hint">&nbsp;</div>'
      }
    `;
    return div;
  };

  summaryRoot.appendChild(
    createSummaryCard(
      "Total incidents",
      s["total incidents"],
      "All incidents processed in this period."
    )
  );
  summaryRoot.appendChild(
    createSummaryCard(
      "Success",
      s["success (heuristic)"],
      "Heuristically successful remediations."
    )
  );
  summaryRoot.appendChild(
    createSummaryCard(
      "Failed",
      s["failed (heuristic)"],
      "Incidents requiring manual follow-up."
    )
  );
  summaryRoot.appendChild(
    createSummaryCard(
      "Unique instances",
      s["unique instances"],
      "Distinct EC2 instances involved."
    )
  );

  // ----- Breakdown cards (event & remediation) -----
  const makeListCard = (title, items) => {
    const div = document.createElement("div");
    div.className = "summary-card";
    const listHtml =
      items.length === 0
        ? '<span class="summary-card-hint">No data.</span>'
        : items
            .map(
              (it) =>
                `<div class="summary-card-hint">${it.name} · ${it.count}</div>`
            )
            .join("");
    div.innerHTML = `
      <div class="summary-card-label">${title}</div>
      <div class="summary-card-value">${
        items.reduce((acc, x) => acc + x.count, 0) || "–"
      }</div>
      ${listHtml}
    `;
    return div;
  };

  breakdownRoot.appendChild(makeListCard("By event type", data.byEvent || []));
  breakdownRoot.appendChild(
    makeListCard("By remediation type", data.byRemediation || [])
  );

  // ----- Incident table -----
  if (data.incidents && data.incidents.length > 0) {
    tbody.innerHTML = "";
    data.incidents.forEach((row) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row["Time (created_at)"] ?? ""}</td>
        <td>${row["Event Type"] ?? ""}</td>
        <td>${row["Instance ID"] ?? ""}</td>
        <td>${row["Remediation Type"] ?? ""}</td>
        <td>${row["Action"] ?? ""}</td>
        <td>${row["Message"] ?? ""}</td>
      `;
      tbody.appendChild(tr);
    });
  }
}

const sampleTicket = {
  source_system: "zendesk",
  source_record_id: "TICKET-DEMO-001",
  record_type: "ticket",
  provider: "openai",
  idempotency_key: "ticket-demo-001-v1",
  payload: {
    customer_name: "Ava Chen",
    customer_email: "ava@example.com",
    subject: "Double charge on invoice",
    description: "Customer reports being billed twice after an upgrade and wants a refund.",
    priority_hint: "high"
  }
};

const sampleLead = {
  source_system: "hubspot",
  source_record_id: "LEAD-DEMO-001",
  record_type: "lead",
  provider: "mock",
  idempotency_key: "lead-demo-001-v1",
  payload: {
    company: "Northwind Labs",
    contact_name: "Ethan Wu",
    role: "Operations Manager",
    inquiry: "Looking for workflow automation and AI-assisted ticket triage integration.",
    deal_size_hint: "mid-market"
  }
};

const el = {
  recordType: document.getElementById("record-type"),
  provider: document.getElementById("provider"),
  sourceSystem: document.getElementById("source-system"),
  sourceRecordId: document.getElementById("source-record-id"),
  idempotencyKey: document.getElementById("idempotency-key"),
  payloadEditor: document.getElementById("payload-editor"),
  responseOutput: document.getElementById("response-output"),
  statusBanner: document.getElementById("status-banner"),
  runsList: document.getElementById("runs-list"),
  runsEmpty: document.getElementById("runs-empty"),
  loadTicket: document.getElementById("load-ticket"),
  loadLead: document.getElementById("load-lead"),
  runSync: document.getElementById("run-sync"),
  replaySync: document.getElementById("replay-sync"),
  loadRuns: document.getElementById("load-runs")
};

let lastSubmittedRequest = null;

function setBanner(type, message) {
  el.statusBanner.textContent = message;
  el.statusBanner.className = `status-banner ${type}`;
}

function clearBanner() {
  el.statusBanner.className = "status-banner hidden";
  el.statusBanner.textContent = "";
}

function pretty(value) {
  return JSON.stringify(value, null, 2);
}

function fillForm(data) {
  el.recordType.value = data.record_type;
  el.sourceSystem.value = data.source_system;
  el.sourceRecordId.value = data.source_record_id;
  el.idempotencyKey.value = data.idempotency_key || "";
  el.provider.value = data.provider || "mock";
  el.payloadEditor.value = pretty(data.payload);
}

function collectRequest() {
  const payload = JSON.parse(el.payloadEditor.value);
  return {
    source_system: el.sourceSystem.value.trim(),
    source_record_id: el.sourceRecordId.value.trim(),
    record_type: el.recordType.value,
    provider: el.provider.value || "mock",
    idempotency_key: el.idempotencyKey.value.trim() || null,
    payload
  };
}

function renderRuns(items) {
  el.runsList.innerHTML = "";
  if (!items || items.length === 0) {
    el.runsEmpty.style.display = "block";
    return;
  }
  el.runsEmpty.style.display = "none";
  for (const item of items) {
    const div = document.createElement("div");
    div.className = "run-item";
    div.innerHTML = `
      <div class="run-topline">
        <span>${item.trace_id}</span>
        <span>${item.status}</span>
      </div>
      <div class="run-meta">
        <span class="badge">${item.record_type}</span>
        <span class="badge">${item.source_system}</span>
        <span class="badge">${item.source_record_id}</span>
        <span class="badge">requested ${item.provider}</span>
      </div>
    `;
    el.runsList.appendChild(div);
  }
}

async function loadProviders() {
  const res = await fetch("/api/v1/sync/providers");
  const data = await res.json();
  el.provider.innerHTML = "";
  for (const name of data.providers || []) {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    el.provider.appendChild(option);
  }
}

async function loadRuns() {
  const res = await fetch("/api/v1/sync/runs?limit=10");
  const data = await res.json();
  renderRuns(data.items || []);
}

async function submit(requestBody) {
  clearBanner();
  const endpoint = requestBody.record_type === "lead" ? "/api/v1/sync/lead" : "/api/v1/sync/ticket";
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestBody)
  });
  const data = await res.json();
  el.responseOutput.textContent = pretty(data);
  if (res.ok && data.status === "success") {
    const replayText = data.idempotent_replay ? " (idempotent replay)" : "";
    setBanner("success", `Sync completed with trace ${data.trace_id}${replayText}.`);
  } else {
    setBanner("error", `Sync failed: ${data.error_message || "Unknown error"}`);
  }
  await loadRuns();
  return data;
}

el.loadTicket.addEventListener("click", () => fillForm(sampleTicket));
el.loadLead.addEventListener("click", () => fillForm(sampleLead));
el.loadRuns.addEventListener("click", loadRuns);

el.runSync.addEventListener("click", async () => {
  try {
    const requestBody = collectRequest();
    lastSubmittedRequest = requestBody;
    await submit(requestBody);
  } catch (error) {
    setBanner("error", `Invalid request payload: ${error.message}`);
  }
});

el.replaySync.addEventListener("click", async () => {
  try {
    const requestBody = lastSubmittedRequest || collectRequest();
    await submit(requestBody);
  } catch (error) {
    setBanner("error", `Replay failed: ${error.message}`);
  }
});

async function init() {
  await loadProviders();
  fillForm(sampleTicket);
  await loadRuns();
}

init().catch((error) => {
  setBanner("error", `Failed to initialize demo UI: ${error.message}`);
});

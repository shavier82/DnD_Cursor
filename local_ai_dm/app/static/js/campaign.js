const campaignId = document.body.dataset.campaignId;
const debugEnabled = document.body.dataset.debug === "true";

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  let data;
  try { data = await res.json(); } catch { data = {}; }
  if (!res.ok) {
    const detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail || res.statusText);
    throw new Error(detail);
  }
  return data;
}

function appendBubble(role, text) {
  const log = document.getElementById("chat-log");
  const div = document.createElement("div");
  div.className = `bubble ${role}`;
  div.textContent = text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

async function refreshOllamaBadge() {
  const badge = document.getElementById("ollama-badge");
  try {
    const status = await fetchJSON("/api/ollama/status");
    badge.textContent = status.available ? `Ollama: ${status.model}` : "Ollama offline";
    badge.className = "badge " + (status.available ? "ok" : "bad");
  } catch {
    badge.textContent = "API error";
    badge.className = "badge bad";
  }
}

async function refreshCampaign() {
  const campaign = await fetchJSON(`/api/campaigns/${campaignId}`);
  document.getElementById("campaign-name").textContent = campaign.name;
  document.getElementById("location").textContent = campaign.current_location || "Unknown";

  const characters = await fetchJSON(`/api/campaigns/${campaignId}/characters`);
  const party = document.getElementById("party-list");
  party.innerHTML = "";
  for (const c of characters) {
    const card = document.createElement("div");
    card.className = "party-card";
    const cond = (c.conditions || []).join(", ") || "none";
    card.innerHTML = `<strong>${c.name}</strong><div class="hp">${c.current_hp}/${c.max_hp} HP · AC ${c.armor_class}</div><div class="muted">${c.character_class || "—"} · ${cond}</div>`;
    party.appendChild(card);
  }
}

async function refreshMessages() {
  const messages = await fetchJSON(`/api/campaigns/${campaignId}/messages`);
  const log = document.getElementById("chat-log");
  log.innerHTML = "";
  for (const m of messages) {
    if (m.role === "user" || m.role === "assistant") {
      appendBubble(m.role, m.content);
    }
  }
}

document.getElementById("add-character").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  await fetchJSON(`/api/campaigns/${campaignId}/characters`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: fd.get("name"),
      player_name: fd.get("player_name") || null,
      character_class: fd.get("character_class") || null,
      race: fd.get("race") || null,
      max_hp: Number(fd.get("max_hp") || 20),
      armor_class: Number(fd.get("armor_class") || 14),
    }),
  });
  e.target.reset();
  await refreshCampaign();
});

document.getElementById("chat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const message = String(fd.get("message") || "").trim();
  if (!message) return;
  appendBubble("user", message);
  e.target.reset();
  try {
    const result = await fetchJSON(`/api/campaigns/${campaignId}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    appendBubble("assistant", result.narration);
    const rollBox = document.getElementById("roll-request");
    if (result.pending_rolls && result.pending_rolls.length) {
      const lines = result.pending_rolls.map((r) => {
        const skill = r.skill ? r.skill : (r.ability || "check");
        const dc = r.dc != null ? ` DC ${r.dc}` : "";
        const mode = r.mode && r.mode !== "normal" ? ` (${r.mode})` : "";
        return `Roll requested: ${skill}${dc}${mode} — ${r.reason || ""}`;
      });
      rollBox.textContent = lines.join("\n");
      rollBox.classList.add("visible");
    } else {
      rollBox.textContent = "";
      rollBox.classList.remove("visible");
    }
    if (debugEnabled && result.debug) {
      document.getElementById("debug-output").textContent = JSON.stringify(
        {
          pending_rolls: result.pending_rolls,
          rag_chunks: result.debug.rag_chunks,
          actions_executed: result.actions_executed,
          actions_rejected: result.actions_rejected,
        },
        null,
        2
      );
    }
    await refreshCampaign();
  } catch (err) {
    appendBubble("assistant", "Error: " + err.message);
  }
});

document.getElementById("roll-dice-btn").addEventListener("click", async () => {
  const expression = prompt("Dice expression", "1d20");
  if (!expression) return;
  const mode = prompt("Mode: normal | advantage | disadvantage", "normal") || "normal";
  try {
    const result = await fetchJSON("/api/dice/roll", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expression, mode }),
    });
    document.getElementById("dice-result").textContent =
      `${result.expression} → ${result.total} (${result.detail})`;
  } catch (err) {
    document.getElementById("dice-result").textContent = "Dice error: " + err.message;
  }
});

refreshOllamaBadge();
refreshCampaign();
refreshMessages();

if (debugEnabled) {
  async function refreshRagStatus() {
    const el = document.getElementById("rag-status");
    if (!el) return;
    try {
      const status = await fetchJSON("/api/documents/status");
      el.textContent = `RAG: ${status.indexed_chunks} chunks from ${status.sources.length || 0} source(s)`;
    } catch (err) {
      el.textContent = "RAG status error: " + err.message;
    }
  }

  const ingestBtn = document.getElementById("ingest-btn");
  if (ingestBtn) {
    ingestBtn.addEventListener("click", async () => {
      ingestBtn.disabled = true;
      ingestBtn.textContent = "Ingesting… (first run can take a few minutes)";
      try {
        const result = await fetchJSON("/api/documents/ingest", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });
        document.getElementById("debug-output").textContent = JSON.stringify(result, null, 2);
        await refreshRagStatus();
      } catch (err) {
        document.getElementById("debug-output").textContent = "Ingest error: " + err.message;
      } finally {
        ingestBtn.disabled = false;
        ingestBtn.textContent = "Ingest sourcebooks";
      }
    });
  }
  refreshRagStatus();
}

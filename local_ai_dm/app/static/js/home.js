async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || res.statusText);
  return data;
}

async function refreshOllama() {
  const el = document.getElementById("ollama-status");
  try {
    const status = await fetchJSON("/api/ollama/status");
    el.textContent = status.message;
    el.style.color = status.available ? "#5ac48a" : "#c45a5a";
  } catch (err) {
    el.textContent = "Could not reach API: " + err.message;
    el.style.color = "#c45a5a";
  }
}

async function refreshCampaigns() {
  const list = document.getElementById("campaign-list");
  const campaigns = await fetchJSON("/api/campaigns");
  list.innerHTML = "";
  if (!campaigns.length) {
    list.innerHTML = "<li class='muted'>No campaigns yet.</li>";
    return;
  }
  for (const c of campaigns) {
    const li = document.createElement("li");
    li.innerHTML = `<a href="/campaign/${c.id}">${c.name}</a> <span class="muted">(${c.current_location || "no location"})</span>`;
    list.appendChild(li);
  }
}

document.getElementById("create-campaign").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  await fetchJSON("/api/campaigns", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: fd.get("name"),
      current_location: fd.get("current_location") || null,
    }),
  });
  e.target.reset();
  await refreshCampaigns();
});

refreshOllama();
refreshCampaigns();

"use strict";

const $ = (id) => document.getElementById(id);
let conversationId = null;
let pollTimer = null;
let prepInterval = null;

// ---- setup / config ------------------------------------------------------
fetch("/api/config").then((r) => r.json()).then((cfg) => {
  $("modeBadge").textContent = cfg.demo_mode ? "DEMO MODE · no live Tavus call" : "LIVE · Tavus examiner";
  window.__SAMPLE = cfg.sample_report;
}).catch(() => {});

function selectedParts() {
  return [...document.querySelectorAll(".part:checked")].map((c) => Number(c.value));
}

// ---- start test ----------------------------------------------------------
$("startBtn").addEventListener("click", async () => {
  const parts = selectedParts();
  $("startError").textContent = "";
  if (parts.length === 0) {
    $("startError").textContent = "Please choose at least one part.";
    return;
  }
  $("startBtn").disabled = true;
  $("startBtn").textContent = "Connecting to examiner…";
  try {
    const res = await fetch("/api/start-test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ parts, candidate_name: $("candidateName").value }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Could not start the test.");
    conversationId = data.conversation_id;
    $("callFrame").src = data.conversation_url;
    show("call");
  } catch (e) {
    $("startError").textContent = e.message;
  } finally {
    $("startBtn").disabled = false;
    $("startBtn").textContent = "Start mock test";
  }
});

// ---- part-2 prep timer (the 1-minute pause) ------------------------------
function setTimerDisplay(secs) {
  const m = Math.floor(secs / 60);
  const s = String(secs % 60).padStart(2, "0");
  $("timer").textContent = `${m}:${s}`;
}
function resetTimer() {
  clearInterval(prepInterval);
  prepInterval = null;
  setTimerDisplay(60);
  $("timer").className = "timer";
  $("prepBtn").disabled = false;
}
$("prepBtn").addEventListener("click", () => {
  let left = 60;
  $("prepBtn").disabled = true;
  setTimerDisplay(left);
  clearInterval(prepInterval);
  prepInterval = setInterval(() => {
    left -= 1;
    setTimerDisplay(Math.max(left, 0));
    $("timer").className = left <= 10 ? "timer done" : "timer warn";
    if (left <= 0) {
      clearInterval(prepInterval);
      prepInterval = null;
      $("timer").textContent = "Speak now";
      $("prepBtn").disabled = false;
    }
  }, 1000);
});
$("resetTimerBtn").addEventListener("click", resetTimer);

// ---- finish + score ------------------------------------------------------
$("finishBtn").addEventListener("click", async () => {
  $("callFrame").src = "about:blank";
  show("report");
  // End the live call so Tavus starts post-call scoring immediately
  // (otherwise it waits for the leave-timeout first).
  if (conversationId) {
    fetch("/api/end-test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_id: conversationId }),
    }).catch(() => {});
  }
  startPolling();
});

// Demo helper: simulate Tavus's post-call POST so the report card is demoable.
$("sampleBtn").addEventListener("click", async () => {
  await fetch("/api/score", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation_id: conversationId || "latest", ...window.__SAMPLE }),
  });
  $("finishBtn").click();
});

function startPolling() {
  $("scoring").classList.remove("hidden");
  $("reportCard").classList.add("hidden");
  clearInterval(pollTimer);
  const id = conversationId || "latest";
  let tries = 0;
  pollTimer = setInterval(async () => {
    tries += 1;
    try {
      const res = await fetch(`/api/report/${encodeURIComponent(id)}`);
      const data = await res.json();
      if (data.status === "ready") {
        clearInterval(pollTimer);
        renderReport(data.report);
      }
    } catch (_) { /* keep polling */ }
    if (tries > 150) clearInterval(pollTimer); // ~5 min safety
  }, 2000);
}

function crit(name, band, evidence, improvement) {
  return `<div class="crit">
    <div class="head"><span class="name">${name}</span><span class="band">${fmt(band)}</span></div>
    <p class="tag">Evidence</p><p>${esc(evidence)}</p>
    <p class="tag">How to improve</p><p>${esc(improvement)}</p>
  </div>`;
}

function renderReport(r) {
  $("scoring").classList.add("hidden");
  const card = $("reportCard");
  card.innerHTML = `
    <div class="overall">
      <div class="big">${fmt(r.overall_band)}</div>
      <div><div style="font-weight:700;font-size:18px">Overall band</div>
        <div class="lbl">Mean of the four criteria, rounded to the nearest 0.5</div></div>
    </div>
    <div class="criteria">
      ${crit("Fluency &amp; Coherence", r.fc_band, r.fc_evidence, r.fc_improvement)}
      ${crit("Lexical Resource", r.lr_band, r.lr_evidence, r.lr_improvement)}
      ${crit("Grammatical Range &amp; Accuracy", r.gra_band, r.gra_evidence, r.gra_improvement)}
      ${crit("Pronunciation", r.pron_band, r.pron_evidence, r.pron_improvement)}
    </div>
    <div class="summary">
      <h3>Examiner summary</h3>
      <p>${esc(r.summary)}</p>
      <div class="actions"><strong>Your top 3 next steps</strong>
        <ol><li>${esc(r.action_1)}</li><li>${esc(r.action_2)}</li><li>${esc(r.action_3)}</li></ol>
      </div>
    </div>`;
  card.classList.remove("hidden");
}

$("againBtn").addEventListener("click", () => {
  clearInterval(pollTimer);
  resetTimer();
  conversationId = null;
  show("setup");
});

// ---- helpers -------------------------------------------------------------
function show(which) {
  for (const s of ["setup", "call", "report"]) $(s).classList.toggle("hidden", s !== which);
  if (which === "call") resetTimer();
}
function fmt(b) { return (b === null || b === undefined || b === "") ? "—" : b; }
function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

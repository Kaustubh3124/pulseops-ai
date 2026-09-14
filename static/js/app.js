/**
 * PulseOps AI - Modern Dashboard Client Controller
 */

let state = {
  activeEventId: 1,
  events: [],
  leads: [],
  selectedLeadId: null,
  activeTierFilter: "ALL",
  searchQuery: "",
};

// DOM Elements
const elements = {
  eventSelector: document.getElementById("event-selector"),
  eventTitleDisplay: document.getElementById("event-title-display"),
  eventDurationDisplay: document.getElementById("event-duration-display"),
  eventStatusDisplay: document.getElementById("event-status-display"),
  eventIdDisplay: document.getElementById("event-id-display"),
  eventTypeBadge: document.getElementById("event-type-badge"),

  kpiTotalAttendees: document.getElementById("kpi-total-attendees"),
  kpiHotLeads: document.getElementById("kpi-hot-leads"),
  kpiWarmLeads: document.getElementById("kpi-warm-leads"),
  kpiGuardrailAcc: document.getElementById("kpi-guardrail-acc"),

  searchInput: document.getElementById("search-input"),
  filterBtns: document.querySelectorAll(".filter-btn"),
  leadsTableBody: document.getElementById("leads-table-body"),

  btnRunPipeline: document.getElementById("btn-run-pipeline"),
  btnSeedDemo: document.getElementById("btn-seed-demo"),

  drawer: document.getElementById("lead-drawer"),
  drawerBackdrop: document.getElementById("drawer-backdrop"),
  drawerCloseBtn: document.getElementById("drawer-close-btn"),
  drawerLeadName: document.getElementById("drawer-lead-name"),
  drawerLeadSubtitle: document.getElementById("drawer-lead-subtitle"),
  drawerTierBadge: document.getElementById("drawer-tier-badge"),
  drawerIcpBadge: document.getElementById("drawer-icp-badge"),
  drawerFinalScore: document.getElementById("drawer-final-score"),
  drawerDetScore: document.getElementById("drawer-det-score"),
  drawerAiScore: document.getElementById("drawer-ai-score"),
  drawerAiReasoning: document.getElementById("drawer-ai-reasoning"),
  drawerGuardrailBadge: document.getElementById("drawer-guardrail-badge"),
  drawerQnaList: document.getElementById("drawer-qna-list"),
  drawerPollBox: document.getElementById("drawer-poll-box"),
  drawerCitedQuote: document.getElementById("drawer-cited-quote"),
  drawerEmailSubject: document.getElementById("drawer-email-subject"),
  drawerEmailBody: document.getElementById("drawer-email-body"),
  drawerCampaignStatus: document.getElementById("drawer-campaign-status"),
  btnCopyEmail: document.getElementById("btn-copy-email"),
  btnDispatchSlack: document.getElementById("btn-dispatch-slack"),
  btnDispatchCrm: document.getElementById("btn-dispatch-crm"),

  toast: document.getElementById("toast"),
  toastMsg: document.getElementById("toast-msg"),
};

// Initialization
document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  await loadEvents();
  await loadAnalytics();
});

function setupEventListeners() {
  elements.eventSelector.addEventListener("change", (e) => {
    state.activeEventId = parseInt(e.target.value);
    const ev = state.events.find((x) => x.id === state.activeEventId);
    if (ev) updateEventHeader(ev);
    loadLeads();
  });

  elements.searchInput.addEventListener("input", (e) => {
    state.searchQuery = e.target.value.toLowerCase();
    renderLeadsTable();
  });

  elements.filterBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      elements.filterBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.activeTierFilter = btn.dataset.tier;
      renderLeadsTable();
    });
  });

  elements.btnRunPipeline.addEventListener("click", runPipeline);
  elements.btnSeedDemo.addEventListener("click", resetDemoData);

  elements.drawerCloseBtn.addEventListener("click", closeDrawer);
  elements.drawerBackdrop.addEventListener("click", closeDrawer);

  elements.btnCopyEmail.addEventListener("click", () => {
    navigator.clipboard.writeText(elements.drawerEmailBody.value);
    showToast("Email draft copied to clipboard!");
  });

  elements.btnDispatchSlack.addEventListener("click", () => dispatchWebhook("SLACK"));
  elements.btnDispatchCrm.addEventListener("click", () => dispatchWebhook("CRM"));
}

async function loadEvents() {
  try {
    const res = await fetch("/api/events");
    const events = await res.json();
    state.events = events;

    elements.eventSelector.innerHTML = "";
    events.forEach((ev) => {
      const opt = document.createElement("option");
      opt.value = ev.id;
      opt.textContent = `${ev.title} (ID: #${ev.id})`;
      elements.eventSelector.appendChild(opt);
    });

    if (events.length > 0) {
      state.activeEventId = events[0].id;
      updateEventHeader(events[0]);
      await loadLeads();
    }
  } catch (err) {
    console.error("Failed to load events:", err);
  }
}

function updateEventHeader(ev) {
  elements.eventTitleDisplay.textContent = ev.title;
  elements.eventDurationDisplay.textContent = `${ev.total_duration_minutes} mins`;
  elements.eventStatusDisplay.textContent = ev.status;
  elements.eventIdDisplay.textContent = `#${ev.id}`;
  elements.eventTypeBadge.textContent = ev.event_type;
}

async function loadLeads() {
  try {
    const res = await fetch(`/api/events/${state.activeEventId}/leads`);
    const leads = await res.json();
    state.leads = leads;
    renderLeadsTable();
    updateKPIsFromLeads(leads);
  } catch (err) {
    console.error("Failed to load leads:", err);
  }
}

async function loadAnalytics() {
  try {
    const res = await fetch("/api/analytics/summary");
    const stats = await res.json();
    elements.kpiGuardrailAcc.textContent = `${stats.guardrail_accuracy}%`;
  } catch (err) {
    console.error("Failed to load analytics:", err);
  }
}

function updateKPIsFromLeads(leads) {
  elements.kpiTotalAttendees.textContent = leads.length;
  const hot = leads.filter((l) => l.intelligence && l.intelligence.intent_tier === "HOT").length;
  const warm = leads.filter((l) => l.intelligence && l.intelligence.intent_tier === "WARM").length;
  elements.kpiHotLeads.textContent = hot;
  elements.kpiWarmLeads.textContent = warm;
}

function renderLeadsTable() {
  const filtered = state.leads.filter((lead) => {
    // Search query filter
    const matchesSearch =
      lead.name.toLowerCase().includes(state.searchQuery) ||
      lead.company.toLowerCase().includes(state.searchQuery) ||
      lead.job_title.toLowerCase().includes(state.searchQuery);

    // Tier filter
    const leadTier = lead.intelligence ? lead.intelligence.intent_tier : "COLD";
    const matchesTier =
      state.activeTierFilter === "ALL" || leadTier === state.activeTierFilter;

    return matchesSearch && matchesTier;
  });

  if (filtered.length === 0) {
    elements.leadsTableBody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; padding: 2.5rem; color: var(--slate-400);">
          No leads match the selected criteria.
        </td>
      </tr>
    `;
    return;
  }

  elements.leadsTableBody.innerHTML = filtered
    .map((lead) => {
      const intel = lead.intelligence || {};
      const score = intel.final_score != null ? intel.final_score.toFixed(1) : "0.0";
      const tier = intel.intent_tier || "COLD";
      const verified = intel.hallucination_verified !== false;

      let tierBadgeClass = "badge-cold";
      let fillClass = "fill-cold";
      if (tier === "HOT") {
        tierBadgeClass = "badge-hot";
        fillClass = "fill-hot";
      } else if (tier === "WARM") {
        tierBadgeClass = "badge-warm";
        fillClass = "fill-warm";
      }

      let icpBadgeClass = "badge-icp-2";
      if (lead.icp_tier.includes("Tier 1")) icpBadgeClass = "badge-icp-1";
      if (lead.icp_tier.includes("Tier 3")) icpBadgeClass = "badge-icp-3";

      const painPoint =
        intel.key_pain_points && intel.key_pain_points.length > 0
          ? intel.key_pain_points[0]
          : "General event technology";

      return `
        <tr>
          <td>
            <div class="attendee-name">${lead.name}</div>
            <div class="attendee-sub">${lead.job_title}</div>
          </td>
          <td>
            <div style="font-weight: 600; color: var(--slate-800);">${lead.company}</div>
            <span class="badge ${icpBadgeClass}" style="margin-top: 0.2rem;">${lead.icp_tier}</span>
          </td>
          <td>
            <div style="font-weight: 600;">${lead.watch_time_minutes} min <span style="font-weight: 400; color: var(--slate-500);">(${lead.watch_percentage}%)</span></div>
            <div style="font-size: 0.78rem; color: var(--slate-500); margin-top: 0.15rem;">
              ${lead.qna_questions.length} Q&A &bull; ${lead.poll_data.length} polls &bull; ${lead.chat_messages_count} chats
            </div>
          </td>
          <td>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span class="score-pill">${score}</span>
              <span class="badge ${tierBadgeClass}">${tier}</span>
            </div>
            <div class="score-progress-bar">
              <div class="score-progress-fill ${fillClass}" style="width: ${score}%;"></div>
            </div>
          </td>
          <td style="max-width: 260px;">
            <div style="font-size: 0.84rem; color: var(--slate-700); line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;" title="${painPoint}">
              ${painPoint}
            </div>
          </td>
          <td>
            ${
              verified
                ? `<span class="guardrail-tag">
                     <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>
                     Grounded
                   </span>`
                : `<span class="guardrail-tag flagged">
                     <svg width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                     Flagged
                   </span>`
            }
          </td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="openLeadDossier(${lead.id})">
              View Dossier
            </button>
          </td>
        </tr>
      `;
    })
    .join("");
}

window.openLeadDossier = async function (leadId) {
  state.selectedLeadId = leadId;
  const lead = state.leads.find((l) => l.id === leadId);
  if (!lead) return;

  const intel = lead.intelligence || {};
  const camp = lead.campaign || {};

  elements.drawerLeadName.textContent = lead.name;
  elements.drawerLeadSubtitle.textContent = `${lead.job_title} at ${lead.company} • ${lead.email}`;

  elements.drawerTierBadge.textContent = `${intel.intent_tier || "COLD"} LEAD`;
  elements.drawerTierBadge.className = `badge ${intel.intent_tier === "HOT" ? "badge-hot" : intel.intent_tier === "WARM" ? "badge-warm" : "badge-cold"}`;

  elements.drawerIcpBadge.textContent = lead.icp_tier;
  elements.drawerFinalScore.textContent = `${(intel.final_score || 0).toFixed(1)} / 100`;
  elements.drawerDetScore.textContent = (intel.deterministic_score || 0).toFixed(1);
  elements.drawerAiScore.textContent = (intel.ai_intent_score || 0).toFixed(1);
  elements.drawerAiReasoning.textContent = intel.ai_reasoning || "Standard participation baseline.";

  // Evidence
  if (lead.qna_questions && lead.qna_questions.length > 0) {
    elements.drawerQnaList.innerHTML = lead.qna_questions
      .map((q) => `<li>"${q}"</li>`)
      .join("");
  } else {
    elements.drawerQnaList.innerHTML = `<li>No questions asked during live broadcast.</li>`;
  }

  if (lead.poll_data && lead.poll_data.length > 0) {
    elements.drawerPollBox.innerHTML = lead.poll_data
      .map((p) => `<strong>${p.poll_question}:</strong> ${p.selected_option}`)
      .join("<br>");
  } else {
    elements.drawerPollBox.innerHTML = "No poll answers recorded.";
  }

  elements.drawerCitedQuote.textContent = intel.ground_truth_quote || "N/A (Calculated from session engagement)";

  // Outreach Draft
  elements.drawerEmailSubject.textContent = camp.email_subject || "Follow up from Zuddl Product Summit";
  elements.drawerEmailBody.value = camp.email_body || "";
  elements.drawerCampaignStatus.textContent = camp.status || "DRAFT";

  // Open Drawer
  elements.drawer.classList.add("active");
  elements.drawerBackdrop.classList.add("active");
};

function closeDrawer() {
  elements.drawer.classList.remove("active");
  elements.drawerBackdrop.classList.remove("active");
}

async function runPipeline() {
  try {
    elements.btnRunPipeline.disabled = true;
    elements.btnRunPipeline.textContent = "Processing...";
    const res = await fetch(`/api/events/${state.activeEventId}/process`, {
      method: "POST",
    });
    const summary = await res.json();
    await loadLeads();
    await loadAnalytics();
    showToast(`Pipeline complete in ${summary.execution_time_ms}ms! Identified ${summary.hot_leads_count} Hot Leads.`);
  } catch (err) {
    console.error("Pipeline run failed:", err);
    showToast("Pipeline execution error.");
  } finally {
    elements.btnRunPipeline.disabled = false;
    elements.btnRunPipeline.innerHTML = `
      <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
      Run PulseOps Pipeline
    `;
  }
}

async function resetDemoData() {
  try {
    elements.btnSeedDemo.disabled = true;
    const res = await fetch("/api/seed-demo", { method: "POST" });
    await loadEvents();
    await loadAnalytics();
    showToast("Demo scenario reloaded successfully!");
  } catch (err) {
    console.error("Failed to seed demo:", err);
  } finally {
    elements.btnSeedDemo.disabled = false;
  }
}

async function dispatchWebhook(target) {
  if (!state.selectedLeadId) return;
  try {
    const overrideBody = elements.drawerEmailBody.value;
    const res = await fetch(`/api/leads/${state.selectedLeadId}/dispatch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target, override_email_body: overrideBody }),
    });
    const data = await res.json();
    elements.drawerCampaignStatus.textContent = "DISPATCHED";
    showToast(`Lead payload successfully pushed to ${target}!`);
  } catch (err) {
    console.error("Dispatch error:", err);
    showToast(`Failed to dispatch to ${target}`);
  }
}

function showToast(msg) {
  elements.toastMsg.textContent = msg;
  elements.toast.classList.add("show");
  setTimeout(() => {
    elements.toast.classList.remove("show");
  }, 3500);
}

/**
 * RetinaAI Frontend Client Logic
 * Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
 */

let patientsList = [];
let activePatient = null;
let activeEye = "OD";
let currentScreeningResult = null;
let selectedFile = null;
let simChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
  loadPatients();
  initSimChart();
  runSimulation();
});

// ---------------- TAB NAVIGATION ----------------
function switchTab(tabName) {
  const tabs = ["screening", "patients", "simulation", "ml-hub"];
  tabs.forEach(t => {
    const el = document.getElementById(`tab-${t}`);
    const btn = document.getElementById(`tab-btn-${t}`);
    if (el) el.classList.add("hidden");
    if (btn) {
      btn.className = "px-3.5 py-1.5 rounded-md text-sm font-medium text-slate-300 hover:text-white hover:bg-brand-800 transition-all flex items-center space-x-1.5";
    }
  });

  const activeEl = document.getElementById(`tab-${tabName}`);
  const activeBtn = document.getElementById(`tab-btn-${tabName}`);
  if (activeEl) activeEl.classList.remove("hidden");
  if (activeBtn) {
    activeBtn.className = "px-3.5 py-1.5 rounded-md text-sm font-medium transition-all bg-sky-600 text-white flex items-center space-x-1.5";
  }

  // Re-render icons if needed
  if (window.lucide) {
    lucide.createIcons();
  }
}

// ---------------- PATIENT MANAGEMENT ----------------
async function loadPatients() {
  try {
    const res = await fetch("/api/patients");
    patientsList = await res.json();
    populatePatientSelect();
    renderPatientsTable(patientsList);
  } catch (err) {
    console.error("Error loading patients:", err);
  }
}

function populatePatientSelect() {
  const select = document.getElementById("active-patient-select");
  select.innerHTML = '<option value="">-- Select Registered Patient --</option>';
  patientsList.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = `${p.full_name} (${p.patient_uid}) - ${p.village}, ${p.district}`;
    select.appendChild(opt);
  });

  // Auto-select first patient if available
  if (patientsList.length > 0 && !activePatient) {
    select.value = patientsList[0].id;
    activePatient = patientsList[0];
  }
}

function onPatientSelected() {
  const select = document.getElementById("active-patient-select");
  const pId = parseInt(select.value);
  activePatient = patientsList.find(p => p.id === pId) || null;
}

function renderPatientsTable(list) {
  const tbody = document.getElementById("patients-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  if (list.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-slate-400">No patients registered yet.</td></tr>`;
    return;
  }

  list.forEach(p => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-50 border-b border-slate-100 transition-colors";
    tr.innerHTML = `
      <td class="py-3 px-4 font-mono font-bold text-sky-700">${p.patient_uid}</td>
      <td class="py-3 px-4 font-bold text-slate-800">${p.full_name}</td>
      <td class="py-3 px-4">${p.age} yrs / ${p.gender}</td>
      <td class="py-3 px-4">${p.village}, ${p.district}</td>
      <td class="py-3 px-4">${p.diabetes_years} yrs</td>
      <td class="py-3 px-4">${p.hba1c ? p.hba1c + '%' : 'N/A'}</td>
      <td class="py-3 px-4">
        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700">
          Screening Active
        </span>
      </td>
      <td class="py-3 px-4 text-right">
        <button onclick="selectPatientForScreening(${p.id})" class="px-2.5 py-1 rounded bg-sky-50 text-sky-700 border border-sky-200 hover:bg-sky-100 font-semibold text-[11px]">
          Screen Fundus
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function filterPatientsTable() {
  const query = document.getElementById("patient-search-input").value.toLowerCase();
  const filtered = patientsList.filter(p => 
    p.full_name.toLowerCase().includes(query) ||
    p.patient_uid.toLowerCase().includes(query) ||
    p.village.toLowerCase().includes(query) ||
    p.district.toLowerCase().includes(query)
  );
  renderPatientsTable(filtered);
}

function selectPatientForScreening(pId) {
  const select = document.getElementById("active-patient-select");
  select.value = pId;
  activePatient = patientsList.find(p => p.id === pId) || null;
  switchTab("screening");
}

function openNewPatientModal() {
  document.getElementById("patient-modal").classList.remove("hidden");
}

function closeNewPatientModal() {
  document.getElementById("patient-modal").classList.add("hidden");
}

async function handleCreatePatient(e) {
  e.preventDefault();

  const nameVal = (document.getElementById("inp-name").value || "").trim();
  const rawAge = document.getElementById("inp-age").value;
  const rawDiab = document.getElementById("inp-diabetes-yrs").value;
  const rawHba1c = document.getElementById("inp-hba1c").value;

  if (!nameVal) {
    alert("Please enter patient name.");
    return;
  }

  const body = {
    full_name: nameVal,
    age: parseInt(rawAge) || 50,
    gender: document.getElementById("inp-gender").value || "Male",
    village: (document.getElementById("inp-village").value || "").trim() || "Rural Village",
    district: (document.getElementById("inp-district").value || "").trim() || "Madurai",
    diabetes_years: rawDiab ? Math.max(0, parseFloat(rawDiab) || 0) : 0.0,
    hba1c: (rawHba1c && parseFloat(rawHba1c) > 0) ? parseFloat(rawHba1c) : null,
    phone: (document.getElementById("inp-phone").value || "").trim() || null,
    hypertension: false,
    smoker: false
  };

  try {
    const res = await fetch("/api/patients", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      let msg = "Failed to register patient";
      if (errData.detail) {
        if (Array.isArray(errData.detail)) {
          msg = errData.detail.map(d => `${d.loc.slice(-1)[0]}: ${d.msg}`).join("\n");
        } else {
          msg = errData.detail;
        }
      }
      throw new Error(msg);
    }

    const newPatient = await res.json();
    patientsList.unshift(newPatient);
    populatePatientSelect();
    renderPatientsTable(patientsList);
    
    // Auto-select this patient
    document.getElementById("active-patient-select").value = newPatient.id;
    activePatient = newPatient;
    
    closeNewPatientModal();
    document.getElementById("new-patient-form").reset();
    switchTab("screening");
  } catch (err) {
    alert("Registration Notice:\n" + err.message);
  }
}

// ---------------- EYE SELECTION ----------------
function setEyeSelection(eye) {
  activeEye = eye;
  const btnOd = document.getElementById("btn-eye-od");
  const btnOs = document.getElementById("btn-eye-os");
  if (eye === "OD") {
    btnOd.className = "px-3 py-1 text-xs font-bold rounded-md bg-white text-sky-700 shadow-sm border border-slate-200";
    btnOs.className = "px-3 py-1 text-xs font-bold rounded-md text-slate-600 hover:text-slate-900";
  } else {
    btnOs.className = "px-3 py-1 text-xs font-bold rounded-md bg-white text-sky-700 shadow-sm border border-slate-200";
    btnOd.className = "px-3 py-1 text-xs font-bold rounded-md text-slate-600 hover:text-slate-900";
  }
}

// ---------------- FILE UPLOAD & SAMPLE GENERATOR ----------------
function handleFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;
  selectedFile = file;
  
  const reader = new FileReader();
  reader.onload = (evt) => {
    const preview = document.getElementById("fundus-preview");
    preview.src = evt.target.result;
    preview.classList.remove("hidden");
    document.getElementById("upload-placeholder").classList.add("hidden");
  };
  reader.readAsDataURL(file);
}

function loadSampleFundusImage() {
  // Generate a realistic retinal fundus canvas blob for instant demonstration
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext("2d");

  // Background dark
  ctx.fillStyle = "#0a0a0c";
  ctx.fillRect(0, 0, 512, 512);

  // Retinal Disc (Orange/Red gradient)
  const grad = ctx.createRadialGradient(256, 256, 40, 256, 256, 230);
  grad.addColorStop(0, "#d35400");
  grad.addColorStop(0.5, "#b93e0b");
  grad.addColorStop(0.85, "#801d00");
  grad.addColorStop(1.0, "#0a0a0c");

  ctx.beginPath();
  ctx.arc(256, 256, 230, 0, Math.PI * 2);
  ctx.fillStyle = grad;
  ctx.fill();

  // Optic Disc (Bright circular feature on nasal side)
  ctx.beginPath();
  ctx.arc(380, 250, 36, 0, Math.PI * 2);
  ctx.fillStyle = "#f39c12";
  ctx.shadowColor = "#f1c40f";
  ctx.shadowBlur = 15;
  ctx.fill();
  ctx.shadowBlur = 0;

  // Retinal Vascular Tree (Branching vessels)
  ctx.strokeStyle = "#4a0000";
  ctx.lineWidth = 3.5;
  ctx.beginPath();
  // Superior temporal arcade
  ctx.moveTo(380, 250);
  ctx.bezierCurveTo(320, 160, 240, 140, 160, 180);
  // Inferior temporal arcade
  ctx.moveTo(380, 250);
  ctx.bezierCurveTo(320, 340, 240, 360, 160, 320);
  ctx.stroke();

  // Sub-pixel Lesions: Microaneurysms (red dots) & Hard Exudates (bright yellow dots)
  ctx.fillStyle = "#300000";
  const maSpots = [[220, 240], [205, 270], [180, 230], [250, 190], [190, 300]];
  maSpots.forEach(([x, y]) => {
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
  });

  ctx.fillStyle = "#fff275";
  const exudates = [[210, 210], [218, 205], [230, 215]];
  exudates.forEach(([x, y]) => {
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, Math.PI * 2);
    ctx.fill();
  });

  // Convert to Blob and set as selectedFile
  canvas.toBlob((blob) => {
    selectedFile = new File([blob], "sample_idrid_fundus.jpg", { type: "image/jpeg" });
    const preview = document.getElementById("fundus-preview");
    preview.src = canvas.toDataURL("image/jpeg");
    preview.classList.remove("hidden");
    document.getElementById("upload-placeholder").classList.add("hidden");
  }, "image/jpeg");
}

// ---------------- RUN AI SCREENING ----------------
async function triggerFundusScreening() {
  if (!activePatient) {
    alert("Please select or register a patient first.");
    return;
  }
  if (!selectedFile) {
    alert("Please upload a fundus photograph or click 'Load Sample IDRiD'.");
    return;
  }

  const btn = document.getElementById("btn-run-screening");
  const btnText = document.getElementById("btn-screen-text");
  btn.disabled = true;
  btnText.textContent = "Analyzing Retinal Microvasculature & Grad-CAM...";

  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("patient_id", activePatient.id);
  formData.append("eye", activeEye);
  formData.append("asha_notes", document.getElementById("asha-notes-input").value || "");

  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      body: formData
    });
    if (!res.ok) throw new Error("Screening inference failed");
    currentScreeningResult = await res.json();
    renderScreeningResults(currentScreeningResult);
  } catch (err) {
    alert("Error during screening: " + err.message);
  } finally {
    btn.disabled = false;
    btnText.textContent = "Run Explainable AI Screening";
  }
}

// ---------------- RENDER SCREENING RESULTS ----------------
function renderScreeningResults(data) {
  document.getElementById("results-placeholder").classList.add("hidden");
  document.getElementById("results-panel").classList.remove("hidden");

  // Triage Badge & Status
  const badgeBox = document.getElementById("triage-badge-container");
  const iconBox = document.getElementById("triage-icon-box");
  const icon = document.getElementById("triage-icon");
  const statusEl = document.getElementById("res-triage-status");
  const urgencyPill = document.getElementById("res-urgency-pill");
  const gradeTitle = document.getElementById("res-grade-title");
  const confVal = document.getElementById("res-confidence-val");

  gradeTitle.textContent = data.grade_name;
  confVal.textContent = data.confidence_percent;

  if (data.is_referable) {
    badgeBox.className = "rounded-xl p-4 border bg-red-50/80 border-red-200 flex items-center justify-between";
    iconBox.className = "w-12 h-12 rounded-xl flex items-center justify-center text-white bg-red-600 shadow-sm";
    icon.setAttribute("data-lucide", "alert-octagon");
    statusEl.className = "font-black text-sm tracking-wide uppercase text-red-700";
    statusEl.textContent = "REFERABLE DR - SPECIALIST REVIEW REQUIRED";
    urgencyPill.className = "text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-200 text-red-900";
    urgencyPill.textContent = data.urgency;
  } else {
    badgeBox.className = "rounded-xl p-4 border bg-emerald-50/80 border-emerald-200 flex items-center justify-between";
    iconBox.className = "w-12 h-12 rounded-xl flex items-center justify-center text-white bg-emerald-600 shadow-sm";
    icon.setAttribute("data-lucide", "check-circle");
    statusEl.className = "font-black text-sm tracking-wide uppercase text-emerald-700";
    statusEl.textContent = "NON-REFERABLE (ROUTINE ANNUAL FOLLOW-UP)";
    urgencyPill.className = "text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-200 text-emerald-900";
    urgencyPill.textContent = data.urgency;
  }

  // Multimodal Images
  document.getElementById("img-display-base").src = data.images.raw_url;
  document.getElementById("img-display-overlay").src = data.images.gradcam_url;
  document.getElementById("img-side-raw").src = data.images.raw_url;
  document.getElementById("img-side-grad").src = data.images.gradcam_url;

  // Lesion Counts
  const findings = data.pathology_findings || {};
  document.getElementById("res-count-ma").textContent = findings.microaneurysms || 0;
  document.getElementById("res-count-hem").textContent = findings.hemorrhages || 0;
  document.getElementById("res-count-ex").textContent = findings.hard_exudates || 0;
  document.getElementById("res-count-nv").textContent = findings.neovascularization || "Absent";

  // Text Rationale
  document.getElementById("res-xai-summary").textContent = data.xai_summary || "";
  document.getElementById("res-asha-guidance").textContent = data.asha_guidance || "";
  document.getElementById("res-model-source").textContent = data.model_source || "";

  // Referral Hospital Box
  const hospBox = document.getElementById("referral-hospital-box");
  if (data.is_referable && data.referral_hospital) {
    hospBox.classList.remove("hidden");
    document.getElementById("res-hosp-name").textContent = data.referral_hospital.name;
    document.getElementById("res-hosp-dist").textContent = `Distance: ~${data.referral_hospital.distance_km} km | Emergency Hotline: ${data.referral_hospital.phone}`;
    document.getElementById("res-recall-period").textContent = data.recall_period;
  } else {
    hospBox.classList.add("hidden");
  }

  // PDF Button
  const pdfBtn = document.getElementById("res-btn-pdf");
  pdfBtn.href = data.report_pdf_url;

  if (window.lucide) lucide.createIcons();
}

// ---------------- VIEWER CONTROLS ----------------
function setViewerMode(mode) {
  const overlayWrap = document.getElementById("overlay-view-wrapper");
  const sideWrap = document.getElementById("side-by-side-wrapper");
  const opacityControl = document.getElementById("opacity-control-group");

  const btnGrad = document.getElementById("mode-btn-gradcam");
  const btnSide = document.getElementById("mode-btn-side");
  const btnClahe = document.getElementById("mode-btn-clahe");

  btnGrad.className = "px-2.5 py-1 text-xs font-semibold rounded-l-lg bg-white text-slate-700 hover:bg-slate-50 border border-slate-200";
  btnSide.className = "px-2.5 py-1 text-xs font-semibold bg-white text-slate-700 hover:bg-slate-50 border-t border-b border-slate-200";
  btnClahe.className = "px-2.5 py-1 text-xs font-semibold rounded-r-lg bg-white text-slate-700 hover:bg-slate-50 border border-slate-200";

  if (mode === "gradcam") {
    btnGrad.className = "px-2.5 py-1 text-xs font-semibold rounded-l-lg bg-sky-600 text-white";
    overlayWrap.classList.remove("hidden");
    sideWrap.classList.add("hidden");
    opacityControl.classList.remove("hidden");
    if (currentScreeningResult) {
      document.getElementById("img-display-base").src = currentScreeningResult.images.raw_url;
      document.getElementById("img-display-overlay").src = currentScreeningResult.images.gradcam_url;
      document.getElementById("img-display-overlay").classList.remove("hidden");
    }
  } else if (mode === "side") {
    btnSide.className = "px-2.5 py-1 text-xs font-semibold bg-sky-600 text-white";
    overlayWrap.classList.add("hidden");
    sideWrap.classList.remove("hidden");
    sideWrap.classList.add("grid");
    opacityControl.classList.add("hidden");
  } else if (mode === "clahe") {
    btnClahe.className = "px-2.5 py-1 text-xs font-semibold rounded-r-lg bg-sky-600 text-white";
    overlayWrap.classList.remove("hidden");
    sideWrap.classList.add("hidden");
    opacityControl.classList.add("hidden");
    if (currentScreeningResult) {
      document.getElementById("img-display-base").src = currentScreeningResult.images.preprocessed_url;
      document.getElementById("img-display-overlay").classList.add("hidden");
    }
  }
}

function adjustHeatmapAlpha(val) {
  const overlay = document.getElementById("img-display-overlay");
  const label = document.getElementById("opacity-label");
  overlay.style.opacity = val / 100;
  label.textContent = `${val}%`;
}

// ---------------- TELEMEDICINE SIMULATOR ----------------
function updateSimSlider(type, val) {
  if (type === "pop") {
    document.getElementById("val-pop").textContent = `${parseInt(val).toLocaleString()} patients`;
  } else if (type === "phc") {
    document.getElementById("val-phc").textContent = `${val} centres`;
  } else if (type === "doc") {
    document.getElementById("val-doc").textContent = `${val} doctors`;
  }
  runSimulation();
}

async function runSimulation() {
  const pop = parseInt(document.getElementById("sim-pop-slider").value);
  const phc = parseInt(document.getElementById("sim-phc-slider").value);
  const bw = parseFloat(document.getElementById("sim-bandwidth-select").value);
  const doc = parseInt(document.getElementById("sim-doc-slider").value);

  try {
    const res = await fetch("/api/simulation/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        annual_population: pop,
        num_phcs: phc,
        bandwidth_mbps: bw,
        doctor_count: doc
      })
    });
    const sim = await res.json();
    renderSimulationDashboard(sim);
  } catch (err) {
    console.error("Simulation error:", err);
  }
}

function renderSimulationDashboard(sim) {
  document.getElementById("sim-res-daily").textContent = Math.round(sim.daily_screening_capacity);
  document.getElementById("sim-res-latency").textContent = `${sim.transfer_latency_sec}s`;
  document.getElementById("sim-res-reduction").textContent = `${sim.workload_reduction_percent}%`;
  document.getElementById("sim-res-needed").textContent = sim.doctors_needed;

  const queueBox = document.getElementById("sim-queue-box");
  const queueTitle = document.getElementById("sim-queue-title");
  const queueDesc = document.getElementById("sim-queue-desc");

  queueDesc.textContent = sim.simulink_queue_status;

  if (sim.doctor_deficit_or_surplus >= 0) {
    queueBox.className = "rounded-xl p-4 border bg-emerald-50 border-emerald-200 text-emerald-900";
    queueTitle.className = "flex items-center space-x-2 font-bold text-sm text-emerald-800";
  } else if (sim.doctor_deficit_or_surplus === -1) {
    queueBox.className = "rounded-xl p-4 border bg-amber-50 border-amber-200 text-amber-900";
    queueTitle.className = "flex items-center space-x-2 font-bold text-sm text-amber-800";
  } else {
    queueBox.className = "rounded-xl p-4 border bg-red-50 border-red-200 text-red-900";
    queueTitle.className = "flex items-center space-x-2 font-bold text-sm text-red-800";
  }

  updateSimChart(sim.daily_screening_capacity, sim.daily_referrals);
}

function initSimChart() {
  const ctx = document.getElementById("simChart");
  if (!ctx) return;

  simChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Unassisted Manual Screening (All Patients)", "RetinaAI Automated Triage (Referral Queue Only)"],
      datasets: [{
        label: "Patients Requiring Specialist Doctor Review / Day",
        data: [400, 60],
        backgroundColor: ["#94a3b8", "#0284c7"],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: "Patients / Day" }
        }
      }
    }
  });
}

function updateSimChart(totalPatients, referablePatients) {
  if (!simChartInstance) return;
  simChartInstance.data.datasets[0].data = [Math.round(totalPatients), Math.round(referablePatients)];
  simChartInstance.update();
}

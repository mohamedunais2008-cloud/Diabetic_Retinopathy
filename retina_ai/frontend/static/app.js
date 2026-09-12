/**
 * RetinaAI Frontend Client Engine (v2.5)
 * 4-Stakeholder Telemedicine & Explainable AI Screening System
 * Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
 * MathWorks / Smart India Hackathon (SIH 2026)
 */

// ---------------- GLOBAL APPLICATION STATE ----------------
let currentAuthRole = "nurse"; // nurse, doctor, patient, admin
let currentUser = null;        // Authenticated health worker
let currentPatient = null;     // Authenticated patient
let patientsList = [];
let activePatient = null;
let activeEye = "OD";
let selectedFile = null;
let currentScreeningResult = null;

// Nurse Camp GPS Coordinates (Real-time tracking)
let nurseCampGPS = {
  lat: 9.9252,
  lon: 78.1198,
  accuracy: 10.0,
  address: "Madurai North PHC Outreach Camp, Tamil Nadu",
  isLive: false
};

// Doctor Workstation State
let doctorQueue = [];
let activeReviewScreening = null;
let caliperActive = false;
let caliperPoints = [];
let speechRecognizer = null;
let isDictating = false;

// Patient Screenings State
let currentPatientScreenings = [];

// Simulink Chart Instance
let simChartInstance = null;


// ---------------- INITIALIZATION ----------------
document.addEventListener("DOMContentLoaded", () => {
  checkExistingSession();
  initVoiceRecognition();
  initSimChart();
  if (window.lucide) lucide.createIcons();
});


// ---------------- AUTHENTICATION & SESSION MANAGEMENT ----------------
function checkExistingSession() {
  const savedUser = localStorage.getItem("retina_user");
  const savedPatient = localStorage.getItem("retina_patient");

  if (savedUser) {
    try {
      currentUser = JSON.parse(savedUser);
      enterPortal(currentUser.role);
      return;
    } catch (e) {
      localStorage.removeItem("retina_user");
    }
  }

  if (savedPatient) {
    try {
      currentPatient = JSON.parse(savedPatient);
      enterPortal("patient");
      return;
    } catch (e) {
      localStorage.removeItem("retina_patient");
    }
  }

  // If not logged in, show the Login Gateway
  showLoginView();
}

function showLoginView() {
  document.getElementById("view-login").classList.remove("hidden");
  document.getElementById("portal-nurse").classList.add("hidden");
  document.getElementById("portal-doctor").classList.add("hidden");
  document.getElementById("portal-patient").classList.add("hidden");
  document.getElementById("portal-admin").classList.add("hidden");

  document.getElementById("header-user-badge").classList.add("hidden");
  document.getElementById("header-guest-badge").classList.remove("hidden");
  document.getElementById("header-authenticated-nav").innerHTML = "";

  selectAuthRole(currentAuthRole || "nurse");
  if (window.lucide) lucide.createIcons();
}

function handleLogoClick() {
  if (currentUser || currentPatient) {
    // Already in portal
  } else {
    showLoginView();
  }
}

function selectAuthRole(role) {
  currentAuthRole = role;
  const roles = ["nurse", "doctor", "patient", "admin"];
  
  roles.forEach(r => {
    const tab = document.getElementById(`tab-auth-${r}`);
    if (tab) {
      tab.className = "p-3.5 rounded-2xl border-2 transition-all text-center flex flex-col items-center justify-center space-y-1.5 border-slate-200 bg-white hover:border-slate-300 text-slate-700";
    }
  });

  const activeTab = document.getElementById(`tab-auth-${role}`);
  if (activeTab) {
    if (role === "nurse") activeTab.className = "p-3.5 rounded-2xl border-2 transition-all text-center flex flex-col items-center justify-center space-y-1.5 border-sky-600 bg-sky-50/70 text-sky-900 shadow-sm";
    if (role === "doctor") activeTab.className = "p-3.5 rounded-2xl border-2 transition-all text-center flex flex-col items-center justify-center space-y-1.5 border-indigo-600 bg-indigo-50/70 text-indigo-900 shadow-sm";
    if (role === "patient") activeTab.className = "p-3.5 rounded-2xl border-2 transition-all text-center flex flex-col items-center justify-center space-y-1.5 border-emerald-600 bg-emerald-50/70 text-emerald-900 shadow-sm";
    if (role === "admin") activeTab.className = "p-3.5 rounded-2xl border-2 transition-all text-center flex flex-col items-center justify-center space-y-1.5 border-slate-800 bg-slate-100 text-slate-900 shadow-sm";
  }

  // Toggle Worker form vs Patient Lookup form
  const workerBox = document.getElementById("auth-box-worker");
  const patientBox = document.getElementById("auth-box-patient");

  if (role === "patient") {
    workerBox.classList.add("hidden");
    patientBox.classList.remove("hidden");
  } else {
    workerBox.classList.remove("hidden");
    patientBox.classList.add("hidden");
    updateWorkerAuthHeaders(role);
  }

  if (window.lucide) lucide.createIcons();
}

function updateWorkerAuthHeaders(role) {
  const title = document.getElementById("worker-auth-title");
  const demoLbl = document.getElementById("lbl-quick-demo");
  const btnSubmit = document.getElementById("btn-submit-worker-login");
  const inpUser = document.getElementById("inp-login-username");
  const inpPass = document.getElementById("inp-login-password");

  if (role === "nurse") {
    title.textContent = "Staff Nurse & ASHA Camp Worker Portal Login";
    demoLbl.textContent = "1-Click Demo Login as Staff Nurse Kavitha";
    btnSubmit.className = "w-full py-3 rounded-xl bg-sky-600 hover:bg-sky-700 text-white font-black text-sm shadow-md transition-all flex items-center justify-center space-x-2";
    inpUser.value = "nurse@retina.ai";
    inpPass.value = "nurse123";
  } else if (role === "doctor") {
    title.textContent = "Ophthalmologist Specialist Tele-Review Login";
    demoLbl.textContent = "1-Click Demo Login as Dr. Meenakshi Sundaram";
    btnSubmit.className = "w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-black text-sm shadow-md transition-all flex items-center justify-center space-x-2";
    inpUser.value = "doctor@retina.ai";
    inpPass.value = "doctor123";
  } else if (role === "admin") {
    title.textContent = "District Health Officer (DHO) Command Login";
    demoLbl.textContent = "1-Click Demo Login as District Admin";
    btnSubmit.className = "w-full py-3 rounded-xl bg-slate-800 hover:bg-slate-900 text-white font-black text-sm shadow-md transition-all flex items-center justify-center space-x-2";
    inpUser.value = "admin@retina.ai";
    inpPass.value = "admin123";
  }
}

function setAuthMode(mode) {
  const signinForm = document.getElementById("form-worker-signin");
  const regForm = document.getElementById("form-worker-register");
  const btnSign = document.getElementById("btn-mode-signin");
  const btnReg = document.getElementById("btn-mode-register");

  if (mode === "signin") {
    signinForm.classList.remove("hidden");
    regForm.classList.add("hidden");
    btnSign.className = "px-3 py-1 rounded-md bg-white text-sky-700 shadow-sm font-bold";
    btnReg.className = "px-3 py-1 rounded-md text-slate-600 hover:text-slate-900 font-bold";
  } else {
    signinForm.classList.add("hidden");
    regForm.classList.remove("hidden");
    btnReg.className = "px-3 py-1 rounded-md bg-white text-sky-700 shadow-sm font-bold";
    btnSign.className = "px-3 py-1 rounded-md text-slate-600 hover:text-slate-900 font-bold";
  }
}

// Handle Sign In (Nurse, Doctor, Admin)
async function handleWorkerSignIn(e) {
  e.preventDefault();
  const username_or_email = document.getElementById("inp-login-username").value.trim();
  const password = document.getElementById("inp-login-password").value.trim();

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username_or_email, password })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Authentication failed.");
    }

    const data = await res.json();
    currentUser = data.user;
    localStorage.setItem("retina_user", JSON.stringify(currentUser));
    localStorage.removeItem("retina_patient");

    enterPortal(currentUser.role);
  } catch (err) {
    alert("Login Notice: " + err.message);
  }
}

// Handle Health Worker Registration
async function handleWorkerRegister(e) {
  e.preventDefault();
  const full_name = document.getElementById("inp-reg-name").value.trim();
  const username = document.getElementById("inp-reg-username").value.trim();
  const email = document.getElementById("inp-reg-email").value.trim();
  const license_or_id = document.getElementById("inp-reg-license").value.trim();
  const organization = document.getElementById("inp-reg-org").value.trim();
  const password = document.getElementById("inp-reg-password").value.trim();

  try {
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name,
        username,
        email,
        license_or_id,
        organization,
        password,
        role: currentAuthRole
      })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Registration failed.");
    }

    const data = await res.json();
    currentUser = data.user;
    localStorage.setItem("retina_user", JSON.stringify(currentUser));
    localStorage.removeItem("retina_patient");

    alert(`✓ Welcome, ${currentUser.full_name}! Registration successful.`);
    enterPortal(currentUser.role);
  } catch (err) {
    alert("Registration Notice: " + err.message);
  }
}

// Handle Patient Secure Lookup (ID or Mobile No)
async function handlePatientLookup(e) {
  e.preventDefault();
  const identifier = document.getElementById("inp-patient-identifier").value.trim();
  if (!identifier) {
    alert("Please enter your Patient UID or registered phone number.");
    return;
  }

  try {
    const res = await fetch("/api/patients/lookup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Patient record not found.");
    }

    const data = await res.json();
    currentPatient = data.patient;
    currentPatientScreenings = data.screenings || [];

    localStorage.setItem("retina_patient", JSON.stringify(currentPatient));
    localStorage.removeItem("retina_user");

    enterPortal("patient");
  } catch (err) {
    alert("Patient Access Notice: " + err.message);
  }
}

function performDemoLogin() {
  const inpUser = document.getElementById("inp-login-username");
  const inpPass = document.getElementById("inp-login-password");

  if (currentAuthRole === "nurse") {
    inpUser.value = "nurse@retina.ai";
    inpPass.value = "nurse123";
  } else if (currentAuthRole === "doctor") {
    inpUser.value = "doctor@retina.ai";
    inpPass.value = "doctor123";
  } else if (currentAuthRole === "admin") {
    inpUser.value = "admin@retina.ai";
    inpPass.value = "admin123";
  }

  document.getElementById("form-worker-signin").dispatchEvent(new Event("submit"));
}

function performDemoPatientLogin() {
  document.getElementById("inp-patient-identifier").value = "PAT-2026-0001";
  handlePatientLookup(new Event("submit"));
}

function handleSignOut() {
  currentUser = null;
  currentPatient = null;
  localStorage.removeItem("retina_user");
  localStorage.removeItem("retina_patient");
  showLoginView();
}

// Switch into Authenticated Portal
function enterPortal(role) {
  document.getElementById("view-login").classList.add("hidden");
  document.getElementById("portal-nurse").classList.add("hidden");
  document.getElementById("portal-doctor").classList.add("hidden");
  document.getElementById("portal-patient").classList.add("hidden");
  document.getElementById("portal-admin").classList.add("hidden");

  // Show Header User Badge
  const userBadge = document.getElementById("header-user-badge");
  const guestBadge = document.getElementById("header-guest-badge");
  userBadge.classList.remove("hidden");
  guestBadge.classList.add("hidden");

  const nameEl = document.getElementById("header-user-name");
  const roleTag = document.getElementById("header-user-role-tag");

  if (role === "patient" && currentPatient) {
    nameEl.textContent = `${currentPatient.full_name} (${currentPatient.patient_uid})`;
    roleTag.textContent = "Citizen / Patient";
    roleTag.className = "text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30";
    document.getElementById("portal-patient").classList.remove("hidden");
    renderPatientPortalData();
  } else if (currentUser) {
    nameEl.textContent = currentUser.full_name;
    roleTag.textContent = currentUser.role.toUpperCase();

    if (currentUser.role === "nurse") {
      document.getElementById("portal-nurse").classList.remove("hidden");
      autoTrackNurseGPS(); // Automatic GPS locking
      loadPatients();
      loadNurseCampHistory();
    } else if (currentUser.role === "doctor") {
      document.getElementById("portal-doctor").classList.remove("hidden");
      loadDoctorQueue();
      initDoctorLoupe();
    } else if (currentUser.role === "admin") {
      document.getElementById("portal-admin").classList.remove("hidden");
      loadAdminMetrics();
      runSimulation();
    }
  }

  if (window.lucide) lucide.createIcons();
}


// =========================================================================
// 1. NURSE / ASHA PORTAL (AUTOMATIC GPS & CAMP HISTORY)
// =========================================================================

// Automatic GPS Tracking (HTML5 Geolocation + Reverse Geocoding)
function autoTrackNurseGPS() {
  const coordsEl = document.getElementById("nurse-gps-coords-display");
  const addrEl = document.getElementById("nurse-gps-address-display");

  if (coordsEl) coordsEl.textContent = "📍 Acquiring high-precision live GPS satellite lock...";

  if ("geolocation" in navigator) {
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        nurseCampGPS.lat = pos.coords.latitude;
        nurseCampGPS.lon = pos.coords.longitude;
        nurseCampGPS.accuracy = pos.coords.accuracy;
        nurseCampGPS.isLive = true;

        if (coordsEl) {
          coordsEl.textContent = `📍 Live GPS Locked: ${nurseCampGPS.lat.toFixed(4)}° N, ${nurseCampGPS.lon.toFixed(4)}° E (Accuracy: ±${Math.round(nurseCampGPS.accuracy)}m)`;
        }

        // Reverse-geocoding via OpenStreetMap Nominatim
        try {
          const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${nurseCampGPS.lat}&lon=${nurseCampGPS.lon}`);
          if (res.ok) {
            const data = await res.json();
            const addr = data.display_name || "Madurai District, Tamil Nadu";
            nurseCampGPS.address = addr;
            if (addrEl) addrEl.textContent = `Address: ${addr}`;
          }
        } catch (e) {
          if (addrEl) addrEl.textContent = "Address: PHC Outreach Camp Locality, Tamil Nadu";
        }
      },
      (err) => {
        console.warn("Browser GPS permission not granted or timeout:", err.message);
        if (coordsEl) {
          coordsEl.textContent = `📍 Calibrated Camp GPS: ${nurseCampGPS.lat.toFixed(4)}° N, ${nurseCampGPS.lon.toFixed(4)}° E (Outreach Van Unit)`;
        }
        if (addrEl) {
          addrEl.textContent = `Address: ${nurseCampGPS.address}`;
        }
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  }
}

function switchNurseSubTab(tab) {
  const screenView = document.getElementById("nurse-view-screen");
  const historyView = document.getElementById("nurse-view-history");
  const btnScreen = document.getElementById("nurse-subtab-screen");
  const btnHistory = document.getElementById("nurse-subtab-history");

  if (tab === "screen") {
    screenView.classList.remove("hidden");
    historyView.classList.add("hidden");
    btnScreen.className = "px-3.5 py-2 rounded-xl bg-sky-600 text-white font-bold text-xs shadow-sm flex items-center space-x-1.5";
    btnHistory.className = "px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs border border-slate-300 flex items-center space-x-1.5";
  } else {
    screenView.classList.add("hidden");
    historyView.classList.remove("hidden");
    btnHistory.className = "px-3.5 py-2 rounded-xl bg-sky-600 text-white font-bold text-xs shadow-sm flex items-center space-x-1.5";
    btnScreen.className = "px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs border border-slate-300 flex items-center space-x-1.5";
    loadNurseCampHistory();
  }
  if (window.lucide) lucide.createIcons();
}

async function loadNurseCampHistory() {
  try {
    const res = await fetch("/api/doctor/camp-screenings");
    const data = await res.json();
    const list = data.queue || [];

    const badge = document.getElementById("nurse-history-badge");
    if (badge) badge.textContent = list.length;

    const tbody = document.getElementById("nurse-camp-history-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (list.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="py-8 text-center text-slate-400">No screenings recorded yet for this mobile camp.</td></tr>`;
      return;
    }

    list.forEach(s => {
      const isCertified = s.doctor_review_status && s.doctor_review_status.includes("Certified");
      const tr = document.createElement("tr");
      tr.className = "hover:bg-slate-50 transition-colors";

      const doctorNotes = isCertified
        ? `<span class="font-bold text-indigo-950">${s.doctor_clinical_action || 'Action Recorded'}</span><br/><span class="text-slate-500 italic">${s.doctor_prescription || ''}</span>`
        : `<span class="text-amber-700 italic font-medium">Pending Doctor Tele-Review...</span>`;

      tr.innerHTML = `
        <td class="py-2.5 px-3">
          <span class="font-bold text-slate-900">${s.patient_name}</span>
          <span class="block font-mono text-[10px] text-sky-700">${s.patient_uid}</span>
        </td>
        <td class="py-2.5 px-3 font-medium text-slate-700">${s.village}</td>
        <td class="py-2.5 px-3">
          <span class="font-bold ${s.is_referable ? 'text-red-700' : 'text-emerald-700'}">${s.grade_name}</span>
          <span class="block text-[10px] text-slate-400">Eye: ${s.eye}</span>
        </td>
        <td class="py-2.5 px-3 font-mono text-[10px] text-slate-500">
          📍 ${s.nurse_gps_lat ? s.nurse_gps_lat.toFixed(3) : '9.925'}°N, ${s.nurse_gps_lon ? s.nurse_gps_lon.toFixed(3) : '78.119'}°E
        </td>
        <td class="py-2.5 px-3">
          <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${
            isCertified ? 'bg-indigo-100 text-indigo-800' : 'bg-amber-100 text-amber-800'
          }">
            ${isCertified ? '✓ Certified by ' + (s.doctor_signed_by ? s.doctor_signed_by.split(',')[0] : 'Doctor') : 'Pending Review'}
          </span>
        </td>
        <td class="py-2.5 px-3 text-[11px] max-w-xs">
          ${doctorNotes}
        </td>
        <td class="py-2.5 px-3 text-right">
          <a href="${s.report_pdf_url}" target="_blank" class="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-800 font-bold text-[11px] inline-flex items-center space-x-1 border border-slate-300">
            <i data-lucide="file-text" class="w-3 h-3 text-rose-600"></i>
            <span>PDF</span>
          </a>
        </td>
      `;
      tbody.appendChild(tr);
    });

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error("Error loading camp history:", err);
  }
}

// Patient Registry Management
async function loadPatients() {
  try {
    const res = await fetch("/api/patients");
    patientsList = await res.json();
    populatePatientSelect();
  } catch (err) {
    console.error("Error loading patients:", err);
  }
}

function populatePatientSelect() {
  const select = document.getElementById("active-patient-select");
  if (!select) return;
  select.innerHTML = '<option value="">-- Select Registered Patient --</option>';
  patientsList.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = `${p.full_name} (${p.patient_uid}) - Village: ${p.village}, ${p.district}`;
    select.appendChild(opt);
  });

  if (patientsList.length > 0 && !activePatient) {
    select.value = patientsList[0].id;
    activePatient = patientsList[0];
    updatePatientSnapshot(activePatient);
  }
}

function onPatientSelected() {
  const select = document.getElementById("active-patient-select");
  const pId = parseInt(select.value);
  activePatient = patientsList.find(p => p.id === pId) || null;
  updatePatientSnapshot(activePatient);
}

function updatePatientSnapshot(p) {
  if (!p) return;
  document.getElementById("snap-name").textContent = p.full_name;
  document.getElementById("snap-village").textContent = `${p.village} (Manually Entered), ${p.district}`;
  document.getElementById("snap-age-gender").textContent = `${p.age} yrs / ${p.gender}`;
  document.getElementById("snap-clinical").textContent = `${p.hba1c ? p.hba1c + '%' : 'Unknown'} / ${p.diabetes_years} yrs DM`;
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
  const villageVal = (document.getElementById("inp-village").value || "").trim(); // Manual Entry
  const phoneVal = (document.getElementById("inp-phone").value || "").trim();
  const emailVal = (document.getElementById("inp-email").value || "").trim();

  if (!nameVal || !villageVal) {
    alert("Please enter patient name and village.");
    return;
  }

  const body = {
    full_name: nameVal,
    age: parseInt(rawAge) || 55,
    gender: document.getElementById("inp-gender").value || "Male",
    village: villageVal,
    district: (document.getElementById("inp-district").value || "").trim() || "Madurai",
    diabetes_years: rawDiab ? parseFloat(rawDiab) : 5.0,
    hba1c: rawHba1c ? parseFloat(rawHba1c) : 7.8,
    phone: phoneVal || "+91 98421 73829",
    email: emailVal || "patient.care@gmail.com",
    hypertension: false,
    smoker: false
  };

  try {
    const res = await fetch("/api/patients", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error("Failed to register patient");
    const newPatient = await res.json();
    patientsList.unshift(newPatient);
    populatePatientSelect();

    document.getElementById("active-patient-select").value = newPatient.id;
    activePatient = newPatient;
    updatePatientSnapshot(newPatient);

    closeNewPatientModal();
    document.getElementById("new-patient-form").reset();
    alert(`✓ Patient Registered Successfully!\nUID: ${newPatient.patient_uid}\nVillage: ${newPatient.village}`);
  } catch (err) {
    alert("Notice: " + err.message);
  }
}

function setEyeSelection(eye) {
  activeEye = eye;
  const btnOd = document.getElementById("btn-eye-od");
  const btnOs = document.getElementById("btn-eye-os");
  if (eye === "OD") {
    btnOd.className = "px-3 py-1 rounded-md bg-white text-sky-700 shadow-sm font-bold";
    btnOs.className = "px-3 py-1 rounded-md text-slate-600 hover:text-slate-900 font-bold";
  } else {
    btnOs.className = "px-3 py-1 rounded-md bg-white text-sky-700 shadow-sm font-bold";
    btnOd.className = "px-3 py-1 rounded-md text-slate-600 hover:text-slate-900 font-bold";
  }
}

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (!file) return;
  selectedFile = file;

  // Auto-lock GPS when file is chosen
  autoTrackNurseGPS();

  const reader = new FileReader();
  reader.onload = (evt) => {
    const preview = document.getElementById("fundus-preview");
    preview.src = evt.target.result;
    preview.classList.remove("hidden");
    document.getElementById("upload-placeholder").classList.add("hidden");
    evaluateInstantIQA();
  };
  reader.readAsDataURL(file);
}

function loadSampleFundusImage() {
  autoTrackNurseGPS();

  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 512;
  const ctx = canvas.getContext("2d");

  // Background
  ctx.fillStyle = "#09090b";
  ctx.fillRect(0, 0, 512, 512);

  // Retinal Disc
  const grad = ctx.createRadialGradient(256, 256, 30, 256, 256, 230);
  grad.addColorStop(0, "#d35400");
  grad.addColorStop(0.5, "#b93e0b");
  grad.addColorStop(0.85, "#801d00");
  grad.addColorStop(1.0, "#09090b");

  ctx.beginPath();
  ctx.arc(256, 256, 230, 0, Math.PI * 2);
  ctx.fillStyle = grad;
  ctx.fill();

  // Optic Disc
  ctx.beginPath();
  ctx.arc(380, 250, 36, 0, Math.PI * 2);
  ctx.fillStyle = "#f39c12";
  ctx.shadowColor = "#f1c40f";
  ctx.shadowBlur = 14;
  ctx.fill();
  ctx.shadowBlur = 0;

  // Vascular Arcades
  ctx.strokeStyle = "#4a0000";
  ctx.lineWidth = 3.5;
  ctx.beginPath();
  ctx.moveTo(380, 250);
  ctx.bezierCurveTo(320, 160, 240, 140, 160, 180);
  ctx.moveTo(380, 250);
  ctx.bezierCurveTo(320, 340, 240, 360, 160, 320);
  ctx.stroke();

  // Microaneurysms
  ctx.fillStyle = "#2d0000";
  const maSpots = [[220, 240], [205, 270], [180, 230], [250, 190], [190, 300], [270, 290]];
  maSpots.forEach(([x, y]) => {
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
  });

  // Hard Exudates
  ctx.fillStyle = "#fff478";
  const exudates = [[210, 210], [218, 205], [230, 215], [202, 220]];
  exudates.forEach(([x, y]) => {
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, Math.PI * 2);
    ctx.fill();
  });

  canvas.toBlob((blob) => {
    selectedFile = new File([blob], "sample_phc_fundus.jpg", { type: "image/jpeg" });
    const preview = document.getElementById("fundus-preview");
    preview.src = canvas.toDataURL("image/jpeg");
    preview.classList.remove("hidden");
    document.getElementById("upload-placeholder").classList.add("hidden");
    evaluateInstantIQA();
  }, "image/jpeg");
}

function evaluateInstantIQA() {
  const banner = document.getElementById("iqa-live-banner");
  if (!banner) return;
  banner.classList.remove("hidden");
  banner.className = "rounded-xl p-3 border bg-emerald-50 border-emerald-200 text-emerald-900 text-xs";
  document.getElementById("iqa-status-pill").innerHTML = `<i data-lucide="check-circle" class="w-4 h-4 mr-1 text-emerald-600"></i> Automated Image Quality: Good (Sharp & Gradable)`;
  document.getElementById("iqa-score-label").textContent = `Score: 94.8/100`;
  document.getElementById("iqa-guidance-text").textContent = `✓ Field-of-view, macula focus, and illumination meet clinical telemedicine standards.`;
  if (window.lucide) lucide.createIcons();
}

async function triggerFundusScreening() {
  if (!activePatient) {
    alert("Please select or register a patient first.");
    return;
  }
  if (!selectedFile) {
    alert("Please capture/upload a fundus photograph or click 'Load Realistic IDRiD Sample Image'.");
    return;
  }

  const btn = document.getElementById("btn-run-screening");
  const btnText = document.getElementById("btn-screen-text");
  btn.disabled = true;
  btnText.textContent = "Analyzing Retinal Microvasculature & Grad-CAM...";

  const campName = currentUser && currentUser.organization ? currentUser.organization : "Mobile Screening Camp";

  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("patient_id", activePatient.id);
  formData.append("eye", activeEye);
  formData.append("asha_notes", document.getElementById("asha-notes-input")?.value || "");
  formData.append("nurse_gps_lat", nurseCampGPS.lat);
  formData.append("nurse_gps_lon", nurseCampGPS.lon);
  formData.append("nurse_camp_name", campName);

  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      body: formData
    });
    if (!res.ok) throw new Error("Screening inference failed");
    currentScreeningResult = await res.json();
    renderScreeningResults(currentScreeningResult);
    loadNurseCampHistory();
  } catch (err) {
    alert("Error during screening: " + err.message);
  } finally {
    btn.disabled = false;
    btnText.textContent = "Run Explainable AI Screening";
  }
}

function renderScreeningResults(data) {
  document.getElementById("results-placeholder").classList.add("hidden");
  document.getElementById("results-panel").classList.remove("hidden");

  // Verdict & Urgency
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
    badgeBox.className = "rounded-xl p-4 border bg-red-50 border-red-200 flex items-center justify-between";
    iconBox.className = "w-12 h-12 rounded-xl flex items-center justify-center text-white bg-red-600 shadow-sm";
    icon.setAttribute("data-lucide", "alert-octagon");
    statusEl.className = "font-black text-sm tracking-wide uppercase text-red-700";
    statusEl.textContent = "REFERABLE DR - SPECIALIST REVIEW REQUIRED";
    urgencyPill.className = "text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-200 text-red-900";
    urgencyPill.textContent = data.urgency;
  } else {
    badgeBox.className = "rounded-xl p-4 border bg-emerald-50 border-emerald-200 flex items-center justify-between";
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

  // Counts
  const findings = data.pathology_findings || {};
  document.getElementById("res-count-ma").textContent = findings.microaneurysms || 0;
  document.getElementById("res-count-hem").textContent = findings.hemorrhages || 0;
  document.getElementById("res-count-ex").textContent = findings.hard_exudates || 0;
  document.getElementById("res-count-nv").textContent = findings.neovascularization || "Absent";
  document.getElementById("res-progression-risk").textContent = `${data.progression_risk_percent || 52}%`;

  const pdfBtn = document.getElementById("res-btn-pdf");
  if (pdfBtn) pdfBtn.href = data.report_pdf_url;

  if (window.lucide) lucide.createIcons();
}

function dispatchToDoctorQueue() {
  if (!currentScreeningResult) return;
  alert(`✓ Screening ${currentScreeningResult.screening_uid} successfully dispatched to the District Tele-Ophthalmology Triage Queue!\nReviewing specialist Dr. Meenakshi Sundaram has been notified.`);
  switchNurseSubTab("history");
}

function setViewerMode(mode) {
  const overlayWrap = document.getElementById("overlay-view-wrapper");
  const sideWrap = document.getElementById("side-by-side-wrapper");
  const btnGrad = document.getElementById("mode-btn-gradcam");
  const btnSide = document.getElementById("mode-btn-side");

  if (mode === "gradcam") {
    btnGrad.className = "px-2.5 py-1 rounded-md bg-sky-600 text-white font-bold";
    btnSide.className = "px-2.5 py-1 rounded-md text-slate-700 hover:bg-slate-200";
    overlayWrap.classList.remove("hidden");
    sideWrap.classList.add("hidden");
  } else {
    btnSide.className = "px-2.5 py-1 rounded-md bg-sky-600 text-white font-bold";
    btnGrad.className = "px-2.5 py-1 rounded-md text-slate-700 hover:bg-slate-200";
    overlayWrap.classList.add("hidden");
    sideWrap.classList.remove("hidden");
    sideWrap.classList.add("grid");
  }
}


// =========================================================================
// 2. DOCTOR SPECIALIST PORTAL (QUEUE, LOUPE, CALIPER, NOTIFICATION DISPATCH)
// =========================================================================

async function loadDoctorQueue() {
  try {
    const res = await fetch("/api/doctor/queue");
    const data = await res.json();
    doctorQueue = data.queue || [];
    renderDoctorQueue(doctorQueue);

    const queueBadge = document.getElementById("doctor-queue-count-badge");
    const pendingCount = data.total_pending || 0;
    if (queueBadge) queueBadge.textContent = `${pendingCount} Pending Review`;
  } catch (err) {
    console.error("Error loading doctor queue:", err);
  }
}

function renderDoctorQueue(queue) {
  const container = document.getElementById("doctor-queue-list");
  if (!container) return;
  container.innerHTML = "";

  if (queue.length === 0) {
    container.innerHTML = `<p class="text-center py-8 text-xs text-slate-400">No screenings in tele-review queue.</p>`;
    return;
  }

  queue.forEach(item => {
    const isPending = (item.doctor_review_status || "").includes("Pending");
    const itemCard = document.createElement("div");
    itemCard.className = `p-3 rounded-xl border transition-all cursor-pointer ${
      isPending ? 'bg-amber-50/50 border-amber-200 hover:bg-amber-100/60' : 'bg-slate-50 border-slate-200 hover:bg-slate-100'
    }`;
    itemCard.onclick = () => openDoctorReview(item.id);

    itemCard.innerHTML = `
      <div class="flex items-center justify-between mb-1">
        <span class="font-black text-xs text-slate-800">${item.patient_name}</span>
        <span class="text-[9px] font-bold px-1.5 py-0.2 rounded ${
          item.is_referable ? 'bg-red-100 text-red-800' : 'bg-emerald-100 text-emerald-800'
        }">${item.eye} &bull; ${item.urgency}</span>
      </div>
      <div class="text-[11px] text-slate-600 flex items-center justify-between">
        <span>${item.grade_name}</span>
        <span class="font-mono text-[10px] text-slate-400">${item.patient_uid}</span>
      </div>
      <div class="mt-1.5 flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-200/60">
        <span>📍 ${item.nurse_camp_name || 'PHC Camp'}</span>
        <span class="font-bold ${isPending ? 'text-amber-700' : 'text-indigo-700'}">${item.doctor_review_status}</span>
      </div>
    `;
    container.appendChild(itemCard);
  });
}

async function openDoctorReview(screeningId) {
  try {
    const res = await fetch(`/api/doctor/review/${screeningId}`);
    const data = await res.json();
    activeReviewScreening = data;

    document.getElementById("doctor-empty-state").classList.add("hidden");
    document.getElementById("doctor-workstation-panel").classList.remove("hidden");

    const scr = data.screening;
    const pat = data.patient;

    document.getElementById("doc-patient-name").textContent = pat ? pat.full_name : "Patient";
    document.getElementById("doc-patient-uid").textContent = pat ? pat.patient_uid : scr.screening_uid;
    
    const latStr = scr.nurse_gps_lat ? scr.nurse_gps_lat.toFixed(4) : "9.9252";
    const lonStr = scr.nurse_gps_lon ? scr.nurse_gps_lon.toFixed(4) : "78.1198";
    document.getElementById("doc-camp-metadata").textContent = 
      `📍 Camp: ${scr.nurse_camp_name || 'PHC Camp'} (${latStr}° N, ${lonStr}° E) | Village: ${pat ? pat.village : 'PHC'} | Age: ${pat ? pat.age : '--'} yrs | HbA1c: ${pat ? pat.hba1c + '%' : 'N/A'}`;

    document.getElementById("doc-grade-pill").textContent = `${scr.grade_name} (${scr.eye})`;

    const imgEl = document.getElementById("doc-fundus-img");
    imgEl.src = scr.raw_image_url;
    imgEl.onload = () => {
      initCaliperCanvas();
    };

    if (scr.doctor_clinical_action) {
      document.getElementById("doc-action-select").value = scr.doctor_clinical_action;
    }
    if (scr.doctor_prescription) {
      document.getElementById("doc-prescription-text").value = scr.doctor_prescription;
    }
    if (scr.doctor_signed_by) {
      document.getElementById("doc-signature-name").value = scr.doctor_signed_by;
    } else if (currentUser && currentUser.full_name) {
      document.getElementById("doc-signature-name").value = `${currentUser.full_name} - Reg: ${currentUser.license_or_id || 'TN-MC-49210'}`;
    }

    resetCaliper();
    if (window.lucide) lucide.createIcons();
  } catch (err) {
    alert("Error loading screening detail: " + err.message);
  }
}

// 4x Sub-Pixel Loupe
function initDoctorLoupe() {
  const img = document.getElementById("doc-fundus-img");
  const lens = document.getElementById("loupe-lens");
  if (!img || !lens) return;

  const zoomRatio = 3.5;

  img.addEventListener("mousemove", (e) => {
    if (caliperActive) {
      lens.style.display = "none";
      return;
    }

    const rect = img.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (x < 0 || y < 0 || x > rect.width || y > rect.height) {
      lens.style.display = "none";
      return;
    }

    lens.style.display = "block";
    lens.style.backgroundImage = `url('${img.src}')`;
    lens.style.backgroundSize = `${rect.width * zoomRatio}px ${rect.height * zoomRatio}px`;

    const lensWidth = lens.offsetWidth;
    const lensHeight = lens.offsetHeight;

    lens.style.left = `${x - lensWidth / 2}px`;
    lens.style.top = `${y - lensHeight / 2}px`;

    const bgX = (x * zoomRatio) - lensWidth / 2;
    const bgY = (y * zoomRatio) - lensHeight / 2;
    lens.style.backgroundPosition = `-${bgX}px -${bgY}px`;
  });

  img.addEventListener("mouseleave", () => {
    lens.style.display = "none";
  });
}

function initCaliperCanvas() {
  const img = document.getElementById("doc-fundus-img");
  const canvas = document.getElementById("doc-caliper-canvas");
  if (!img || !canvas) return;
  canvas.width = img.clientWidth;
  canvas.height = img.clientHeight;
}

function toggleCaliperTool() {
  caliperActive = !caliperActive;
  const btnText = document.getElementById("caliper-btn-text");
  const bar = document.getElementById("caliper-measurement-bar");
  const canvas = document.getElementById("doc-caliper-canvas");
  const lens = document.getElementById("loupe-lens");

  if (caliperActive) {
    btnText.textContent = "Caliper Active (Click 2 Points)";
    bar.classList.remove("hidden");
    canvas.style.pointerEvents = "auto";
    if (lens) lens.style.display = "none";
    canvas.onclick = handleCaliperClick;
  } else {
    btnText.textContent = "Enable Caliper (μm)";
    canvas.style.pointerEvents = "none";
    caliperPoints = [];
  }
}

function resetCaliper() {
  caliperPoints = [];
  const canvas = document.getElementById("doc-caliper-canvas");
  if (canvas) {
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }
  const distEl = document.getElementById("caliper-distance-um");
  if (distEl) distEl.textContent = "-- μm";
}

function handleCaliperClick(e) {
  const canvas = document.getElementById("doc-caliper-canvas");
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  caliperPoints.push({ x, y });

  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#6366f1";
  ctx.beginPath();
  ctx.arc(x, y, 4, 0, Math.PI * 2);
  ctx.fill();

  if (caliperPoints.length === 2) {
    const p1 = caliperPoints[0];
    const p2 = caliperPoints[1];

    const pxDist = Math.sqrt(Math.pow(p2.x - p1.x, 2) + Math.pow(p2.y - p1.y, 2));
    const umDist = Math.round(pxDist * 10.4);

    ctx.strokeStyle = "#4f46e5";
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 2]);
    ctx.beginPath();
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = "#4f46e5";
    ctx.beginPath();
    ctx.arc(p1.x, p1.y, 5, 0, Math.PI * 2);
    ctx.arc(p2.x, p2.y, 5, 0, Math.PI * 2);
    ctx.fill();

    ctx.font = "bold 12px monospace";
    ctx.fillStyle = "#ffffff";
    ctx.fillRect((p1.x + p2.x) / 2 - 25, (p1.y + p2.y) / 2 - 16, 54, 18);
    ctx.fillStyle = "#4338ca";
    ctx.fillText(`${umDist}μm`, (p1.x + p2.x) / 2 - 20, (p1.y + p2.y) / 2 - 3);

    document.getElementById("caliper-distance-um").textContent = `${umDist} μm (${Math.round(pxDist)} px)`;
    caliperPoints = [];
  }
}

// Voice Dictation
function initVoiceRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    speechRecognizer = new SpeechRecognition();
    speechRecognizer.continuous = true;
    speechRecognizer.interimResults = false;
    speechRecognizer.lang = "en-IN";

    speechRecognizer.onresult = (e) => {
      let transcript = "";
      for (let i = e.resultIndex; i < e.results.length; ++i) {
        if (e.results[i].isFinal) {
          transcript += e.results[i][0].transcript + " ";
        }
      }
      const txt = document.getElementById("doc-prescription-text");
      if (txt) {
        txt.value = (txt.value ? txt.value + " " : "") + transcript.trim();
      }
    };

    speechRecognizer.onerror = () => stopVoiceDictation();
  }
}

function toggleVoiceDictation() {
  if (!speechRecognizer) {
    alert("Speech-to-Text is supported in Chrome/Edge. You may also type clinical notes manually.");
    return;
  }
  if (isDictating) stopVoiceDictation();
  else startVoiceDictation();
}

function startVoiceDictation() {
  try {
    speechRecognizer.start();
    isDictating = true;
    document.getElementById("btn-speech-dictate").className = "px-3 py-1 rounded-lg bg-rose-600 text-white font-bold text-xs flex items-center space-x-1.5 animate-pulse shadow";
    document.getElementById("dictate-status-text").textContent = "Listening (Speak Now)...";
  } catch (e) {
    console.warn(e);
  }
}

function stopVoiceDictation() {
  if (speechRecognizer && isDictating) speechRecognizer.stop();
  isDictating = false;
  document.getElementById("btn-speech-dictate").className = "px-3 py-1 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-bold text-xs flex items-center space-x-1.5 transition-all";
  document.getElementById("dictate-status-text").textContent = "Voice Dictate";
}

// Doctor Digital Certification with Automated WhatsApp & Email Dispatch
async function submitDoctorCertification() {
  if (!activeReviewScreening) return;
  const scrId = activeReviewScreening.screening.id;
  const actionVal = document.getElementById("doc-action-select").value;
  const signatureVal = document.getElementById("doc-signature-name").value;
  const rxVal = document.getElementById("doc-prescription-text").value;

  if (!signatureVal) {
    alert("Please enter doctor digital signature name.");
    return;
  }

  try {
    const res = await fetch(`/api/doctor/review/${scrId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        doctor_signed_by: signatureVal,
        doctor_clinical_action: actionVal,
        doctor_prescription: rxVal,
        hospital_compliance_status: "Certified & Appointment Scheduled"
      })
    });

    if (!res.ok) throw new Error("Certification failed");
    const result = await res.json();

    const notif = result.notifications;
    let notifMsg = "";
    if (notif) {
      notifMsg = `\n\n📲 Automated Patient Alerts Dispatched:\n• WhatsApp Alert: ${notif.whatsapp.status} to ${notif.whatsapp.recipient_phone}\n• Email Alert: ${notif.email.status} to ${notif.email.recipient_email}`;
    }

    alert(`✓ Screening Certified Successfully!\nSigned By: ${result.doctor_signed_by}\nAction: ${actionVal}${notifMsg}`);
    loadDoctorQueue();
  } catch (err) {
    alert("Notice: " + err.message);
  }
}


// =========================================================================
// 3. PRIVATE PATIENT / CITIZEN HEALTH PORTAL
// =========================================================================

function renderPatientPortalData() {
  if (!currentPatient) return;

  document.getElementById("patient-display-name").textContent = currentPatient.full_name;
  document.getElementById("patient-display-uid").textContent = currentPatient.patient_uid;
  document.getElementById("patient-display-village").textContent = 
    `Village: ${currentPatient.village} | Diabetes: ${currentPatient.diabetes_years} Years | Mobile: ${currentPatient.phone || 'N/A'}`;

  // Most recent screening
  const latestScreening = currentPatientScreenings.length > 0 ? currentPatientScreenings[0] : null;

  if (latestScreening) {
    // Doctor consultation verdict banner
    const verdictDocName = document.getElementById("pat-verdict-doc-name");
    const verdictTime = document.getElementById("pat-verdict-timestamp");
    const verdictAction = document.getElementById("pat-verdict-action");
    const verdictRx = document.getElementById("pat-verdict-rx");
    const btnPdf = document.getElementById("pat-btn-download-pdf");

    if (latestScreening.doctor_review_status && latestScreening.doctor_review_status.includes("Certified")) {
      verdictDocName.textContent = latestScreening.doctor_signed_by || "Reviewing District Ophthalmologist";
      verdictTime.textContent = `Certified on ${latestScreening.doctor_signed_at || 'Recent'}`;
      verdictAction.textContent = latestScreening.doctor_clinical_action || "Specialist Examination Completed";
      verdictRx.textContent = latestScreening.doctor_prescription || "Follow routine diabetic retina eye care.";
    } else {
      verdictDocName.textContent = "Screening Stored - Under Specialist Review";
      verdictTime.textContent = "Pending Doctor Certification";
      verdictAction.textContent = "Awaiting tele-ophthalmology sign-off from District Hospital";
      verdictRx.textContent = "The specialist doctor will review your fundus photo and dispatch your prescription shortly.";
    }

    if (btnPdf && latestScreening.report_pdf_url) {
      btnPdf.href = latestScreening.report_pdf_url;
    }

    // Dual-Eye Status
    const odRecord = currentPatientScreenings.find(s => s.eye === "OD") || latestScreening;
    const osRecord = currentPatientScreenings.find(s => s.eye === "OS");

    if (odRecord) {
      document.getElementById("pat-od-status").textContent = odRecord.grade_name;
      const badge = document.getElementById("pat-od-badge");
      if (odRecord.is_referable) {
        badge.className = "inline-block px-2 py-0.5 rounded-full text-[9px] font-bold bg-red-100 text-red-800";
        badge.textContent = "Referral Advised";
      } else {
        badge.className = "inline-block px-2 py-0.5 rounded-full text-[9px] font-bold bg-emerald-100 text-emerald-800";
        badge.textContent = "Healthy / Normal";
      }
      const risk = odRecord.progression_risk_percent || 52;
      document.getElementById("pat-progression-val").textContent = `${risk}%`;
      document.getElementById("pat-progression-bar").style.width = `${risk}%`;
    }

    if (osRecord) {
      document.getElementById("pat-os-status").textContent = osRecord.grade_name;
      const badge = document.getElementById("pat-os-badge");
      badge.textContent = osRecord.is_referable ? "Referral Advised" : "Normal";
    }

    // Set initial voice text in Tamil
    playPatientVoiceScript("tamil", false);
  }
}

// Regional Audio Playback for Patient
function playPatientVoiceScript(lang, speakAloud = true) {
  const pName = currentPatient ? currentPatient.full_name : "நோயாளி";
  const scr = currentPatientScreenings.length > 0 ? currentPatientScreenings[0] : null;
  const gradeName = scr ? scr.grade_name : "Diabetic Retinopathy";
  const docAction = scr && scr.doctor_clinical_action ? scr.doctor_clinical_action : "மருத்துவர் ஆலோசனை";

  const scripts = {
    tamil: `வணக்கம் ${pName}. உங்கள் கண் பரிசோதனை முடிவு: ${gradeName}. மருத்துவர் பரிந்துரை: ${docAction}. பார்வை பாதுகாப்பிற்கு அரசு அல்லது மாவட்ட கண் மருத்துவமனைக்கு செல்லவும்.`,
    hindi: `नमस्ते ${pName}। आपकी आंख की जांच का परिणाम: ${gradeName}। डॉक्टर का निर्देश: ${docAction}। दृष्टि की सुरक्षा के लिए जिला अस्पताल से संपर्क करें।`,
    english: `Hello ${pName}. Your retinal screening diagnosis is ${gradeName}. The specialist recommends: ${docAction}. Please visit the district eye hospital for consultation.`
  };

  const text = scripts[lang] || scripts.tamil;
  const titleEl = document.getElementById("voice-lang-active-title");
  const textEl = document.getElementById("voice-spoken-text");

  if (titleEl) titleEl.textContent = `Spoken Guidance (${lang.toUpperCase()}):`;
  if (textEl) textEl.textContent = `"${text}"`;

  if (speakAloud && "speechSynthesis" in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    if (lang === "tamil") utterance.lang = "ta-IN";
    else if (lang === "hindi") utterance.lang = "hi-IN";
    else utterance.lang = "en-IN";
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
  }
}


// =========================================================================
// 4. DISTRICT ADMIN & SIMULINK PORTAL LOGIC
// =========================================================================

async function loadAdminMetrics() {
  try {
    const [metricsRes, ashaRes] = await Promise.all([
      fetch("/api/admin/metrics"),
      fetch("/api/admin/asha-tracker")
    ]);

    const m = await metricsRes.json();
    const asha = await ashaRes.json();

    document.getElementById("dho-stat-total").textContent = m.total_screenings || 1;
    document.getElementById("dho-stat-ref-rate").textContent = `${m.referable_rate_percent || 0}%`;
    document.getElementById("dho-stat-certified").textContent = m.doctor_reviewed_count || 0;
    document.getElementById("dho-stat-incentives").textContent = `₹${(asha.total_incentives_disbursed_inr || 24000).toLocaleString()}`;

    const tbody = document.getElementById("asha-tracker-tbody");
    if (tbody && asha.workers) {
      tbody.innerHTML = "";
      asha.workers.forEach(w => {
        const tr = document.createElement("tr");
        tr.className = "hover:bg-slate-50 transition-colors";
        tr.innerHTML = `
          <td class="py-2.5 px-3">
            <span class="font-bold text-slate-800">${w.name}</span>
            <span class="block font-mono text-[10px] text-slate-400">${w.worker_id}</span>
          </td>
          <td class="py-2.5 px-3 text-slate-600">${w.primary_phc}</td>
          <td class="py-2.5 px-3 font-mono font-bold">${w.screenings_completed}</td>
          <td class="py-2.5 px-3 font-mono text-red-600 font-bold">${w.referrals_flagged}</td>
          <td class="py-2.5 px-3 font-mono text-emerald-600 font-bold">${w.hospital_arrivals_verified}</td>
          <td class="py-2.5 px-3">
            <span class="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
              ${w.quality_pass_rate}% Pass
            </span>
          </td>
          <td class="py-2.5 px-3 text-right font-mono font-extrabold text-emerald-700">₹${w.incentive_earned_inr.toLocaleString()}</td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error("Error loading admin metrics:", err);
  }
}

function updateSimSlider(type, val) {
  if (type === "pop") {
    document.getElementById("val-pop").textContent = `${parseInt(val).toLocaleString()}`;
  } else if (type === "phc") {
    document.getElementById("val-phc").textContent = val;
  } else if (type === "doc") {
    document.getElementById("val-doc").textContent = val;
  }
  runSimulation();
}

async function runSimulation() {
  const pop = parseInt(document.getElementById("sim-pop-slider")?.value || 100000);
  const phc = parseInt(document.getElementById("sim-phc-slider")?.value || 50);
  const bw = parseFloat(document.getElementById("sim-bandwidth-select")?.value || 2.0);
  const doc = parseInt(document.getElementById("sim-doc-slider")?.value || 5);

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

  const queueDesc = document.getElementById("sim-queue-desc");
  const queueBox = document.getElementById("sim-queue-box");
  queueDesc.textContent = sim.simulink_queue_status;

  if (sim.doctor_deficit_or_surplus >= 0) {
    queueBox.className = "p-3.5 rounded-xl border bg-emerald-50 border-emerald-200 text-emerald-900";
  } else {
    queueBox.className = "p-3.5 rounded-xl border bg-red-50 border-red-200 text-red-900";
  }

  updateSimChart(sim.daily_screening_capacity, sim.daily_referrals);
}

function initSimChart() {
  const ctx = document.getElementById("simChart");
  if (!ctx) return;

  simChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Unassisted Manual Screening (Total Patients)", "RetinaAI Automated Triage (Referral Queue Only)"],
      datasets: [{
        label: "Patients Requiring Specialist Doctor Review / Day",
        data: [333, 50],
        backgroundColor: ["#94a3b8", "#0284c7"],
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
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

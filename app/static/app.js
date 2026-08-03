const API = "/api/v1";
const state = { students: [], courses: [], user: null, editor: null };
const $ = (id) => document.getElementById(id);

async function request(path, options = {}) {
  const token = state.user?.access_token || sessionStorage.getItem("campus_token");
  const headers = { "Content-Type": "application/json", ...(token ? {Authorization: `Bearer ${token}`} : {}), ...(options.headers || {}) };
  const response = await fetch(API + path, { ...options, headers });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try { const body = await response.json(); message = typeof body.detail === "string" ? body.detail : message; } catch {}
    throw new Error(message);
  }
  return response.status === 204 ? null : response.json();
}

function toast(message, error = false) {
  const node = $("toast"); node.textContent = message; node.className = `toast show${error ? " error" : ""}`;
  clearTimeout(toast.timer); toast.timer = setTimeout(() => node.className = "toast", 2600);
}

function initials(name) { return name.split(/\s+/).slice(0, 2).map(x => x[0]).join("").toUpperCase(); }
function escapeHtml(value) { const div = document.createElement("div"); div.textContent = value ?? ""; return div.innerHTML; }

async function loadData() {
  const canBrowseStudents = ["administrator", "teacher"].includes(state.user.role);
  const studentRequest = canBrowseStudents ? request("/students") : request(`/students/${state.user.student_id}`).then(item => [item]);
  [state.students, state.courses] = await Promise.all([studentRequest, request("/courses")]);
  renderDashboard(); renderStudents(); renderCourses(); fillSelects();
}

function applyRole() {
  const role = state.user.role, admin = role === "administrator", staff = admin || role === "teacher";
  document.querySelectorAll(".admin-only").forEach(x => x.classList.toggle("hidden", !admin));
  document.querySelectorAll(".staff-only").forEach(x => x.classList.toggle("hidden", !staff));
  document.body.classList.toggle("viewer-mode", !staff);
  $("studentsHeading").textContent = staff ? "Students" : role === "parent" ? "My student" : "My profile";
  $("studentsDescription").textContent = staff ? "Manage student profiles and view academic progress." : "View the student information linked to this account.";
  $("academicsNavLabel").textContent = staff ? "Academics" : "My academic report";
}

function renderDashboard() {
  $("studentCount").textContent = state.students.length; $("courseCount").textContent = state.courses.length;
  $("recentStudents").innerHTML = state.students.slice(0, 5).map(s => `<div class="compact-row"><span class="person-mark">${initials(s.name)}</span><div><b>${escapeHtml(s.name)}</b><br><small>${s.student_id} · Year ${s.year}</small></div><span class="badge">Active</span></div>`).join("");
}

function renderStudents(list = state.students) {
  const admin = state.user?.role === "administrator";
  $("studentTotal").textContent = `${list.length} student${list.length === 1 ? "" : "s"}`;
  $("studentRows").innerHTML = list.map(s => `<tr><td><div class="row-person"><span class="person-mark">${initials(s.name)}</span><div><b>${escapeHtml(s.name)}</b><br><small class="muted">${s.student_id}</small></div></div></td><td>${escapeHtml(s.department)}</td><td><span class="badge">Year ${s.year}</span></td><td><div class="actions"><button class="action-btn" onclick="showReport('${s.student_id}')" title="Report">◎</button>${admin ? `<button class="action-btn" onclick="editStudent('${s.student_id}')" title="Edit">✎</button><button class="action-btn danger" onclick="deleteStudent('${s.student_id}')" title="Delete">×</button>` : ""}</div></td></tr>`).join("") || `<tr><td colspan="4" class="muted">No students found.</td></tr>`;
}

function renderCourses(list = state.courses) {
  const admin = state.user?.role === "administrator";
  $("courseTotal").textContent = `${list.length} course${list.length === 1 ? "" : "s"}`;
  $("courseGrid").innerHTML = list.map(c => `<article class="course-card"><span class="course-code">${c.code}</span><h3>${escapeHtml(c.name)}</h3><div class="course-card-foot"><span>${c.credits} credits</span>${admin ? `<div class="actions"><button class="action-btn" onclick="editCourse('${c.code}')">✎</button><button class="action-btn danger" onclick="deleteCourse('${c.code}')">×</button></div>` : ""}</div></article>`).join("") || `<p class="muted">No courses found.</p>`;
}

function fillSelects() {
  const students = state.students.map(s => `<option value="${s.student_id}">${s.student_id} — ${escapeHtml(s.name)}</option>`).join("");
  const courses = state.courses.map(c => `<option value="${c.code}">${c.code} — ${escapeHtml(c.name)}</option>`).join("");
  ["enrollStudent", "scoreStudent", "reportStudent"].forEach(id => $(id).innerHTML = students);
  ["enrollCourse", "scoreCourse"].forEach(id => $(id).innerHTML = courses);
}

function go(page) {
  document.querySelectorAll(".page").forEach(x => x.classList.remove("active")); $(page + "Page").classList.add("active");
  document.querySelectorAll(".nav-item[data-page]").forEach(x => x.classList.toggle("active", x.dataset.page === page));
  $("pageTitle").textContent = page[0].toUpperCase() + page.slice(1); document.querySelector(".sidebar").classList.remove("open");
}

function openEditor(type, item = null) {
  state.editor = { type, item }; const isStudent = type === "student";
  $("dialogEyebrow").textContent = item ? "EDIT RECORD" : "NEW RECORD";
  $("dialogTitle").textContent = `${item ? "Edit" : "Add"} ${type}`;
  $("dialogFields").innerHTML = isStudent
    ? `${item ? "" : `<label>Student ID<input name="student_id" maxlength="20" required></label>`}<label>Full name<input name="name" value="${escapeHtml(item?.name || "")}" required></label><label>Year<input name="year" type="number" min="1" max="8" value="${item?.year || 1}" required></label>`
    : `${item ? "" : `<label>Course code<input name="code" maxlength="20" required></label>`}<label>Course name<input name="name" value="${escapeHtml(item?.name || "")}" required></label><label>Credits<input name="credits" type="number" min="1" max="20" value="${item?.credits || 3}" required></label>`;
  $("editorDialog").showModal();
}

window.editStudent = id => openEditor("student", state.students.find(x => x.student_id === id));
window.editCourse = code => openEditor("course", state.courses.find(x => x.code === code));
window.deleteStudent = async id => { if (!confirm(`Delete student ${id}?`)) return; try { await request(`/students/${id}`, {method:"DELETE"}); await loadData(); toast("Student deleted."); } catch(e) { toast(e.message, true); } };
window.deleteCourse = async code => { if (!confirm(`Delete course ${code}?`)) return; try { await request(`/courses/${code}`, {method:"DELETE"}); await loadData(); toast("Course deleted."); } catch(e) { toast(e.message, true); } };
window.showReport = async id => { go("academics"); $("reportStudent").value = id; await generateReport(id); };

async function generateReport(id) {
  try {
    const r = await request(`/students/${id}/report`), result = $("reportResult");
    result.innerHTML = `<div class="report-header"><div><span class="eyebrow">ACADEMIC REPORT</span><h2>${escapeHtml(r.student.name)}</h2><p class="muted">${r.student.student_id} · ${escapeHtml(r.student.department)} · Year ${r.student.year}</p></div><div class="gpa-box"><small>OVERALL GPA</small><strong>${r.overall_gpa ?? "—"}</strong></div></div><div class="table-card report-table"><table><thead><tr><th>Course</th><th>Credits</th><th>Score</th><th>Grade</th><th>GPA</th></tr></thead><tbody>${r.courses.map(c => `<tr><td><b>${c.code}</b><br><small class="muted">${escapeHtml(c.name)}</small></td><td>${c.credits}</td><td>${c.score ?? "Pending"}</td><td>${c.grade ?? "—"}</td><td>${c.gpa ?? "—"}</td></tr>`).join("") || `<tr><td colspan="5">No enrollments yet.</td></tr>`}</tbody></table></div>`;
    result.classList.remove("hidden");
  } catch(e) { toast(e.message, true); }
}

function enterApp() { $("profileName").textContent = state.user.username; $("profileRole").textContent = state.user.role; $("welcomeName").textContent = state.user.username; $("loginView").classList.add("hidden"); $("appView").classList.remove("hidden"); applyRole(); return loadData(); }
function updateParentField() { const parent = $("username").value.trim().toLowerCase() === "parent"; $("parentStudentField").classList.toggle("hidden", !parent); $("parentStudentId").required = parent; }
$("username").addEventListener("input", updateParentField);
$("loginForm").addEventListener("submit", async e => { e.preventDefault(); try { state.user = await request("/auth/login", {method:"POST", body:JSON.stringify({username:$("username").value, password:$("password").value, student_id:$("parentStudentId").value || null})}); sessionStorage.setItem("campus_token", state.user.access_token); sessionStorage.setItem("campus_user", JSON.stringify(state.user)); await enterApp(); } catch(err) { toast(err.message, true); } });
$("logoutBtn").onclick = () => { state.user = null; sessionStorage.removeItem("campus_token"); sessionStorage.removeItem("campus_user"); $("appView").classList.add("hidden"); $("loginView").classList.remove("hidden"); go("dashboard"); };
document.querySelectorAll("[data-demo]").forEach(button => button.onclick = () => { const [user,password] = button.dataset.demo.split("|"); $("username").value=user; $("password").value=password; $("parentStudentId").value = ""; updateParentField(); if (user === "parent") $("parentStudentId").focus(); });
document.querySelectorAll("[data-page]").forEach(x => x.onclick = () => go(x.dataset.page));
document.querySelectorAll("[data-go]").forEach(x => x.onclick = () => go(x.dataset.go));
$("menuBtn").onclick = () => document.querySelector(".sidebar").classList.toggle("open");
$("addStudentBtn").onclick = () => openEditor("student"); $("addCourseBtn").onclick = () => openEditor("course");
$("closeDialog").onclick = $("cancelDialog").onclick = () => $("editorDialog").close();
$("studentSearch").oninput = e => { const q=e.target.value.toLowerCase(); renderStudents(state.students.filter(s => `${s.student_id} ${s.name}`.toLowerCase().includes(q))); };
$("courseSearch").oninput = e => { const q=e.target.value.toLowerCase(); renderCourses(state.courses.filter(c => `${c.code} ${c.name}`.toLowerCase().includes(q))); };
$("editorForm").addEventListener("submit", async e => { e.preventDefault(); const data=Object.fromEntries(new FormData(e.target)); const {type,item}=state.editor; try { if(type==="student"){data.year=Number(data.year); await request(item?`/students/${item.student_id}`:"/students",{method:item?"PUT":"POST",body:JSON.stringify(data)});}else{data.credits=Number(data.credits);await request(item?`/courses/${item.code}`:"/courses",{method:item?"PUT":"POST",body:JSON.stringify(data)});} $("editorDialog").close(); await loadData(); toast(`${type[0].toUpperCase()+type.slice(1)} saved.`); } catch(err){toast(err.message,true);} });
$("enrollForm").onsubmit = async e => { e.preventDefault(); try { await request("/enrollments",{method:"POST",body:JSON.stringify({student_id:$("enrollStudent").value,course_code:$("enrollCourse").value})}); toast("Enrollment created."); } catch(err){toast(err.message,true);} };
$("scoreForm").onsubmit = async e => { e.preventDefault(); try { await request(`/enrollments/${$("scoreStudent").value}/${$("scoreCourse").value}/score`,{method:"PUT",body:JSON.stringify({score:Number($("scoreValue").value)})}); toast("Score recorded."); } catch(err){toast(err.message,true);} };
$("reportForm").onsubmit = e => { e.preventDefault(); generateReport($("reportStudent").value); };

try { const saved = JSON.parse(sessionStorage.getItem("campus_user")); if (saved?.access_token) { state.user = saved; enterApp().catch(() => $("logoutBtn").click()); } } catch { sessionStorage.clear(); }

// Sidebar Drawer Toggle
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  if (sidebar) sidebar.classList.toggle("show");
}

// Notifications Flyout
function openNotifications() {
  const modal = document.getElementById("notificationModal");
  if (modal) modal.classList.add("show");
}

function closeNotifications() {
  const modal = document.getElementById("notificationModal");
  if (modal) modal.classList.remove("show");
}

// Teacher Edit Modals
function openTeacherEdit(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add("show");
}

function closeTeacherEdit(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove("show");
}

// Global Click listener to close sidebar on small screens
document.addEventListener("click", function(e) {
  const sidebar = document.getElementById("sidebar");
  const menuBtn = document.querySelector(".menu-btn");
  if (window.innerWidth <= 850 && sidebar && !sidebar.contains(e.target) && menuBtn && !menuBtn.contains(e.target)) {
    sidebar.classList.remove("show");
  }
});

// Real-time Table Search Filter
function filterTable(inputId, tableId) {
  const input = document.getElementById(inputId);
  const table = document.getElementById(tableId);
  if (!input || !table) return;
  const filter = input.value.toLowerCase().trim();
  const rows = table.getElementsByTagName("tr");
  for (let i = 1; i < rows.length; i++) {
    const text = rows[i].textContent.toLowerCase();
    rows[i].style.display = text.indexOf(filter) > -1 ? "" : "none";
  }
}

// What-If Grade / Attendance Calculator
function calculateAttendanceWhatIf() {
  const currentPct = parseFloat(document.getElementById("currentAttendancePct")?.value || "85");
  const totalClasses = parseInt(document.getElementById("totalClassesHeld")?.value || "40", 10);
  const addClasses = parseInt(document.getElementById("additionalClassesToAttend")?.value || "0", 10);

  const currentlyAttended = Math.round((currentPct / 100) * totalClasses);
  const newAttended = currentlyAttended + addClasses;
  const newTotal = totalClasses + addClasses;

  const projectedPct = newTotal > 0 ? Math.round((newAttended / newTotal) * 100) : currentPct;
  const resultElem = document.getElementById("projectedAttendanceResult");
  if (resultElem) {
    resultElem.textContent = projectedPct + "%";
    resultElem.style.color = projectedPct >= 75 ? "var(--success)" : "var(--danger)";
  }
  
  const diffElem = document.getElementById("attendanceDelta");
  if (diffElem) {
    const diff = projectedPct - currentPct;
    diffElem.textContent = (diff >= 0 ? "+" : "") + diff + "% change";
  }
}

function calculateMarksWhatIf() {
  const currentAvg = parseFloat(document.getElementById("currentMarksAvg")?.value || "78");
  const examsDone = parseInt(document.getElementById("examsConducted")?.value || "5", 10);
  const nextExamScore = parseFloat(document.getElementById("projectedNextScore")?.value || "85");

  const totalScoreCurrent = currentAvg * examsDone;
  const newTotalScore = totalScoreCurrent + nextExamScore;
  const newAvg = Math.round((newTotalScore / (examsDone + 1)) * 10) / 10;

  const resultElem = document.getElementById("projectedMarksResult");
  if (resultElem) {
    resultElem.textContent = newAvg + " / 100";
    resultElem.style.color = newAvg >= 75 ? "var(--primary)" : "var(--text-main)";
  }

  const diffElem = document.getElementById("marksDelta");
  if (diffElem) {
    const diff = Math.round((newAvg - currentAvg) * 10) / 10;
    diffElem.textContent = (diff >= 0 ? "+" : "") + diff + " pts change";
  }
}

// Notice Live Preview Handler
function updateNoticePreview() {
  const title = document.getElementById("noticeTitleInput")?.value || "Notice Title Preview";
  const type = document.getElementById("noticeTypeInput")?.value || "General";
  const priority = document.getElementById("noticePriorityInput")?.value || "Normal";
  const message = document.getElementById("noticeMessageInput")?.value || "Detailed announcement message will appear here...";
  const date = document.getElementById("noticeDateInput")?.value || new Date().toISOString().split("T")[0];

  const prevTitle = document.getElementById("prevNoticeTitle");
  const prevType = document.getElementById("prevNoticeType");
  const prevPriority = document.getElementById("prevNoticePriority");
  const prevMsg = document.getElementById("prevNoticeMessage");
  const prevDate = document.getElementById("prevNoticeDate");

  if (prevTitle) prevTitle.textContent = title;
  if (prevType) prevType.textContent = type;
  if (prevPriority) {
    prevPriority.textContent = priority;
    prevPriority.className = "badge " + (priority === "Urgent" ? "urgent" : priority === "Important" ? "important" : "normal");
  }
  if (prevMsg) prevMsg.textContent = message;
  if (prevDate) prevDate.textContent = "Date: " + date;
}

// Quick Demo Login Helper
function fillDemo(email, pass) {
  const emailInput = document.getElementById("loginEmail");
  const passInput = document.getElementById("loginPassword");
  if (emailInput) emailInput.value = email;
  if (passInput) passInput.value = pass;
}

// Print Question Paper Function
function printQuestionPaper() {
  window.print();
}

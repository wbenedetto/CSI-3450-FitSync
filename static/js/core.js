/* ═══════════════════════════════════════════════════════
   core.js  —  App state, navigation config, auth,
               router, toast, and modal utilities.
   Depends on: db.js
   ═══════════════════════════════════════════════════════ */

'use strict';

/* ── App state ────────────────────────────────────────── */
var STATE = {
  role:               '',
  loggedInMemberId:   'M001',
  loggedInEmpId:      'E01'
};

/* ── Navigation config ────────────────────────────────── */
var NAV = {
  member: [
    { id: 'm-profile',  label: 'My Profile',      icon: '👤' },
    { id: 'm-classes',  label: 'Browse Classes',   icon: '📅' },
    { id: 'm-checkins', label: 'Check-in History', icon: '✔'  }
  ],
  employee: [
    { id: 'e-members',    label: 'Members',          icon: '👥' },
    { id: 'e-register',   label: 'Register Member',  icon: '+'  },
    { id: 'e-checkin',    label: 'Record Check-in',  icon: '📍' },
    { id: 'e-classes',    label: 'Class Schedule',   icon: '📅' },
    { id: 'e-class-new',  label: 'Create Class',     icon: '+'  },
    { id: 'e-attendance', label: 'Attendance',       icon: '✔'  },
    { id: 'e-equipment',  label: 'Equipment',        icon: '🔧' },
    { id: 'e-tickets',    label: 'Tickets',          icon: '🎫' }
  ]
};

/* ── Toast ────────────────────────────────────────────── */
function toast(msg, type) {
  var el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast show' + (type ? ' ' + type : '');
  setTimeout(function(){ el.classList.remove('show'); }, 2800);
}

/* ── Modal ────────────────────────────────────────────── */
function openModal(html) {
  document.getElementById('modal-box').innerHTML = html;
  document.getElementById('modal-overlay').classList.remove('hidden');
}
function closeModal(e) {
  if (!e || e.target === document.getElementById('modal-overlay'))
    document.getElementById('modal-overlay').classList.add('hidden');
}

/* ── Auth ─────────────────────────────────────────────── */
function login(role) {
  STATE.role = role;
  document.getElementById('login-screen').classList.add('hidden');
  document.getElementById('main-app').classList.remove('hidden');
  renderSidebar(role);
  navigate(NAV[role][0].id);
}

function logout() {
  document.getElementById('main-app').classList.add('hidden');
  document.getElementById('login-screen').classList.remove('hidden');
}

/* ── Sidebar ──────────────────────────────────────────── */
function renderSidebar(role) {
  var labels = { member: 'Member Portal', employee: 'Employee Portal' };
  document.getElementById('sidebar-role-label').textContent = labels[role];

  var html = '';
  NAV[role].forEach(function(item) {
    html += '<button class="nav-item" id="nav-' + item.id + '" onclick="navigate(\'' + item.id + '\')">'
          + '<span class="nav-icon">' + item.icon + '</span>' + item.label
          + '</button>';
  });
  document.getElementById('sidebar-nav').innerHTML = html;
}

/* ── Router ───────────────────────────────────────────── */
function navigate(view) {
  document.querySelectorAll('.nav-item').forEach(function(el){ el.classList.remove('active'); });
  var el = document.getElementById('nav-' + view);
  if (el) el.classList.add('active');

  var routes = {
    /* Member pages — defined in member.js */
    'm-profile':    pageMemberProfile,
    'm-classes':    pageMemberClasses,
    'm-checkins':   pageMemberCheckins,
    /* Employee pages — defined in employee.js */
    'e-members':    pageEmpMembers,
    'e-register':   pageEmpRegister,
    'e-checkin':    pageEmpCheckin,
    'e-classes':    pageEmpClasses,
    'e-class-new':  pageEmpClassNew,
    'e-attendance': pageEmpAttendance,
    'e-equipment':  pageEmpEquipment,
    'e-tickets':    pageEmpTickets
  };

  if (routes[view]) routes[view]();
}

/* ── Page setter (used by all page functions) ─────────── */
function setPage(title, sub, actions, body) {
  document.getElementById('page-title').textContent   = title;
  document.getElementById('page-sub').textContent     = sub     || '';
  document.getElementById('topbar-actions').innerHTML = actions || '';
  document.getElementById('page-body').innerHTML      = body;
}
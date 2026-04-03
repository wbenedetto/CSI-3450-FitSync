/* ═══════════════════════════════════════════════════════
   employee.js  —  All Employee portal page renderers
   Depends on: db.js, core.js
   Pages: Members, Register, Check-in, Classes,
          Create Class, Attendance, Equipment, Tickets
   ═══════════════════════════════════════════════════════ */

'use strict';

/* ── Members list ─────────────────────────────────────── */
function pageEmpMembers() {
  var html = '<div class="card"><div class="table-wrap"><table>'
    + '<thead><tr><th>ID</th><th>Member</th><th>Phone</th><th>DOB</th><th>Tier</th><th>ECONTACT</th><th>Actions</th></tr></thead>'
    + '<tbody>';

  DB.members.forEach(function(m) {
    var tier = tierById(m.tierId);
    var ec   = econtactById(m.econtactId);
    var tierBadge = tier.id === 2
      ? '<span class="badge badge-purple">Premium</span>'
      : '<span class="badge badge-gray">Basic</span>';

    html += '<tr>'
      + '<td style="color:var(--text3);font-size:11px">' + m.id + '</td>'
      + '<td><div class="member-row">'
      + '<div class="avatar">' + initials(m.fname, m.lname) + '</div>'
      + '<div><div class="member-name">' + m.fname + ' ' + m.lname + '</div></div>'
      + '</div></td>'
      + '<td>' + m.phone + '</td>'
      + '<td style="font-size:12px;color:var(--text2)">' + m.dob + '</td>'
      + '<td>' + tierBadge + '</td>'
      + '<td style="font-size:12px;color:var(--text2)">' + ec.fname + ' ' + ec.lname + ' / ' + ec.phone + '</td>'
      + '<td><div class="btn-row">'
      + '<button class="btn btn-sm" onclick="openEditMemberModal(\'' + m.id + '\')">Edit</button>'
      + '<button class="btn btn-danger btn-sm" onclick="promptDeleteMember(\'' + m.id + '\')">Delete</button>'
      + '</div></td>'
      + '</tr>';
  });

  html += '</tbody></table></div></div>';
  setPage('Members', DB.members.length + ' registered members',
    '<button class="btn btn-primary" onclick="navigate(\'e-register\')">+ New Member</button>',
    html);
}

function openEditMemberModal(memId) {
  var m  = memberById(memId);
  var ec = econtactById(m.econtactId);
  openModal(
    '<div class="modal-title">Edit Member — ' + m.fname + ' ' + m.lname + '</div>'
    + '<div class="form-section-title">Member Info</div>'
    + '<div class="form-group"><label class="form-label">First Name</label>'
    + '<input class="form-control" id="em-fname" value="' + m.fname + '"></div>'
    + '<div class="form-group"><label class="form-label">Last Name</label>'
    + '<input class="form-control" id="em-lname" value="' + m.lname + '"></div>'
    + '<div class="form-group"><label class="form-label">Phone</label>'
    + '<input class="form-control" id="em-phone" value="' + m.phone + '"></div>'
    + '<div class="form-group"><label class="form-label">Membership Tier</label>'
    + '<select class="form-control" id="em-tier">'
    + DB.tiers.map(function(t){
        return '<option value="' + t.id + '"' + (t.id === m.tierId ? ' selected' : '') + '>' + t.name + '</option>';
      }).join('')
    + '</select></div>'
    + '<div class="form-divider"></div>'
    + '<div class="form-section-title">ECONTACT</div>'
    + '<div class="form-group"><label class="form-label">First Name</label>'
    + '<input class="form-control" id="em-ec-fname" value="' + ec.fname + '"></div>'
    + '<div class="form-group"><label class="form-label">Last Name</label>'
    + '<input class="form-control" id="em-ec-lname" value="' + ec.lname + '"></div>'
    + '<div class="form-group"><label class="form-label">Phone</label>'
    + '<input class="form-control" id="em-ec-phone" value="' + ec.phone + '"></div>'
    + '<div class="modal-footer">'
    + '<button class="btn btn-ghost" onclick="closeModal()">Cancel</button>'
    + '<button class="btn btn-primary" onclick="saveEditMember(\'' + memId + '\')">Save</button>'
    + '</div>'
  );
}

function saveEditMember(memId) {
  var m  = memberById(memId);
  var ec = econtactById(m.econtactId);
  m.fname    = document.getElementById('em-fname').value.trim()    || m.fname;
  m.lname    = document.getElementById('em-lname').value.trim()    || m.lname;
  m.phone    = document.getElementById('em-phone').value.trim()    || m.phone;
  m.tierId   = parseInt(document.getElementById('em-tier').value);
  ec.fname   = document.getElementById('em-ec-fname').value.trim() || ec.fname;
  ec.lname   = document.getElementById('em-ec-lname').value.trim() || ec.lname;
  ec.phone   = document.getElementById('em-ec-phone').value.trim() || ec.phone;
  closeModal();
  toast('Member updated!');
  pageEmpMembers();
}

function promptDeleteMember(memId) {
  var m = memberById(memId);
  openModal(
    '<div class="modal-title">Delete Member</div>'
    + '<p style="font-size:13px;color:var(--text2);margin-bottom:1rem">Permanently delete <strong>'
    + m.fname + ' ' + m.lname + '</strong>? Their registrations and check-ins will also be removed.</p>'
    + '<div class="modal-footer">'
    + '<button class="btn btn-ghost" onclick="closeModal()">Cancel</button>'
    + '<button class="btn btn-danger" onclick="confirmDeleteMember(\'' + memId + '\')">Delete</button>'
    + '</div>'
  );
}

function confirmDeleteMember(memId) {
  DB.members       = DB.members.filter(function(m){ return m.id !== memId; });
  DB.registrations = DB.registrations.filter(function(r){ return r.memId !== memId; });
  DB.checkins      = DB.checkins.filter(function(c){ return c.memId !== memId; });
  closeModal();
  toast('Member account deleted.');
  pageEmpMembers();
}

/* ── Register New Member ──────────────────────────────── */
function pageEmpRegister() {
  var html = '<div class="card" style="max-width:560px">'
    + '<div class="form-section-title">Member Information</div>'
    + '<div class="form-row">'
    + '<div class="form-group"><label class="form-label">First Name *</label>'
    + '<input class="form-control" id="rg-fname" placeholder="First name"></div>'
    + '<div class="form-group"><label class="form-label">Last Name *</label>'
    + '<input class="form-control" id="rg-lname" placeholder="Last name"></div>'
    + '</div>'
    + '<div class="form-row">'
    + '<div class="form-group"><label class="form-label">Date of Birth *</label>'
    + '<input class="form-control" id="rg-dob" type="date"></div>'
    + '<div class="form-group"><label class="form-label">Phone *</label>'
    + '<input class="form-control" id="rg-phone" placeholder="10-digit number"></div>'
    + '</div>'
    + '<div class="form-group"><label class="form-label">Membership Tier *</label>'
    + '<select class="form-control" id="rg-tier">'
    + DB.tiers.map(function(t){ return '<option value="' + t.id + '">' + t.name + ' — ' + fmtCost(t.cost) + '/mo</option>'; }).join('')
    + '</select></div>'
    + '<div class="form-divider"></div>'
    + '<div class="form-section-title">Emergency Contact (ECONTACT)</div>'
    + '<div class="form-row">'
    + '<div class="form-group"><label class="form-label">First Name *</label>'
    + '<input class="form-control" id="rg-ec-fname" placeholder="First name"></div>'
    + '<div class="form-group"><label class="form-label">Last Name *</label>'
    + '<input class="form-control" id="rg-ec-lname" placeholder="Last name"></div>'
    + '</div>'
    + '<div class="form-group"><label class="form-label">Phone *</label>'
    + '<input class="form-control" id="rg-ec-phone" placeholder="Emergency phone"></div>'
    + '<div class="btn-row" style="margin-top:1.25rem">'
    + '<button class="btn btn-primary" onclick="submitRegister()">Create Account</button>'
    + '<button class="btn btn-ghost" onclick="navigate(\'e-members\')">Cancel</button>'
    + '</div></div>';

  setPage('Register Member', 'Create a new member account', '', html);
}

function submitRegister() {
  var fname  = document.getElementById('rg-fname').value.trim();
  var lname  = document.getElementById('rg-lname').value.trim();
  var dob    = document.getElementById('rg-dob').value;
  var phone  = document.getElementById('rg-phone').value.trim();
  var tierId = parseInt(document.getElementById('rg-tier').value);
  var ecf    = document.getElementById('rg-ec-fname').value.trim();
  var ecl    = document.getElementById('rg-ec-lname').value.trim();
  var ecp    = document.getElementById('rg-ec-phone').value.trim();

  if (!fname || !lname || !dob || !phone || !ecf || !ecl || !ecp) {
    toast('Please fill in all required fields.', 'error'); return;
  }
  var ecId = DB._nextEcontactId++;
  DB.econtacts.push({ id: ecId, fname: ecf, lname: ecl, phone: ecp });

  var memId = 'M' + pad(DB._nextMemberId++);
  DB.members.push({ id: memId, fname: fname, lname: lname, dob: dob, phone: phone, tierId: tierId, econtactId: ecId });

  toast('Member ' + fname + ' ' + lname + ' registered! (ID: ' + memId + ')');
  navigate('e-members');
}

/* ── Record Check-in ──────────────────────────────────── */
function pageEmpCheckin() {
  var today     = new Date().toISOString().split('T')[0];
  var todayList = DB.checkins.filter(function(c){ return c.date === today; });

  var html = '<div class="form-row" style="align-items:start">'
    + '<div class="card" style="margin-bottom:0"><div class="card-header">Record Check-in (CHECKIN)</div>'
    + '<div class="form-group"><label class="form-label">Member *</label>'
    + '<select class="form-control" id="ck-mem">'
    + DB.members.map(function(m){ return '<option value="' + m.id + '">' + m.fname + ' ' + m.lname + ' (' + m.id + ')</option>'; }).join('')
    + '</select></div>'
    + '<div class="form-group"><label class="form-label">Guest Brought?</label>'
    + '<select class="form-control" id="ck-guest">'
    + '<option value="0">No guest</option><option value="1">1 guest</option>'
    + '</select></div>'
    + '<div class="form-hint" style="margin-bottom:0.75rem">Date &amp; time set to now automatically.</div>'
    + '<button class="btn btn-primary" onclick="recordCheckin()">Check In</button>'
    + '</div>'
    + '<div class="metric" style="margin-bottom:0">'
    + '<div class="metric-label">Today\'s Check-ins</div>'
    + '<div class="metric-value green">' + todayList.length + '</div>'
    + '</div></div>'
    + '<div class="card" style="margin-top:1.25rem"><div class="card-header">All Check-ins</div>'
    + '<div class="table-wrap"><table>'
    + '<thead><tr><th>ID</th><th>Member</th><th>Date</th><th>Time</th><th>Guest</th></tr></thead>'
    + '<tbody>';

  DB.checkins.slice().reverse().forEach(function(c) {
    var mem = memberById(c.memId);
    if (!mem) return;
    html += '<tr>'
      + '<td style="color:var(--text3);font-size:11px">' + c.id + '</td>'
      + '<td><div class="member-row"><div class="avatar">' + initials(mem.fname, mem.lname) + '</div>'
      + mem.fname + ' ' + mem.lname + '</div></td>'
      + '<td>' + c.date + '</td>'
      + '<td>' + fmtTime(c.time) + '</td>'
      + '<td><span class="badge ' + (c.guest ? 'badge-blue' : 'badge-gray') + '">' + (c.guest ? 'Yes' : 'No') + '</span></td>'
      + '</tr>';
  });

  html += '</tbody></table></div></div>';
  setPage('Record Check-in', 'Log member arrivals', '', html);
}

function recordCheckin() {
  var memId = document.getElementById('ck-mem').value;
  var guest = parseInt(document.getElementById('ck-guest').value);
  var now   = new Date();
  var ckId  = 'CK' + pad(DB._nextCheckinId++);
  DB.checkins.push({
    id: ckId, memId: memId,
    date: now.toISOString().split('T')[0],
    time: now.toTimeString().slice(0, 5),
    guest: guest
  });
  var mem = memberById(memId);
  toast(mem.fname + ' ' + mem.lname + ' checked in!');
  pageEmpCheckin();
}

/* ── Class Schedule ───────────────────────────────────── */
function pageEmpClasses() {
  var html = '<div class="card"><div class="table-wrap"><table>'
    + '<thead><tr><th>ID</th><th>Class Name</th><th>Instructor (Employee)</th>'
    + '<th>Date / Time</th><th>Duration</th><th>Enrolled</th><th>Fill</th><th>Actions</th></tr></thead>'
    + '<tbody>';

  DB.classes.forEach(function(c) {
    var emp      = employeeById(c.empId);
    var enrolled = classEnrolled(c.id);
    var pct      = Math.round(enrolled / c.cap * 100);
    var barCls   = pct >= 100 ? 'red' : pct >= 70 ? 'amber' : '';

    html += '<tr>'
      + '<td style="color:var(--text3);font-size:11px">' + c.id + '</td>'
      + '<td><strong>' + c.name + '</strong></td>'
      + '<td>' + emp.fname + ' ' + emp.lname + '</td>'
      + '<td>' + fmtDate(c.start)
      + '<br><span style="font-size:11px;color:var(--text2)">' + c.start.split(' ')[1] + '</span></td>'
      + '<td>' + c.length + ' min</td>'
      + '<td>' + enrolled + ' / ' + c.cap + '</td>'
      + '<td style="min-width:80px"><div class="progress">'
      + '<div class="progress-bar ' + barCls + '" style="width:' + pct + '%"></div></div></td>'
      + '<td><div class="btn-row">'
      + '<button class="btn btn-sm" onclick="openEditClassModal(\'' + c.id + '\')">Edit</button>'
      + '<button class="btn btn-danger btn-sm" onclick="deleteClass(\'' + c.id + '\')">Delete</button>'
      + '</div></td></tr>';
  });

  html += '</tbody></table></div></div>';
  setPage('Class Schedule', 'All scheduled classes',
    '<button class="btn btn-primary" onclick="navigate(\'e-class-new\')">+ New Class</button>',
    html);
}

function openEditClassModal(classId) {
  var c = DB.classes.find(function(x){ return x.id === classId; });
  openModal(
    '<div class="modal-title">Edit Class — ' + c.name + '</div>'
    + '<div class="form-group"><label class="form-label">Class Name</label>'
    + '<input class="form-control" id="ec-name" value="' + c.name + '"></div>'
    + '<div class="form-row">'
    + '<div class="form-group"><label class="form-label">Start Date &amp; Time</label>'
    + '<input class="form-control" id="ec-start" type="datetime-local" value="' + c.start.replace(' ', 'T') + '"></div>'
    + '<div class="form-group"><label class="form-label">Duration (min)</label>'
    + '<input class="form-control" id="ec-len" type="number" min="15" max="120" value="' + c.length + '"></div>'
    + '</div>'
    + '<div class="form-group"><label class="form-label">Instructor (Employee)</label>'
    + '<select class="form-control" id="ec-emp">'
    + DB.employees.map(function(e) {
        var teaching = employeeLeadsClass(e.id);
        var taken    = teaching && teaching.id !== classId;
        return '<option value="' + e.id + '"'
             + (e.id === c.empId ? ' selected' : '')
             + (taken ? ' disabled' : '') + '>'
             + e.fname + ' ' + e.lname
             + (taken ? ' (leads another class)' : '') + '</option>';
      }).join('')
    + '</select>'
    + '<div class="form-hint">An employee may lead at most one class.</div></div>'
    + '<div class="modal-footer">'
    + '<button class="btn btn-ghost" onclick="closeModal()">Cancel</button>'
    + '<button class="btn btn-primary" onclick="saveEditClass(\'' + classId + '\')">Save</button>'
    + '</div>'
  );
}

function saveEditClass(classId) {
  var c    = DB.classes.find(function(x){ return x.id === classId; });
  c.name   = document.getElementById('ec-name').value.trim()             || c.name;
  c.start  = document.getElementById('ec-start').value.replace('T', ' ') || c.start;
  c.length = parseInt(document.getElementById('ec-len').value)            || c.length;
  c.empId  = document.getElementById('ec-emp').value;
  closeModal();
  toast('Class updated!');
  pageEmpClasses();
}

function deleteClass(classId) {
  var enrolled = classEnrolled(classId);
  if (enrolled > 0) {
    toast('Cannot delete: ' + enrolled + ' member(s) enrolled.', 'error'); return;
  }
  var cls    = DB.classes.find(function(c){ return c.id === classId; });
  DB.classes = DB.classes.filter(function(c){ return c.id !== classId; });
  toast('Class "' + cls.name + '" deleted.');
  pageEmpClasses();
}

/* ── Create Class ─────────────────────────────────────── */
function pageEmpClassNew() {
  var available = DB.employees.filter(function(e){ return !employeeLeadsClass(e.id); });

  var html = '<div class="card" style="max-width:520px">'
    + '<div class="form-group"><label class="form-label">Class Name *</label>'
    + '<input class="form-control" id="nc-name" placeholder="e.g. Morning Yoga"></div>'
    + '<div class="form-row">'
    + '<div class="form-group"><label class="form-label">Start Date &amp; Time *</label>'
    + '<input class="form-control" id="nc-start" type="datetime-local"></div>'
    + '<div class="form-group"><label class="form-label">Duration (minutes) *</label>'
    + '<input class="form-control" id="nc-len" type="number" placeholder="45" min="15" max="120"></div>'
    + '</div>'
    + '<div class="form-group"><label class="form-label">Capacity</label>'
    + '<input class="form-control" id="nc-cap" type="number" value="10" min="1" max="10">'
    + '<div class="form-hint">Maximum capacity is 10 (system constraint).</div></div>'
    + '<div class="form-group"><label class="form-label">Assigned Instructor (Employee) *</label>'
    + '<select class="form-control" id="nc-emp">'
    + (available.length === 0
        ? '<option value="">No available employees</option>'
        : available.map(function(e){
            return '<option value="' + e.id + '">' + e.fname + ' ' + e.lname + ' (' + e.id + ')</option>';
          }).join(''))
    + '</select>'
    + '<div class="form-hint">Only employees not already leading a class are listed.</div></div>'
    + '<div class="alert alert-info">&#8505; Only Premium members may register for classes.</div>'
    + '<div class="btn-row" style="margin-top:1rem">'
    + '<button class="btn btn-primary" onclick="submitCreateClass()">Create Class</button>'
    + '<button class="btn btn-ghost" onclick="navigate(\'e-classes\')">Cancel</button>'
    + '</div></div>';

  setPage('Create Class', 'Add a new class', '', html);
}

function submitCreateClass() {
  var name  = document.getElementById('nc-name').value.trim();
  var start = document.getElementById('nc-start').value.replace('T', ' ');
  var len   = parseInt(document.getElementById('nc-len').value);
  var cap   = Math.min(10, parseInt(document.getElementById('nc-cap').value) || 10);
  var empId = document.getElementById('nc-emp').value;

  if (!name || !start || !len || !empId) {
    toast('Please fill in all required fields.', 'error'); return;
  }
  if (employeeLeadsClass(empId)) {
    toast('That employee already leads a class.', 'error'); return;
  }
  var classId = 'C' + pad(DB._nextClassId++);
  DB.classes.push({ id: classId, name: name, start: start, length: len, cap: cap, empId: empId });
  toast('Class "' + name + '" created! (' + classId + ')');
  navigate('e-classes');
}

/* ── Attendance ───────────────────────────────────────── */
function pageEmpAttendance() {
  var html = '';

  if (DB.classes.length === 0) {
    html = '<div class="card"><div class="empty-state">No classes scheduled.</div></div>';
  } else {
    DB.classes.forEach(function(c) {
      var emp  = employeeById(c.empId);
      var regs = DB.registrations.filter(function(r){ return r.classId === c.id; });

      html += '<div class="card">'
        + '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem">'
        + '<div><div class="card-title">' + c.name + '</div>'
        + '<div style="font-size:12px;color:var(--text2)">'
        + fmtDate(c.start) + ' &nbsp;·&nbsp; ' + c.length + ' min'
        + ' &nbsp;·&nbsp; Instructor: ' + emp.fname + ' ' + emp.lname
        + '</div></div>'
        + '<div class="btn-row">'
        + '<span class="badge badge-blue">' + regs.length + ' / ' + c.cap + '</span>'
        + '<button class="btn btn-sm btn-primary" onclick="openRegisterMemberForClass(\'' + c.id + '\')">+ Add Member</button>'
        + '</div></div>';

      if (regs.length === 0) {
        html += '<div class="empty-state" style="padding:1rem">No members registered.</div>';
      } else {
        regs.forEach(function(r) {
          var mem = memberById(r.memId);
          if (!mem) return;
          html += '<div class="attendance-item">'
            + '<div class="member-row"><div class="avatar">' + initials(mem.fname, mem.lname) + '</div>'
            + '<div><div class="member-name">' + mem.fname + ' ' + mem.lname + '</div>'
            + '<div class="member-id">' + mem.id + ' &nbsp;·&nbsp; Reg #' + r.regNum + '</div>'
            + '</div></div>'
            + '<button class="btn btn-danger btn-xs" onclick="empRemoveFromClass(\'' + c.id + '\',\'' + r.memId + '\')">Remove</button>'
            + '</div>';
        });
      }
      html += '</div>';
    });
  }
  setPage('Attendance', 'Manage class registrations', '', html);
}

function openRegisterMemberForClass(classId) {
  var cls      = DB.classes.find(function(c){ return c.id === classId; });
  var enrolled = classEnrolled(classId);
  if (enrolled >= cls.cap) { toast('Class is full.', 'error'); return; }

  var eligible = DB.members.filter(function(m){
    return m.tierId === 2 && !alreadyRegistered(classId, m.id);
  });
  if (eligible.length === 0) { toast('No eligible Premium members available.', 'error'); return; }

  openModal(
    '<div class="modal-title">Register Member for ' + cls.name + '</div>'
    + '<div class="form-group"><label class="form-label">Premium Member</label>'
    + '<select class="form-control" id="reg-mem-sel">'
    + eligible.map(function(m){ return '<option value="' + m.id + '">' + m.fname + ' ' + m.lname + '</option>'; }).join('')
    + '</select></div>'
    + '<div class="modal-footer">'
    + '<button class="btn btn-ghost" onclick="closeModal()">Cancel</button>'
    + '<button class="btn btn-primary" onclick="empAddToClass(\'' + classId + '\')">Register</button>'
    + '</div>'
  );
}

function empAddToClass(classId) {
  var memId = document.getElementById('reg-mem-sel').value;
  var cls   = DB.classes.find(function(c){ return c.id === classId; });
  DB.registrations.push({ classId: classId, memId: memId, regNum: classEnrolled(classId) + 1 });
  closeModal();
  var mem = memberById(memId);
  toast(mem.fname + ' ' + mem.lname + ' registered for ' + cls.name + '!');
  pageEmpAttendance();
}

function empRemoveFromClass(classId, memId) {
  DB.registrations = DB.registrations.filter(function(r){
    return !(r.classId === classId && r.memId === memId);
  });
  var mem = memberById(memId);
  toast((mem ? mem.fname + ' ' + mem.lname : 'Member') + ' removed.');
  pageEmpAttendance();
}

/* ── Equipment ────────────────────────────────────────── */
function pageEmpEquipment() {
  var op    = DB.equipment.filter(function(e){ return e.status === 'Operational'; }).length;
  var nonop = DB.equipment.filter(function(e){ return e.status !== 'Operational'; }).length;

  var html = '<div class="metric-grid metric-grid-3">'
    + '<div class="metric"><div class="metric-label">Total Equipment</div>'
    + '<div class="metric-value">' + DB.equipment.length + '</div></div>'
    + '<div class="metric"><div class="metric-label">Operational</div>'
    + '<div class="metric-value green">' + op + '</div></div>'
    + '<div class="metric"><div class="metric-label">Non-operational</div>'
    + '<div class="metric-value red">' + nonop + '</div></div>'
    + '</div>'
    + '<div class="card"><div class="table-wrap"><table>'
    + '<thead><tr><th>ID</th><th>Equipment</th><th>Status</th><th>Action</th></tr></thead>'
    + '<tbody>';

  DB.equipment.forEach(function(e) {
    var ok    = e.status === 'Operational';
    var badge = ok
      ? '<span class="badge badge-green"><span class="dot dot-green"></span>Operational</span>'
      : '<span class="badge badge-red"><span class="dot dot-red"></span>Non-operational</span>';
    var btn = ok
      ? '<button class="btn btn-danger btn-sm" onclick="markNonOp(\'' + e.id + '\')">Mark Broken</button>'
      : '<button class="btn btn-sm" onclick="openNewTicketModal(\'' + e.id + '\')">Create Ticket</button>';

    html += '<tr>'
      + '<td style="color:var(--text3);font-size:11px">' + e.id + '</td>'
      + '<td>' + e.name + '</td>'
      + '<td>' + badge + '</td>'
      + '<td>' + btn + '</td>'
      + '</tr>';
  });

  html += '</tbody></table></div></div>';
  setPage('Equipment', 'Gym equipment status', '', html);
}

function markNonOp(equipId) {
  var e    = equipById(equipId);
  e.status = 'Non-operational';
  toast(e.name + ' marked non-operational.', 'error');
  pageEmpEquipment();
}

function openNewTicketModal(equipId) {
  var e = equipById(equipId);
  openModal(
    '<div class="modal-title">New Maintenance Ticket</div>'
    + '<div class="form-group"><label class="form-label">Equipment</label>'
    + '<input class="form-control" value="' + e.name + '" readonly></div>'
    + '<div class="form-group"><label class="form-label">Filed By (Employee)</label>'
    + '<select class="form-control" id="tk-emp">'
    + DB.employees.map(function(emp){
        return '<option value="' + emp.id + '"' + (emp.id === STATE.loggedInEmpId ? ' selected' : '') + '>'
             + emp.fname + ' ' + emp.lname + '</option>';
      }).join('')
    + '</select></div>'
    + '<div class="form-group"><label class="form-label">Description *</label>'
    + '<textarea class="form-control" id="tk-desc" placeholder="Describe the issue..."></textarea></div>'
    + '<div class="modal-footer">'
    + '<button class="btn btn-ghost" onclick="closeModal()">Cancel</button>'
    + '<button class="btn btn-primary" onclick="submitTicket(\'' + equipId + '\')">Submit Ticket</button>'
    + '</div>'
  );
}

function submitTicket(equipId) {
  var desc  = document.getElementById('tk-desc').value.trim();
  var empId = document.getElementById('tk-emp').value;
  if (!desc) { toast('Please describe the issue.', 'error'); return; }
  var tkId  = 'TK' + pad(DB._nextTicketId++);
  DB.tickets.push({
    id: tkId, equipId: equipId,
    date: new Date().toISOString().split('T')[0],
    desc: desc, empId: empId, resolved: false
  });
  closeModal();
  toast('Ticket ' + tkId + ' submitted!');
}

/* ── Tickets ──────────────────────────────────────────── */
function pageEmpTickets() {
  var open     = DB.tickets.filter(function(t){ return !t.resolved; });
  var resolved = DB.tickets.filter(function(t){ return t.resolved; });

  var html = '<div class="metric-grid metric-grid-2">'
    + '<div class="metric"><div class="metric-label">Open Tickets</div>'
    + '<div class="metric-value red">' + open.length + '</div></div>'
    + '<div class="metric"><div class="metric-label">Resolved</div>'
    + '<div class="metric-value green">' + resolved.length + '</div></div>'
    + '</div>'
    + '<div class="card"><div class="card-header">Open Tickets</div>';

  if (open.length === 0) {
    html += '<div class="empty-state">No open tickets — all equipment operational!</div>';
  } else {
    open.forEach(function(t) {
      var eq  = equipById(t.equipId);
      var emp = employeeById(t.empId);
      html += '<div class="ticket-card"><div class="ticket-dot"></div>'
        + '<div style="flex:1">'
        + '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">'
        + '<strong style="font-size:13px">' + eq.name + '</strong>'
        + '<span style="font-size:11px;color:var(--text3)">' + t.id + ' &nbsp;·&nbsp; ' + t.date + '</span></div>'
        + '<div style="font-size:12px;color:var(--text2);margin-bottom:4px">' + t.desc + '</div>'
        + '<div style="font-size:11px;color:var(--text3);margin-bottom:8px">Filed by: ' + emp.fname + ' ' + emp.lname + '</div>'
        + '<button class="btn btn-primary btn-sm" onclick="resolveTicket(\'' + t.id + '\')">Mark Resolved</button>'
        + '</div></div>';
    });
  }
  html += '</div>';

  if (resolved.length > 0) {
    html += '<div class="card"><div class="card-header">Resolved Tickets</div>';
    resolved.forEach(function(t) {
      var eq  = equipById(t.equipId);
      var emp = employeeById(t.empId);
      html += '<div class="ticket-card"><div class="ticket-dot resolved"></div>'
        + '<div style="flex:1">'
        + '<div style="display:flex;align-items:center;justify-content:space-between">'
        + '<strong style="font-size:13px">' + eq.name + '</strong>'
        + '<span style="font-size:11px;color:var(--text3)">' + t.id + ' &nbsp;·&nbsp; ' + t.date + '</span></div>'
        + '<div style="font-size:12px;color:var(--text3);margin-top:3px">' + t.desc + '</div>'
        + '<div style="font-size:11px;color:var(--text3);margin-top:2px">Filed by: ' + emp.fname + ' ' + emp.lname + '</div>'
        + '</div></div>';
    });
    html += '</div>';
  }

  setPage('Maintenance Tickets', 'EMPLOYEE Files TICKET — EQUIPMENT Assigned to TICKET', '', html);
}

function resolveTicket(ticketId) {
  var tk      = DB.tickets.find(function(t){ return t.id === ticketId; });
  tk.resolved = true;
  var eq      = equipById(tk.equipId);
  eq.status   = 'Operational';
  toast('Ticket resolved — ' + eq.name + ' is now operational!');
  pageEmpTickets();
}
/* ═══════════════════════════════════════════════════════
   member.js  —  All Member portal page renderers
   Depends on: db.js, core.js
   Pages: My Profile, Browse Classes, Check-in History
   ═══════════════════════════════════════════════════════ */

'use strict';

/* ── My Profile ───────────────────────────────────────── */
function pageMemberProfile() {
  var mem  = memberById(STATE.loggedInMemberId);
  var tier = tierById(mem.tierId);
  var ec   = econtactById(mem.econtactId);
  var tierBadge = tier.id === 2
    ? '<span class="badge badge-purple">Premium</span>'
    : '<span class="badge badge-gray">Basic</span>';

  var html =
    '<div class="profile-header">'
    + '<div class="avatar avatar-lg">' + initials(mem.fname, mem.lname) + '</div>'
    + '<div>'
    + '<div class="profile-name">' + mem.fname + ' ' + mem.lname + '</div>'
    + '<div class="profile-detail">' + tierBadge + ' &nbsp; ID: ' + mem.id + '</div>'
    + '</div></div>'

    + '<div class="form-row">'

    /* Left col — personal info */
    + '<div class="card"><div class="card-header">Personal Information</div>'
    + '<div class="form-group"><label class="form-label">First Name</label>'
    + '<input class="form-control" id="pf-fname" value="' + mem.fname + '"></div>'
    + '<div class="form-group"><label class="form-label">Last Name</label>'
    + '<input class="form-control" id="pf-lname" value="' + mem.lname + '"></div>'
    + '<div class="form-group"><label class="form-label">Date of Birth</label>'
    + '<input class="form-control" id="pf-dob" type="date" value="' + mem.dob + '"></div>'
    + '<div class="form-group"><label class="form-label">Phone</label>'
    + '<input class="form-control" id="pf-phone" value="' + mem.phone + '"></div>'
    + '<button class="btn btn-primary btn-sm" onclick="saveMemberProfile()">Save Changes</button>'
    + '</div>'

    /* Right col */
    + '<div>'

    /* ECONTACT */
    + '<div class="card"><div class="card-header">Emergency Contact (ECONTACT)</div>'
    + '<div class="form-group"><label class="form-label">First Name</label>'
    + '<input class="form-control" id="ec-fname" value="' + ec.fname + '"></div>'
    + '<div class="form-group"><label class="form-label">Last Name</label>'
    + '<input class="form-control" id="ec-lname" value="' + ec.lname + '"></div>'
    + '<div class="form-group"><label class="form-label">Phone</label>'
    + '<input class="form-control" id="ec-phone" value="' + ec.phone + '"></div>'
    + '<button class="btn btn-primary btn-sm" onclick="saveEcontact()">Save Contact</button>'
    + '</div>'

    /* Tier */
    + '<div class="card"><div class="card-header">Membership Tier</div>'
    + '<div style="font-size:15px;font-weight:700;margin:0 0 4px">'
    + tier.name + ' — ' + fmtCost(tier.cost) + '/mo</div>'
    + '<div class="form-hint" style="margin-bottom:0.75rem">Billing renews monthly.</div>'
    + '<div class="form-group"><label class="form-label">Change Tier</label>'
    + '<select class="form-control" id="tier-sel">'
    + DB.tiers.map(function(t){
        return '<option value="' + t.id + '"' + (t.id === tier.id ? ' selected' : '') + '>'
             + t.name + ' — ' + fmtCost(t.cost) + '/mo</option>';
      }).join('')
    + '</select></div>'
    + '<div class="alert alert-info">&#8505; Only Premium members may enroll in classes.</div>'
    + '<button class="btn btn-primary btn-sm" onclick="changeTier()">Update Tier</button>'
    + '</div>'

    + '</div></div>'; /* end right col / form-row */

  setPage('My Profile', 'Manage your account', '', html);
}

function saveMemberProfile() {
  var mem   = memberById(STATE.loggedInMemberId);
  mem.fname = document.getElementById('pf-fname').value.trim() || mem.fname;
  mem.lname = document.getElementById('pf-lname').value.trim() || mem.lname;
  mem.dob   = document.getElementById('pf-dob').value          || mem.dob;
  mem.phone = document.getElementById('pf-phone').value.trim() || mem.phone;
  toast('Profile updated!');
}

function saveEcontact() {
  var mem  = memberById(STATE.loggedInMemberId);
  var ec   = econtactById(mem.econtactId);
  ec.fname = document.getElementById('ec-fname').value.trim() || ec.fname;
  ec.lname = document.getElementById('ec-lname').value.trim() || ec.lname;
  ec.phone = document.getElementById('ec-phone').value.trim() || ec.phone;
  toast('Emergency contact saved!');
}

function changeTier() {
  var mem    = memberById(STATE.loggedInMemberId);
  mem.tierId = parseInt(document.getElementById('tier-sel').value);
  toast('Membership tier updated!');
  pageMemberProfile();
}

/* ── Browse Classes ───────────────────────────────────── */
function pageMemberClasses() {
  var mem       = memberById(STATE.loggedInMemberId);
  var isPremium = mem.tierId === 2;
  var html      = '';

  if (!isPremium) {
    html += '<div class="alert alert-warn">&#9888; Upgrade to Premium to register for classes.</div>';
  }

  html += '<div class="class-grid">';

  DB.classes.forEach(function(c) {
    var emp     = employeeById(c.empId);
    var enrolled= classEnrolled(c.id);
    var spots   = c.cap - enrolled;
    var inClass = isPremium && alreadyRegistered(c.id, STATE.loggedInMemberId);
    var pct     = Math.round(enrolled / c.cap * 100);
    var barCls  = pct >= 100 ? 'red' : pct >= 70 ? 'amber' : '';

    var spotBadge = spots <= 0 ? '<span class="badge badge-red">Full</span>'
                  : spots <= 2 ? '<span class="badge badge-amber">' + spots + ' left</span>'
                  : '<span class="badge badge-green">' + spots + ' open</span>';

    var btn;
    if (inClass) {
      btn = '<button class="btn btn-danger btn-sm" onclick="memberDropClass(\'' + c.id + '\')">Drop Class</button>';
    } else if (!isPremium || spots <= 0) {
      btn = '<button class="btn btn-sm" disabled style="opacity:0.4;cursor:not-allowed">'
          + (spots <= 0 ? 'Full' : 'Premium Only') + '</button>';
    } else {
      btn = '<button class="btn btn-primary btn-sm" onclick="memberRegisterClass(\'' + c.id + '\')">Register</button>';
    }

    html += '<div class="class-card">'
      + '<div style="display:flex;align-items:flex-start;justify-content:space-between">'
      + '<div class="class-card-name">' + c.name + '</div>'
      + (inClass ? '<span class="badge badge-green">Enrolled</span>' : spotBadge)
      + '</div>'
      + '<div class="class-card-emp">Instructor: ' + emp.fname + ' ' + emp.lname + '</div>'
      + '<div class="class-card-meta">'
      + '<span>🕐 ' + fmtDate(c.start) + '</span>'
      + '<span>⏱ ' + c.length + ' min</span>'
      + '<span>👤 ' + enrolled + '/' + c.cap + '</span>'
      + '</div>'
      + '<div class="progress"><div class="progress-bar ' + barCls + '" style="width:' + pct + '%"></div></div>'
      + '<div class="class-card-footer">' + btn + '</div>'
      + '</div>';
  });

  html += '</div>';
  setPage('Browse Classes', 'Available classes — Premium members only', '', html);
}

function memberRegisterClass(classId) {
  var mem = memberById(STATE.loggedInMemberId);
  if (mem.tierId !== 2) { toast('Premium membership required.', 'error'); return; }
  var cls = DB.classes.find(function(c){ return c.id === classId; });
  if (classEnrolled(classId) >= cls.cap) { toast('Class is full.', 'error'); return; }
  if (alreadyRegistered(classId, mem.id)) { toast('Already registered.', 'error'); return; }
  DB.registrations.push({ classId: classId, memId: mem.id, regNum: classEnrolled(classId) + 1 });
  toast('Registered for ' + cls.name + '!');
  pageMemberClasses();
}

function memberDropClass(classId) {
  var cls = DB.classes.find(function(c){ return c.id === classId; });
  DB.registrations = DB.registrations.filter(function(r){
    return !(r.classId === classId && r.memId === STATE.loggedInMemberId);
  });
  toast('Dropped from ' + cls.name);
  pageMemberClasses();
}

/* ── Check-in History ─────────────────────────────────── */
function pageMemberCheckins() {
  var mine = DB.checkins.filter(function(c){ return c.memId === STATE.loggedInMemberId; });

  var html = '<div class="card"><div class="card-header">Check-in History (' + mine.length + ' visits)</div>';

  if (mine.length === 0) {
    html += '<div class="empty-state">No check-ins recorded yet.</div>';
  } else {
    mine.slice().reverse().forEach(function(c){
      html += '<div class="checkin-row">'
        + '<div>'
        + '<div style="font-size:13px;font-weight:600">' + c.date + '</div>'
        + '<div style="font-size:12px;color:var(--text2)">' + fmtTime(c.time) + '</div>'
        + '</div>'
        + '<span class="badge ' + (c.guest ? 'badge-blue' : 'badge-gray') + '">'
        + (c.guest ? '+ 1 guest' : 'No guest') + '</span>'
        + '</div>';
    });
  }

  html += '</div>';
  setPage('Check-in History', 'Your gym visit log', '', html);
}
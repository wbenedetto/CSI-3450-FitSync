/* ═══════════════════════════════════════════════════════
   db.js  —  In-memory database & helper functions
   Mirrors Phase 3 ERD entities exactly:
   TIER, MEMBER, ECONTACT, CHECKIN,
   CLASS, REGISTRATION, EMPLOYEE, EQUIPMENT, TICKET
   ═══════════════════════════════════════════════════════ */

'use strict';

var DB = {

  /* TIER — Tier_ID, Tier_Name, Tier_Cost (cents) */
  tiers: [
    { id: 1, name: 'Basic',   cost: 1999 },
    { id: 2, name: 'Premium', cost: 4999 }
  ],

  /* ECONTACT — Emer_ID, Emer_FName, Emer_LName, Emer_Phone
     1:1 with MEMBER (each contact belongs to exactly one member) */
  econtacts: [
    { id: 1, fname: 'Sarah',  lname: 'Blake',  phone: '5559876543' },
    { id: 2, fname: 'Miguel', lname: 'Cruz',   phone: '5558765432' },
    { id: 3, fname: 'Carmen', lname: 'Rivera', phone: '5557654321' },
    { id: 4, fname: 'Ji',     lname: 'Park',   phone: '5556543210' },
    { id: 5, fname: 'David',  lname: 'Lee',    phone: '5555432109' }
  ],

  /* MEMBER — Mem_ID, Mem_FName, Mem_LName, Mem_DOB, Mem_Phone,
              TIER_Tier_ID, ECONTACT_Emer_ID */
  members: [
    { id: 'M001', fname: 'Jordan', lname: 'Blake',  dob: '1992-04-15', phone: '5551234567', tierId: 2, econtactId: 1 },
    { id: 'M002', fname: 'Taylor', lname: 'Cruz',   dob: '1988-11-02', phone: '5552345678', tierId: 1, econtactId: 2 },
    { id: 'M003', fname: 'Alex',   lname: 'Rivera', dob: '1995-07-23', phone: '5553456789', tierId: 2, econtactId: 3 },
    { id: 'M004', fname: 'Sam',    lname: 'Park',   dob: '1990-03-08', phone: '5554567890', tierId: 1, econtactId: 4 },
    { id: 'M005', fname: 'Morgan', lname: 'Lee',    dob: '1997-09-14', phone: '5555678901', tierId: 2, econtactId: 5 }
  ],

  /* EMPLOYEE — Emp_ID, Emp_FName, Emp_LName, Emp_Phone
     Leads CLASS (1:1) and Files TICKET (1:M) */
  employees: [
    { id: 'E01', fname: 'Riley', lname: 'Morgan', phone: '5550001111' },
    { id: 'E02', fname: 'Devon', lname: 'Hayes',  phone: '5550002222' },
    { id: 'E03', fname: 'Chris', lname: 'Nolan',  phone: '5550003333' },
    { id: 'E04', fname: 'Sam',   lname: 'Ortiz',  phone: '5550004444' }
  ],

  /* CLASS — Class_ID, Class_Name, Class_Start, Class_Length, Class_Cap,
             EMPLOYEE_Emp_ID (1:1 — one employee leads each class) */
  classes: [
    { id: 'C001', name: 'Power Yoga',     start: '2025-03-31 09:00', length: 60, cap: 10, empId: 'E03' },
    { id: 'C002', name: 'HIIT Training',  start: '2025-04-01 18:00', length: 45, cap: 10, empId: 'E04' },
    { id: 'C003', name: 'Spin Cycle',     start: '2025-04-02 07:00', length: 50, cap: 10, empId: 'E01' },
    { id: 'C004', name: 'Core & Stretch', start: '2025-04-03 12:00', length: 45, cap: 10, empId: 'E03' },
    { id: 'C005', name: 'Boxing Basics',  start: '2025-04-04 17:00', length: 60, cap: 10, empId: 'E02' }
  ],

  /* REGISTRATION — CLASS_Class_ID, MEMBER_Mem_ID, Reg_Num
     Composite PK; Premium-only; enrollment <= cap */
  registrations: [
    { classId: 'C001', memId: 'M001', regNum: 1 },
    { classId: 'C001', memId: 'M003', regNum: 2 },
    { classId: 'C001', memId: 'M005', regNum: 3 },
    { classId: 'C002', memId: 'M001', regNum: 1 },
    { classId: 'C002', memId: 'M003', regNum: 2 },
    { classId: 'C003', memId: 'M005', regNum: 1 },
    { classId: 'C004', memId: 'M001', regNum: 1 },
    { classId: 'C004', memId: 'M003', regNum: 2 },
    { classId: 'C004', memId: 'M005', regNum: 3 },
    { classId: 'C005', memId: 'M003', regNum: 1 }
  ],

  /* CHECKIN — Arv_ID, Arv_Date, Arv_Time, Guest_Brought, MEMBER_Mem_ID
     MEMBER Logs CHECKIN (1:M); guest = 0 or 1 */
  checkins: [
    { id: 'CK001', memId: 'M001', date: '2025-03-27', time: '07:42', guest: 0 },
    { id: 'CK002', memId: 'M003', date: '2025-03-27', time: '09:15', guest: 1 },
    { id: 'CK003', memId: 'M005', date: '2025-03-26', time: '18:30', guest: 0 },
    { id: 'CK004', memId: 'M001', date: '2025-03-26', time: '08:00', guest: 0 },
    { id: 'CK005', memId: 'M002', date: '2025-03-25', time: '17:45', guest: 1 }
  ],

  /* EQUIPMENT — Equip_ID, Equip_Name, Equip_Status */
  equipment: [
    { id: 'EQ01', name: 'Treadmill #1',   status: 'Operational'     },
    { id: 'EQ02', name: 'Treadmill #2',   status: 'Non-operational' },
    { id: 'EQ03', name: 'Bench Press A',  status: 'Operational'     },
    { id: 'EQ04', name: 'Cable Machine',  status: 'Non-operational' },
    { id: 'EQ05', name: 'Rowing Machine', status: 'Operational'     },
    { id: 'EQ06', name: 'Elliptical #1',  status: 'Operational'     },
    { id: 'EQ07', name: 'Leg Press',      status: 'Operational'     },
    { id: 'EQ08', name: 'Smith Machine',  status: 'Operational'     }
  ],

  /* TICKET — Ticket_ID, Ticket_Date, Ticket_Desc, Ticket_Resolved,
              EQUIPMENT_Equip_ID, EMPLOYEE_Emp_ID */
  tickets: [
    { id: 'TK001', equipId: 'EQ02', date: '2025-03-20', desc: 'Belt slipping — needs replacement.',   empId: 'E02', resolved: false },
    { id: 'TK002', equipId: 'EQ04', date: '2025-03-24', desc: 'Pulley cable snapped on rep attempt.', empId: 'E01', resolved: false }
  ],

  /* Auto-increment counters */
  _nextMemberId:   6,
  _nextCheckinId:  6,
  _nextTicketId:   3,
  _nextClassId:    6,
  _nextEcontactId: 6
};

/* ── Lookup helpers ───────────────────────────────────── */
function memberById(id)   { return DB.members.find(function(m){ return m.id === id; }); }
function tierById(id)     { return DB.tiers.find(function(t){ return t.id === id; }); }
function econtactById(id) { return DB.econtacts.find(function(e){ return e.id === id; }); }
function employeeById(id) { return DB.employees.find(function(e){ return e.id === id; }); }
function equipById(id)    { return DB.equipment.find(function(e){ return e.id === id; }); }

function classEnrolled(cid) {
  return DB.registrations.filter(function(r){ return r.classId === cid; }).length;
}
function alreadyRegistered(cid, mid) {
  return DB.registrations.some(function(r){ return r.classId === cid && r.memId === mid; });
}
function employeeLeadsClass(empId) {
  return DB.classes.find(function(c){ return c.empId === empId; });
}

/* ── Format helpers ───────────────────────────────────── */
function pad(n)     { return String(n).padStart(4, '0'); }
function fmtCost(c) { return '$' + (c / 100).toFixed(2); }
function fmtDate(dt){
  var d = new Date(dt);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}
function fmtTime(t) {
  var p = t.split(':');
  var h = +p[0];
  return (h % 12 || 12) + ':' + p[1] + ' ' + (h < 12 ? 'AM' : 'PM');
}
function initials(f, l) { return ((f || '')[0] + (l || '')[0]).toUpperCase(); }
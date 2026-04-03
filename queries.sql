-- ═══════════════════════════════════════════════════════════════
--  FitSync Gym Management System
--  SQL Transaction Queries — Phase 3
--  CSI 3450: Database Design
--
--  Entities: TIER, MEMBER, ECONTACT, CHECKIN,
--            CLASS, REGISTRATION, EMPLOYEE, EQUIPMENT, TICKET
--  No TRAINER — employees lead classes.
-- ═══════════════════════════════════════════════════════════════
 
USE fitsync;
 
-- ───────────────────────────────────────────────────────────────
--  SECTION 1: MEMBER TRANSACTIONS
-- ───────────────────────────────────────────────────────────────
 
-- 1.1  Read — view member profile with tier and ECONTACT
-- Maps to: Membership information (View)
SELECT
    m.Mem_ID,
    m.Mem_FName,
    m.Mem_LName,
    m.Mem_DOB,
    m.Mem_Phone,
    t.Tier_Name,
    t.Tier_Cost,
    ec.Emer_FName,
    ec.Emer_LName,
    ec.Emer_Phone
FROM MEMBER m
JOIN TIER     t  ON m.TIER_Tier_ID     = t.Tier_ID
JOIN ECONTACT ec ON m.ECONTACT_Emer_ID = ec.Emer_ID
WHERE m.Mem_ID = :mem_id;
 
-- 1.2  Update — member updates personal info
-- Maps to: Membership management (Update)
UPDATE MEMBER
SET Mem_FName = :fname,
    Mem_LName = :lname,
    Mem_DOB   = :dob,
    Mem_Phone = :phone
WHERE Mem_ID = :mem_id;
 
-- 1.3  Update — member updates ECONTACT
-- Maps to: Membership management (Update)
UPDATE ECONTACT
SET Emer_FName = :fname,
    Emer_LName = :lname,
    Emer_Phone = :phone
WHERE Emer_ID = :emer_id;
 
-- 1.4  Update — member changes their membership tier
-- Maps to: Membership management (Update)
UPDATE MEMBER
SET TIER_Tier_ID = :new_tier_id
WHERE Mem_ID = :mem_id;
 
-- 1.5  Read — view all available classes (with enrollment info)
-- Maps to: Membership information (View)
SELECT
    c.Class_ID,
    c.Class_Name,
    c.Class_Start,
    c.Class_Length,
    c.Class_Cap,
    CONCAT(e.Emp_FName, ' ', e.Emp_LName)        AS Instructor,
    COUNT(r.MEMBER_Mem_ID)                        AS Enrolled,
    (c.Class_Cap - COUNT(r.MEMBER_Mem_ID))        AS Open_Spots
FROM CLASS c
JOIN EMPLOYEE e ON c.EMPLOYEE_Emp_ID = e.Emp_ID
LEFT JOIN REGISTRATION r ON c.Class_ID = r.CLASS_Class_ID
GROUP BY c.Class_ID, c.Class_Name, c.Class_Start,
         c.Class_Length, c.Class_Cap, e.Emp_FName, e.Emp_LName
ORDER BY c.Class_Start;
 
-- 1.6  Create — member registers for a class
-- Maps to: Employee duties (Read/Update) / member self-registration
-- Triggers: trg_premium_only, trg_class_capacity
INSERT INTO REGISTRATION (CLASS_Class_ID, MEMBER_Mem_ID, Reg_Num)
VALUES (
    :class_id,
    :mem_id,
    (SELECT COALESCE(MAX(Reg_Num), 0) + 1
     FROM REGISTRATION
     WHERE CLASS_Class_ID = :class_id)
);
 
-- 1.7  Delete — member drops a class
DELETE FROM REGISTRATION
WHERE CLASS_Class_ID = :class_id
  AND MEMBER_Mem_ID  = :mem_id;
 
-- 1.8  Read — member views own check-in history (CHECKIN table)
-- Maps to: Membership information (View)
SELECT
    Arv_ID,
    Arv_Date,
    Arv_Time,
    Guest_Brought
FROM CHECKIN
WHERE MEMBER_Mem_ID = :mem_id
ORDER BY Arv_Date DESC, Arv_Time DESC;
 
 
-- ───────────────────────────────────────────────────────────────
--  SECTION 2: EMPLOYEE TRANSACTIONS
-- ───────────────────────────────────────────────────────────────
 
-- 2.1  Read — view all members
-- Maps to: Employee duties (Read/Update)
SELECT
    m.Mem_ID,
    m.Mem_FName,
    m.Mem_LName,
    m.Mem_DOB,
    m.Mem_Phone,
    t.Tier_Name,
    CONCAT(ec.Emer_FName, ' ', ec.Emer_LName) AS EC_Name,
    ec.Emer_Phone                              AS EC_Phone
FROM MEMBER m
JOIN TIER     t  ON m.TIER_Tier_ID     = t.Tier_ID
JOIN ECONTACT ec ON m.ECONTACT_Emer_ID = ec.Emer_ID
ORDER BY m.Mem_LName, m.Mem_FName;
 
-- 2.2  Search — find member by ID or name
-- Maps to: Search entries / user authentication
SELECT
    Mem_ID, Mem_FName, Mem_LName, Mem_Phone, TIER_Tier_ID
FROM MEMBER
WHERE Mem_ID    LIKE CONCAT('%', :search, '%')
   OR Mem_FName LIKE CONCAT('%', :search, '%')
   OR Mem_LName LIKE CONCAT('%', :search, '%')
ORDER BY Mem_LName;
 
-- 2.3  Create — register a new member (two-step)
-- Step 1: insert ECONTACT first
INSERT INTO ECONTACT (Emer_FName, Emer_LName, Emer_Phone)
VALUES (:ec_fname, :ec_lname, :ec_phone);
 
-- Step 2: insert MEMBER referencing the new ECONTACT
INSERT INTO MEMBER
    (Mem_ID, Mem_FName, Mem_LName, Mem_DOB, Mem_Phone,
     TIER_Tier_ID, ECONTACT_Emer_ID)
VALUES
    (:mem_id, :fname, :lname, :dob, :phone,
     :tier_id, LAST_INSERT_ID());
 
-- 2.4  Update — employee edits member account + ECONTACT
UPDATE MEMBER
SET Mem_FName    = :fname,
    Mem_LName    = :lname,
    Mem_Phone    = :phone,
    TIER_Tier_ID = :tier_id
WHERE Mem_ID = :mem_id;
 
UPDATE ECONTACT
SET Emer_FName = :ec_fname,
    Emer_LName = :ec_lname,
    Emer_Phone = :ec_phone
WHERE Emer_ID = :emer_id;
 
-- 2.5  Delete — employee deletes member account
-- ON DELETE CASCADE handles REGISTRATION and CHECKIN rows
-- Maps to: Employee membership management (Delete)
DELETE FROM MEMBER
WHERE Mem_ID = :mem_id;
 
-- 2.6  Create — record member check-in (CHECKIN table)
-- Maps to: Employee duties (Read/Update) — record check-ins
INSERT INTO CHECKIN (Arv_Date, Arv_Time, Guest_Brought, MEMBER_Mem_ID)
VALUES (:arv_date, :arv_time, :guest, :mem_id);
 
-- 2.7  Read — view all check-ins
SELECT
    ck.Arv_ID,
    ck.Arv_Date,
    ck.Arv_Time,
    ck.Guest_Brought,
    CONCAT(m.Mem_FName, ' ', m.Mem_LName) AS Member_Name
FROM CHECKIN ck
JOIN MEMBER m ON ck.MEMBER_Mem_ID = m.Mem_ID
ORDER BY ck.Arv_Date DESC, ck.Arv_Time DESC;
 
-- 2.8  Create — employee registers member for a class
-- Triggers enforce Premium-only and capacity cap
INSERT INTO REGISTRATION (CLASS_Class_ID, MEMBER_Mem_ID, Reg_Num)
VALUES (
    :class_id,
    :mem_id,
    (SELECT COALESCE(MAX(Reg_Num), 0) + 1
     FROM REGISTRATION
     WHERE CLASS_Class_ID = :class_id)
);
 
-- 2.9  Read — view class schedule (all classes)
-- Maps to: Employees' Duties (Read)
SELECT
    c.Class_ID,
    c.Class_Name,
    c.Class_Start,
    c.Class_Length,
    c.Class_Cap,
    CONCAT(e.Emp_FName, ' ', e.Emp_LName)  AS Instructor,
    COUNT(r.MEMBER_Mem_ID)                  AS Enrolled
FROM CLASS c
JOIN EMPLOYEE e ON c.EMPLOYEE_Emp_ID = e.Emp_ID
LEFT JOIN REGISTRATION r ON c.Class_ID = r.CLASS_Class_ID
GROUP BY c.Class_ID, c.Class_Name, c.Class_Start,
         c.Class_Length, c.Class_Cap, e.Emp_FName, e.Emp_LName
ORDER BY c.Class_Start;
 
-- 2.10 Create — create a new class
-- Constraint: EMPLOYEE_Emp_ID is UNIQUE (one employee leads at most one class)
-- Maps to: Employees' Duties (Create)
INSERT INTO CLASS
    (Class_Name, Class_Start, Class_Length, Class_Cap, EMPLOYEE_Emp_ID)
VALUES
    (:name, :start, :length, :cap, :emp_id);
 
-- 2.11 Update — edit a class
-- Maps to: Employees' Duties (Update)
UPDATE CLASS
SET Class_Name   = :name,
    Class_Start  = :start,
    Class_Length = :length
WHERE Class_ID = :class_id;
 
-- 2.12 Delete — delete class with zero registrations
-- Trigger trg_no_delete_enrolled_class also enforces this
-- Maps to: Employee class management (Delete)
DELETE FROM CLASS
WHERE Class_ID = :class_id
  AND NOT EXISTS (
      SELECT 1 FROM REGISTRATION
      WHERE CLASS_Class_ID = :class_id
  );
 
-- 2.13 Delete — remove member from class (attendance management)
-- Maps to: Employees' Duties (Delete)
DELETE FROM REGISTRATION
WHERE CLASS_Class_ID = :class_id
  AND MEMBER_Mem_ID  = :mem_id;
 
-- 2.14 Read — view class attendance roster
-- Maps to: Employees' Duties (Read/Update)
SELECT
    r.Reg_Num,
    m.Mem_ID,
    m.Mem_FName,
    m.Mem_LName,
    m.Mem_Phone
FROM REGISTRATION r
JOIN MEMBER m ON r.MEMBER_Mem_ID = m.Mem_ID
WHERE r.CLASS_Class_ID = :class_id
ORDER BY r.Reg_Num;
 
-- 2.15 Read — view all equipment
SELECT
    Equip_ID, Equip_Name, Equip_Status
FROM EQUIPMENT
ORDER BY Equip_Status, Equip_Name;
 
-- 2.16 Update — mark equipment non-operational
UPDATE EQUIPMENT
SET Equip_Status = 'Non-operational'
WHERE Equip_ID = :equip_id;
 
-- 2.17 Create — file a maintenance ticket
-- Maps to: employee creates tickets for non-operational equipment
INSERT INTO TICKET
    (Ticket_Date, Ticket_Desc, Ticket_Resolved,
     EQUIPMENT_Equip_ID, EMPLOYEE_Emp_ID)
VALUES
    (:date, :desc, 0, :equip_id, :emp_id);
 
-- 2.18 Update — resolve a ticket (trigger restores equipment status)
UPDATE TICKET
SET Ticket_Resolved = 1
WHERE Ticket_ID = :ticket_id;
 
-- 2.19 Read — view open tickets
SELECT
    tk.Ticket_ID,
    tk.Ticket_Date,
    tk.Ticket_Desc,
    eq.Equip_Name,
    eq.Equip_Status,
    CONCAT(emp.Emp_FName, ' ', emp.Emp_LName) AS Filed_By
FROM TICKET tk
JOIN EQUIPMENT eq  ON tk.EQUIPMENT_Equip_ID = eq.Equip_ID
JOIN EMPLOYEE  emp ON tk.EMPLOYEE_Emp_ID    = emp.Emp_ID
WHERE tk.Ticket_Resolved = 0
ORDER BY tk.Ticket_Date DESC;
 
-- 2.20 Search / Auth — validate employee login
SELECT Emp_ID, Emp_FName, Emp_LName
FROM EMPLOYEE
WHERE Emp_ID = :emp_id;
 
-- 2.21 Search / Auth — validate member login
SELECT Mem_ID, Mem_FName, Mem_LName, TIER_Tier_ID
FROM MEMBER
WHERE Mem_ID = :mem_id;
 
 
-- ───────────────────────────────────────────────────────────────
--  SECTION 3: REPORTING QUERIES
-- ───────────────────────────────────────────────────────────────
 
-- 3.1  Members per tier
SELECT
    t.Tier_Name,
    COUNT(m.Mem_ID) AS Member_Count
FROM TIER t
LEFT JOIN MEMBER m ON t.Tier_ID = m.TIER_Tier_ID
GROUP BY t.Tier_ID, t.Tier_Name;
 
-- 3.2  Class fill rates
SELECT
    c.Class_ID,
    c.Class_Name,
    c.Class_Start,
    CONCAT(e.Emp_FName, ' ', e.Emp_LName)              AS Instructor,
    c.Class_Cap,
    COUNT(r.MEMBER_Mem_ID)                             AS Enrolled,
    ROUND(COUNT(r.MEMBER_Mem_ID) / c.Class_Cap * 100, 1) AS Fill_Pct
FROM CLASS c
JOIN EMPLOYEE e ON c.EMPLOYEE_Emp_ID = e.Emp_ID
LEFT JOIN REGISTRATION r ON c.Class_ID = r.CLASS_Class_ID
GROUP BY c.Class_ID, c.Class_Name, c.Class_Start,
         e.Emp_FName, e.Emp_LName, c.Class_Cap
ORDER BY c.Class_Start;
 
-- 3.3  Equipment status summary
SELECT
    Equip_Status,
    COUNT(*) AS Count
FROM EQUIPMENT
GROUP BY Equip_Status;
 
-- 3.4  Ticket counts per employee
SELECT
    CONCAT(e.Emp_FName, ' ', e.Emp_LName) AS Employee,
    COUNT(tk.Ticket_ID)                    AS Total_Tickets,
    SUM(CASE WHEN tk.Ticket_Resolved = 0 THEN 1 ELSE 0 END) AS Open_Tickets
FROM EMPLOYEE e
LEFT JOIN TICKET tk ON e.Emp_ID = tk.EMPLOYEE_Emp_ID
GROUP BY e.Emp_ID, e.Emp_FName, e.Emp_LName;
 
-- 3.5  Daily check-in counts (last 30 days)
SELECT
    Arv_Date,
    COUNT(*)           AS Total_Checkins,
    SUM(Guest_Brought) AS Guests_Brought
FROM CHECKIN
WHERE Arv_Date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY Arv_Date
ORDER BY Arv_Date DESC;
 
-- 3.6  Most active members by class enrollment
SELECT
    m.Mem_ID,
    CONCAT(m.Mem_FName, ' ', m.Mem_LName) AS Member,
    t.Tier_Name,
    COUNT(r.CLASS_Class_ID)               AS Classes_Enrolled
FROM MEMBER m
JOIN TIER t ON m.TIER_Tier_ID = t.Tier_ID
LEFT JOIN REGISTRATION r ON m.Mem_ID = r.MEMBER_Mem_ID
GROUP BY m.Mem_ID, m.Mem_FName, m.Mem_LName, t.Tier_Name
ORDER BY Classes_Enrolled DESC;
 
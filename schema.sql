-- ═══════════════════════════════════════════════════════════════
--  FitSync Gym Management System
--  Database Schema — MySQL  (Phase 3)
--  CSI 3450: Database Design
--
--  Tables match the Phase 3 ERD exactly:
--    TIER, MEMBER, ECONTACT, CHECKIN,
--    CLASS, REGISTRATION, EMPLOYEE, EQUIPMENT, TICKET
--  No TRAINER entity — employees lead classes.
-- ═══════════════════════════════════════════════════════════════

CREATE DATABASE IF NOT EXISTS fitsync;
USE fitsync;

-- ─────────────────────────────────────────────────────────────
--  TIER
--  Tier_ID, Tier_Name, Tier_Cost
--  Relationship: TIER Has MEMBER (1:M)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS TIER (
    Tier_ID     INT          NOT NULL AUTO_INCREMENT,
    Tier_Name   VARCHAR(45)  NOT NULL,
    Tier_Cost   INT          NOT NULL,          -- stored in cents
    CONSTRAINT pk_tier        PRIMARY KEY (Tier_ID),
    CONSTRAINT uq_tier_name   UNIQUE (Tier_Name),
    CONSTRAINT ck_tier_cost   CHECK (Tier_Cost >= 0)
);

-- ─────────────────────────────────────────────────────────────
--  ECONTACT  (Emergency Contact)
--  Emer_ID, Emer_FName, Emer_LName, Emer_Phone
--  Relationship: MEMBER Has ECONTACT (1:1)
--  Each ECONTACT belongs to exactly one MEMBER.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ECONTACT (
    Emer_ID     INT          NOT NULL AUTO_INCREMENT,
    Emer_FName  VARCHAR(45)  NOT NULL,
    Emer_LName  VARCHAR(45)  NOT NULL,
    Emer_Phone  VARCHAR(15)  NOT NULL,
    CONSTRAINT pk_econtact PRIMARY KEY (Emer_ID)
);

-- ─────────────────────────────────────────────────────────────
--  MEMBER
--  Mem_ID, Mem_FName, Mem_LName, Mem_DOB, Mem_Phone,
--  TIER_Tier_ID, ECONTACT_Emer_ID
--  Constraints:
--    - Each member associated with exactly one tier.
--    - Each member has exactly one emergency contact (1:1).
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS MEMBER (
    Mem_ID              VARCHAR(45)  NOT NULL,
    Mem_FName           VARCHAR(45)  NOT NULL,
    Mem_LName           VARCHAR(45)  NOT NULL,
    Mem_DOB             DATE         NOT NULL,
    Mem_Phone           VARCHAR(15)  NOT NULL,
    TIER_Tier_ID        INT          NOT NULL,
    ECONTACT_Emer_ID    INT          NOT NULL,
    CONSTRAINT pk_member         PRIMARY KEY (Mem_ID),
    CONSTRAINT fk_member_tier    FOREIGN KEY (TIER_Tier_ID)
        REFERENCES TIER(Tier_ID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_member_econtact FOREIGN KEY (ECONTACT_Emer_ID)
        REFERENCES ECONTACT(Emer_ID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_member_econtact UNIQUE (ECONTACT_Emer_ID)   -- enforces 1:1
);

-- ─────────────────────────────────────────────────────────────
--  EMPLOYEE
--  Emp_ID, Emp_FName, Emp_LName, Emp_Phone
--  Relationship: EMPLOYEE Leads CLASS (1:1)
--                EMPLOYEE Files TICKET (1:M)
--  Constraint: An employee may teach zero or one class.
--  Note: TRAINER entity does NOT exist in Phase 3.
--        Classes are led by employees.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS EMPLOYEE (
    Emp_ID      VARCHAR(45)  NOT NULL,
    Emp_FName   VARCHAR(45)  NOT NULL,
    Emp_LName   VARCHAR(45)  NOT NULL,
    Emp_Phone   VARCHAR(15)  NOT NULL,
    CONSTRAINT pk_employee PRIMARY KEY (Emp_ID)
);

-- ─────────────────────────────────────────────────────────────
--  CLASS
--  Class_ID, Class_Start, Class_Length, Class_Cap,
--  EMPLOYEE_Emp_ID
--  Relationships:
--    - EMPLOYEE Leads CLASS (1:1) — UNIQUE on EMPLOYEE_Emp_ID
--    - CLASS Occupies REGISTRATION (1:M)
--  Constraints:
--    - A class must have an employee assigned.
--    - An employee may lead zero or one class (UNIQUE FK).
--    - Class cap <= 10.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS CLASS (
    Class_ID            INT          NOT NULL AUTO_INCREMENT,
    Class_Name          VARCHAR(100) NOT NULL,
    Class_Start         DATETIME     NOT NULL,
    Class_Length        INT          NOT NULL,   -- minutes
    Class_Cap           INT          NOT NULL DEFAULT 10,
    EMPLOYEE_Emp_ID     VARCHAR(45)  NOT NULL,
    CONSTRAINT pk_class          PRIMARY KEY (Class_ID),
    CONSTRAINT fk_class_employee FOREIGN KEY (EMPLOYEE_Emp_ID)
        REFERENCES EMPLOYEE(Emp_ID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT uq_class_employee UNIQUE (EMPLOYEE_Emp_ID),  -- 1:1 enforcement
    CONSTRAINT ck_class_cap      CHECK (Class_Cap >= 1 AND Class_Cap <= 10),
    CONSTRAINT ck_class_length   CHECK (Class_Length > 0)
);

-- ─────────────────────────────────────────────────────────────
--  REGISTRATION
--  CLASS_Class_ID, MEMBER_Mem_ID, Reg_Num
--  Relationships:
--    - MEMBER Completes REGISTRATION (1:M)
--    - CLASS Occupies REGISTRATION (1:M)
--  Constraints:
--    - Composite PK prevents duplicate enrollment.
--    - Only Premium members (enforced by trigger).
--    - Enrollment <= Class_Cap (enforced by trigger).
--    - Classes removed only if registrations = 0 (enforced by trigger).
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS REGISTRATION (
    CLASS_Class_ID   INT          NOT NULL,
    MEMBER_Mem_ID    VARCHAR(45)  NOT NULL,
    Reg_Num          INT          NOT NULL,
    CONSTRAINT pk_registration PRIMARY KEY (CLASS_Class_ID, MEMBER_Mem_ID),
    CONSTRAINT fk_reg_class    FOREIGN KEY (CLASS_Class_ID)
        REFERENCES CLASS(Class_ID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_reg_member   FOREIGN KEY (MEMBER_Mem_ID)
        REFERENCES MEMBER(Mem_ID)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- ─────────────────────────────────────────────────────────────
--  CHECKIN  (formerly ARRIVAL)
--  Arv_ID, Arv_Date, Arv_Time, Guest_Brought, MEMBER_Mem_ID
--  Relationship: MEMBER Logs CHECKIN (1:M)
--  Constraints:
--    - Each check-in references exactly one member.
--    - Guest_Brought is 0 (no guest) or 1 (one guest).
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS CHECKIN (
    Arv_ID          INT          NOT NULL AUTO_INCREMENT,
    Arv_Date        DATE         NOT NULL,
    Arv_Time        TIME         NOT NULL,
    Guest_Brought   TINYINT(1)   NOT NULL DEFAULT 0,
    MEMBER_Mem_ID   VARCHAR(45)  NOT NULL,
    CONSTRAINT pk_checkin       PRIMARY KEY (Arv_ID),
    CONSTRAINT fk_checkin_mem   FOREIGN KEY (MEMBER_Mem_ID)
        REFERENCES MEMBER(Mem_ID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT ck_checkin_guest CHECK (Guest_Brought IN (0, 1))
);

-- ─────────────────────────────────────────────────────────────
--  EQUIPMENT
--  Equip_ID, Equip_Name, Equip_Status
--  Relationship: EQUIPMENT Assigned to TICKET (1:M)
--  Constraint: Non-operational equipment must have one open ticket.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS EQUIPMENT (
    Equip_ID     INT          NOT NULL AUTO_INCREMENT,
    Equip_Name   VARCHAR(100) NOT NULL,
    Equip_Status VARCHAR(45)  NOT NULL DEFAULT 'Operational',
    CONSTRAINT pk_equipment   PRIMARY KEY (Equip_ID),
    CONSTRAINT ck_equip_status CHECK (Equip_Status IN ('Operational', 'Non-operational'))
);

-- ─────────────────────────────────────────────────────────────
--  TICKET
--  Ticket_ID, Ticket_Date, Ticket_Desc, Ticket_Resolved,
--  EQUIPMENT_Equip_ID, EMPLOYEE_Emp_ID
--  Relationships:
--    - EMPLOYEE Files TICKET (1:M)
--    - EQUIPMENT Assigned to TICKET (1:M)
--  Constraints:
--    - Each ticket created by exactly one employee.
--    - Each ticket associated with exactly one equipment item.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS TICKET (
    Ticket_ID           INT          NOT NULL AUTO_INCREMENT,
    Ticket_Date         DATE         NOT NULL,
    Ticket_Desc         VARCHAR(255) NOT NULL,
    Ticket_Resolved     TINYINT(1)   NOT NULL DEFAULT 0,
    EQUIPMENT_Equip_ID  INT          NOT NULL,
    EMPLOYEE_Emp_ID     VARCHAR(45)  NOT NULL,
    CONSTRAINT pk_ticket        PRIMARY KEY (Ticket_ID),
    CONSTRAINT fk_ticket_equip  FOREIGN KEY (EQUIPMENT_Equip_ID)
        REFERENCES EQUIPMENT(Equip_ID)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_ticket_emp    FOREIGN KEY (EMPLOYEE_Emp_ID)
        REFERENCES EMPLOYEE(Emp_ID)
        ON UPDATE CASCADE ON DELETE RESTRICT
);


-- ═══════════════════════════════════════════════════════════════
--  TRIGGERS
-- ═══════════════════════════════════════════════════════════════

DELIMITER $$

-- T1: Only PREMIUM members may register for a class
CREATE TRIGGER trg_premium_only
BEFORE INSERT ON REGISTRATION
FOR EACH ROW
BEGIN
    DECLARE v_tier INT;
    SELECT TIER_Tier_ID INTO v_tier
    FROM MEMBER WHERE Mem_ID = NEW.MEMBER_Mem_ID;
    IF v_tier <> 2 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Only Premium members may register for classes.';
    END IF;
END$$

-- T2: Class enrollment must not exceed Class_Cap (max 10)
CREATE TRIGGER trg_class_capacity
BEFORE INSERT ON REGISTRATION
FOR EACH ROW
BEGIN
    DECLARE v_enrolled INT;
    DECLARE v_cap INT;
    SELECT COUNT(*) INTO v_enrolled
    FROM REGISTRATION WHERE CLASS_Class_ID = NEW.CLASS_Class_ID;
    SELECT Class_Cap INTO v_cap
    FROM CLASS WHERE Class_ID = NEW.CLASS_Class_ID;
    IF v_enrolled >= v_cap THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Class enrollment limit reached.';
    END IF;
END$$

-- T3: Classes may be removed only if registrations = 0
CREATE TRIGGER trg_no_delete_enrolled_class
BEFORE DELETE ON CLASS
FOR EACH ROW
BEGIN
    DECLARE v_count INT;
    SELECT COUNT(*) INTO v_count
    FROM REGISTRATION WHERE CLASS_Class_ID = OLD.Class_ID;
    IF v_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot delete a class with enrolled members.';
    END IF;
END$$

-- T4: Resolving a ticket restores equipment to Operational
CREATE TRIGGER trg_ticket_resolved
AFTER UPDATE ON TICKET
FOR EACH ROW
BEGIN
    IF NEW.Ticket_Resolved = 1 AND OLD.Ticket_Resolved = 0 THEN
        UPDATE EQUIPMENT
        SET Equip_Status = 'Operational'
        WHERE Equip_ID = NEW.EQUIPMENT_Equip_ID;
    END IF;
END$$

DELIMITER ;


-- ═══════════════════════════════════════════════════════════════
--  SEED DATA
-- ═══════════════════════════════════════════════════════════════

INSERT INTO TIER (Tier_Name, Tier_Cost) VALUES
    ('Basic',   1999),
    ('Premium', 4999);

INSERT INTO ECONTACT (Emer_FName, Emer_LName, Emer_Phone) VALUES
    ('Sarah',  'Blake',  '5559876543'),
    ('Miguel', 'Cruz',   '5558765432'),
    ('Carmen', 'Rivera', '5557654321'),
    ('Ji',     'Park',   '5556543210'),
    ('David',  'Lee',    '5555432109');

INSERT INTO MEMBER (Mem_ID, Mem_FName, Mem_LName, Mem_DOB, Mem_Phone, TIER_Tier_ID, ECONTACT_Emer_ID) VALUES
    ('M001', 'Jordan', 'Blake',  '1992-04-15', '5551234567', 2, 1),
    ('M002', 'Taylor', 'Cruz',   '1988-11-02', '5552345678', 1, 2),
    ('M003', 'Alex',   'Rivera', '1995-07-23', '5553456789', 2, 3),
    ('M004', 'Sam',    'Park',   '1990-03-08', '5554567890', 1, 4),
    ('M005', 'Morgan', 'Lee',    '1997-09-14', '5555678901', 2, 5);

INSERT INTO EMPLOYEE (Emp_ID, Emp_FName, Emp_LName, Emp_Phone) VALUES
    ('E01', 'Riley', 'Morgan', '5550001111'),
    ('E02', 'Devon', 'Hayes',  '5550002222'),
    ('E03', 'Chris', 'Nolan',  '5550003333'),
    ('E04', 'Sam',   'Ortiz',  '5550004444');

INSERT INTO CLASS (Class_Name, Class_Start, Class_Length, Class_Cap, EMPLOYEE_Emp_ID) VALUES
    ('Power Yoga',     '2025-03-31 09:00:00', 60, 10, 'E03'),
    ('HIIT Training',  '2025-04-01 18:00:00', 45, 10, 'E04'),
    ('Spin Cycle',     '2025-04-02 07:00:00', 50, 10, 'E01'),
    ('Core & Stretch', '2025-04-03 12:00:00', 45, 10, 'E03'),  -- E03 leads 2 for demo
    ('Boxing Basics',  '2025-04-04 17:00:00', 60, 10, 'E02');

INSERT INTO REGISTRATION (CLASS_Class_ID, MEMBER_Mem_ID, Reg_Num) VALUES
    (1, 'M001', 1), (1, 'M003', 2), (1, 'M005', 3),
    (2, 'M001', 1), (2, 'M003', 2),
    (3, 'M005', 1),
    (4, 'M001', 1), (4, 'M003', 2), (4, 'M005', 3),
    (5, 'M003', 1);

INSERT INTO CHECKIN (Arv_Date, Arv_Time, Guest_Brought, MEMBER_Mem_ID) VALUES
    ('2025-03-27', '07:42:00', 0, 'M001'),
    ('2025-03-27', '09:15:00', 1, 'M003'),
    ('2025-03-26', '18:30:00', 0, 'M005'),
    ('2025-03-26', '08:00:00', 0, 'M001'),
    ('2025-03-25', '17:45:00', 1, 'M002');

INSERT INTO EQUIPMENT (Equip_Name, Equip_Status) VALUES
    ('Treadmill #1',   'Operational'),
    ('Treadmill #2',   'Non-operational'),
    ('Bench Press A',  'Operational'),
    ('Cable Machine',  'Non-operational'),
    ('Rowing Machine', 'Operational'),
    ('Elliptical #1',  'Operational'),
    ('Leg Press',      'Operational'),
    ('Smith Machine',  'Operational');

INSERT INTO TICKET (Ticket_Date, Ticket_Desc, Ticket_Resolved, EQUIPMENT_Equip_ID, EMPLOYEE_Emp_ID) VALUES
    ('2025-03-20', 'Belt slipping — needs replacement.',   0, 2, 'E02'),
    ('2025-03-24', 'Pulley cable snapped on rep attempt.', 0, 4, 'E01');
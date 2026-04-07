--  FitSync Gym Management System
--  Database Schema (Phase 3)
--  CSI 3450: Database Design

CREATE DATABASE IF NOT EXISTS fitsync;
USE fitsync;

-- Tier Table
CREATE TABLE IF NOT EXISTS Tier (
    Tier_ID INT PRIMARY KEY AUTO_INCREMENT,
    Tier_Name VARCHAR(25) NOT NULL,
    Tier_Cost DECIMAL(6,2) NOT NULL
);

-- Emergency Contant Table
CREATE TABLE IF NOT EXISTS EContact (
    Econ_ID INT PRIMARY KEY AUTO_INCREMENT,
    Econ_FName VARCHAR(45) NOT NULL,
    Econ_LName VARCHAR(45) NOT NULL,
    Econ_Phone VARCHAR(15) NOT NULL
);

-- Employee Table
CREATE TABLE IF NOT EXISTS Employee (
    Emp_ID INT PRIMARY KEY AUTO_INCREMENT,
    Emp_FName VARCHAR(45) NOT NULL,
    Emp_LName VARCHAR(45) NOT NULL,
    Emp_Phone VARCHAR(15) NOT NULL UNIQUE
);

-- Equipment Table
CREATE TABLE IF NOT EXISTS Equipment (
    Equip_ID INT PRIMARY KEY AUTO_INCREMENT,
    Equip_Name VARCHAR(45) NOT NULL,
    Equip_Status VARCHAR(45) NOT NULL DEFAULT 'Operational'
);

-- Member Table
CREATE TABLE IF NOT EXISTS Member (
    Mem_ID INT PRIMARY KEY AUTO_INCREMENT,
    Mem_FName VARCHAR(45) NOT NULL,
    Mem_LName VARCHAR(45) NOT NULL,
    Mem_DOB DATE NOT NULL,
    Mem_Email VARCHAR(45) NOT NULL UNIQUE,
    Mem_Phone VARCHAR(15) NOT NULL UNIQUE,
    Tier_ID INT NOT NULL,
    Econ_ID INT NOT NULL UNIQUE,
    FOREIGN KEY (Tier_ID) REFERENCES Tier(Tier_ID),
    FOREIGN KEY (Econ_ID) REFERENCES EContact(Econ_ID)
);

-- Check In Table
CREATE TABLE IF NOT EXISTS CheckIn (
    Check_ID INT PRIMARY KEY AUTO_INCREMENT,
    Check_Datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Guest_Brought TINYINT NOT NULL DEFAULT 0 CHECK (Guest_Brought IN (0,1)),
    Mem_ID INT NOT NULL,
    FOREIGN KEY (Mem_ID) REFERENCES Member(Mem_ID)
);

-- Class Table
CREATE TABLE IF NOT EXISTS Class (
    Class_ID INT PRIMARY KEY AUTO_INCREMENT,
    Class_Name VARCHAR(45) NOT NULL,
    Class_Start DATETIME NOT NULL,
    Class_Length INT NOT NULL,
    Class_Cap INT NOT NULL DEFAULT 10 CHECK (Class_Cap <= 10),
    Emp_ID INT NOT NULL UNIQUE,
    FOREIGN KEY (Emp_ID) REFERENCES Employee(Emp_ID)
);

-- Registration Table
CREATE TABLE IF NOT EXISTS Registration (
    Class_ID INT NOT NULL,
    Mem_ID INT NOT NULL,
    PRIMARY KEY (Class_ID, Mem_ID),
    Reg_Num INT NOT NULL,
    FOREIGN KEY (Class_ID) REFERENCES Class(Class_ID),
    FOREIGN KEY (Mem_ID) REFERENCES Member(Mem_ID)
);

-- Ticket Table
CREATE TABLE IF NOT EXISTS Ticket (
    Ticket_ID INT PRIMARY KEY AUTO_INCREMENT,
    Ticket_Date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Ticket_Desc VARCHAR(255) NOT NULL,
    Ticket_Status VARCHAR(20) NOT NULL DEFAULT 'Open',
    Emp_ID INT NOT NULL,
    Equip_ID INT NOT NULL,
    FOREIGN KEY (Emp_ID) REFERENCES Employee(Emp_ID),
    FOREIGN KEY (Equip_ID) REFERENCES Equipment(Equip_ID)
);

-- Seed Data (Tier Table)
INSERT IGNORE INTO Tier (Tier_ID, Tier_Name, Tier_Cost)
VALUES
    (0001, 'Basic', 25.00),
    (0002, 'Premium', 40.00);

-- Seed Data (Emergency Contact Table)
INSERT IGNORE INTO EContact (Econ_ID, Econ_FName, Econ_LName, Econ_Phone)
VALUES
    (1001, 'John', 'Smith', '(248)-345-4598'),
    (1002, 'Maria', 'Jones', '(586)-324-8462'),
    (1003, 'Kanye', 'West', '(313)-980-0098'),
    (1004, 'Emma', 'Green', '(248)-921-6942'),
    (1005, 'Michael', 'Brown', '(248)-555-1005'),
    (1006, 'Ashley', 'Taylor', '(586)-555-1006'),
    (1007, 'Daniel', 'White', '(313)-555-1007'),
    (1008, 'Sophia', 'Hall', '(248)-555-1008'),
    (1009, 'David', 'Allen', '(586)-555-1009'),
    (1010, 'Olivia', 'Young', '(313)-555-1010');

-- Seed Data (Employee Table)
INSERT IGNORE INTO Employee (Emp_ID, Emp_FName, Emp_LName, Emp_Phone)
VALUES
    (1001, 'John', 'Smith', '(248)-345-4598'),
    (1002, 'Maria', 'Jones', '(586)-324-8462'),
    (1003, 'Kanye', 'West', '(313)-980-0098'),
    (1004, 'Emma', 'Green', '(248)-921-6942'),
    (1005, 'Michael', 'Brown', '(248)-555-1005');

-- Seed Data (Equipment Table)
INSERT IGNORE INTO Equipment (Equip_ID, Equip_Name, Equip_Status)
VALUES
    (3001, 'Elliptical #1', 'Operational'),
    (3002, 'Elliptical #2', 'Operational'),
    (3003, 'Elliptical #3', 'Operational'),
    (3004, 'Stationary Bike #1', 'Operational'),
    (3005, 'Stationary Bike #2', 'Non-Operational'),
    (3006, 'Stationary Bike #3', 'Operational'),
    (3007, 'Treadmill #1', 'Non-Operational'),
    (3008, 'Treadmill #2', 'Operational'),
    (3009, 'Treadmill #3', 'Operational'),
    (3010, 'Stair Master #1', 'Operational'),
    (3011, 'Stair Master #2', 'Operational'),
    (3012, 'Stair Master #3', 'Operational'),
    (3013, 'Squat Rack #1', 'Operational'),
    (3014, 'Squat Rack #2', 'Operational'),
    (3015, 'Bench Press #1', 'Operational'),
    (3016, 'Bench Press #2', 'Operational'),
    (3017, 'Quad Stack Cable Machine #1', 'Operational'),
    (3018, 'Quad Stack Cable Machine #2', 'Operational'),
    (3019, 'Quad Stack Cable Machine #3', 'Non-Operational'),
    (3020, 'Quad Stack Cable Machine #4', 'Operational'),
    (3021, 'Pendulum Squat', 'Operational'),
    (3022, 'Leg Press', 'Operational'),
    (3023, 'Pec Deck', 'Operational'),
    (3024, 'Shoulder Press', 'Non-Operational'),
    (3025, 'Leg Extension', 'Operational'),
    (3026, 'Leg Curl', 'Operational'),
    (3027, 'Calf Extension', 'Operational'),
    (3028, 'Cable Row', 'Operational'),
    (3029, 'Dumbbell Rack #1', 'Operational'),
    (3030, 'Dumbbell Rack #2', 'Operational'),
    (3031, 'Dumbbell Rack #3', 'Operational');

-- Seed Data (Member Table)
INSERT IGNORE INTO Member (Mem_ID, Mem_FName, Mem_LName, Mem_DOB, Mem_Email, Mem_Phone, Tier_ID, Econ_ID)
VALUES
    (3001, 'Ethan', 'Moore', '2001-03-15', 'ethan.moore@gmail.com', '(248)-600-3001', 0001, 1001),
    (3002, 'Olivia', 'Jackson', '1999-07-22', 'olivia.jackson@outlook.com', '(586)-600-3002', 0002, 1002),
    (3003, 'Liam', 'Martin', '2002-11-05', 'liam.martin@yahoo.com', '(313)-600-3003', 0001, 1003),
    (3004, 'Ava', 'Lee', '1998-01-18', 'ava.lee@hotmail.com', '(248)-600-3004', 0002, 1004),
    (3005, 'Noah', 'Perez', '2000-09-10', 'noah.perez@gmail.com', '(586)-600-3005', 0001, 1005),
    (3006, 'Sophia', 'Thompson', '2003-04-27', 'sophia.thompson@outlook.com', '(313)-600-3006', 0002, 1006),
    (3007, 'Mason', 'White', '1997-06-13', 'mason.white@yahoo.com', '(248)-600-3007', 0001, 1007),
    (3008, 'Isabella', 'Lopez', '2001-12-01', 'isabella.lopez@gmail.com', '(586)-600-3008', 0002, 1008),
    (3009, 'Lucas', 'Hill', '1996-08-19', 'lucas.hill@hotmail.com', '(313)-600-3009', 0001, 1009),
    (3010, 'Mia', 'Scott', '2002-02-25', 'mia.scott@outlook.com', '(248)-600-3010', 0002, 1010);

-- Seed Data (Check In Table)
INSERT IGNORE INTO CheckIn (Check_ID, Check_Datetime, Guest_Brought, Mem_ID)
VALUES
    (4001, '2023-10-06 14:30:00', 0, 3010),
    (4002, '2023-10-07 09:00:00', 1, 3001),
    (4003, '2023-10-07 17:30:00', 0, 3002),
    (4004, '2023-10-08 08:00:00', 1, 3003),
    (4005, '2023-10-08 18:30:00', 0, 3004),
    (4006, '2023-10-09 07:00:00', 0, 3005),
    (4007, '2023-10-09 16:30:00', 1, 3006),
    (4008, '2023-10-10 10:00:00', 0, 3007),
    (4009, '2023-10-10 19:30:00', 1, 3008),
    (4010, '2023-10-11 11:00:00', 0, 3009);

-- Seed Data (Class Table)
INSERT IGNORE INTO Class (Class_ID, Class_Name, Class_Start, Class_Length, Class_Cap, Emp_ID)
VALUES
    (5001, 'Pilates', '2023-10-14 12:00:00', 60, 10, 1001),
    (5002, 'Yoga', '2023-10-14 08:00:00', 60, 10, 1002),
    (5003, 'Spin', '2023-10-14 09:30:00', 45, 10, 1003),
    (5004, 'Zumba', '2023-10-14 11:00:00', 60, 10, 1004),
    (5005, 'Kickboxing', '2023-10-14 13:30:00', 45, 10, 1005);

-- Seed Data (Registration Table)
INSERT IGNORE INTO Registration (Class_ID, Mem_ID, Reg_Num)
VALUES
    (5001, 3001, 1),
    (5001, 3002, 2),
    (5001, 3003, 3),
    (5002, 3004, 4),
    (5002, 3005, 5),
    (5003, 3006, 6),
    (5003, 3007, 7),
    (5004, 3008, 8),
    (5004, 3009, 9),
    (5005, 3010, 10);

-- Seed Data (Ticket Table)
INSERT IGNORE INTO Ticket (Ticket_ID, Ticket_Date, Ticket_Desc, Ticket_Status, Emp_ID, Equip_ID)
VALUES
    (6001, '2023-10-14 11:32:12', 'Loose pedal resistance and the display is not responding.', 'Open', 1004, 3005),
    (6002, '2023-10-14 12:05:00', 'Belt will not move properly and makes a grinding noise during use.', 'Open', 1002, 3007),
    (6003, '2023-10-14 13:18:30', 'Damaged cable attachment.', 'Open', 1004, 3019),
    (6004, '2023-10-14 14:40:45', 'The seat will not lock into place.', 'Open', 1005, 3024);



-- -- ═══════════════════════════════════════════════════════════════
-- --  TRIGGERS
-- -- ═══════════════════════════════════════════════════════════════

-- DELIMITER $$

-- -- T1: Only PREMIUM members may register for a class
-- CREATE TRIGGER trg_premium_only
-- BEFORE INSERT ON REGISTRATION
-- FOR EACH ROW
-- BEGIN
--     DECLARE v_tier INT;
--     SELECT TIER_Tier_ID INTO v_tier
--     FROM MEMBER WHERE Mem_ID = NEW.MEMBER_Mem_ID;
--     IF v_tier <> 2 THEN
--         SIGNAL SQLSTATE '45000'
--         SET MESSAGE_TEXT = 'Only Premium members may register for classes.';
--     END IF;
-- END$$

-- -- T2: Class enrollment must not exceed Class_Cap (max 10)
-- CREATE TRIGGER trg_class_capacity
-- BEFORE INSERT ON REGISTRATION
-- FOR EACH ROW
-- BEGIN
--     DECLARE v_enrolled INT;
--     DECLARE v_cap INT;
--     SELECT COUNT(*) INTO v_enrolled
--     FROM REGISTRATION WHERE CLASS_Class_ID = NEW.CLASS_Class_ID;
--     SELECT Class_Cap INTO v_cap
--     FROM CLASS WHERE Class_ID = NEW.CLASS_Class_ID;
--     IF v_enrolled >= v_cap THEN
--         SIGNAL SQLSTATE '45000'
--         SET MESSAGE_TEXT = 'Class enrollment limit reached.';
--     END IF;
-- END$$

-- -- T3: Classes may be removed only if registrations = 0
-- CREATE TRIGGER trg_no_delete_enrolled_class
-- BEFORE DELETE ON CLASS
-- FOR EACH ROW
-- BEGIN
--     DECLARE v_count INT;
--     SELECT COUNT(*) INTO v_count
--     FROM REGISTRATION WHERE CLASS_Class_ID = OLD.Class_ID;
--     IF v_count > 0 THEN
--         SIGNAL SQLSTATE '45000'
--         SET MESSAGE_TEXT = 'Cannot delete a class with enrolled members.';
--     END IF;
-- END$$

-- -- T4: Resolving a ticket restores equipment to Operational
-- CREATE TRIGGER trg_ticket_resolved
-- AFTER UPDATE ON TICKET
-- FOR EACH ROW
-- BEGIN
--     IF NEW.Ticket_Resolved = 1 AND OLD.Ticket_Resolved = 0 THEN
--         UPDATE EQUIPMENT
--         SET Equip_Status = 'Operational'
--         WHERE Equip_ID = NEW.EQUIPMENT_Equip_ID;
--     END IF;
-- END$$

-- DELIMITER ;
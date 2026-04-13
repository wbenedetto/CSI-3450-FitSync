import os
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from mysql.connector import pooling
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
import re

# Load Environment Variables
load_dotenv()

app = FastAPI(title="FitSync API")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Connection Pool
db_pool = pooling.MySQLConnectionPool(
    pool_name="fitsync_pool",
    pool_size=10,
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME")
)

def get_db_conn():
    """Retrieves a connection from the connection pool."""
    return db_pool.get_connection()

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )

@app.post("/login")
def login(role: str = Form(...), user_id: int = Form(...)):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        if role == "member":
            cursor.execute("""
                SELECT 1
                FROM Member
                WHERE Mem_ID = %s
            """, (user_id,))
            member_exists = cursor.fetchone()

            if member_exists:
                return RedirectResponse(url=f"/member/{user_id}", status_code=303)

        elif role == "employee":
            cursor.execute("""
                SELECT 1
                FROM Employee
                WHERE Emp_ID = %s
            """, (user_id,))
            employee_exists = cursor.fetchone()

            if employee_exists:
                return RedirectResponse(url=f"/employee/{user_id}/members", status_code=303)

        return RedirectResponse(url="/?error=invalid_id", status_code=303)

    finally:
        cursor.close()
        conn.close()

@app.get("/member/{mem_id}")
def member_profile(request: Request, mem_id: int):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT m.Mem_ID, m.Mem_FName, m.Mem_LName, m.Mem_DOB, m.Mem_Email, m.Mem_Phone, t.Tier_Name, t.Tier_Cost, ec.Econ_FName, ec.Econ_LName, ec.Econ_Phone, m.Tier_ID
            FROM Member m
            JOIN Tier t ON m.Tier_ID = t.Tier_ID
            JOIN EContact ec ON m.Econ_ID = ec.Econ_ID
            WHERE m.Mem_ID = %s
        """, (mem_id,))

        member = cursor.fetchone()

        if not member:
            return {"detail": "Member not found"}

        return templates.TemplateResponse(
            request=request,
            name="member_profile.html",
            context={"member": member}
        )
    finally:
        cursor.close()
        conn.close()
        
@app.post("/member/{mem_id}/update-profile")
def update_member_profile(
    mem_id: int,
    mem_fname: str = Form(...),
    mem_lname: str = Form(...),
    mem_dob: str = Form(...),
    mem_phone: str = Form(...)
):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Member
            SET Mem_FName = %s,
                Mem_LName = %s,
                Mem_DOB = %s,
                Mem_Phone = %s
            WHERE Mem_ID = %s
        """, (mem_fname, mem_lname, mem_dob, mem_phone, mem_id))

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/member/{mem_id}", status_code=303)

@app.post("/member/{mem_id}/update-contact")
def update_member_contact(
    mem_id: int,
    econ_fname: str = Form(...),
    econ_lname: str = Form(...),
    econ_phone: str = Form(...)
):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE EContact ec
            JOIN Member m ON m.Econ_ID = ec.Econ_ID
            SET ec.Econ_FName = %s,
                ec.Econ_LName = %s,
                ec.Econ_Phone = %s
            WHERE m.Mem_ID = %s
        """, (econ_fname, econ_lname, econ_phone, mem_id))

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/member/{mem_id}", status_code=303)

@app.post("/member/{mem_id}/update-tier")
def update_member_tier(
    mem_id: int,
    tier_id: int = Form(...)
):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Member
            SET Tier_ID = %s
            WHERE Mem_ID = %s
        """, (tier_id, mem_id))

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/member/{mem_id}", status_code=303)

@app.get("/member/{mem_id}/classes")
def member_classes(request: Request, mem_id: int):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT m.Mem_ID, m.Mem_FName, m.Mem_LName, m.Tier_ID, t.Tier_Name
            FROM Member m
            JOIN Tier t ON m.Tier_ID = t.Tier_ID
            WHERE m.Mem_ID = %s
        """, (mem_id,))
        member = cursor.fetchone()

        if not member:
            return {"detail": "Member not found"}

        cursor.execute("""
            SELECT c.Class_ID, c.Class_Name, c.Class_Start, c.Class_Length, c.Class_Cap, c.Emp_ID,
                CONCAT(e.Emp_FName, ' ', e.Emp_LName) AS Instructor,
                COUNT(r.Mem_ID) AS Enrolled_Count,
                MAX(CASE WHEN r.Mem_ID = %s THEN 1 ELSE 0 END) AS Is_Enrolled
            FROM Class c
            JOIN Employee e ON c.Emp_ID = e.Emp_ID
            LEFT JOIN Registration r ON c.Class_ID = r.Class_ID
            GROUP BY c.Class_ID, c.Class_Name, c.Class_Start, c.Class_Length, c.Class_Cap, c.Emp_ID, e.Emp_FName, e.Emp_LName
            ORDER BY c.Class_Start
        """, (mem_id,))
        classes = cursor.fetchall()

        return templates.TemplateResponse(
            request=request,
            name="member_classes.html",
            context={
                "member": member,
                "classes": classes
            }
        )
    finally:
        cursor.close()
        conn.close()
        
@app.post("/member/{mem_id}/classes/{class_id}/register")
def register_for_class(mem_id: int, class_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT Tier_ID
            FROM Member
            WHERE Mem_ID = %s
        """, (mem_id,))
        member_row = cursor.fetchone()

        if not member_row:
            return {"detail": "Member not found"}

        if member_row[0] != 2:
            return RedirectResponse(url=f"/member/{mem_id}/classes", status_code=303)

        cursor.execute("""
            SELECT COUNT(*)
            FROM Registration
            WHERE Mem_ID = %s AND Class_ID = %s
        """, (mem_id, class_id))
        already_registered = cursor.fetchone()[0]

        if already_registered > 0:
            return RedirectResponse(url=f"/member/{mem_id}/classes", status_code=303)

        cursor.execute("""
            SELECT Class_Cap
            FROM Class
            WHERE Class_ID = %s
        """, (class_id,))
        class_row = cursor.fetchone()

        if not class_row:
            return {"detail": "Class not found"}

        class_cap = class_row[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM Registration
            WHERE Class_ID = %s
        """, (class_id,))
        enrolled_count = cursor.fetchone()[0]

        if enrolled_count >= class_cap:
            return RedirectResponse(url=f"/member/{mem_id}/classes", status_code=303)

        cursor.execute("""
            SELECT COALESCE(MAX(Reg_Num), 0) + 1
            FROM Registration
        """)
        next_reg_num = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO Registration (Class_ID, Mem_ID, Reg_Num)
            VALUES (%s, %s, %s)
        """, (class_id, mem_id, next_reg_num))

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/member/{mem_id}/classes", status_code=303)

@app.post("/member/{mem_id}/classes/{class_id}/drop")
def drop_class(mem_id: int, class_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM Registration
            WHERE Mem_ID = %s AND Class_ID = %s
        """, (mem_id, class_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/member/{mem_id}/classes", status_code=303)

@app.get("/member/{mem_id}/checkins")
def member_checkins(request: Request, mem_id: int):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT m.Mem_ID, m.Mem_FName, m.Mem_LName
            FROM Member m
            WHERE m.Mem_ID = %s
        """, (mem_id,))
        member = cursor.fetchone()

        if not member:
            return {"detail": "Member not found"}

        cursor.execute("""
            SELECT Check_ID, Check_Datetime, Guest_Brought
            FROM CheckIn
            WHERE Mem_ID = %s
            ORDER BY Check_Datetime DESC
        """, (mem_id,))
        checkins = cursor.fetchall()

        return templates.TemplateResponse(
            request=request,
            name="member_checkins.html",
            context={
                "member": member,
                "checkins": checkins
            }
        )
    finally:
        cursor.close()
        conn.close()
        
@app.post("/member/{mem_id}/checkin")
def create_member_checkin(
    mem_id: int,
    guest_brought: int = Form(...)
):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO CheckIn (Guest_Brought, Mem_ID)
            VALUES (%s, %s)
        """, (guest_brought, mem_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/member/{mem_id}/checkins", status_code=303)

@app.get("/employee/{emp_id}/members")
def employee_members(request: Request, emp_id: int):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT m.Mem_ID, m.Mem_FName, m.Mem_LName, m.Mem_Phone, m.Mem_DOB, t.Tier_Name, ec.Econ_FName, ec.Econ_LName, ec.Econ_Phone
            FROM Member m
            JOIN Tier t ON m.Tier_ID = t.Tier_ID
            JOIN EContact ec ON m.Econ_ID = ec.Econ_ID
            ORDER BY m.Mem_ID
        """)
        members = cursor.fetchall()

        return templates.TemplateResponse(
            request=request,
            name="employee_members.html",
            context={
                "emp_id": emp_id,
                "members": members
            }
        )
    finally:
        cursor.close()
        conn.close()
        
@app.get("/employee/{emp_id}/members/{mem_id}/edit")
def employee_edit_member(request: Request, emp_id: int, mem_id: int):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 1
            FROM Employee
            WHERE Emp_ID = %s
        """, (emp_id,))
        employee = cursor.fetchone()

        if not employee:
            return {"detail": "Employee not found"}

        cursor.execute("""
            SELECT m.Mem_ID, m.Mem_FName, m.Mem_LName, m.Mem_DOB, m.Mem_Email, m.Mem_Phone, m.Tier_ID, t.Tier_Name, t.Tier_Cost, ec.Econ_FName, ec.Econ_LName, ec.Econ_Phone
            FROM Member m
            JOIN Tier t ON m.Tier_ID = t.Tier_ID
            JOIN EContact ec ON m.Econ_ID = ec.Econ_ID
            WHERE m.Mem_ID = %s
        """, (mem_id,))
        member = cursor.fetchone()

        if not member:
            return {"detail": "Member not found"}

        return templates.TemplateResponse(
            request=request,
            name="employee_edit_member.html",
            context={
                "emp_id": emp_id,
                "member": member
            }
        )
    finally:
        cursor.close()
        conn.close()
        
@app.post("/employee/{emp_id}/members/{mem_id}/update-profile")
def employee_update_member_profile(
    emp_id: int,
    mem_id: int,
    mem_fname: str = Form(...),
    mem_lname: str = Form(...),
    mem_dob: str = Form(...),
    mem_phone: str = Form(...),
    mem_email: str = Form(...)
):
    
    name_pattern = r"^[A-Za-z\s\-']+$"
    phone_pattern = r"^\(\d{3}\)-\d{3}-\d{4}$"

    if not re.fullmatch(name_pattern, mem_fname.strip()):
        return RedirectResponse(url=f"/employee/{emp_id}/members/{mem_id}/edit", status_code=303)

    if not re.fullmatch(name_pattern, mem_lname.strip()):
        return RedirectResponse(url=f"/employee/{emp_id}/members/{mem_id}/edit", status_code=303)

    if not re.fullmatch(phone_pattern, mem_phone.strip()):
        return RedirectResponse(url=f"/employee/{emp_id}/members/{mem_id}/edit", status_code=303)

    if len(mem_email.strip()) > 45:
        return RedirectResponse(url=f"/employee/{emp_id}/members/{mem_id}/edit", status_code=303)

    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Member
            SET Mem_FName = %s,
                Mem_LName = %s,
                Mem_DOB = %s,
                Mem_Phone = %s,
                Mem_Email = %s
            WHERE Mem_ID = %s
        """, (mem_fname, mem_lname, mem_dob, mem_phone, mem_email, mem_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/members/{mem_id}/edit", status_code=303)

@app.post("/employee/{emp_id}/members/{mem_id}/update-contact")
def employee_update_member_contact(
    emp_id: int,
    mem_id: int,
    econ_fname: str = Form(...),
    econ_lname: str = Form(...),
    econ_phone: str = Form(...)
):
    
    name_pattern = r"^[A-Za-z\s\-']+$"
    phone_pattern = r"^\(\d{3}\)-\d{3}-\d{4}$"

    if not re.fullmatch(name_pattern, econ_fname.strip()):
        return RedirectResponse(url=f"/employee/{emp_id}/members/{mem_id}/edit", status_code=303)

    if not re.fullmatch(name_pattern, econ_lname.strip()):
        return RedirectResponse(url=f"/employee/{emp_id}/members/{mem_id}/edit", status_code=303)

    if not re.fullmatch(phone_pattern, econ_phone.strip()):
        return RedirectResponse(url=f"/employee/{emp_id}/members/{mem_id}/edit", status_code=303)

    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE EContact ec
            JOIN Member m ON m.Econ_ID = ec.Econ_ID
            SET ec.Econ_FName = %s,
                ec.Econ_LName = %s,
                ec.Econ_Phone = %s
            WHERE m.Mem_ID = %s
        """, (econ_fname, econ_lname, econ_phone, mem_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/members/{mem_id}/edit", status_code=303)

@app.post("/employee/{emp_id}/members/{mem_id}/update-tier")
def employee_update_member_tier(
    emp_id: int,
    mem_id: int,
    tier_id: int = Form(...)
):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Member
            SET Tier_ID = %s
            WHERE Mem_ID = %s
        """, (tier_id, mem_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/members/{mem_id}/edit", status_code=303)

@app.post("/employee/{emp_id}/members/{mem_id}/delete")
def employee_delete_member(emp_id: int, mem_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT Econ_ID
            FROM Member
            WHERE Mem_ID = %s
        """, (mem_id,))
        member_row = cursor.fetchone()

        if not member_row:
            return RedirectResponse(url=f"/employee/{emp_id}/members", status_code=303)

        econ_id = member_row[0]

        cursor.execute("DELETE FROM CheckIn WHERE Mem_ID = %s", (mem_id,))
        cursor.execute("DELETE FROM Registration WHERE Mem_ID = %s", (mem_id,))
        cursor.execute("DELETE FROM Member WHERE Mem_ID = %s", (mem_id,))
        cursor.execute("DELETE FROM EContact WHERE Econ_ID = %s", (econ_id,))

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/members", status_code=303)

@app.get("/employee/{emp_id}/members/new")
def employee_new_member(request: Request, emp_id: int):
    return templates.TemplateResponse(
        request=request,
        name="employee_new_member.html",
        context={"emp_id": emp_id}
    )

@app.post("/employee/{emp_id}/members/create")
def employee_create_member(
    request: Request,
    emp_id: int,
    mem_fname: str = Form(...),
    mem_lname: str = Form(...),
    mem_dob: str = Form(...),
    mem_phone: str = Form(...),
    mem_email: str = Form(...),
    tier_id: str = Form(...),
    econ_fname: str = Form(...),
    econ_lname: str = Form(...),
    econ_phone: str = Form(...)
):
    form_data = {
        "mem_fname": mem_fname.strip(),
        "mem_lname": mem_lname.strip(),
        "mem_dob": mem_dob.strip(),
        "mem_phone": mem_phone.strip(),
        "mem_email": mem_email.strip(),
        "tier_id": tier_id.strip(),
        "econ_fname": econ_fname.strip(),
        "econ_lname": econ_lname.strip(),
        "econ_phone": econ_phone.strip(),
    }

    def render_error(message: str):
        return templates.TemplateResponse(
            request=request,
            name="employee_new_member.html",
            context={
                "emp_id": emp_id,
                "error": message,
                "form_data": form_data
            }
        )

    name_pattern = r"^[A-Za-z\s\-']+$"
    phone_pattern = r"^\(\d{3}\)-\d{3}-\d{4}$"

    if not re.fullmatch(name_pattern, form_data["mem_fname"]):
        return render_error("Member first name must contain letters only.")
    if not re.fullmatch(name_pattern, form_data["mem_lname"]):
        return render_error("Member last name must contain letters only.")
    if not re.fullmatch(name_pattern, form_data["econ_fname"]):
        return render_error("Emergency contact first name must contain letters only.")
    if not re.fullmatch(name_pattern, form_data["econ_lname"]):
        return render_error("Emergency contact last name must contain letters only.")
    if not re.fullmatch(phone_pattern, form_data["mem_phone"]):
        return render_error("Member phone must be in the format (###)-###-####.")
    if not re.fullmatch(phone_pattern, form_data["econ_phone"]):
        return render_error("Emergency contact phone must be in the format (###)-###-####.")
    if len(form_data["mem_email"]) > 45:
        return render_error("Email is too long.")
    if form_data["tier_id"] not in ("1", "2"):
        return render_error("Please choose a valid membership tier.")

    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO EContact (Econ_FName, Econ_LName, Econ_Phone)
            VALUES (%s, %s, %s)
        """, (form_data["econ_fname"], form_data["econ_lname"], form_data["econ_phone"]))
        econ_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO Member (
                Mem_FName, Mem_LName, Mem_DOB, Mem_Email,
                Mem_Phone, Tier_ID, Econ_ID
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            form_data["mem_fname"],
            form_data["mem_lname"],
            form_data["mem_dob"],
            form_data["mem_email"],
            form_data["mem_phone"],
            int(form_data["tier_id"]),
            econ_id
        ))

        conn.commit()
        
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/members", status_code=303)

@app.get("/employee/{emp_id}/checkins")
def employee_checkins(request: Request, emp_id: int):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT Mem_ID, Mem_FName, Mem_LName
            FROM Member
            ORDER BY Mem_FName, Mem_LName
        """)
        members = cursor.fetchall()

        cursor.execute("""
            SELECT c.Check_ID, c.Check_Datetime, c.Guest_Brought, m.Mem_ID, m.Mem_FName, m.Mem_LName
            FROM CheckIn c
            JOIN Member m ON c.Mem_ID = m.Mem_ID
            ORDER BY c.Check_Datetime DESC
        """)
        checkins = cursor.fetchall()

        cursor.execute("""
            SELECT COUNT(*) AS count
            FROM CheckIn
            WHERE DATE(Check_Datetime) = CURDATE()
        """)
        today_checkins = cursor.fetchone()["count"]

        return templates.TemplateResponse(
            request=request,
            name="employee_checkins.html",
            context={
                "emp_id": emp_id,
                "members": members,
                "checkins": checkins,
                "today_checkins": today_checkins
            }
        )
    finally:
        cursor.close()
        conn.close()

@app.post("/employee/{emp_id}/checkins/create")
def employee_create_checkin(
    emp_id: int,
    mem_id: int = Form(...),
    guest_brought: int = Form(...)
):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO CheckIn (Guest_Brought, Mem_ID)
            VALUES (%s, %s)
        """, (guest_brought, mem_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/checkins", status_code=303)

@app.get("/employee/{emp_id}/classes")
def employee_classes(request: Request, emp_id: int):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT c.Class_ID, c.Class_Name, c.Class_Start, c.Class_Length, c.Class_Cap, CONCAT(e.Emp_FName, ' ', e.Emp_LName) AS Instructor, COUNT(r.Mem_ID) AS Enrolled_Count
            FROM Class c
            JOIN Employee e ON c.Emp_ID = e.Emp_ID
            LEFT JOIN Registration r ON c.Class_ID = r.Class_ID
            GROUP BY c.Class_ID, c.Class_Name, c.Class_Start, c.Class_Length, c.Class_Cap, e.Emp_FName, e.Emp_LName
            ORDER BY c.Class_Start
        """)
        classes = cursor.fetchall()

        return templates.TemplateResponse(
            request=request,
            name="employee_classes.html",
            context={
                "emp_id": emp_id,
                "classes": classes
            }
        )
    finally:
        cursor.close()
        conn.close()
        
@app.get("/employee/{emp_id}/classes/{class_id}/edit")
def employee_edit_class(request: Request, emp_id: int, class_id: int):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT c.Class_ID, c.Class_Name, c.Class_Start, c.Class_Length, c.Class_Cap, c.Emp_ID, CONCAT(e.Emp_FName, ' ', e.Emp_LName) AS Instructor
            FROM Class c
            JOIN Employee e ON c.Emp_ID = e.Emp_ID
            WHERE c.Class_ID = %s
        """, (class_id,))
        cls = cursor.fetchone()

        if not cls:
            return {"detail": "Class not found"}

        cursor.execute("""
            SELECT Emp_ID, Emp_FName, Emp_LName
            FROM Employee
            ORDER BY Emp_FName, Emp_LName
        """)
        employees = cursor.fetchall()

        return templates.TemplateResponse(
            request=request,
            name="employee_edit_class.html",
            context={
                "emp_id": emp_id,
                "cls": cls,
                "employees": employees
            }
        )
    finally:
        cursor.close()
        conn.close()
        
@app.post("/employee/{emp_id}/classes/{class_id}/update")
def employee_update_class(
    request: Request,
    emp_id: int,
    class_id: int,
    class_name: str = Form(...),
    class_start: str = Form(...),
    class_length: int = Form(...),
    class_cap: int = Form(...),
    instructor_id: int = Form(...)
):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT c.Class_ID, c.Class_Name, c.Class_Start, c.Class_Length, c.Class_Cap, c.Emp_ID, CONCAT(e.Emp_FName, ' ', e.Emp_LName) AS Instructor
            FROM Class c
            JOIN Employee e ON c.Emp_ID = e.Emp_ID
            WHERE c.Class_ID = %s
        """, (class_id,))
        cls = cursor.fetchone()

        cursor.execute("""
            SELECT Emp_ID, Emp_FName, Emp_LName
            FROM Employee
            ORDER BY Emp_FName, Emp_LName
        """)
        employees = cursor.fetchall()

        cursor.execute("""
            SELECT 1
            FROM Class
            WHERE Emp_ID = %s AND Class_ID <> %s
        """, (instructor_id, class_id))
        conflicting_class = cursor.fetchone()

        if conflicting_class:
            return templates.TemplateResponse(
                request=request,
                name="employee_edit_class.html",
                context={
                    "emp_id": emp_id,
                    "cls": cls,
                    "employees": employees,
                    "error": "That employee is already assigned to another class."
                }
            )

        cursor2 = conn.cursor()
        try:
            cursor2.execute("""
                UPDATE Class
                SET Class_Name = %s,
                    Class_Start = %s,
                    Class_Length = %s,
                    Class_Cap = %s,
                    Emp_ID = %s
                WHERE Class_ID = %s
            """, (class_name, class_start, class_length, class_cap, instructor_id, class_id))
            conn.commit()
        finally:
            cursor2.close()

    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/classes/{class_id}/edit", status_code=303)

@app.post("/employee/{emp_id}/classes/{class_id}/delete")
def employee_delete_class(emp_id: int, class_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM Registration
            WHERE Class_ID = %s
        """, (class_id,))

        cursor.execute("""
            DELETE FROM Class
            WHERE Class_ID = %s
        """, (class_id,))

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/classes", status_code=303)

@app.get("/employee/{emp_id}/classes/new")
def employee_new_class(request: Request, emp_id: int):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT e.Emp_ID, e.Emp_FName, e.Emp_LName
            FROM Employee e
            LEFT JOIN Class c ON e.Emp_ID = c.Emp_ID
            WHERE c.Emp_ID IS NULL
            ORDER BY e.Emp_FName, e.Emp_LName
        """)
        available_employees = cursor.fetchall()

        return templates.TemplateResponse(
            request=request,
            name="employee_new_class.html",
            context={
                "emp_id": emp_id,
                "available_employees": available_employees
            }
        )
    finally:
        cursor.close()
        conn.close()

@app.post("/employee/{emp_id}/classes/create")
def employee_create_class(
    request: Request,
    emp_id: int,
    class_name: str = Form(...),
    class_start: str = Form(...),
    class_length: int = Form(...),
    class_cap: int = Form(...),
    instructor_id: int = Form(...)
):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT e.Emp_ID, e.Emp_FName, e.Emp_LName
            FROM Employee e
            LEFT JOIN Class c ON e.Emp_ID = c.Emp_ID
            WHERE c.Emp_ID IS NULL
            ORDER BY e.Emp_FName, e.Emp_LName
        """)
        available_employees = cursor.fetchall()

        if class_cap < 1 or class_cap > 10:
            return templates.TemplateResponse(
                request=request,
                name="employee_new_class.html",
                context={
                    "emp_id": emp_id,
                    "available_employees": available_employees,
                    "error": "Capacity must be between 1 and 10."
                }
            )

        cursor.execute("""
            SELECT 1
            FROM Class
            WHERE Emp_ID = %s
        """, (instructor_id,))
        existing_assignment = cursor.fetchone()

        if existing_assignment:
            return templates.TemplateResponse(
                request=request,
                name="employee_new_class.html",
                context={
                    "emp_id": emp_id,
                    "available_employees": available_employees,
                    "error": "That employee is already assigned to another class."
                }
            )

        cursor2 = conn.cursor()
        try:
            cursor2.execute("""
                INSERT INTO Class (
                    Class_Name,
                    Class_Start,
                    Class_Length,
                    Class_Cap,
                    Emp_ID
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (class_name, class_start, class_length, class_cap, instructor_id))
            conn.commit()
        finally:
            cursor2.close()

    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/classes", status_code=303)

@app.get("/employee/{emp_id}/attendance")
def employee_attendance(request: Request, emp_id: int):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT c.Class_ID, c.Class_Name, c.Class_Start, c.Class_Length, c.Class_Cap, c.Emp_ID, CONCAT(e.Emp_FName, ' ', e.Emp_LName) AS Instructor, COUNT(r.Mem_ID) AS Enrolled_Count
            FROM Class c
            JOIN Employee e ON c.Emp_ID = e.Emp_ID
            LEFT JOIN Registration r ON c.Class_ID = r.Class_ID
            GROUP BY c.Class_ID, c.Class_Name, c.Class_Start, c.Class_Length, c.Class_Cap, c.Emp_ID, e.Emp_FName, e.Emp_LName
            ORDER BY c.Class_Start
        """)
        classes = cursor.fetchall()

        for cls in classes:
            cursor.execute("""
                SELECT m.Mem_ID, m.Mem_FName, m.Mem_LName, r.Reg_Num
                FROM Registration r
                JOIN Member m ON r.Mem_ID = m.Mem_ID
                WHERE r.Class_ID = %s
                ORDER BY r.Reg_Num
            """, (cls["Class_ID"],))
            cls["members"] = cursor.fetchall()

            cursor.execute("""
                SELECT m.Mem_ID, m.Mem_FName, m.Mem_LName
                FROM Member m
                JOIN Tier t ON m.Tier_ID = t.Tier_ID
                WHERE t.Tier_Name = 'Premium'
                  AND m.Mem_ID NOT IN (
                      SELECT Mem_ID
                      FROM Registration
                      WHERE Class_ID = %s
                  )
                ORDER BY m.Mem_FName, m.Mem_LName
            """, (cls["Class_ID"],))
            cls["available_members"] = cursor.fetchall()

        return templates.TemplateResponse(
            request=request,
            name="employee_attendance.html",
            context={
                "emp_id": emp_id,
                "classes": classes
            }
        )
    finally:
        cursor.close()
        conn.close()

@app.post("/employee/{emp_id}/attendance/{class_id}/add")
def employee_add_attendance_member(
    emp_id: int,
    class_id: int,
    mem_id: int = Form(...)
):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT Tier_ID
            FROM Member
            WHERE Mem_ID = %s
        """, (mem_id,))
        member_row = cursor.fetchone()
        if not member_row or member_row[0] != 2:
            return RedirectResponse(url=f"/employee/{emp_id}/attendance", status_code=303)

        cursor.execute("""
            SELECT COUNT(*)
            FROM Registration
            WHERE Class_ID = %s AND Mem_ID = %s
        """, (class_id, mem_id))
        already_in_class = cursor.fetchone()[0]
        if already_in_class:
            return RedirectResponse(url=f"/employee/{emp_id}/attendance", status_code=303)

        cursor.execute("""
            SELECT Class_Cap
            FROM Class
            WHERE Class_ID = %s
        """, (class_id,))
        class_row = cursor.fetchone()
        if not class_row:
            return RedirectResponse(url=f"/employee/{emp_id}/attendance", status_code=303)

        class_cap = class_row[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM Registration
            WHERE Class_ID = %s
        """, (class_id,))
        enrolled_count = cursor.fetchone()[0]

        if enrolled_count >= class_cap:
            return RedirectResponse(url=f"/employee/{emp_id}/attendance", status_code=303)

        cursor.execute("""
            SELECT COALESCE(MAX(Reg_Num), 0) + 1
            FROM Registration
            WHERE Class_ID = %s
        """, (class_id,))
        next_reg_num = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO Registration (Class_ID, Mem_ID, Reg_Num)
            VALUES (%s, %s, %s)
        """, (class_id, mem_id, next_reg_num))

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/attendance", status_code=303)

@app.post("/employee/{emp_id}/attendance/{class_id}/remove/{mem_id}")
def employee_remove_attendance_member(emp_id: int, class_id: int, mem_id: int):
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM Registration
            WHERE Class_ID = %s AND Mem_ID = %s
        """, (class_id, mem_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/attendance", status_code=303)

@app.get("/employee/{emp_id}/equipment")
def employee_equipment(request: Request, emp_id: int):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT Equip_ID, Equip_Name, Equip_Status
            FROM Equipment
            ORDER BY Equip_ID
        """)
        equipment = cursor.fetchall()

        total_equipment = len(equipment)
        operational_count = sum(1 for item in equipment if item["Equip_Status"] == "Operational")
        non_operational_count = sum(1 for item in equipment if item["Equip_Status"] != "Operational")

        return templates.TemplateResponse(
            request=request,
            name="employee_equipment.html",
            context={
                "emp_id": emp_id,
                "equipment": equipment,
                "total_equipment": total_equipment,
                "operational_count": operational_count,
                "non_operational_count": non_operational_count
            }
        )
    finally:
        cursor.close()
        conn.close()

@app.post("/employee/{emp_id}/equipment/{equip_id}/toggle")
def employee_toggle_equipment_status(emp_id: int, equip_id: int):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT Equip_Status
            FROM Equipment
            WHERE Equip_ID = %s
        """, (equip_id,))
        row = cursor.fetchone()

        if not row:
            return RedirectResponse(url=f"/employee/{emp_id}/equipment", status_code=303)

        current_status = row["Equip_Status"]

        if current_status == "Operational":
            cursor.execute("""
                UPDATE Equipment
                SET Equip_Status = 'Non-Operational'
                WHERE Equip_ID = %s
            """, (equip_id,))

            cursor.execute("""
                INSERT INTO Ticket (Ticket_Desc, Ticket_Status, Emp_ID, Equip_ID)
                VALUES (%s, 'Open', %s, %s)
            """, ("Description pending.", emp_id, equip_id))

        else:
            cursor.execute("""
                UPDATE Equipment
                SET Equip_Status = 'Operational'
                WHERE Equip_ID = %s
            """, (equip_id,))

            cursor.execute("""
                UPDATE Ticket
                SET Ticket_Status = 'Resolved'
                WHERE Equip_ID = %s AND Ticket_Status = 'Open'
            """, (equip_id,))

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/equipment", status_code=303)

@app.post("/employee/{emp_id}/equipment/create")
def employee_create_equipment(
    emp_id: int,
    equip_name: str = Form(...)
):
    equip_name = equip_name.strip()

    if not equip_name:
        return RedirectResponse(url=f"/employee/{emp_id}/equipment", status_code=303)

    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO Equipment (Equip_Name)
            VALUES (%s)
        """, (equip_name,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/equipment", status_code=303)

@app.get("/employee/{emp_id}/tickets")
def employee_tickets(request: Request, emp_id: int):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT t.Ticket_ID, t.Ticket_Date, t.Ticket_Desc, t.Ticket_Status, e.Equip_Name, emp.Emp_FName, emp.Emp_LName
            FROM Ticket t
            JOIN Equipment e ON t.Equip_ID = e.Equip_ID
            JOIN Employee emp ON t.Emp_ID = emp.Emp_ID
            ORDER BY t.Ticket_Date DESC
        """)
        tickets = cursor.fetchall()

        open_tickets = [ticket for ticket in tickets if ticket["Ticket_Status"] == "Open"]
        resolved_tickets = [ticket for ticket in tickets if ticket["Ticket_Status"] != "Open"]

        return templates.TemplateResponse(
            request=request,
            name="employee_tickets.html",
            context={
                "emp_id": emp_id,
                "open_tickets": open_tickets,
                "resolved_tickets": resolved_tickets,
                "open_count": len(open_tickets),
                "resolved_count": len(resolved_tickets)
            }
        )
    finally:
        cursor.close()
        conn.close()

@app.post("/employee/{emp_id}/tickets/{ticket_id}/resolve")
def employee_resolve_ticket(emp_id: int, ticket_id: int):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT Equip_ID
            FROM Ticket
            WHERE Ticket_ID = %s
        """, (ticket_id,))
        ticket = cursor.fetchone()

        if not ticket:
            return RedirectResponse(url=f"/employee/{emp_id}/tickets", status_code=303)

        equip_id = ticket["Equip_ID"]

        cursor.execute("""
            UPDATE Ticket
            SET Ticket_Status = 'Resolved'
            WHERE Ticket_ID = %s
        """, (ticket_id,))

        cursor.execute("""
            UPDATE Equipment
            SET Equip_Status = 'Operational'
            WHERE Equip_ID = %s
        """, (equip_id,))

        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/tickets", status_code=303)

@app.post("/employee/{emp_id}/tickets/{ticket_id}/update-description")
def employee_update_ticket_description(
    emp_id: int,
    ticket_id: int,
    ticket_desc: str = Form(...)
):
    ticket_desc = ticket_desc.strip()

    if not ticket_desc:
        return RedirectResponse(url=f"/employee/{emp_id}/tickets", status_code=303)

    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Ticket
            SET Ticket_Desc = %s
            WHERE Ticket_ID = %s
        """, (ticket_desc, ticket_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url=f"/employee/{emp_id}/tickets", status_code=303)
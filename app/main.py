import os
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from mysql.connector import pooling
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse

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
                return RedirectResponse(url=f"/employee/{user_id}", status_code=303)

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
            SELECT
                m.Mem_ID,
                m.Mem_FName,
                m.Mem_LName,
                m.Mem_DOB,
                m.Mem_Email,
                m.Mem_Phone,
                t.Tier_Name,
                t.Tier_Cost,
                ec.Econ_FName,
                ec.Econ_LName,
                ec.Econ_Phone,
                m.Tier_ID
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
            SELECT
                m.Mem_ID,
                m.Mem_FName,
                m.Mem_LName,
                m.Tier_ID,
                t.Tier_Name
            FROM Member m
            JOIN Tier t ON m.Tier_ID = t.Tier_ID
            WHERE m.Mem_ID = %s
        """, (mem_id,))
        member = cursor.fetchone()

        if not member:
            return {"detail": "Member not found"}

        cursor.execute("""
            SELECT
                c.Class_ID,
                c.Class_Name,
                c.Class_Start,
                c.Class_Length,
                c.Class_Cap,
                c.Emp_ID,
                CONCAT(e.Emp_FName, ' ', e.Emp_LName) AS Instructor,
                COUNT(r.Mem_ID) AS Enrolled_Count,
                MAX(CASE WHEN r.Mem_ID = %s THEN 1 ELSE 0 END) AS Is_Enrolled
            FROM Class c
            JOIN Employee e ON c.Emp_ID = e.Emp_ID
            LEFT JOIN Registration r ON c.Class_ID = r.Class_ID
            GROUP BY
                c.Class_ID,
                c.Class_Name,
                c.Class_Start,
                c.Class_Length,
                c.Class_Cap,
                c.Emp_ID,
                e.Emp_FName,
                e.Emp_LName
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
            SELECT
                m.Mem_ID,
                m.Mem_FName,
                m.Mem_LName
            FROM Member m
            WHERE m.Mem_ID = %s
        """, (mem_id,))
        member = cursor.fetchone()

        if not member:
            return {"detail": "Member not found"}

        cursor.execute("""
            SELECT
                Check_ID,
                Check_Datetime,
                Guest_Brought
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

@app.get("/employee/{emp_id}")
def employee_placeholder(emp_id: int):
    return {"detail": f"Employee page for ID {emp_id} not built yet"}
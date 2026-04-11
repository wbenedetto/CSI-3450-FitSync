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

# @app.get("/")
# def dashboard(request: Request):
#     """
#     Renders a very simple test page.
#     Fetches all Member records from the database.
#     """
#     conn = get_db_conn()
#     cursor = conn.cursor(dictionary=True)

#     try:
#         cursor.execute("SELECT * FROM Member")
#         members = cursor.fetchall()

#         return templates.TemplateResponse(
#             request=request,
#             name="dashboard.html", #TEST HTML FILE - CHANGE THIS TO (index.html) LATER
#             context={"members": members}
#         )
#     finally:
#         cursor.close()
#         conn.close()

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )

@app.post("/login")
def login(role: str = Form(...)):
    if role == "member":
        return RedirectResponse(url="/member", status_code=303)
    return RedirectResponse(url="/employee", status_code=303)

@app.get("/member")
def member_placeholder():
    return {"detail": "Member page not built yet"}

@app.get("/employee")
def employee_placeholder():
    return {"detail": "Employee page not built yet"}
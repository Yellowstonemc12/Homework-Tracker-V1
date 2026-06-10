from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from supabase import create_client
from datetime import datetime

app = FastAPI()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

@app.get("/supabase-test")
async def supabase_test():
    result = supabase.table("test_connection").insert({
        "message": "Hello from Vercel!"
    }).execute()

    return {
        "success": True,
        "data": result.data
    }

@app.get("/debug")
def debug():
    return {
        "url": SUPABASE_URL
    }

# ===== MEMORY STORAGE =====
data_store = {}
history_store = {}

# ===== STYLE =====
def style():
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500&display=swap');

    body{
        font-family:'Fredoka',sans-serif;
        background:#f5f3ff;
        padding:20px;
        color:#444;
    }

    .wrapper{
        max-width:750px;
        margin:auto;
    }

    .header{
        display:flex;
        justify-content:space-between;
        align-items:center;
        margin-bottom:10px;
    }

    h2{
        font-weight:500;
        margin:0;
    }

    .stats{
        display:flex;
        gap:10px;
        margin:15px 0;
    }

    .stat{
        flex:1;
        background:white;
        padding:10px;
        border-radius:12px;
        text-align:center;
        box-shadow:0 2px 6px rgba(0,0,0,.04);
    }

    .stat-title{
        font-size:12px;
        color:#888;
    }

    .stat-value{
        font-size:18px;
        color:#6d28d9;
    }

    .card{
        background:white;
        padding:16px;
        border-radius:14px;
        margin-bottom:15px;
        box-shadow:0 2px 8px rgba(0,0,0,.04);
    }

    input,select{
        width:100%;
        padding:10px;
        margin:6px 0;
        border-radius:10px;
        border:1px solid #eee;
        font-family:inherit;
        box-sizing:border-box;
    }

    button{
        padding:10px 16px;
        background:#8b5cf6;
        color:white;
        border:none;
        border-radius:10px;
        cursor:pointer;
        font-family:inherit;
    }

    button:hover{
        background:#7c3aed;
    }

    .logout{
        background:#fda4af;
    }

    .logout:hover{
        background:#fb7185;
    }

    table{
        width:100%;
        border-collapse:collapse;
        margin-top:10px;
    }

    th,td{
        padding:8px;
        text-align:center;
    }

    th{
        background:#f5f3ff;
    }

    tr{
        border-bottom:1px solid #eee;
    }
    </style>
    """

# ===== LOGIN =====
@app.get("/", response_class=HTMLResponse)
def login():
    return f"""
    {style()}

    <div class="wrapper">
        <div class="card">

            <h2>✨ Homework Tracker</h2>

            <form method="post" action="/login">

                <input
                    name="username"
                    placeholder="Enter your name"
                    required
                >

                <button>Enter</button>

            </form>

        </div>
    </div>
    """

@app.post("/login")
async def do_login(request: Request):

    form = await request.form()

    username = form.get("username")

    return RedirectResponse(
        url=f"/home?user={username}",
        status_code=303
    )

# ===== HOME =====
@app.get("/home", response_class=HTMLResponse)
def home(user: str = ""):

    if not user:
        return RedirectResponse("/", status_code=303)

    active = data_store.get(user, [])

    total = len(active)

    students = len(
        set(item["student"] for item in active)
    ) if active else 0

    priority = sum(
        1 for item in active
        if item["priority"] == "High"
    )

    rows = ""

    for item in active:
        rows += f"""
        <tr>
            <td>{item['date']}</td>
            <td>{item['homework']}</td>
            <td>{item['student']}</td>
            <td>{item['priority']}</td>
            <td>
                <form method="post"
                      action="/complete/{user}/{item['id']}">
                    <button>Done</button>
                </form>
            </td>
        </tr>
        """

    return f"""
    {style()}

    <div class="wrapper">

        <div class="header">

            <h2>📚 Homework Tracker</h2>

            <div>

                <form action="/history"
                      method="get"
                      style="display:inline;">

                    <input
                        type="hidden"
                        name="user"
                        value="{user}"
                    >

                    <button>
                        📜 History
                    </button>

                </form>

                <form action="/"
                      method="get"
                      style="display:inline;">

                    <button class="logout">
                        Logout
                    </button>

                </form>

            </div>

        </div>

        <div class="stats">

            <div class="stat">
                <div class="stat-title">Total</div>
                <div class="stat-value">{total}</div>
            </div>

            <div class="stat">
                <div class="stat-title">Students</div>
                <div class="stat-value">{students}</div>
            </div>

            <div class="stat">
                <div class="stat-title">Priority</div>
                <div class="stat-value">{priority}</div>
            </div>

        </div>

        <div class="card">

            <h3>Add Record</h3>

            <form method="post" action="/add">

                <input
                    type="hidden"
                    name="user"
                    value="{user}"
                >

                <input
                    name="homework"
                    placeholder="Homework"
                    required
                >

                <input
                    name="student"
                    placeholder="Student"
                    required
                >

                <select name="priority">
                    <option>Low</option>
                    <option>Medium</option>
                    <option>High</option>
                </select>

                <button>Add</button>

            </form>

        </div>

        <div class="card">

            <h3>Records</h3>

            <table>

                <tr>
                    <th>Date</th>
                    <th>Homework</th>
                    <th>Student</th>
                    <th>Priority</th>
                    <th></th>
                </tr>

                {rows}

            </table>

        </div>

    </div>
    """

# ===== HISTORY PAGE =====
@app.get("/history", response_class=HTMLResponse)
def history_page(user: str = ""):
    
    user_history = history_store.get(user, [])

    history_rows = ""

    for item in user_history:
        history_rows += f"""
        <tr>
            <td>{item['date']}</td>
            <td>{item['homework']}</td>
            <td>{item['student']}</td>
            <td>{item['priority']}</td>
        </tr>
        """

    student_names = sorted(
    list(
        set(
            item["student"]
            for item in user_history
        )
    )
)

    options = ""

    for student in student_names:
        options += f"""
        <option value="{student}">
            {student}
        </option>
        """

    return f"""
    {style()}

    <div class="wrapper">

        <div class="card">

            <h2>📜 History</h2>

            <table>

                <tr>
                    <th>Date</th>
                    <th>Homework</th>
                    <th>Student</th>
                    <th>Priority</th>
                </tr>

                {history_rows}

            </table>

        </div>

        <div class="card">

            <h3>Delete Student History</h3>

            <form method="post"
                  action="/delete-student?user={user}">

                <select name="student">
                    {options}
                </select>

                <button>
                    Delete Student History
                </button>

            </form>

        </div>

        <div class="card">

            <form method="post"
                  action="/delete-all?user={user}">

                <button class="logout">
                    Delete All History
                </button>

            </form>

        </div>

        <div class="card">

            <form action="/home"
                  method="get">

                <input
                    type="hidden"
                    name="user"
                    value="{user}"
                >

                <button>
                    ← Back
                </button>

            </form>

        </div>

    </div>
    """

# ===== ADD =====
@app.post("/add")
async def add(request: Request):

    form = await request.form()

    user = form.get("user")
    homework = form.get("homework")
    student = form.get("student")
    priority = form.get("priority")

    if user not in data_store:
        data_store[user] = []

    data_store[user].append({
        "id": len(data_store[user]) + 1,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "homework": homework,
        "student": student,
        "priority": priority
    })

    return RedirectResponse(
        url=f"/home?user={user}",
        status_code=303
    )

# ===== COMPLETE =====
@app.post("/complete/{user}/{item_id}")
def complete(user: str, item_id: int):

    if user in data_store:

        for i, item in enumerate(data_store[user]):

            if item["id"] == item_id:

                if user not in history_store:
                    history_store[user] = []
                
                history_store[user].append(item)

                data_store[user].pop(i)
                break

    return RedirectResponse(
        url=f"/home?user={user}",
        status_code=303
    )

# ===== DELETE STUDENT =====
@app.post("/delete-student")
async def delete_student(
    request: Request,
    user: str = ""
):
    form = await request.form()

    student = form.get("student")

    if user in history_store:
        history_store[user] = [
            item
            for item in history_store[user]
            if item["student"] != student
        ]

    return RedirectResponse(
        url=f"/history?user={user}",
        status_code=303
    )

# ===== DELETE ALL =====
@app.post("/delete-all")
def delete_all(user: str = ""):

    if user in history_store:
        history_store[user] = []

    return RedirectResponse(
        url=f"/history?user={user}",
        status_code=303
    )

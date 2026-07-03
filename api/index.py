from fastapi import FastAPI, Request
from fastapi import UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
import csv
import json
import io
import os
from supabase import create_client
from datetime import datetime
import bcrypt


app = FastAPI()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

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



        .records-section{
        margin-bottom:20px;
    }
    
    .website-footer{
        display:flex;
        justify-content:flex-end;
        margin-top:6px;
        padding-right:6px;
    }
    
    .website-link{
        color:#b3b3b3;
        text-decoration:none;
        font-size:12px;
        transition:0.2s ease;
    }
    
    .website-link:hover{
        color:#8b5cf6;
    }

    .alert-error{
        background:#fef2f2;
        color:#b91c1c;
        border:1px solid #fecaca;
        border-radius:10px;
        padding:12px;
        margin-bottom:15px;
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

            <h2>✨ Homework Tracker YS</h2>
            
            <p>Welcome back.</p>
            
            <form method="post" action="/login">
            
                <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    required
                >
            
                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    required
                >
            
                <button>
                    Log In
                </button>
            
            </form>
            
            <br>
            
            <p>
                Don't have an account?
                <a href="/signup">
                    Create one →
                </a>
            </p>
        <div>
    <div>
    """

@app.post("/login")
async def do_login(request: Request):

    form = await request.form()

    email = form.get("email")
    password = form.get("password")

    # Find the user by email
    result = (
        supabase.table("users")
        .select("*")
        .eq("email", email)
        .execute()
    )

    # User doesn't exist
    if not result.data:
        return HTMLResponse(f"""
        {style()}
        
        <div class="wrapper">
            <div class="card">
        
                <div class="alert-error">
                    ❌ Invalid email or password.
                </div>
        
                <p>
                    Please check your details and try again.
                </p>
        
                <form action="/" method="get">
                    <button>
                        ← Back to Login
                    </button>
                </form>
        
            </div>
        </div>
        """)

    user = result.data[0]

    # Check password
    if not bcrypt.checkpw(
        password.encode("utf-8"),
        user["password_hash"].encode("utf-8")
    ):
    return HTMLResponse(f"""
    {style()}
    
    <div class="wrapper">
        <div class="card">
    
            <div class="alert-error">
                ❌ Invalid email or password.
            </div>
    
            <p>
                Please check your details and try again.
            </p>
    
            <form action="/" method="get">
                <button>
                    ← Back to Login
                </button>
            </form>
    
        </div>
    </div>
    """)

    # Login successful
    return RedirectResponse(
        url=f"/home?user={user['full_name']}",
        status_code=303
    )


@app.get("/signup", response_class=HTMLResponse)
def signup():
    return f"""
    {style()}

    <div class="wrapper">
        <div class="card">

            <h2>Create Account</h2>
            <p>Sign up to use Homework Tracker YS.</p>

            <form method="post" action="/signup">

                <input
                    name="full_name"
                    placeholder="Username"
                    required
                >

                <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    required
                >

                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    required
                >

                <button>Create Account</button>

            </form>

            <br>

            <a href="/">
                ← Back to Login
            </a>

        </div>
    </div>
    """


@app.post("/signup")
async def signup_post(request: Request):
    form = await request.form()

    full_name = form.get("full_name")
    email = form.get("email")
    password = form.get("password")

    # Hash the password
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    # Check if the email already exists
    existing = (
        supabase.table("users")
        .select("*")
        .eq("email", email)
        .execute()
    )

    if existing.data:
        return HTMLResponse("""
            <h2>Email already registered.</h2>
            <a href="/signup">← Back</a>
        """)

    # Save the user
    supabase.table("users").insert({
        "full_name": full_name,
        "email": email,
        "password_hash": password_hash
    }).execute()

    return HTMLResponse(f"""
    {style()}
    
    <div class="wrapper">
        <div class="card">
    
            <h2>🎉 Account Created!</h2>
    
            <p>
                Your account has been created successfully.
                You can now log in.
            </p>
    
            <form action="/" method="get">
                <button>
                    Go to Login →
                </button>
            </form>
    
        </div>
    </div>
    """)

# ===== HOME =====
@app.get("/home", response_class=HTMLResponse)
def home(user: str = ""):

    if not user:
        return RedirectResponse("/", status_code=303)

    result = (
        supabase.table("homework")
        .select("*")
        .eq("username", user)
        .execute()
    )

    active = result.data

    students_result = (
        supabase.table("students")
        .select("id")
        .eq("username", user)
        .limit(1)
        .execute()
    )

    has_students = len(students_result.data) > 0

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
            <td>{item['date_created'][:10]}</td>
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

    import_card = ""

    if not has_students:
        import_card = f"""
        <div class="card">
            <h3>📂 Import Student List</h3>
    
            <form
                method="post"
                action="/import?user={user}"
                enctype="multipart/form-data"
            >
                <input
                    type="file"
                    name="file"
                    accept=".csv"
                    required
                >
    
                <button>
                    Upload CSV
                </button>
            </form>
        </div>
        """


    student_lookup = {}

    students_data = (
        supabase.table("students")
        .select("index_no, student_name")
        .eq("username", user)
        .execute()
    )
    
    for row in students_data.data:
        student_lookup[row["index_no"]] = row["student_name"]

    print(student_lookup)
    
    student_json = json.dumps(student_lookup)

    
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

        {import_card}

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
                    id="studentInput"
                    name="student"
                    placeholder="Student"
                    required
                    oninput="identifyStudent()"
                >
                
                <div
                    id="studentMatch"
                    style="
                        margin-top:4px;
                        font-size:14px;
                        color:#6d28d9;
                        opacity:0;
                        transform:translateY(-3px);
                        transition:
                            opacity 0.25s ease,
                            transform 0.25s ease;
                    "
                >
                </div>

                <select name="priority">
                    <option>Low</option>
                    <option>Medium</option>
                    <option>High</option>
                </select>

                <button>Add</button>

            </form>

        </div>

        <div class="records-section">
    
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
    
        <div class="website-footer">
            <a
                class="website-link"
                href="https://homework-tracker-ys.mystrikingly.com/"
                target="_blank"
            >
                🌐 Learn more about Homework Tracker YS →
            </a>
        </div>
    
    </div>


    <script>
    const students = {student_json};
    
    function identifyStudent() {{
    
        const value =
            document.getElementById(
                "studentInput"
            ).value.toLowerCase();
    
        const box =
            document.getElementById(
                "studentMatch"
            );
    
        if (value.trim() === "") {{
            box.style.opacity = "0";
            box.style.transform =
                "translateY(-3px)";
    
            setTimeout(() => {{
                box.innerHTML = "";
            }}, 250);
    
            return;
        }}
    
        let found = "";
    
        for (const [indexNo, name] of Object.entries(students)) {{
    
            if (
                indexNo.toLowerCase().includes(value) ||
                name.toLowerCase().includes(value)
            ) {{
                found = name;
                break;
            }}
        }}
    
        if (found) {{
            box.innerHTML =
                "✅ Student identified: " + found;
    
            box.style.opacity = "1";
            box.style.transform =
                "translateY(0)";
        }} else {{
            box.style.opacity = "0";
            box.style.transform =
                "translateY(-3px)";
    
            setTimeout(() => {{
                box.innerHTML = "";
            }}, 250);
        }}
    }}

    </script>
                 
    """

# ===== HISTORY PAGE =====

@app.get("/history", response_class=HTMLResponse)
def history_page(user: str = ""):

    result = (
        supabase.table("history")
        .select("*")
        .eq("username", user)
        .execute()
    )

    user_history = result.data

    history_rows = ""
    for item in user_history:
        history_rows += f"""
        <tr>
            <td>{item['completed_at'][:10]}</td>
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


@app.get("/debug-homework")
def debug_homework():
    result = supabase.table("homework").select("*").execute()
    return result.data

@app.get("/debug-import")
def debug_import():
    return {"ok": True}

@app.get("/debug-students")
def debug_students():
    result = supabase.table("students").select("*").execute()
    return result.data

@app.get("/debug-history")
def debug_history():
    result = supabase.table("history").select("*").execute()
    return result.data

# ===== IMPORT PAGE =====

@app.get("/import", response_class=HTMLResponse)
def import_page(user: str = ""):
    return f"""
    {style()}
    <div class="wrapper">
        <div class="card">
            <h2>📂 Import Students</h2>

            <form
                method="post"
                action="/import?user={user}"
                enctype="multipart/form-data"
            >
                <input
                    type="file"
                    name="file"
                    accept=".csv"
                    required
                >

                <button>
                    Upload CSV
                </button>
            </form>
        </div>
    </div>
    """

    
@app.post("/import")
async def import_csv(
    file: UploadFile = File(...),
    user: str = ""
):
    content = await file.read()
    text = content.decode("utf-8")

    reader = csv.reader(
        io.StringIO(text)
    )

    for row in reader:

        if len(row) < 2:
            continue

        supabase.table("students").insert({
            "username": user,
            "index_no": row[0],
            "student_name": row[1]
        }).execute()

    return RedirectResponse(
        url=f"/home?user={user}",
        status_code=303
    )
    
# ===== ADD =====

@app.post("/add")
async def add(request: Request):
    form = await request.form()

    user = form.get("user")
    homework = form.get("homework")
    student = form.get("student")
    priority = form.get("priority")

    student_result = (
        supabase.table("students")
        .select("*")
        .eq("username", user)
        .eq("index_no", student)
        .execute()
    )

    if student_result.data:
        student = student_result.data[0]["student_name"]

    supabase.table("homework").insert({
        "username": user,
        "homework": homework,
        "student": student,
        "priority": priority
    }).execute()

    return RedirectResponse(
        url=f"/home?user={user}",
        status_code=303
    )

# ===== COMPLETE =====
@app.post("/complete/{user}/{item_id}")
def complete(user: str, item_id: int):

    result = (
        supabase.table("homework")
        .select("*")
        .eq("id", item_id)
        .execute()
    )

    if result.data:
        item = result.data[0]

        supabase.table("history").insert({
            "username": user,
            "homework": item["homework"],
            "student": item["student"],
            "priority": item["priority"]
        }).execute()

        supabase.table("homework") \
            .delete() \
            .eq("id", item_id) \
            .execute()

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

    supabase.table("history") \
        .delete() \
        .eq("username", user) \
        .eq("student", student) \
        .execute()

    return RedirectResponse(
        url=f"/history?user={user}",
        status_code=303
    )

# ===== DELETE ALL =====
@app.post("/delete-all")
def delete_all(user: str = ""):

    supabase.table("history") \
        .delete() \
        .eq("username", user) \
        .execute()

    return RedirectResponse(
        url=f"/history?user={user}",
        status_code=303
    )

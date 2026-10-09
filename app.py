"""
AI-Driven Career & Skill Gap Analyzer
Aligned with UN SDG 8: Decent Work & Economic Growth | AICTE - IBM SkillsBuild

Run:  pip install -r requirements.txt
      streamlit run app.py
"""
import hashlib
import hmac
import html
import json
import re
import secrets
import sqlite3
import time
from contextlib import closing
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    from pypdf import PdfReader
except ImportError:  # PDF upload becomes optional
    PdfReader = None

# =====================================================================
# PAGE CONFIG
# =====================================================================
st.set_page_config(
    page_title="Skill Gap Analyzer",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Palette
INK = "#0C1220"
PANEL = "#141C30"
LINE = "#25304A"
TEXT = "#E8ECF4"
MUTED = "#8E9AB5"
SAFFRON = "#FFB547"
TEAL = "#3DD6C3"
CORAL = "#FF6B6B"

# =====================================================================
# STYLING
# =====================================================================
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=DM+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp {{ font-family: 'DM Sans', sans-serif; }}
.stApp {{
    background:
        radial-gradient(900px 500px at 85% -10%, rgba(255,181,71,0.10), transparent 60%),
        radial-gradient(800px 500px at -10% 110%, rgba(61,214,195,0.08), transparent 60%),
        {INK};
    color: {TEXT};
}}
#MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
.block-container {{ padding-top: 2rem; max-width: 1150px; }}

h1, h2, h3, .display {{ font-family: 'Bricolage Grotesque', sans-serif !important; letter-spacing: -0.02em; }}

/* Sidebar */
section[data-testid="stSidebar"] {{ background: {PANEL}; border-right: 1px solid {LINE}; }}
section[data-testid="stSidebar"] .brand {{
    font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.35rem;
    padding: .2rem 0 1rem 0; color: {TEXT};
}}
section[data-testid="stSidebar"] .brand span {{ color: {SAFFRON}; }}
section[data-testid="stSidebar"] .stRadio label {{
    padding: .55rem .8rem; border-radius: 10px; width: 100%; transition: background .15s;
}}
section[data-testid="stSidebar"] .stRadio label:hover {{ background: rgba(255,255,255,.05); }}
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{ gap: .15rem; }}
.userchip {{
    display:flex; align-items:center; gap:.65rem; padding:.7rem; border:1px solid {LINE};
    border-radius: 12px; margin-bottom: 1rem; background: rgba(255,255,255,.02);
}}
.avatar {{
    width:36px; height:36px; border-radius:50%; background:{SAFFRON}; color:{INK};
    display:flex; align-items:center; justify-content:center; font-weight:700;
}}
.userchip small {{ color:{MUTED}; display:block; line-height:1.1; }}

/* Hero */
.hero h1 {{ font-size: clamp(2.2rem, 5vw, 3.6rem); font-weight: 800; line-height: 1.05; margin: 0 0 1rem 0; }}
.hero p {{ color: {MUTED}; font-size: 1.1rem; max-width: 34rem; line-height: 1.6; }}
.hero .sdg {{ color: {SAFFRON}; font-size: .9rem; margin-top: 1.2rem; }}

/* Panels */
.panel {{
    background: {PANEL}; border: 1px solid {LINE}; border-radius: 16px; padding: 1.4rem 1.5rem;
}}
.stat {{ background:{PANEL}; border:1px solid {LINE}; border-radius:14px; padding:1.1rem 1.3rem; }}
.stat .label {{ color:{MUTED}; font-size:.85rem; }}
.stat .value {{ font-family:'Bricolage Grotesque'; font-weight:800; font-size:1.9rem; margin-top:.15rem; }}

.feature {{ border-left: 3px solid {SAFFRON}; padding: .2rem 0 .2rem 1rem; margin-bottom: 1.1rem; }}
.feature b {{ font-family:'Bricolage Grotesque'; font-size:1.05rem; }}
.feature div {{ color:{MUTED}; font-size:.95rem; margin-top:.15rem; }}

/* Skill chips */
.chip {{
    display:inline-block; padding:.3rem .75rem; margin:0 .35rem .45rem 0; border-radius:999px;
    font-size:.88rem; font-weight:500; border:1px solid;
}}
.chip.ok {{ color:{TEAL}; border-color:rgba(61,214,195,.4); background:rgba(61,214,195,.08); }}
.chip.miss {{ color:{CORAL}; border-color:rgba(255,107,107,.4); background:rgba(255,107,107,.08); }}
.chip.neutral {{ color:{TEXT}; border-color:{LINE}; background:rgba(255,255,255,.03); }}

/* Roadmap */
.week {{ background:{PANEL}; border:1px solid {LINE}; border-radius:14px; padding:1.1rem 1.3rem; margin-bottom:.9rem; }}
.week h4 {{ margin:0 0 .15rem 0; font-family:'Bricolage Grotesque'; font-size:1.1rem; }}
.week .theme {{ color:{SAFFRON}; font-size:.9rem; margin-bottom:.6rem; }}
.week ul {{ margin:0; padding-left:1.1rem; color:{TEXT}; }}
.week li {{ margin-bottom:.25rem; }}

/* Inputs & buttons */
.stButton > button, .stFormSubmitButton > button {{
    border-radius: 10px; font-weight: 600; border: 1px solid {LINE}; transition: transform .1s;
}}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
    background: {SAFFRON}; color: {INK}; border: none;
}}
.stButton > button:hover, .stFormSubmitButton > button:hover {{ transform: translateY(-1px); }}
.stTextInput input, .stTextArea textarea {{ border-radius: 10px; }}
div[data-baseweb="select"] > div {{ border-radius: 10px; }}
button[data-baseweb="tab"] {{ font-weight: 600; }}
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================================
# DATA
# =====================================================================
JOB_BENCHMARKS = {
    "Data Analyst": ["Python", "SQL", "Excel", "Power BI", "Tableau", "Statistics", "Pandas"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "SQL", "Docker", "Git"],
    "Full-Stack Developer": ["JavaScript", "React", "Node.js", "HTML/CSS", "Git", "SQL", "REST APIs", "Docker"],
    "Cloud Architect": ["AWS", "Docker", "Kubernetes", "Linux", "Networking", "Python", "Terraform", "Security"],
    "Cybersecurity Analyst": ["Networking", "Linux", "Python", "Ethical Hacking", "SIEM", "Cryptography", "Firewalls"],
    "DevOps Engineer": ["Docker", "Kubernetes", "CI/CD", "Linux", "Python", "Git", "AWS", "Terraform"],
}
ALL_SKILLS = sorted({s for skills in JOB_BENCHMARKS.values() for s in skills})

# Words the resume scanner looks for, per skill
SKILL_ALIASES = {
    "Python": ["python"], "SQL": ["sql", "mysql", "postgresql", "sqlite"], "Excel": ["excel", "spreadsheet"],
    "Power BI": ["power bi", "powerbi"], "Tableau": ["tableau"], "Statistics": ["statistics", "statistical"],
    "Pandas": ["pandas"], "Machine Learning": ["machine learning", "scikit-learn", "sklearn"],
    "Deep Learning": ["deep learning", "neural network"], "TensorFlow": ["tensorflow"], "PyTorch": ["pytorch"],
    "Docker": ["docker"], "Git": ["git", "github", "gitlab"], "JavaScript": ["javascript", "typescript"],
    "React": ["react", "reactjs"], "Node.js": ["node.js", "nodejs", "node js", "express"],
    "HTML/CSS": ["html", "css"], "REST APIs": ["rest api", "restful", "rest apis", "api"],
    "AWS": ["aws", "amazon web services", "ec2", "s3"], "Kubernetes": ["kubernetes", "k8s"],
    "Linux": ["linux", "ubuntu", "bash"], "Networking": ["networking", "tcp/ip", "dns", "routing"],
    "Terraform": ["terraform"], "Security": ["security", "owasp"], "Ethical Hacking": ["ethical hacking", "penetration testing", "pentest"],
    "SIEM": ["siem", "splunk"], "Cryptography": ["cryptography", "encryption"], "Firewalls": ["firewall"],
    "CI/CD": ["ci/cd", "jenkins", "github actions", "gitlab ci"],
}

WEEK_THEMES = [
    "Core foundations",
    "Hands-on practice with tools",
    "Build a project",
    "Interview prep and portfolio",
]

# =====================================================================
# DATABASE + AUTH (SQLite, salted PBKDF2 password hashes)
# =====================================================================
DB_PATH = "career_app.db"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(db()) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY, name TEXT NOT NULL, salt TEXT NOT NULL,
                pw_hash TEXT NOT NULL, skills TEXT DEFAULT '[]', created TEXT NOT NULL)"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL, role TEXT NOT NULL,
                score INTEGER NOT NULL, matched TEXT, missing TEXT, ts TEXT NOT NULL)"""
        )
        conn.commit()


def hash_pw(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 150_000).hex()


def register_user(name: str, email: str, password: str):
    name, email = name.strip(), email.strip().lower()
    if len(name) < 2:
        return False, "Enter your full name."
    if not EMAIL_RE.match(email):
        return False, "Enter a valid email address."
    if len(password) < 6:
        return False, "Password needs at least 6 characters."
    salt = secrets.token_hex(16)
    try:
        with closing(db()) as conn:
            conn.execute(
                "INSERT INTO users (email, name, salt, pw_hash, created) VALUES (?,?,?,?,?)",
                (email, name, salt, hash_pw(password, salt), datetime.now().isoformat(timespec="seconds")),
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists. Log in instead."
    return True, "Account created. You can log in now."


def authenticate(email: str, password: str):
    with closing(db()) as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
    if row and hmac.compare_digest(row["pw_hash"], hash_pw(password, row["salt"])):
        return dict(row)
    return None


def get_user(email: str):
    with closing(db()) as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return dict(row) if row else None


def save_skills(email: str, skills):
    with closing(db()) as conn:
        conn.execute("UPDATE users SET skills = ? WHERE email = ?", (json.dumps(sorted(skills)), email))
        conn.commit()


def change_password(email: str, old: str, new: str):
    if not authenticate(email, old):
        return False, "Current password is incorrect."
    if len(new) < 6:
        return False, "New password needs at least 6 characters."
    salt = secrets.token_hex(16)
    with closing(db()) as conn:
        conn.execute("UPDATE users SET salt = ?, pw_hash = ? WHERE email = ?", (salt, hash_pw(new, salt), email))
        conn.commit()
    return True, "Password updated."


def save_history(email, role, score, matched, missing):
    with closing(db()) as conn:
        conn.execute(
            "INSERT INTO history (email, role, score, matched, missing, ts) VALUES (?,?,?,?,?,?)",
            (email, role, score, json.dumps(matched), json.dumps(missing), datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()


def load_history(email) -> pd.DataFrame:
    with closing(db()) as conn:
        rows = conn.execute("SELECT role, score, ts FROM history WHERE email = ? ORDER BY id DESC", (email,)).fetchall()
    return pd.DataFrame([dict(r) for r in rows], columns=["role", "score", "ts"])


init_db()

# =====================================================================
# HELPERS
# =====================================================================
def esc(s) -> str:
    return html.escape(str(s))


def chips(items, kind):
    if not items:
        return f"<span style='color:{MUTED}'>None</span>"
    return "".join(f"<span class='chip {kind}'>{esc(i)}</span>" for i in items)


def analyze(role, user_skills):
    required = JOB_BENCHMARKS[role]
    matched = [s for s in required if s in user_skills]
    missing = [s for s in required if s not in user_skills]
    score = round(len(matched) / len(required) * 100)
    return {"role": role, "required": required, "matched": matched, "missing": missing, "score": score}


def score_label(score):
    if score >= 80:
        return "Placement ready", TEAL
    if score >= 50:
        return "Getting there", SAFFRON
    return "Early stage", CORAL


def gauge(score):
    _, colour = score_label(score)
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "%", "font": {"size": 46, "color": TEXT, "family": "Bricolage Grotesque"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": MUTED},
                "bar": {"color": colour, "thickness": 0.28},
                "bgcolor": PANEL,
                "borderwidth": 0,
                "steps": [{"range": [0, 100], "color": "#1B2540"}],
            },
        )
    )
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=0), paper_bgcolor="rgba(0,0,0,0)", font={"color": TEXT})
    return fig


def radar(required, matched):
    have = [1 if s in matched else 0 for s in required]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[1] * len(required) + [1], theta=required + [required[0]], name="Role needs",
                                  line=dict(color=SAFFRON, dash="dot"), fill=None))
    fig.add_trace(go.Scatterpolar(r=have + [have[0]], theta=required + [required[0]], name="You have",
                                  line=dict(color=TEAL), fill="toself", fillcolor="rgba(61,214,195,0.25)"))
    fig.update_layout(
        height=340, margin=dict(l=40, r=40, t=20, b=20), paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=False, range=[0, 1]),
                   angularaxis=dict(gridcolor=LINE, linecolor=LINE)),
        legend=dict(orientation="h", y=-0.1), font={"color": TEXT},
    )
    return fig


def build_roadmap(missing, role):
    """Spread missing skills across the 4 weeks."""
    half = (len(missing) + 1) // 2
    first, second = missing[:half], missing[half:]
    skill_list = ", ".join(missing) if missing else "your core skills"
    return {
        "Week 1": (WEEK_THEMES[0], [f"Learn the fundamentals of {s}" for s in first] or ["Revise fundamentals of your strongest skills"]),
        "Week 2": (WEEK_THEMES[1], [f"Practise {s} with small exercises" for s in second] or [f"Practise {s} with small exercises" for s in first]),
        "Week 3": (WEEK_THEMES[2], [f"Build one {role} project using {skill_list}", "Push the project to GitHub with a clear README"]),
        "Week 4": (WEEK_THEMES[3], ["Solve 15 role-specific interview questions", "Record a 2-minute walkthrough of your project",
                                    "Update your resume and LinkedIn with the new skills"]),
    }


def extract_resume_text(uploaded):
    if uploaded is None:
        return ""
    if uploaded.name.lower().endswith(".pdf"):
        if PdfReader is None:
            st.error("PDF reading needs the `pypdf` package. Run `pip install pypdf` or paste your resume text.")
            return ""
        return "\n".join((p.extract_text() or "") for p in PdfReader(uploaded).pages)
    return uploaded.read().decode("utf-8", errors="ignore")


def detect_skills(text):
    low = text.lower()
    found = []
    for skill, words in SKILL_ALIASES.items():
        for w in words:
            if re.search(rf"(?<![a-z0-9]){re.escape(w)}(?![a-z0-9])", low):
                found.append(skill)
                break
    return sorted(found)


# =====================================================================
# SESSION STATE
# =====================================================================
st.session_state.setdefault("user", None)
st.session_state.setdefault("last_result", None)

# =====================================================================
# SIDEBAR
# =====================================================================
user = st.session_state["user"]
st.sidebar.markdown("<div class='brand'>Skill<span>Gap</span> 🧭</div>", unsafe_allow_html=True)

if user is None:
    menu = ["Home", "Login / Register"]
else:
    initial = esc(user["name"][:1].upper())
    st.sidebar.markdown(
        f"<div class='userchip'><div class='avatar'>{initial}</div>"
        f"<div><b>{esc(user['name'])}</b><small>{esc(user['email'])}</small></div></div>",
        unsafe_allow_html=True,
    )
    menu = ["Dashboard", "Resume Scanner", "Learning Roadmap", "Profile"]

# Allow other pages to jump somewhere (e.g. after login)
if "goto" in st.session_state:
    st.session_state["nav"] = st.session_state.pop("goto")
if st.session_state.get("nav") not in menu:
    st.session_state["nav"] = menu[0]

choice = st.sidebar.radio("Navigate", menu, key="nav", label_visibility="collapsed")

if user is not None:
    st.sidebar.write("")
    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state["user"] = None
        st.session_state["last_result"] = None
        st.rerun()


# =====================================================================
# PAGES
# =====================================================================
def page_home():
    left, right = st.columns([1.25, 1], gap="large")
    with left:
        st.markdown(
            """
            <div class="hero">
              <h1>Know exactly which skills stand between you and the job.</h1>
              <p>Pick a target role, mark what you already know, and get a readiness score
              with a 4-week plan to close the gap.</p>
              <div class="sdg">Aligned with UN SDG 8: Decent Work and Economic Growth · AICTE – IBM SkillsBuild</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button("Create your free account", type="primary"):
            st.session_state["goto"] = "Login / Register"
            st.rerun()
    with right:
        st.markdown(
            f"""
            <div class="panel">
              <div class="feature"><b>Benchmark against real roles</b>
                <div>Six job profiles, from Data Analyst to DevOps Engineer.</div></div>
              <div class="feature"><b>Get a readiness score</b>
                <div>See your match percentage and the exact skills you are missing.</div></div>
              <div class="feature"><b>Follow a 4-week plan</b>
                <div>Weekly tasks built from your own skill gaps.</div></div>
              <div class="feature" style="margin-bottom:0"><b>Scan your resume</b>
                <div>Upload a PDF or text file and we find the skills for you.</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def page_auth():
    _, mid, _ = st.columns([1, 1.4, 1])
    with mid:
        st.markdown("<h2 style='text-align:center;margin-bottom:.2rem'>Welcome</h2>"
                    f"<p style='text-align:center;color:{MUTED}'>Log in to save your skills and track progress.</p>",
                    unsafe_allow_html=True)
        tab_login, tab_reg = st.tabs(["Log in", "Create account"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)
            if submitted:
                if not email or not password:
                    st.error("Enter your email and password.")
                else:
                    found = authenticate(email, password)
                    if found:
                        st.session_state["user"] = found
                        st.session_state["goto"] = "Dashboard"
                        st.rerun()
                    else:
                        st.error("Email or password is incorrect.")

        with tab_reg:
            with st.form("register_form"):
                name = st.text_input("Full name")
                new_email = st.text_input("Email", key="reg_email", placeholder="you@example.com")
                new_pass = st.text_input("Password (min 6 characters)", type="password", key="reg_pass")
                confirm = st.text_input("Confirm password", type="password")
                reg = st.form_submit_button("Create account", type="primary", use_container_width=True)
            if reg:
                if new_pass != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(name, new_email, new_pass)
                    (st.success if ok else st.error)(msg)


def page_dashboard():
    st.markdown(f"## Hi {esc(user['name'].split()[0])}, let's check your readiness")
    saved = json.loads(user.get("skills") or "[]")

    c1, c2 = st.columns([1, 2])
    with c1:
        role = st.selectbox("Target role", list(JOB_BENCHMARKS.keys()))
    with c2:
        skills = st.multiselect("Skills you already have", ALL_SKILLS, default=[s for s in saved if s in ALL_SKILLS])

    if st.button("Analyze my skill gap", type="primary"):
        with st.spinner("Comparing your skills with the role..."):
            time.sleep(0.6)
        result = analyze(role, skills)
        st.session_state["last_result"] = result
        save_history(user["email"], role, result["score"], result["matched"], result["missing"])

    result = st.session_state["last_result"]
    if not result:
        st.info("Choose a role and your skills, then select **Analyze my skill gap**.")
        return

    label, colour = score_label(result["score"])
    st.write("")
    s1, s2, s3 = st.columns(3)
    s1.markdown(f"<div class='stat'><div class='label'>Target role</div><div class='value' style='font-size:1.35rem'>{esc(result['role'])}</div></div>", unsafe_allow_html=True)
    s2.markdown(f"<div class='stat'><div class='label'>Skills matched</div><div class='value'>{len(result['matched'])} / {len(result['required'])}</div></div>", unsafe_allow_html=True)
    s3.markdown(f"<div class='stat'><div class='label'>Status</div><div class='value' style='color:{colour}'>{label}</div></div>", unsafe_allow_html=True)

    st.write("")
    g, r = st.columns(2)
    with g:
        st.markdown("#### Market readiness")
        st.plotly_chart(gauge(result["score"]), use_container_width=True)
    with r:
        st.markdown("#### Skill coverage")
        st.plotly_chart(radar(result["required"], result["matched"]), use_container_width=True)

    a, b = st.columns(2)
    with a:
        st.markdown(f"<div class='panel'><b>You have</b><br><br>{chips(result['matched'], 'ok')}</div>", unsafe_allow_html=True)
    with b:
        st.markdown(f"<div class='panel'><b>You need to learn</b><br><br>{chips(result['missing'], 'miss')}</div>", unsafe_allow_html=True)

    st.write("")
    if result["missing"]:
        st.success("Your 4-week plan is ready. Open **Learning Roadmap** from the sidebar.")
    else:
        st.balloons()
        st.success("You cover every skill for this role. Focus on projects and interview prep.")


def page_resume():
    st.markdown("## Resume Scanner")
    st.caption("Upload a .pdf or .txt resume, or paste the text. We look for skills used by the six roles.")
    role = st.selectbox("Compare with role", list(JOB_BENCHMARKS.keys()))
    up = st.file_uploader("Resume file", type=["pdf", "txt"])
    pasted = st.text_area("Or paste resume text", height=160)

    if st.button("Scan resume", type="primary"):
        text = extract_resume_text(up) or pasted
        if not text.strip():
            st.error("Upload a file or paste some text first.")
            return
        st.session_state["scan"] = {"role": role, "found": detect_skills(text)}

    scan = st.session_state.get("scan")
    if not scan:
        return
    found = scan["found"]
    result = analyze(scan["role"], found)
    st.write("")
    st.markdown(f"<div class='panel'><b>Skills found in your resume ({len(found)})</b><br><br>{chips(found, 'neutral')}</div>", unsafe_allow_html=True)
    st.write("")
    m1, m2 = st.columns(2)
    m1.metric(f"Match for {scan['role']}", f"{result['score']}%")
    m2.metric("Missing skills", len(result["missing"]))
    st.markdown(f"<div class='panel'><b>Add these to your resume or learn them</b><br><br>{chips(result['missing'], 'miss')}</div>", unsafe_allow_html=True)
    st.write("")
    if st.button("Save detected skills to my profile"):
        merged = set(json.loads(user.get("skills") or "[]")) | set(found)
        save_skills(user["email"], merged)
        st.session_state["user"] = get_user(user["email"])
        st.success("Skills saved. They will be pre-selected on your dashboard.")


def page_roadmap():
    st.markdown("## Your 4-week learning roadmap")
    result = st.session_state["last_result"]
    if not result:
        st.info("Run an analysis on the **Dashboard** first so we know which skills to plan for.")
        return
    st.markdown(f"Plan for **{esc(result['role'])}** · current readiness **{result['score']}%**")
    st.write("")
    plan = build_roadmap(result["missing"], result["role"])
    lines = []
    for week, (theme, tasks) in plan.items():
        items = "".join(f"<li>{esc(t)}</li>" for t in tasks)
        st.markdown(f"<div class='week'><h4>{week}</h4><div class='theme'>{esc(theme)}</div><ul>{items}</ul></div>", unsafe_allow_html=True)
        lines.append(f"{week}: {theme}\n" + "\n".join(f"  - {t}" for t in tasks))
    st.download_button("Download plan (.txt)", "\n\n".join(lines), file_name="4_week_roadmap.txt")


def page_profile():
    st.markdown("## Profile")
    st.markdown(f"<div class='panel'><b>{esc(user['name'])}</b><br><span style='color:{MUTED}'>{esc(user['email'])} · member since {esc(user['created'][:10])}</span></div>", unsafe_allow_html=True)
    st.write("")

    st.markdown("#### My skills")
    saved = [s for s in json.loads(user.get("skills") or "[]") if s in ALL_SKILLS]
    chosen = st.multiselect("Saved skills", ALL_SKILLS, default=saved, key="profile_skills")
    if st.button("Save skills", type="primary"):
        save_skills(user["email"], chosen)
        st.session_state["user"] = get_user(user["email"])
        st.success("Skills saved.")

    st.markdown("#### Progress")
    hist = load_history(user["email"])
    if hist.empty:
        st.info("No analyses yet. Your scores will appear here.")
    else:
        hist_sorted = hist.iloc[::-1].reset_index(drop=True)
        fig = go.Figure(go.Scatter(x=hist_sorted["ts"], y=hist_sorted["score"], mode="lines+markers",
                                   line=dict(color=SAFFRON), marker=dict(size=8)))
        fig.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(range=[0, 100], gridcolor=LINE),
                          xaxis=dict(gridcolor=LINE), font={"color": TEXT})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(hist.rename(columns={"role": "Role", "score": "Score %", "ts": "When"}), use_container_width=True, hide_index=True)

    st.markdown("#### Change password")
    with st.form("pw_form", clear_on_submit=True):
        old = st.text_input("Current password", type="password")
        new = st.text_input("New password", type="password")
        if st.form_submit_button("Update password"):
            ok, msg = change_password(user["email"], old, new)
            (st.success if ok else st.error)(msg)


# =====================================================================
# ROUTER
# =====================================================================
if choice == "Home":
    page_home()
elif choice == "Login / Register":
    page_auth()
elif user is None:
    st.warning("Please log in first.")
elif choice == "Dashboard":
    page_dashboard()
elif choice == "Resume Scanner":
    page_resume()
elif choice == "Learning Roadmap":
    page_roadmap()
elif choice == "Profile":
    page_profile()

import streamlit as st
import requests
import pandas as pd
import json
from datetime import date, datetime

# ── PAGE CONFIG ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="FENG Online Sessions Portal – Koya University",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CONSTANTS ────────────────────────────────────────────────────────
VIEW_PASSWORD  = "FENG@2026HE"
ADMIN_PASSWORD = "FENG@Admin2026"

SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyQiO8spr8SyutzZNMbbPmOTlG47wsoM36_vyOCBlULqLpxBoi3GbJxWvsxWLvemDaB/exec"

DEPARTMENTS = ["DPTE", "DARE", "DMME", "DCEN", "DCHE", "DGEN", "DSWE"]

DEPT_NAMES = {
    "DPTE": "Petroleum Engineering",
    "DARE": "Architecture Engineering",
    "DMME": "Mechanical & Manufacturing Eng.",
    "DCEN": "Civil Engineering",
    "DCHE": "Chemical Engineering",
    "DGEN": "Geotechnical Engineering",
    "DSWE": "Software Engineering",
}

DEPT_COLORS = {
    "DPTE": "#4B1E7F", "DARE": "#1e4fa0", "DMME": "#0f6e4a",
    "DCEN": "#7a2020", "DCHE": "#1a5c72", "DGEN": "#8a4a00", "DSWE": "#5c3d8a",
}

SHEET_IDS = {
    "DPTE": "1E9oXG5u_ITlnZy2yH4R7Few24JPh_DZYMM9ptUuBbQg",
    "DARE": "1V-UN0Rj2yvactIaSD9cLtbSsatwBwS7NHc6AwK0c8ww",
    "DMME": "10uJ_2Lki743P1jm3X4HboY_3gKI_Wi4J6xn12ZM3skY",
    "DCEN": "190vQBiMIyqFZRRojhc0BFtClHd4MFOiRNah8n_qdYtM",
    "DCHE": "1XF1km7oVgozs6hxNZhX0rG2kCJnUEqYwAxKjYh7c0bQ",
    "DGEN": "1yxGzAmBRa2GNk1pyJ3L21hj4ch_pl-Kn6I3hJSlZyxE",
    "DSWE": "1D32A1mdGSj8zVlBdTTka1fpeRcQ1ff3C6WUiViCAkMk",
}

PUBLISHED_CSV_URLS = {
    "DPTE": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSNVQ5GH8bCeNVk9mDw0mxthCcI9k8uloQ_s3K4kP156b63rT6_R3TvH5bOOXWgKTAeH6OgldHOueRQ/pub?gid=0&single=true&output=csv",
    "DARE": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQX2lpxikPN7PMbrrAOr670_VdY6TbcU12uBNkHi06U4sWKvYC61kd5tACaLz69HnXsnf7WspqYwZy/pub?output=csv",
    "DMME": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQiYk9qjKt9AYoEkOTe_iUSctC5s4wh-XkJl8BUldgiu_9ccysAX3LOF2VLH-si5u5zQoe5ixE3lfyQ/pub?output=csv",
    "DCEN": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRC-QPhkaJoyWbnagq4EjT3sScpG1c-l3Tmx2URFqNg9gc0ZBzkfB7yD05xYja_yRcTr7Nl7hRh5mPf/pub?output=csv",
    "DCHE": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTaxSh3NftPVKskBgUxTbqWvzdpDzsY9nW2A-BmsQllpTM1YeyhxzL3k6hRyp4PrVzqkgrHNvA4uBTs/pub?output=csv",
    "DGEN": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRY6ZncPIHgWVGB6xG8Kiiu7FMiC5VBAwo4gt4H2QFCQFAQiOSumvBDvF2hlcQ2nQaV9YEiPFtvQnG0/pub?output=csv",
    "DSWE": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS5YCWxkEtuskhr_HtxtZgLfqymAx9Q4GO4hFX2Ed9shOrPLj_vaPCuW2mUA1roJhn4EH8XGmmlxjmj/pub?output=csv",
}

# ── SESSION STATE ────────────────────────────────────────────────────
if "authenticated_view" not in st.session_state:
    st.session_state.authenticated_view = False
if "authenticated_admin" not in st.session_state:
    st.session_state.authenticated_admin = False
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Submit Session"

# ── STYLING ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Header */
.feng-header {
    background: linear-gradient(135deg, #2e0e52 0%, #4B1E7F 55%, #6b35a8 100%);
    padding: 22px 36px;
    border-radius: 16px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 4px 32px rgba(46,14,82,0.45);
}
.feng-header h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.6rem;
    color: white;
    margin: 0;
    line-height: 1.3;
}
.feng-header .sub {
    font-size: 0.78rem;
    color: #f5e6a3;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin-top: 4px;
}
.feng-badge {
    margin-left: auto;
    background: rgba(201,168,76,0.2);
    border: 1px solid rgba(201,168,76,0.5);
    color: #f5e6a3;
    padding: 6px 16px;
    border-radius: 30px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    white-space: nowrap;
}

/* Session cards */
.session-card {
    background: white;
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 14px;
    border: 1px solid #d8cff0;
    box-shadow: 0 2px 12px rgba(75,30,127,0.08);
    transition: box-shadow 0.2s;
}
.session-card.completed { opacity: 0.7; border-color: #e5e7eb; }
.card-top { display: flex; gap: 8px; margin-bottom: 10px; align-items: center; }
.dept-badge {
    color: white;
    padding: 3px 11px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}
.type-badge {
    padding: 3px 11px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.type-live { background: #fee2e2; color: #dc2626; }
.type-rec  { background: #dcfce7; color: #15803d; }
.status-badge {
    margin-left: auto;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.73rem;
    font-weight: 600;
}
.badge-today    { background: #fef9c3; color: #92400e; }
.badge-upcoming { background: #eff6ff; color: #1e40af; }
.badge-completed{ background: #f1f5f9; color: #64748b; }
.card-subject { font-size: 1.05rem; font-weight: 700; color: #1a1033; margin-bottom: 6px; }
.card-meta { font-size: 0.83rem; color: #6b7280; margin-bottom: 3px; }
.card-link {
    display: inline-block;
    margin-top: 10px;
    padding: 8px 18px;
    background: linear-gradient(135deg, #4B1E7F, #6b35a8);
    color: white;
    border-radius: 8px;
    text-decoration: none;
    font-size: 0.83rem;
    font-weight: 600;
}
.card-link.ended { background: #fee2e2; color: #991b1b; }

/* Info banner */
.info-banner {
    background: linear-gradient(135deg, #ede6f9, #f5f0fe);
    border-left: 4px solid #4B1E7F;
    border-radius: 10px;
    padding: 12px 18px;
    font-size: 0.85rem;
    color: #2e0e52;
    margin-bottom: 20px;
}

/* Dept pill */
.dept-pill {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 700;
    color: white;
    margin: 3px;
    cursor: pointer;
}

/* Hide Streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# ── HEADER ───────────────────────────────────────────────────────────
st.markdown("""
<div class="feng-header">
  <div>
    <h1>🎓 FENG Online Sessions Portal</h1>
    <div class="sub">Faculty of Engineering · Koya University · Postgraduate & Scientific Affairs</div>
  </div>
  <div class="feng-badge">Koya University</div>
</div>
""", unsafe_allow_html=True)

# ── HELPERS ──────────────────────────────────────────────────────────
def get_session_status(session_date_str):
    if not session_date_str:
        return "upcoming"
    try:
        today = date.today()
        d = datetime.strptime(session_date_str, "%Y-%m-%d").date()
        if d < today:
            return "completed"
        elif d == today:
            return "today"
        else:
            return "upcoming"
    except:
        return "upcoming"

def fmt_date(d):
    if not d:
        return "—"
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%d %b %Y")
    except:
        return d

@st.cache_data(ttl=60)
def load_sessions_for_dept(dept):
    url = PUBLISHED_CSV_URLS.get(dept)
    if not url:
        return []
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return []
        text = r.text.strip()
        if text.startswith("<"):
            return []
        from io import StringIO
        df = pd.read_csv(StringIO(text))
        df.columns = [c.strip().lower() for c in df.columns]

        col_map = {
            "dept":      ["department", "dept"],
            "stage":     ["stage", "year", "stage / year"],
            "subject":   ["subject", "module", "course", "title", "subject / course name"],
            "lecturer":  ["lecturer", "tutor", "instructor", "teacher", "lecturer name"],
            "date":      ["date", "session date"],
            "time":      ["time", "session time"],
            "type":      ["type", "session type"],
            "link":      ["link", "url", "session link"],
            "notes":     ["notes", "note", "comments", "additional notes"],
            "submitted": ["submitted", "timestamp", "submitted on"],
        }

        def find_col(names):
            for n in names:
                if n in df.columns:
                    return n
            return None

        sessions = []
        for _, row in df.iterrows():
            s = {}
            for key, aliases in col_map.items():
                col = find_col(aliases)
                val = str(row[col]).strip() if col and pd.notna(row[col]) else ""
                val = val.strip('"')
                s[key] = val
            if not s["dept"]:
                s["dept"] = dept
            if s["link"] and s["link"].startswith("http"):
                sessions.append(s)
        return sessions
    except Exception as e:
        return []

def load_all_sessions():
    all_sessions = []
    for dept in DEPARTMENTS:
        all_sessions.extend(load_sessions_for_dept(dept))
    return all_sessions

def submit_session(payload):
    try:
        r = requests.post(SCRIPT_URL, data=json.dumps(payload), timeout=15,
                          headers={"Content-Type": "text/plain"})
        return True, "Session submitted successfully!"
    except Exception as e:
        return False, f"Network error: {e}"

def render_session_card(s):
    status = get_session_status(s.get("date", ""))
    color = DEPT_COLORS.get(s.get("dept", ""), "#4B1E7F")
    is_live = s.get("type", "") == "Live Class"
    is_completed = status == "completed"
    is_today = status == "today"

    status_html = (
        '<span class="status-badge badge-completed">🔴 Completed</span>' if is_completed else
        '<span class="status-badge badge-today">📅 Today</span>' if is_today else
        '<span class="status-badge badge-upcoming">⏳ Upcoming</span>'
    )
    type_html = (
        f'<span class="type-badge type-live">🔴 {s.get("type","")}</span>' if is_live else
        f'<span class="type-badge type-rec">▶️ {s.get("type","")}</span>'
    )
    link_label = "🔴 Session Ended" if is_completed else ("🔴 Join Live Class" if is_live else "▶️ Watch Recording")
    link_class = "card-link ended" if is_completed else "card-link"
    notes_html = f'<div class="card-meta" style="font-style:italic">💬 {s.get("notes","")}</div>' if s.get("notes") else ""

    st.markdown(f"""
    <div class="session-card {'completed' if is_completed else ''}">
      <div class="card-top">
        <span class="dept-badge" style="background:{color}">{s.get('dept','')}</span>
        {type_html}
        {status_html}
      </div>
      <div class="card-subject">{s.get('subject','—')}</div>
      <div class="card-meta">👤 {s.get('lecturer','—')} &nbsp;|&nbsp; 📚 {s.get('stage','—')}</div>
      <div class="card-meta">📅 {fmt_date(s.get('date',''))} &nbsp;{'🕐 ' + s.get('time','') if s.get('time') else ''}</div>
      <div class="card-meta" style="color:#9b6dca;font-size:0.75rem">{DEPT_NAMES.get(s.get('dept',''), s.get('dept',''))}</div>
      {notes_html}
      <a class="{link_class}" href="{s.get('link','#')}" target="_blank">{link_label} ↗</a>
      <div style="font-size:0.7rem;color:#aaa;margin-top:6px">Submitted: {s.get('submitted','—')}</div>
    </div>
    """, unsafe_allow_html=True)

# ── TAB NAVIGATION ───────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🚀 Submit Session", "📋 View Sessions"])

# ════════════════════════════════════════════════════════════════════
# TAB 1 — SUBMIT SESSION
# ════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("""
    <div class="info-banner">
      ✅ <strong>7/7 department sheets connected.</strong>
      Fill in the form below to submit a session. It will be saved directly to the matching department's Google Sheet.
    </div>
    """, unsafe_allow_html=True)

    with st.form("submit_form", clear_on_submit=True):
        st.markdown("### 📝 Submit an Online Session")

        col1, col2 = st.columns(2)
        with col1:
            dept = st.selectbox("Department *", [""] + DEPARTMENTS,
                                format_func=lambda x: x if not x else f"{x} – {DEPT_NAMES.get(x,'')}")
        with col2:
            stage = st.selectbox("Stage / Year *", ["", "Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5", "Postgraduate"])

        col3, col4 = st.columns(2)
        with col3:
            subject = st.text_input("Subject / Module *", placeholder="e.g. Fluid Mechanics")
        with col4:
            lecturer = st.text_input("Lecturer Name *", placeholder="e.g. Dr. Ahmed Hassan")

        col5, col6 = st.columns(2)
        with col5:
            session_date = st.date_input("Session Date *", value=date.today())
        with col6:
            session_time = st.text_input("Session Time", placeholder="e.g. 10:00 AM")

        session_type = st.radio("Session Type *", ["Live Class", "Recording"], horizontal=True)

        link = st.text_input("Session Link *", placeholder="https://zoom.us/... or https://drive.google.com/...")

        notes = st.text_area("Notes (optional)", placeholder="Any additional info for students...")

        submitted = st.form_submit_button("🚀 Submit Session", use_container_width=True)

        if submitted:
            errors = []
            if not dept:       errors.append("Department")
            if not stage:      errors.append("Stage")
            if not subject:    errors.append("Subject")
            if not lecturer:   errors.append("Lecturer")
            if not link:       errors.append("Session Link")
            if link and not link.startswith("http"):
                st.error("⚠️ Link must start with https://")
            elif errors:
                st.error(f"⚠️ Please fill in: {', '.join(errors)}")
            else:
                payload = {
                    "dept":      dept,
                    "stage":     stage,
                    "subject":   subject,
                    "lecturer":  lecturer,
                    "date":      str(session_date),
                    "time":      session_time,
                    "type":      session_type,
                    "link":      link,
                    "notes":     notes,
                    "submitted": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
                    "sheetId":   SHEET_IDS.get(dept, ""),
                }
                with st.spinner(f"Saving to {dept} sheet..."):
                    ok, msg = submit_session(payload)
                if ok:
                    st.success(f"✅ Session submitted to {dept} – {DEPT_NAMES[dept]}! It will appear in View Sessions within seconds.")
                else:
                    st.error(f"❌ {msg}")

# ════════════════════════════════════════════════════════════════════
# TAB 2 — VIEW SESSIONS (password protected)
# ════════════════════════════════════════════════════════════════════
with tab2:
    if not st.session_state.authenticated_view:
        st.markdown("### 🔒 View Sessions")
        st.markdown("Enter the password to view all sessions.")

        with st.form("pw_form"):
            pw = st.text_input("Password", type="password", placeholder="Enter password...")
            pw_submit = st.form_submit_button("Unlock", use_container_width=True)

            if pw_submit:
                if pw == VIEW_PASSWORD or pw == ADMIN_PASSWORD:
                    st.session_state.authenticated_view = True
                    if pw == ADMIN_PASSWORD:
                        st.session_state.authenticated_admin = True
                    st.rerun()
                else:
                    st.error("❌ Wrong password. Try again.")
    else:
        # ── FILTERS ──
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1:
            st.markdown("### 📋 All Sessions")
        with col_h2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            filter_dept = st.selectbox("Department", ["All"] + DEPARTMENTS, key="fd")
        with col_f2:
            filter_type = st.selectbox("Type", ["All", "Live Class", "Recording"], key="ft")
        with col_f3:
            filter_status = st.selectbox("Status", ["All", "upcoming", "today", "completed"], key="fs")
        with col_f4:
            search = st.text_input("🔍 Search", placeholder="Subject, lecturer...", key="search")

        # ── LOAD ──
        with st.spinner("Loading sessions from Google Sheets..."):
            all_sessions = load_all_sessions()

        # ── FILTER ──
        filtered = all_sessions
        if filter_dept != "All":
            filtered = [s for s in filtered if s.get("dept") == filter_dept]
        if filter_type != "All":
            filtered = [s for s in filtered if s.get("type") == filter_type]
        if filter_status != "All":
            filtered = [s for s in filtered if get_session_status(s.get("date","")) == filter_status]
        if search:
            q = search.lower()
            filtered = [s for s in filtered if
                        q in s.get("subject","").lower() or
                        q in s.get("lecturer","").lower() or
                        q in s.get("dept","").lower()]

        # Sort newest first
        def sort_key(s):
            try:
                return datetime.strptime(s.get("date",""), "%Y-%m-%d")
            except:
                return datetime.min
        filtered.sort(key=sort_key, reverse=True)

        st.markdown(f"**{len(filtered)} session{'s' if len(filtered) != 1 else ''} found**")

        if not filtered:
            st.info("📭 No sessions found. Try adjusting the filters or submitting a session first.")
        else:
            # Show in 2-column grid on wide screens
            cols = st.columns(2)
            for i, s in enumerate(filtered):
                with cols[i % 2]:
                    render_session_card(s)

        # ── LOCK BUTTON ──
        st.divider()
        if st.button("🔒 Lock Sessions", use_container_width=False):
            st.session_state.authenticated_view = False
            st.session_state.authenticated_admin = False
            st.rerun()

# ── FOOTER ───────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;font-size:0.78rem;color:#9b6dca'>"
    "FENG Online Sessions Portal · Koya University · "
    "Postgraduate &amp; Scientific Affairs Office<br>"
    "<span style='font-size:0.74rem;color:#b9a0d8'>Under the supervision of "
    "<strong>Assist. Prof. Dr. Sarhad Ahmed</strong></span>"
    "</div>",
    unsafe_allow_html=True
)

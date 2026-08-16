import streamlit as st
import pandas as pd
import numpy as np
import requests
import hashlib

st.set_page_config(
    page_title="USJ-R Civil Engineering Cloud Advising Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 SYSTEM THEMING & CUSTOM CSS (GREEN & GOLD)
# ==========================================
st.markdown("""
<style>
    .reportview-container {
        background: #F4F6F4;
    }
    .sidebar .sidebar-content {
        background: #004D26;
        color: white;
    }
    h1, h2, h3 {
        color: #006633 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background-color: #006633;
        color: white !important;
        border-radius: 6px;
        font-weight: bold;
        border: 2px solid #FFCC00;
    }
    .stButton>button:hover {
        background-color: #FFCC00;
        color: #004D26 !important;
        border-color: #006633;
    }
    /* Bento Grid semester card styling */
    .semester-card {
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #ddd;
        margin-bottom: 10px;
        text-align: center;
        font-weight: 500;
    }
    .semester-card-completed {
        background-color: #E2F0D9;
        border-color: #385723;
        color: #385723;
    }
    .semester-card-progress {
        background-color: #FFF2CC;
        border-color: #F4B183;
        color: #7F6000;
    }
    .semester-card-locked {
        background-color: #F2F2F2;
        border-color: #BFBFBF;
        color: #7F7F7F;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🗄️ MASTER CURRICULUM DATABASE
# ==========================================
CURRICULUM = {
    # 1st Year Sem 1
    "EM 1A1": {"desc": "Engineering Calculus 1", "units": 3, "prereqs": [], "level": "1st Year, Sem 1"},
    "NS 1A1": {"desc": "Chemistry for Engineers (Lec)", "units": 3, "prereqs": [], "level": "1st Year, Sem 1"},
    "NS 1A2": {"desc": "Chemistry for Engineers (Lab)", "units": 1, "prereqs": ["NS 1A1"], "level": "1st Year, Sem 1"},
    "CE 1A1": {"desc": "Civil Engineering Orientation", "units": 2, "prereqs": [], "level": "1st Year, Sem 1"},
    "ES 1": {"desc": "Engineering Drawing and Plans", "units": 2, "prereqs": [], "level": "1st Year, Sem 1"},
    "GE STS": {"desc": "Science, Technology, Engineering & Society", "units": 3, "prereqs": [], "level": "1st Year, Sem 1"},
    "ReEd 1": {"desc": "Initium Fidei: Doing Catholic Theology", "units": 3, "prereqs": [], "level": "1st Year, Sem 1"},
    "PE 1": {"desc": "Physical Education 1", "units": 2, "prereqs": [], "level": "1st Year, Sem 1"},
    "NSTP 1": {"desc": "Civic Welfare Training Service 11", "units": 3, "prereqs": [], "level": "1st Year, Sem 1"},
    "GUIDANCE 1": {"desc": "Adjustment to College Life Phase 1", "units": 1, "prereqs": [], "level": "1st Year, Sem 1"},
    
    # 1st Year Sem 2
    "EM 1B1": {"desc": "Engineering Calculus 2", "units": 3, "prereqs": ["EM 1A1"], "level": "1st Year, Sem 2"},
    "NS 1B1": {"desc": "Physics for Engineers (Lec)", "units": 3, "prereqs": ["EM 1A1"], "level": "1st Year, Sem 2"},
    "NS 1B2": {"desc": "Physics for Engineers (Lab)", "units": 1, "prereqs": ["EM 1A1", "NS 1B1"], "level": "1st Year, Sem 2"},
    "ES 2A": {"desc": "Computer-Aided Drafting", "units": 2, "prereqs": ["ES 1"], "level": "1st Year, Sem 2"},
    "GE MMW": {"desc": "Mathematics in the Modern World", "units": 3, "prereqs": [], "level": "1st Year, Sem 2"},
    "GE UTS": {"desc": "Understanding the Self", "units": 3, "prereqs": [], "level": "1st Year, Sem 2"},
    "ReEd 2": {"desc": "Written That You May Believe: Biblical Exegesis", "units": 3, "prereqs": ["ReEd 1"], "level": "1st Year, Sem 2"},
    "PE 2": {"desc": "Physical Education 2", "units": 2, "prereqs": ["PE 1"], "level": "1st Year, Sem 2"},
    "NSTP 2": {"desc": "Civic Welfare Training Service 12", "units": 3, "prereqs": ["NSTP 1"], "level": "1st Year, Sem 2"},
    "GUIDANCE 2": {"desc": "Adjustment to College Life Phase 2", "units": 1, "prereqs": ["GUIDANCE 1"], "level": "1st Year, Sem 2"},

    # 2nd Year Sem 1
    "CE 2A1": {"desc": "Fundamentals of Surveying", "units": 4, "prereqs": ["EM 1B1", "NS 1B1"], "level": "2nd Year, Sem 1"},
    "EM 2A1": {"desc": "Differential Equations", "units": 3, "prereqs": ["EM 1B1"], "level": "2nd Year, Sem 1"},
    "ES 3": {"desc": "Statics of Rigid Bodies", "units": 3, "prereqs": ["EM 1B1", "NS 1B1"], "level": "2nd Year, Sem 1"},
    "ES 6": {"desc": "Engineering Economics", "units": 3, "prereqs": [], "level": "2nd Year, Sem 1"},
    "ES 14": {"desc": "Environmental Science and Engineering", "units": 3, "prereqs": ["NS 1A1"], "level": "2nd Year, Sem 1"},
    "EP 1": {"desc": "English Proficiency Level 1", "units": 3, "prereqs": [], "level": "2nd Year, Sem 1"},
    "ReEd 3": {"desc": "Our Restless Hearts: Doing Catholic Morality", "units": 3, "prereqs": ["ReEd 2"], "level": "2nd Year, Sem 1"},
    "PE 3": {"desc": "Physical Education 3", "units": 2, "prereqs": ["PE 2"], "level": "2nd Year, Sem 1"},

    # 2nd Year Sem 2
    "CE 2B1": {"desc": "Highway and Railroad Engineering", "units": 3, "prereqs": ["CE 2A1"], "level": "2nd Year, Sem 2"},
    "CE Tech": {"desc": "Civil Engineering Technology", "units": 1, "prereqs": [], "level": "2nd Year, Sem 2"},
    "ES 4": {"desc": "Dynamics of Rigid Bodies", "units": 2, "prereqs": ["ES 3"], "level": "2nd Year, Sem 2"},
    "ES 9": {"desc": "Computer Fundamentals and Programming", "units": 2, "prereqs": [], "level": "2nd Year, Sem 2"},
    "ES 10": {"desc": "Mechanics of Deformable Bodies", "units": 4, "prereqs": ["ES 3"], "level": "2nd Year, Sem 2"},
    "GE TCW": {"desc": "The Contemporary World", "units": 3, "prereqs": [], "level": "2nd Year, Sem 2"},
    "GE PC": {"desc": "Purposive Communication", "units": 3, "prereqs": ["EP 1"], "level": "2nd Year, Sem 2"},
    "ReEd 4": {"desc": "A Call to Action: Catholic Social Thought", "units": 3, "prereqs": ["ReEd 3"], "level": "2nd Year, Sem 2"},
    "PE 4": {"desc": "Physical Education 4", "units": 2, "prereqs": ["PE 3"], "level": "2nd Year, Sem 2"},

    # 2nd Year Summer
    "CE 2S1": {"desc": "Geology for Civil Engineers", "units": 2, "prereqs": ["NS 1A1"], "level": "2nd Year, Summer"},
    "CE 2S2": {"desc": "Construction Materials and Testing", "units": 3, "prereqs": ["ES 10"], "level": "2nd Year, Summer"},
    "GE AA": {"desc": "Art Appreciation", "units": 3, "prereqs": [], "level": "2nd Year, Summer"},

    # 3rd Year Sem 1
    "CE 3A1": {"desc": "Structural Theory", "units": 4, "prereqs": ["ES 10"], "level": "3rd Year, Sem 1"},
    "CE 3A2": {"desc": "Numerical Solutions to CE Problems", "units": 3, "prereqs": ["EM 2A1"], "level": "3rd Year, Sem 1"},
    "CE 3A3": {"desc": "Building Systems Design", "units": 3, "prereqs": ["ES 1", "ES 2A"], "level": "3rd Year, Sem 1"},
    "AC 3A1": {"desc": "Engineering Utilities 1", "units": 3, "prereqs": ["NS 1B1", "NS 1B2"], "level": "3rd Year, Sem 1"},
    "AC 3A2": {"desc": "Engineering Utilities 2", "units": 3, "prereqs": ["NS 1B1", "NS 1B2"], "level": "3rd Year, Sem 1"},
    "EDA 1CE": {"desc": "Engineering Data Analysis for CE", "units": 3, "prereqs": [], "level": "3rd Year, Sem 1"},
    "ES 7": {"desc": "Engineering Management", "units": 2, "prereqs": [], "level": "3rd Year, Sem 1"},
    "EfCom": {"desc": "Effective Communication and Human Relations", "units": 3, "prereqs": ["GE PC"], "level": "3rd Year, Sem 1"},

    # 3rd Year Sem 2
    "CE 3B1": {"desc": "Quantity Surveying", "units": 2, "prereqs": ["CE 3A3", "CE 2S2"], "level": "3rd Year, Sem 2"},
    "CE 3B2": {"desc": "Principles of Steel Design", "units": 3, "prereqs": ["CE 3A1", "CE 2S2"], "level": "3rd Year, Sem 2"},
    "CE 3B3": {"desc": "Principles of Reinforced/Prestressed Concrete", "units": 4, "prereqs": ["CE 3A1", "CE 2S2"], "level": "3rd Year, Sem 2"},
    "CE 3B4": {"desc": "Hydrology", "units": 2, "prereqs": [], "level": "3rd Year, Sem 2"},
    "CE 3B5": {"desc": "Hydraulics", "units": 5, "prereqs": ["ES 4", "ES 10"], "level": "3rd Year, Sem 2"},
    "CE 3B6": {"desc": "Geotechnical Engineering 1 (Soil Mechanics)", "units": 4, "prereqs": ["ES 10", "CE 2S1"], "level": "3rd Year, Sem 2"},
    "CE 3B7": {"desc": "Principles of Transportation Engineering", "units": 3, "prereqs": ["CE 2B1"], "level": "3rd Year, Sem 2"},
    "GE ET": {"desc": "Ethics", "units": 3, "prereqs": [], "level": "3rd Year, Sem 2"},

    # 3rd Year Summer
    "OJT": {"desc": "CE Industry Immersion (OJT) - 240 hours", "units": 3, "prereqs": [], "level": "3rd Year, Summer"},

    # 4th Year Sem 1
    "CE 4A1": {"desc": "CE Project 1", "units": 2, "prereqs": [], "level": "4th Year, Sem 1"},
    "CE 4A2": {"desc": "Integrated Course 1 for CE", "units": 3, "prereqs": [], "level": "4th Year, Sem 1"},
    "CE 4A3": {"desc": "Construction Method and Project Management", "units": 3, "prereqs": [], "level": "4th Year, Sem 1"},
    "CE Elec 1": {"desc": "Professional Course - Specialized 1", "units": 3, "prereqs": [], "level": "4th Year, Sem 1"},
    "CE Elec 2": {"desc": "Professional Course - Specialized 2", "units": 3, "prereqs": [], "level": "4th Year, Sem 1"},
    "CE Elec 3": {"desc": "Professional Course - Specialized 3", "units": 3, "prereqs": [], "level": "4th Year, Sem 1"},
    "GE EPM": {"desc": "Eastern Philosophy", "units": 3, "prereqs": [], "level": "4th Year, Sem 1"},
    "ES 12": {"desc": "Technopreneurship 101", "units": 3, "prereqs": [], "level": "4th Year, Sem 1"},

    # 4th Year Sem 2
    "CE 4B1": {"desc": "CE Project 2", "units": 2, "prereqs": ["CE 4A1"], "level": "4th Year, Sem 2"},
    "CE 4B2": {"desc": "CE Law, Ethics and Contracts", "units": 2, "prereqs": [], "level": "4th Year, Sem 2"},
    "CE 4B3": {"desc": "Integrated Course 2 for CE", "units": 3, "prereqs": [], "level": "4th Year, Sem 2"},
    "CE 4B4": {"desc": "Integrated Course 3 for CE", "units": 3, "prereqs": [], "level": "4th Year, Sem 2"},
    "CE Elec 4": {"desc": "Professional Course - Specialized 4", "units": 3, "prereqs": [], "level": "4th Year, Sem 2"},
    "CE Elec 5": {"desc": "Professional Course - Specialized 5", "units": 3, "prereqs": [], "level": "4th Year, Sem 2"},
    "Rizal": {"desc": "Life and Works of Dr Jose Rizal", "units": 3, "prereqs": [], "level": "4th Year, Sem 2"},
    "GE RPH": {"desc": "Readings in Philippine History", "units": 3, "prereqs": [], "level": "4th Year, Sem 2"}
}

SEMESTERS_LIST = ["", "1sem24-25", "2sem24-25", "sum24-25", "1sem25-26", "2sem25-26", "sum25-26", "1sem26-27", "2sem26-27", "sum26-27"]
GRADES_LIST = ["", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "3.0", "5.0", "INC", "W"]

# ==========================================
# 🗄️ GOOGLE APPS SCRIPT WEB API ROUTER CONNECTION
# ==========================================
def call_db_api(action, payload):
    if "database_url" not in st.secrets:
        st.error("Registration error: 'st.secrets has no key \"database_url\". Did you forget to add it to your app settings on Streamlit Cloud?")
        st.stop()
    url = st.secrets["database_url"]
    payload["action"] = action
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"Server returned HTTP status {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==========================================
# 💾 INITIALIZE SESSION STATE
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "active_student" not in st.session_state:
    st.session_state.active_student = None
if "grades_dict" not in st.session_state:
    st.session_state.grades_dict = {}

# ==========================================
# 🔑 LOGIN & REGISTRATION LAYOUT
# ==========================================
if not st.session_state.logged_in:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='color: #006633;'>🎓 USJ-R Civil Engineering</h1>
        <h3 style='color: #FFCC00;'>Voluntary Student Advising & Scheduling Sandbox</h3>
        <p style='color: #666; max-width: 600px; margin: 0 auto;'>
            Welcome, Josenians! This is your official supplementary advising portal. Use this safe sandbox to privately input your grades, check critical prerequisites, and simulate schedules ahead of official enrollment.
        </p>
    </div>
    """, unsafe_allow_html=True)

    auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "📝 Register Account"])

    with auth_tab1:
        st.subheader("Access Your Scheduling Sandbox")
        st_id = st.text_input("Student ID / Faculty ID", placeholder="e.g., 20261234", key="login_id")
        pwd = st.text_input("Password", type="password", placeholder="Enter your sandbox password", key="login_pwd")
        
        if st.button("Log In"):
            if not st_id or not pwd:
                st.warning("Please enter both your Student ID and Password.")
            else:
                if st_id == "USJR-CE-CHAIR" and pwd == "USJR-CE-CHAIR":
                    st.session_state.logged_in = True
                    st.session_state.active_student = {
                        "student_id": "USJR-CE-CHAIR",
                        "name": "CE Department Chairperson Office",
                        "standing": "Chairman Portal",
                        "gwa": 0.0,
                        "units": 0
                    }
                    st.success("Welcome, Department Chairperson!")
                    st.rerun()
                else:
                    with st.spinner("Authenticating..."):
                        res = call_db_api("login", {"student_id": st_id, "password_hash": hash_password(pwd)})
                        if res.get("success"):
                            st.session_state.logged_in = True
                            st.session_state.active_student = res.get("user")
                            
                            # Load grades
                            grades_res = call_db_api("get_grades", {"student_id": st_id})
                            loaded_grades = {}
                            if grades_res.get("success"):
                                for g in grades_res.get("grades", []):
                                    loaded_grades[g["course_code"]] = [
                                        (g["att1_grade"], g["att1_term"]),
                                        (g["att2_grade"], g["att2_term"]),
                                        (g["att3_grade"], g["att3_term"])
                                    ]
                            
                            # Initialize missing
                            for code in CURRICULUM.keys():
                                if code not in loaded_grades:
                                    loaded_grades[code] = [("", ""), ("", ""), ("", "")]
                            st.session_state.grades_dict = loaded_grades
                            st.success(f"Welcome back, {res['user']['name']}!")
                            st.rerun()
                        else:
                            st.error(f"Login failed: {res.get('error', 'Invalid Student ID or Password.')}")

    with auth_tab2:
        st.subheader("Register New Account")
        reg_id = st.text_input("Student ID", placeholder="e.g., 20261234", key="reg_id")
        reg_name = st.text_input("Full Name", placeholder="Given Name Surname", key="reg_name")
        reg_pwd = st.text_input("Create Password", type="password", placeholder="Create a secure password", key="reg_pwd")
        
        if st.button("Register"):
            if not reg_id or not reg_name or not reg_pwd:
                st.warning("All fields are required for registration.")
            else:
                with st.spinner("Registering account..."):
                    res = call_db_api("register", {
                        "student_id": reg_id,
                        "name": reg_name,
                        "password_hash": hash_password(reg_pwd)
                    })
                    if res.get("success"):
                        st.success("Registration successful! You can now log in under the 'Sign In' tab.")
                    else:
                        st.error(f"Registration error: {res.get('error')}")
    st.stop()

# ==========================================
# 👥 LOGGED-IN PORTAL INTERFACE
# ==========================================
active_student = st.session_state.active_student
active_student_id = active_student["student_id"]

# Sidebar controls
with st.sidebar:
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h3 style='color: #FFCC00; margin:0;'>🎓 JOSENIAN PORTAL</h3>
        <p style='color: #ccc; font-size: 0.9em; margin:0;'>Civil Engineering Sandbox</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background-color: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
        <p style='margin: 0; color: #FFCC00; font-weight: bold;'>{active_student['name']}</p>
        <p style='margin: 0; font-size: 0.85em; color: #ddd;'>ID: {active_student_id}</p>
        <hr style='margin: 10px 0; border-color: rgba(255,255,255,0.2);' />
        <p style='margin: 0; font-size: 0.85em; color: #ddd;'>Standing: <b>{active_student['standing']}</b></p>
        <p style='margin: 0; font-size: 0.85em; color: #ddd;'>Curriculum GWA: <b>{active_student['gwa']:.3f}</b></p>
        <p style='margin: 0; font-size: 0.85em; color: #ddd;'>Completed Units: <b>{active_student['units']} / 183</b></p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔒 Log Out"):
        st.session_state.logged_in = False
        st.session_state.active_student = None
        st.session_state.grades_dict = {}
        st.success("Logged out successfully!")
        st.rerun()

# Chairperson Admin View Override
if active_student_id == "USJR-CE-CHAIR":
    st.title("🕵️ Chairman Administrative Dashboard")
    st.markdown("Use this portal to safely monitor overall department stats, trailing INCs, and sequence bottlenecks.")
    
    admin_tab1, admin_tab2, admin_tab3 = st.tabs(["👥 Student Directory", "⚠️ Trailing Incompletes (INC)", "🎯 Bottleneck Mapping"])
    
    with admin_tab1:
        st.subheader("Enrolled Student Roster")
        with st.spinner("Loading roster..."):
            roster_res = call_db_api("get_all_students", {})
            if roster_res.get("success"):
                df_roster = pd.DataFrame(roster_res.get("students", []))
                if not df_roster.empty:
                    df_roster.columns = ["Student ID", "Full Name", "Standing", "Curriculum GWA", "Completed Units"]
                    st.dataframe(df_roster, use_container_width=True)
                else:
                    st.info("No students are currently registered in this database.")
            else:
                st.error(f"Roster error: {roster_res.get('error')}")

    with admin_tab2:
        st.subheader("Active Incompletes (INC) Tracking")
        st.markdown("Students with uncomplied Incomplete (INC) marks that must be resolved within 1 year.")
        with st.spinner("Tracking INC marks..."):
            inc_res = call_db_api("get_all_inc_marks", {})
            if inc_res.get("success"):
                df_inc = pd.DataFrame(inc_res.get("inc_marks", []))
                if not df_inc.empty:
                    df_inc.columns = ["Student ID", "Name", "Course Code", "Att 1 Grade", "Att 1 Term", "Att 2 Grade", "Att 2 Term", "Att 3 Grade", "Att 3 Term"]
                    st.dataframe(df_inc, use_container_width=True)
                else:
                    st.success("🎉 Brilliant! There are zero active incompletes in your department records right now!")
            else:
                st.error(f"INC query error: {inc_res.get('error')}")

    with admin_tab3:
        st.subheader("Prerequisite Gateway Pipeline Bottlenecks")
        st.markdown("Displays students who are currently blocked because they have not completed key gateway prerequisites.")
        gateways = ["ES 3", "ES 10", "CE 3A1", "CE 3B5"]
        with st.spinner("Compiling bottleneck mapping..."):
            gate_res = call_db_api("get_sequence_bottlenecks", {"gateways": gateways})
            if gate_res.get("success"):
                bottlenecks = gate_res.get("bottlenecks", {})
                cols = st.columns(len(gateways))
                for idx, g_code in enumerate(gateways):
                    with cols[idx]:
                        st.markdown(f"### 🎯 {g_code}")
                        st.caption(CURRICULUM[g_code]["desc"])
                        st.metric("Blocked Students", len(bottlenecks.get(g_code, [])))
                        if bottlenecks.get(g_code):
                            st.markdown("**List of Students:**")
                            for s_name in bottlenecks.get(g_code):
                                st.write(f"• {s_name}")
                        else:
                            st.success("None blocked!")
            else:
                st.error(f"Bottleneck mapping error: {gate_res.get('error')}")
    st.stop()

# ==========================================
# 🧮 LOGICAL CALCULATION FUNCTIONS (GROUNDED)
# ==========================================
def evaluate_course_status(attempts):
    passed = False
    failed = False
    incomplete = False
    highest_passing_grade = None
    last_grade = ""
    last_term = ""

    # Trace active attempts (up to 3)
    for gr, tm in attempts:
        if gr != "":
            last_grade = gr
            last_term = tm
            if gr in ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "3.0"]:
                passed = True
                grade_num = float(gr)
                if highest_passing_grade is None or grade_num < highest_passing_grade:
                    highest_passing_grade = grade_num
            elif gr in ["5.0", "W"]:
                failed = True
            elif gr == "INC":
                incomplete = True

    if passed:
        return "Passed", highest_passing_grade
    elif last_grade == "INC":
        return "Incomplete (INC)", None
    elif failed:
        return "Failed", None
    else:
        return "", None

# Calculate student profile real-time
course_status_map = {}
gwa_points_sum = 0.0
gwa_units_sum = 0.0
completed_units_by_level = {"1st Year": 0, "2nd Year": 0, "3rd Year": 0, "4th Year": 0}
total_units_by_level = {"1st Year": 0, "2nd Year": 0, "3rd Year": 0, "4th Year": 0}

for code, details in CURRICULUM.items():
    year_level = details["level"].split(",")[0]
    total_units_by_level[year_level] += details["units"]
    
    attempts = st.session_state.grades_dict.get(code, [("", ""), ("", ""), ("", "")])
    status, grade_val = evaluate_course_status(attempts)
    course_status_map[code] = status
    
    if status == "Passed":
        completed_units_by_level[year_level] += details["units"]
        gwa_points_sum += grade_val * details["units"]
        gwa_units_sum += details["units"]

total_completed_units = sum(completed_units_by_level.values())
total_curriculum_units = sum(total_units_by_level.values())
remaining_curriculum_units = total_curriculum_units - total_completed_units
cumulative_gwa = round(gwa_points_sum / gwa_units_sum, 3) if gwa_units_sum > 0 else 0.0

# Calculate standing dynamically
if total_completed_units >= 153:
    academic_standing_level = "4th Year Standing"
elif total_completed_units >= 100:
    academic_standing_level = "3rd Year Standing"
elif total_completed_units >= 45:
    academic_standing_level = "2nd Year Standing"
else:
    academic_standing_level = "1st Year Standing"

# Update active student profile locally if changed
if academic_standing_level != active_student["standing"] or abs(cumulative_gwa - active_student["gwa"]) > 0.001 or total_completed_units != active_student["units"]:
    active_student["standing"] = academic_standing_level
    active_student["units"] = total_completed_units
    active_student["gwa"] = cumulative_gwa
    # Sync with database
    call_db_api("update_profile", {
        "student_id": active_student_id,
        "standing": academic_standing_level,
        "gwa": cumulative_gwa,
        "units": total_completed_units
    })

# ==========================================
# 🎛️ TABBED APP CONTAINER
# ==========================================
tab1, tab_planner, tab_grades, tab_ref = st.tabs([
    "📊 Academic Dashboard",
    "📋 Proposed Enrollment Planner",
    "🎓 Student Grade Record",
    "📖 Curriculum Reference"
])

# --------------------------------------------------
# TAB 1: ACADEMIC DASHBOARD
# --------------------------------------------------
with tab1:
    st.markdown("### Josenian CE Academic Roadmap")
    
    # Bento Grid for Year & Sem Progress
    bento_cols = st.columns(4)
    sem_keys = [
        ("1st Year, Sem 1", "1st Yr - 1st Sem"),
        ("1st Year, Sem 2", "1st Yr - 2nd Sem"),
        ("2nd Year, Sem 1", "2nd Yr - 1st Sem"),
        ("2nd Year, Sem 2", "2nd Yr - 2nd Sem")
    ]
    
    for idx, (level_key, title) in enumerate(sem_keys):
        with bento_cols[idx]:
            # Check completion
            sem_courses = [code for code, details in CURRICULUM.items() if details["level"] == level_key]
            passed_courses = [code for code in sem_courses if course_status_map.get(code) == "Passed"]
            inc_courses = [code for code in sem_courses if course_status_map.get(code) == "Incomplete (INC)"]
            
            if len(passed_courses) == len(sem_courses):
                status_class = "semester-card-completed"
                lbl = "🟢 Completed"
            elif len(passed_courses) > 0 or len(inc_courses) > 0:
                status_class = "semester-card-progress"
                lbl = "🟡 In Progress"
            else:
                status_class = "semester-card-locked"
                lbl = "⚪ Locked"
                
            st.markdown(f"""
            <div class='semester-card {status_class}'>
                <p style='margin:0; font-size:0.8em; text-transform:uppercase; letter-spacing:1px;'>{title}</p>
                <h3 style='margin:10px 0 5px 0; color:inherit !important;'>{len(passed_courses)} / {len(sem_courses)} Passed</h3>
                <p style='margin:0; font-size:0.85em; font-weight:bold;'>{lbl}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Critical Pathway Gateways Sidebar/Panel
    st.markdown("### 🎯 Critical Pathway Bottlenecks")
    gateways = [
        ("ES 3", "Statics"),
        ("ES 10", "Deformables"),
        ("CE 3A1", "Structural Theory"),
        ("CE 3B5", "Hydraulics")
    ]
    
    gate_cols = st.columns(4)
    for idx, (g_code, label) in enumerate(gateways):
        with gate_cols[idx]:
            status = course_status_map.get(g_code, "")
            if status == "Passed":
                color = "#2E7D32"
                icon = "🟢 Eligible / Cleared"
            elif status == "Incomplete (INC)":
                color = "#F57F17"
                icon = "🟡 Prerequisite INC Backlog"
            elif status == "Failed":
                color = "#C62828"
                icon = "🔴 Prerequisite Failure"
            else:
                color = "#757575"
                icon = "⚪ Unattempted"
            
            st.markdown(f"""
            <div style='background-color: {color}; color: white; padding: 12px; border-radius: 8px; text-align: center;'>
                <p style='margin: 0; font-size:0.85em; text-transform:uppercase;'>{label} ({g_code})</p>
                <p style='margin: 5px 0 0 0; font-size:1em; font-weight:bold;'>{icon}</p>
            </div>
            """, unsafe_allow_html=True)

# --------------------------------------------------
# TAB 2: PROPOSED ENROLLMENT PLANNER
# --------------------------------------------------
with tab_planner:
    st.markdown("### Proposed Enrollment Planner & Simulator")
    st.write("Construct your upcoming semester's schedule to simulate clearance. Prerequisite validation evaluates instantly.")
    
    plan_courses = []
    for i in range(8):
        course_sel = st.selectbox(f"Select Course {i+1}", [""] + list(CURRICULUM.keys()), key=f"plan_course_sel_{i}")
        if course_sel:
            plan_courses.append(course_sel)
            
    if plan_courses:
        records = []
        total_planned_units = 0
        for code in plan_courses:
            details = CURRICULUM[code]
            prereqs = details["prereqs"]
            
            # Check clearance
            cleared = True
            issues = []
            for pre in prereqs:
                if course_status_map.get(pre) != "Passed":
                    cleared = False
                    issues.append(f"{pre} is incomplete.")
                    
            status_text = "🟢 Approved / Eligible" if cleared else f"🔴 Prerequisite Blocked: {', '.join(issues)}"
            records.append({
                "Course Code": code,
                "Course Description": details["desc"],
                "Units": details["units"],
                "Prerequisites": ", ".join(prereqs) if prereqs else "None",
                "Simulation Status": status_text
            })
            total_planned_units += details["units"]
            
        df_plan = pd.DataFrame(records)
        st.dataframe(df_plan, use_container_width=True)
        st.metric("Total Selected Units", total_planned_units)
    else:
        st.info("Choose courses from the selectors above to begin simulating your planner!")

# --------------------------------------------------
# TAB 3: STUDENT GRADE RECORD
# --------------------------------------------------
with tab_grades:
    st.markdown("### Academic Grade Record Ledger")
    st.write("Update your historical grades below. White cells are editable. Changes will sync immediately to your private database.")
    
    # Render interactive grid for all courses
    records = []
    for code, details in CURRICULUM.items():
        attempts = st.session_state.grades_dict.get(code, [("", ""), ("", ""), ("", "")])
        records.append({
            "Course Code": code,
            "Description": details["desc"],
            "Term": details["level"],
            "Units": details["units"],
            "Att 1 Grade": attempts[0][0],
            "Att 1 Term": attempts[0][1],
            "Att 2 Grade": attempts[1][0],
            "Att 2 Term": attempts[1][1],
            "Att 3 Grade": attempts[2][0],
            "Att 3 Term": attempts[2][1],
        })
        
    df_grades = pd.DataFrame(records)
    
    edited_df = st.data_editor(
        df_grades,
        column_config={
            "Course Code": st.column_config.TextColumn("Code", width=65, disabled=True),
            "Description": st.column_config.TextColumn("Description", width=250, disabled=True),
            "Term": st.column_config.TextColumn("Regular Term", width=110, disabled=True),
            "Units": st.column_config.NumberColumn("Units", width=45, disabled=True),
            "Att 1 Grade": st.column_config.SelectboxColumn("Att 1 Grade", options=GRADES_LIST, width=60),
            "Att 1 Term": st.column_config.SelectboxColumn("Att 1 Term", options=SEMESTERS_LIST, width=75),
            "Att 2 Grade": st.column_config.SelectboxColumn("Att 2 Grade", options=GRADES_LIST, width=60),
            "Att 2 Term": st.column_config.SelectboxColumn("Att 2 Term", options=SEMESTERS_LIST, width=75),
            "Att 3 Grade": st.column_config.SelectboxColumn("Att 3 Grade", options=GRADES_LIST, width=60),
            "Att 3 Term": st.column_config.SelectboxColumn("Att 3 Term", options=SEMESTERS_LIST, width=75),
        },
        use_container_width=True,
        hide_index=True,
        key="grade_ledger_editor"
    )
    
    if st.button("💾 Sync Grade Ledger"):
        with st.spinner("Syncing records with cloud sheet database..."):
            success_count = 0
            for idx, row in edited_df.iterrows():
                code = row["Course Code"]
                # check if anything changed
                old_attempts = st.session_state.grades_dict.get(code, [("", ""), ("", ""), ("", "")])
                new_attempts = [
                    (row["Att 1 Grade"], row["Att 1 Term"]),
                    (row["Att 2 Grade"], row["Att 2 Term"]),
                    (row["Att 3 Grade"], row["Att 3 Term"])
                ]
                
                if old_attempts != new_attempts:
                    res = call_db_api("save_grade", {
                        "student_id": active_student_id,
                        "course_code": code,
                        "grades": {
                            "att1_grade": row["Att 1 Grade"],
                            "att1_term": row["Att 1 Term"],
                            "att2_grade": row["Att 2 Grade"],
                            "att2_term": row["Att 2 Term"],
                            "att3_grade": row["Att 3 Grade"],
                            "att3_term": row["Att 3 Term"]
                        }
                    })
                    if res.get("success"):
                        st.session_state.grades_dict[code] = new_attempts
                        success_count += 1
            st.success("Successfully synced grade updates to Google Sheet!")
            st.rerun()

# --------------------------------------------------
# TAB 4: CURRICULUM REFERENCE
# --------------------------------------------------
with tab_ref:
    st.markdown("### Civil Engineering Prospectus Reference")
    st.write("Standard 183-unit Bachelor of Science in Civil Engineering (BSCE) Curriculum map.")
    
    df_ref = pd.DataFrame([
        {
            "Course Code": code,
            "Description": details["desc"],
            "Units": details["units"],
            "Regular Term Placement": details["level"],
            "Prerequisites": ", ".join(details["prereqs"]) if details["prereqs"] else "None"
        } for code, details in CURRICULUM.items()
    ])
    st.dataframe(df_ref, use_container_width=True, hide_index=True)

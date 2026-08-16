import streamlit as st
import pandas as pd
import numpy as np
import requests

# ==========================================
# 🎨 SYSTEM CONFIGURATION & THEMING
# ==========================================
st.set_page_config(
    page_title="USJ-R Civil Engineering Advising Portal",
    page_icon="👷‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for USJ-R branding (Forest Green #006633 & Athletic Gold #FFCC00)
st.markdown("""
<style>
    /* Main branding styles */
    .stApp {
        background-color: #f9fbf9;
    }
    .main-header {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        color: #006633;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-header {
        color: #db9d00;
        font-weight: 600;
        margin-top: 0px;
        margin-bottom: 20px;
        font-size: 1.1rem;
    }
    /* Buttons */
    div.stButton > button:first-child {
        background-color: #006633;
        color: white;
        border-radius: 5px;
        border: 1px solid #00552b;
        font-weight: bold;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #FFCC00;
        color: #006633;
        border-color: #FFCC00;
    }
    /* Cards and containers */
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #006633;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .gold-metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FFCC00;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .sidebar-brand {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #006633;
        margin-bottom: 1.5rem;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🗄️ MASTER CURRICULUM DATABASE (73 COURSES)
# ==========================================
CURRICULUM = {
    # FIRST YEAR - 1st Semester
    "EM 1A1": {"name": "Engineering Calculus 1", "units": 3, "prereq": [], "coreq": [], "year": "1st Year", "sem": "1st Semester"},
    "NS 1A1": {"name": "Chemistry for Engineers (Lec)", "units": 3, "prereq": [], "coreq": [], "year": "1st Year", "sem": "1st Semester"},
    "NS 1A2": {"name": "Chemistry for Engineers (Lab)", "units": 1, "prereq": [], "coreq": ["NS 1A1"], "year": "1st Year", "sem": "1st Semester"},
    "CE 1A1": {"name": "Civil Engineering Orientation", "units": 2, "prereq": [], "coreq": [], "year": "1st Year", "sem": "1st Semester"},
    "ES 1": {"name": "Engineering Drawing and Plans", "units": 2, "prereq": [], "coreq": [], "year": "1st Year", "sem": "1st Semester"},
    "GE STS": {"name": "Science, Technology, Engineering and Society", "units": 3, "prereq": [], "coreq": [], "year": "1st Year", "sem": "1st Semester"},
    "ReEd 1": {"name": "Initium Fidei: An Introduction to Doing Catholic Theology", "units": 3, "prereq": [], "coreq": [], "year": "1st Year", "sem": "1st Semester"},
    "PE 1": {"name": "Physical Education 1", "units": 2, "prereq": [], "coreq": [], "year": "1st Year", "sem": "1st Semester"},
    "NSTP 1": {"name": "Civic Welfare Training Service (CWTS) 11/ROTC 11", "units": 3, "prereq": [], "coreq": [], "year": "1st Year", "sem": "1st Semester"},
    "GUIDANCE 1": {"name": "Adjustment to College Life Phase 1", "units": 1, "prereq": [], "coreq": [], "year": "1st Year", "sem": "1st Semester", "non_academic": True},

    # FIRST YEAR - 2nd Semester
    "EM 1B1": {"name": "Engineering Calculus 2", "units": 3, "prereq": ["EM 1A1"], "coreq": [], "year": "1st Year", "sem": "2nd Semester"},
    "NS 1B1": {"name": "Physics for Engineers (Lec)", "units": 3, "prereq": ["EM 1A1", "NS 1A1"], "coreq": ["EM 1B1"], "year": "1st Year", "sem": "2nd Semester"},
    "NS 1B2": {"name": "Physics for Engineers (Lab)", "units": 1, "prereq": ["EM 1A1", "NS 1A1"], "coreq": ["NS 1B1", "EM 1B1"], "year": "1st Year", "sem": "2nd Semester"},
    "ES 2": {"name": "Computer-Aided Drafting", "units": 2, "prereq": ["ES 1"], "coreq": [], "year": "1st Year", "sem": "2nd Semester"},
    "ReEd 2": {"name": "Written That You May Believe: An Introduction to Biblical Exegesis", "units": 3, "prereq": ["ReEd 1"], "coreq": [], "year": "1st Year", "sem": "2nd Semester"},
    "GE MMW": {"name": "Mathematics in the Modern World", "units": 3, "prereq": [], "coreq": [], "year": "1st Year", "sem": "2nd Semester"},
    "GE UTS": {"name": "Understanding the Self", "units": 3, "prereq": [], "coreq": [], "year": "1st Year", "sem": "2nd Semester"},
    "PE 2": {"name": "Physical Education 2", "units": 2, "prereq": ["PE 1"], "coreq": [], "year": "1st Year", "sem": "2nd Semester"},
    "NSTP 2": {"name": "Civic Welfare Training Service (CWTS) 12/ROTC 12", "units": 3, "prereq": ["NSTP 1"], "coreq": [], "year": "1st Year", "sem": "2nd Semester"},
    "GUIDANCE 2": {"name": "Adjustment to College Life Phase 2", "units": 1, "prereq": [], "coreq": [], "year": "1st Year", "sem": "2nd Semester", "non_academic": True},

    # SECOND YEAR - 1st Semester
    "EM 2A1": {"name": "Differential Equations", "units": 3, "prereq": ["EM 1B1"], "coreq": [], "year": "2nd Year", "sem": "1st Semester"},
    "ES 3": {"name": "Statics of Rigid Bodies", "units": 3, "prereq": ["EM 1B1", "NS 1B1"], "coreq": [], "year": "2nd Year", "sem": "1st Semester"},
    "CE 2A1": {"name": "Fundamentals of Surveying", "units": 4, "prereq": ["ES 1"], "coreq": [], "year": "2nd Year", "sem": "1st Semester"},
    "ES 6": {"name": "Engineering Economics", "units": 3, "prereq": ["2nd Year Standing"], "coreq": [], "year": "2nd Year", "sem": "1st Semester"},
    "ES 14": {"name": "Environmental Science and Engineering", "units": 3, "prereq": ["NS 1A1"], "coreq": [], "year": "2nd Year", "sem": "1st Semester"},
    "EP 1": {"name": "English Proficiency Level 1", "units": 3, "prereq": [], "coreq": [], "year": "2nd Year", "sem": "1st Semester"},
    "PE 3": {"name": "Physical Education 3", "units": 2, "prereq": ["PE 2"], "coreq": [], "year": "2nd Year", "sem": "1st Semester"},
    "ReEd 3": {"name": "Our Restless Hearts: An Introduction to Doing Catholic Morality", "units": 3, "prereq": ["ReEd 2"], "coreq": [], "year": "2nd Year", "sem": "1st Semester"},

    # SECOND YEAR - 2nd Semester
    "GE TCW": {"name": "The Contemporary World", "units": 3, "prereq": [], "coreq": [], "year": "2nd Year", "sem": "2nd Semester"},
    "ES 4": {"name": "Dynamics of Rigid Bodies", "units": 2, "prereq": ["ES 3"], "coreq": [], "year": "2nd Year", "sem": "2nd Semester"},
    "ES 10": {"name": "Mechanics of Deformable Bodies", "units": 4, "prereq": ["ES 3"], "coreq": [], "year": "2nd Year", "sem": "2nd Semester"},
    "CE 2B1": {"name": "Highway and Railroad Engineering", "units": 3, "prereq": ["CE 2A1"], "coreq": [], "year": "2nd Year", "sem": "2nd Semester"},
    "CE Tech": {"name": "Civil Engineering Technology 1", "units": 1, "prereq": [], "coreq": [], "year": "2nd Year", "sem": "2nd Semester"},
    "GE PC": {"name": "Purposive Communication", "units": 3, "prereq": ["EP 1"], "coreq": [], "year": "2nd Year", "sem": "2nd Semester"},
    "ES 9": {"name": "Computer Fundamentals and Programming", "units": 2, "prereq": [], "coreq": [], "year": "2nd Year", "sem": "2nd Semester"},
    "PE 4": {"name": "Physical Education 4", "units": 2, "prereq": ["PE 3"], "coreq": [], "year": "2nd Year", "sem": "2nd Semester"},
    "ReEd 4": {"name": "A Call to Action: An Introduction to Catholic Social Thought", "units": 3, "prereq": ["ReEd 3"], "coreq": [], "year": "2nd Year", "sem": "2nd Semester"},

    # SECOND YEAR - Summer
    "CE 2S1": {"name": "Geology for Civil Engineers", "units": 2, "prereq": ["NS 1A1"], "coreq": [], "year": "2nd Year", "sem": "Summer"},
    "CE 2S2": {"name": "Construction Materials and Testing", "units": 3, "prereq": ["ES 10"], "coreq": [], "year": "2nd Year", "sem": "Summer"},
    "GE AA": {"name": "Art Appreciation", "units": 3, "prereq": [], "coreq": [], "year": "2nd Year", "sem": "Summer"},

    # THIRD YEAR - 1st Semester
    "CE 3A1": {"name": "Structural Theory", "units": 4, "prereq": ["ES 10"], "coreq": [], "year": "3rd Year", "sem": "1st Semester"},
    "CE 3A2": {"name": "Numerical Solutions to CE Problems", "units": 3, "prereq": ["EM 2A1"], "coreq": [], "year": "3rd Year", "sem": "1st Semester"},
    "CE 3A3": {"name": "Building Systems Design", "units": 3, "prereq": ["ES 1", "ES 2"], "coreq": [], "year": "3rd Year", "sem": "1st Semester"},
    "AC 3A1": {"name": "Engineering Utilities 1", "units": 3, "prereq": ["NS 1B1", "NS 1B2"], "coreq": [], "year": "3rd Year", "sem": "1st Semester"},
    "AC 3A2": {"name": "Engineering Utilities 2", "units": 3, "prereq": ["NS 1B1", "NS 1B2"], "coreq": [], "year": "3rd Year", "sem": "1st Semester"},
    "EDA 1CE": {"name": "Engineering Data Analysis for CE", "units": 3, "prereq": ["3rd Year Standing"], "coreq": [], "year": "3rd Year", "sem": "1st Semester"},
    "ES 7": {"name": "Engineering Management", "units": 2, "prereq": ["3rd Year Standing"], "coreq": [], "year": "3rd Year", "sem": "1st Semester"},
    "EfCOM": {"name": "Effective Communication and Human Relations", "units": 3, "prereq": ["GE PC"], "coreq": [], "year": "3rd Year", "sem": "1st Semester"},

    # THIRD YEAR - 2nd Semester
    "CE 3B1": {"name": "Quantity Surveying", "units": 2, "prereq": ["CE 3A3", "CE 2S2"], "coreq": [], "year": "3rd Year", "sem": "2nd Semester"},
    "CE 3B2": {"name": "Principles of Steel Design", "units": 3, "prereq": ["CE 3A1", "CE 2S2"], "coreq": [], "year": "3rd Year", "sem": "2nd Semester"},
    "CE 3B3": {"name": "Principles of Reinforced/Prestressed Concrete", "units": 4, "prereq": ["CE 3A1", "CE 2S2"], "coreq": [], "year": "3rd Year", "sem": "2nd Semester"},
    "CE 3B4": {"name": "Hydrology", "units": 2, "prereq": ["3rd Year Standing"], "coreq": ["CE 3B5"], "year": "3rd Year", "sem": "2nd Semester"},
    "CE 3B5": {"name": "Hydraulics", "units": 5, "prereq": ["ES 4", "ES 10"], "coreq": [], "year": "3rd Year", "sem": "2nd Semester"},
    "CE 3B6": {"name": "Geotechnical Engineering 1 (Soil Mechanics)", "units": 4, "prereq": ["ES 10", "CE 2S1"], "coreq": [], "year": "3rd Year", "sem": "2nd Semester"},
    "CE 3B7": {"name": "Principles of Transportation Engineering", "units": 3, "prereq": ["CE 2B1"], "coreq": [], "year": "3rd Year", "sem": "2nd Semester"},
    "GE ET": {"name": "Ethics", "units": 3, "prereq": [], "coreq": [], "year": "3rd Year", "sem": "2nd Semester"},

    # THIRD YEAR - Summer
    "OJT": {"name": "CE Industry Immersion (OJT) - 240 hours minimum", "units": 3, "prereq": ["4th Year Standing"], "coreq": [], "year": "3rd Year", "sem": "Summer"},

    # FOURTH YEAR - 1st Semester
    "CE 4A1": {"name": "CE Project 1", "units": 2, "prereq": ["4th Year Standing"], "coreq": [], "year": "4th Year", "sem": "1st Semester"},
    "CE 4A2": {"name": "Integrated Course 1 for CE", "units": 3, "prereq": ["4th Year Standing"], "coreq": [], "year": "4th Year", "sem": "1st Semester"},
    "CE 4A3": {"name": "Construction Method and Project Management", "units": 3, "prereq": ["4th Year Standing"], "coreq": [], "year": "4th Year", "sem": "1st Semester"},
    "CE Elec 1": {"name": "Professional Course - Specialized 1", "units": 3, "prereq": ["4th Year Standing"], "coreq": [], "year": "4th Year", "sem": "1st Semester"},
    "CE Elec 2": {"name": "Professional Course - Specialized 2", "units": 3, "prereq": ["4th Year Standing"], "coreq": [], "year": "4th Year", "sem": "1st Semester"},
    "CE Elec 3": {"name": "Professional Course - Specialized 3", "units": 3, "prereq": ["4th Year Standing"], "coreq": [], "year": "4th Year", "sem": "1st Semester"},
    "GE EPM": {"name": "Eastern Philosophy", "units": 3, "prereq": [], "coreq": [], "year": "4th Year", "sem": "1st Semester"},
    "ES 12": {"name": "Technopreneurship 101", "units": 3, "prereq": ["4th Year Standing"], "coreq": [], "year": "4th Year", "sem": "1st Semester"},

    # FOURTH YEAR - 2nd Semester
    "CE 4B1": {"name": "CE Project 2", "units": 2, "prereq": ["CE 4A1"], "coreq": [], "year": "4th Year", "sem": "2nd Semester"},
    "CE 4B2": {"name": "CE Law, Ethics and Contracts", "units": 2, "prereq": ["4th Year Standing"], "coreq": [], "year": "4th Year", "sem": "2nd Semester"},
    "CE 4B3": {"name": "Integrated Course 2 for CE", "units": 3, "prereq": ["4th Year Standing"], "coreq": [], "year": "4th Year", "sem": "2nd Semester"},
    "CE 4B4": {"name": "Integrated Course 3 for CE", "units": 3, "prereq": ["4th Year Standing"], "coreq": [], "year": "4th Year", "sem": "2nd Semester"},
    "CE Elec 4": {"name": "Professional Course - Specialized 4", "units": 3, "prereq": ["4th Year Standing"], "coreq": [], "year": "4th Year", "sem": "2nd Semester"},
    "CE Elec 5": {"name": "Professional Course - Specialized 5", "units": 3, "prereq": ["4th Year Standing"], "coreq": [], "year": "4th Year", "sem": "2nd Semester"},
    "Rizal": {"name": "Life and Works of Dr Jose Rizal", "units": 3, "prereq": [], "coreq": [], "year": "4th Year", "sem": "2nd Semester"},
    "GE RPH": {"name": "Readings in Philippine History", "units": 3, "prereq": [], "coreq": [], "year": "4th Year", "sem": "2nd Semester"}
}

SEMESTERS = ["", "1sem24-25", "2sem24-25", "sum24-25", "1sem25-26", "2sem25-26", "sum25-26", "1sem26-27", "2sem26-27", "sum26-27"]
GRADES = ["", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "3.0", "5.0", "INC", "W"]

# Validate database_url from Streamlit secrets
if "database_url" in st.secrets:
    DB_URL = st.secrets["database_url"]
else:
    DB_URL = ""
    st.warning("⚠️ database_url Secret not detected. Local simulation mode enabled.")

# ==========================================
# 💾 API HELPER FUNCTIONS FOR GOOGLE SHEETS
# ==========================================
def call_api(action, payload):
    if not DB_URL:
        return {"success": False, "error": "No database URL configured."}
    payload["action"] = action
    try:
        r = requests.post(DB_URL, json=payload, timeout=10)
        if r.status_code == 200:
            return r.json()
        return {"success": False, "error": f"Server returned HTTP status {r.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==========================================
# 🧮 LOGICAL CALCULATION FUNCTIONS (GROUNDED)
# ==========================================
def evaluate_course_status(attempts):
    """
    Evaluates attempts dictionary to find the status:
    - Passed: '1.0' to '3.0'
    - Failed: '5.0'
    - Incomplete: 'INC'
    - Withdrawn: 'W'
    """
    last_grade = ""
    last_term = ""
    
    # Trace through attempt slots to find the final active grade
    for i in range(3, 0, -1):
        g = attempts.get(f"att{i}_grade", "")
        t = attempts.get(f"att{i}_term", "")
        if g != "":
            last_grade = g
            last_term = t
            break
            
    if last_grade == "":
        return {"status": "Not Taken", "grade": "", "term": ""}
        
    if last_grade in ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "3.0"]:
        return {"status": "Passed", "grade": last_grade, "term": last_term}
    elif last_grade == "5.0":
        return {"status": "Failed", "grade": last_grade, "term": last_term}
    elif last_grade == "INC":
        return {"status": "Incomplete", "grade": last_grade, "term": last_term}
    elif last_grade == "W":
        return {"status": "Withdrawn", "grade": last_grade, "term": last_term}
        
    return {"status": "Not Taken", "grade": "", "term": ""}

def calculate_academic_summary(grades_list):
    """
    Computes GWA, completed units, year standing, active INCs.
    """
    # Initialize a clean grades map for lookup
    grades_map = {g["course_code"]: g for g in grades_list}
    
    completed_units_by_level = {"1st Year": 0, "2nd Year": 0, "3rd Year": 0, "4th Year": 0}
    total_units_by_level = {"1st Year": 0, "2nd Year": 0, "3rd Year": 0, "4th Year": 0}
    
    gwa_points_sum = 0.0
    gwa_units_sum = 0.0
    active_inc_count = 0
    
    for code, details in CURRICULUM.items():
        is_non_acad = details.get("non_academic", False)
        units = details["units"]
        level = details["year"]
        
        # Accumulate total curriculum units
        if not is_non_acad:
            total_units_by_level[level] += units
            
        # Check student attempts
        course_grade = grades_map.get(code, {})
        attempts = {
            "att1_grade": course_grade.get("att1_grade", ""),
            "att1_term": course_grade.get("att1_term", ""),
            "att2_grade": course_grade.get("att2_grade", ""),
            "att2_term": course_grade.get("att2_term", ""),
            "att3_grade": course_grade.get("att3_grade", ""),
            "att3_term": course_grade.get("att3_term", "")
        }
        
        eval_result = evaluate_course_status(attempts)
        status = eval_result["status"]
        grade_val = eval_result["grade"]
        
        if status == "Passed":
            if not is_non_acad:
                completed_units_by_level[level] += units
                # Add to GWA
                try:
                    gwa_points_sum += float(grade_val) * units
                    gwa_units_sum += units
                except:
                    pass
        elif status == "Incomplete":
            active_inc_count += 1
            
    total_completed_units = sum(completed_units_by_level.values())
    total_curriculum_units = sum(total_units_by_level.values())
    remaining_curriculum_units = total_curriculum_units - total_completed_units
    
    cumulative_gwa = round(gwa_points_sum / gwa_units_sum, 3) if gwa_units_sum > 0 else 0.0
    
    # Establish Year Standing according to Student Academic Advising Version 1.0 guidelines:
    # 4th Year Standing: >= 153 completed units
    # 3rd Year Standing: >= 100 completed units
    # 2nd Year Standing: >= 45 completed units
    if total_completed_units >= 153:
        standing = "4th Year"
    elif total_completed_units >= 100:
        standing = "3rd Year"
    elif total_completed_units >= 45:
        standing = "2nd Year"
    else:
        standing = "1st Year"
        
    return {
        "completed_units": total_completed_units,
        "remaining_units": remaining_curriculum_units,
        "gwa": cumulative_gwa,
        "inc_count": active_inc_count,
        "standing": standing,
        "completed_units_by_level": completed_units_by_level,
        "total_units_by_level": total_units_by_level,
        "grades_map": grades_map
    }

# ==========================================
# 👥 USER AUTHENTICATION & LOGIN STATE
# ==========================================
if "user_authenticated" not in st.session_state:
    st.session_state["user_authenticated"] = False
    st.session_state["user_role"] = None  # "student" or "chairman"
    st.session_state["student_id"] = None
    st.session_state["student_name"] = None

# ==========================================
# 🏛️ BRAND HEADER & LOGO PANEL
# ==========================================
header_col1, header_col2 = st.columns([1, 6])
with header_col1:
    # Golden Crown & Seal representation
    st.markdown("""
        <div style="display:flex; justify-content:center; align-items:center; height:100px;">
            <span style="font-size: 65px;">🏛️</span>
        </div>
    """, unsafe_allow_html=True)
with header_col2:
    st.markdown("<h1 class='main-header'>UNIVERSITY OF SAN JOSE - RECOLETOS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='sub-header'>Civil Engineering Department • Student Academic Advising Portal</h3>", unsafe_allow_html=True)

# ==========================================
# 🚪 LOGIN / REGISTRATION WORKFLOW
# ==========================================
if not st.session_state["user_authenticated"]:
    login_tab, register_tab = st.tabs(["🔒 Student Login", "📝 Student Registration"])
    
    with login_tab:
        st.subheader("Login to your Advising Account")
        login_col1, login_col2 = st.columns(2)
        with login_col1:
            student_id = st.text_input("Student ID Number", placeholder="e.g., 20241011")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            # Login action
            if st.button("Log In", key="login_btn"):
                if not student_id or not password:
                    st.error("Please fill up both ID and Password fields.")
                else:
                    # Check for chairperson access override
                    if student_id == "chairman1947" and password == "RecoletosCE":
                        st.session_state["user_authenticated"] = True
                        st.session_state["user_role"] = "chairman"
                        st.session_state["student_id"] = "ADMIN"
                        st.session_state["student_name"] = "CE Chairperson"
                        st.success("Successfully logged in as Chairperson!")
                        st.rerun()
                    else:
                        # Standard student login via Apps Script
                        import hashlib
                        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
                        res = call_api("login", {"student_id": student_id, "password_hash": pwd_hash})
                        
                        if res.get("success"):
                            st.session_state["user_authenticated"] = True
                            st.session_state["user_role"] = "student"
                            st.session_state["student_id"] = res["user"]["student_id"]
                            st.session_state["student_name"] = res["user"]["name"]
                            st.success(f"Welcome back, {res['user']['name']}!")
                            st.rerun()
                        else:
                            st.error(f"Login error: {res.get('error', 'Unknown credential error')}")
                            
    with register_tab:
        st.subheader("Create an Advising Profile")
        reg_col1, reg_col2 = st.columns(2)
        with reg_col1:
            new_id = st.text_input("Assign Student ID Number", placeholder="e.g., 20241011")
            new_name = st.text_input("Complete Name (Last, First, Middle)", placeholder="e.g., Dela Cruz, Juan Santos")
            new_pwd = st.text_input("Choose Password", type="password", placeholder="••••••••")
            
            if st.button("Register Account", key="register_btn"):
                if not new_id or not new_name or not new_pwd:
                    st.error("Please fill up all the fields to register.")
                else:
                    import hashlib
                    pwd_hash = hashlib.sha256(new_pwd.encode()).hexdigest()
                    res = call_api("register", {
                        "student_id": new_id,
                        "name": new_name,
                        "password_hash": pwd_hash
                    })
                    if res.get("success"):
                        st.success("Registration successful! You can now log in using the Login tab.")
                    else:
                        st.error(f"Registration error: {res.get('error', 'Could not create account')}")

# ==========================================
# 🏠 CHAIRPERSON / DEPARTMENT VIEWS
# ==========================================
elif st.session_state["user_role"] == "chairman":
    # Sidebar
    with st.sidebar:
        st.markdown("<div class='sidebar-brand'><h3>Advising Console</h3></div>", unsafe_allow_html=True)
        st.write(f"Logged in: **{st.session_state['student_name']}**")
        if st.button("Log Out"):
            st.session_state["user_authenticated"] = False
            st.session_state["user_role"] = None
            st.rerun()
            
    # Main Tabs for Chairman
    chair_tab1, chair_tab2, chair_tab3 = st.tabs(["📊 Student Overview", "⚠️ Active Department INCs", "🚦 Sequence Bottlenecks"])
    
    with chair_tab1:
        st.subheader("Department Student Directory")
        st.write("All registered Civil Engineering students and their current standing:")
        
        # Pull from Google Sheets API
        res = call_api("get_all_students", {})
        if res.get("success"):
            students_list = res.get("students", [])
            if students_list:
                df = pd.DataFrame(students_list)
                df.columns = ["Student ID", "Complete Name", "Year Standing", "Cumulative GWA", "Completed Units"]
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No students have registered in the portal yet.")
        else:
            st.error(f"Error fetching directory: {res.get('error')}")
            
    with chair_tab2:
        st.subheader("Unremoved Incomplete (INC) Marks")
        st.write("Current incomplete grades recorded across the department:")
        
        res = call_api("get_all_inc_marks", {})
        if res.get("success"):
            inc_list = res.get("inc_marks", [])
            if inc_list:
                df_inc = pd.DataFrame(inc_list)
                df_inc.columns = ["Student ID", "Student Name", "Course Code", "Att 1 Grade", "Att 1 Term", "Att 2 Grade", "Att 2 Term", "Att 3 Grade", "Att 3 Term"]
                st.dataframe(df_inc, use_container_width=True)
            else:
                st.success("✅ No incomplete marks found across the registered database!")
        else:
            st.error(f"Error fetching INC records: {res.get('error')}")
            
    with chair_tab3:
        st.subheader("Prerequisite Bottleneck Tracker")
        st.write("See who hasn't completed vital gateway course sequences:")
        
        gateways = ["EM 1A1", "EM 1B1", "ES 3", "ES 10", "CE 2A1", "CE 3A1"]
        res = call_api("get_sequence_bottlenecks", {"gateways": gateways})
        if res.get("success"):
            bottlenecks = res.get("bottlenecks", {})
            for course, students in bottlenecks.items():
                st.markdown(f"**🚦 {course} - {CURRICULUM[course]['name']}**")
                if students:
                    st.write(", ".join(students))
                else:
                    st.success("All registered students have passed this course!")
                st.markdown("<hr style='margin: 10px 0;'/>", unsafe_allow_html=True)
        else:
            st.error(f"Error fetching bottlenecks: {res.get('error')}")

# ==========================================
# 🎓 ACTIVE STUDENT ADVISING SYSTEM
# ==========================================
elif st.session_state["user_role"] == "student":
    
    # Refresh grades from the web app
    active_student_id = st.session_state["student_id"]
    active_student_name = st.session_state["student_name"]
    
    # Initialize / Pull student grades
    res_grades = call_api("get_grades", {"student_id": active_student_id})
    if not res_grades.get("success"):
        st.error(f"Failed to fetch academic history: {res_grades.get('error')}")
        st.stop()
        
    student_grades_raw = res_grades.get("grades", [])
    summary = calculate_academic_summary(student_grades_raw)
    
    # Push updated profile values to google sheets roster automatically
    call_api("update_profile", {
        "student_id": active_student_id,
        "standing": summary["standing"],
        "gwa": summary["gwa"],
        "units": summary["completed_units"]
    })
    
    # Sidebar Advising Profile
    with st.sidebar:
        st.markdown("<div class='sidebar-brand'><h3>Advising Profile</h3></div>", unsafe_allow_html=True)
        st.write(f"Student: **{active_student_name}**")
        st.write(f"ID: **{active_student_id}**")
        st.write(f"Standing: **{summary['standing']}**")
        st.write(f"GWA: **{summary['gwa']:.3f}**")
        st.write(f"Completed Units: **{summary['completed_units']} / 171**")
        
        st.markdown("<hr/>", unsafe_allow_html=True)
        if st.button("Log Out"):
            st.session_state["user_authenticated"] = False
            st.session_state["user_role"] = None
            st.rerun()

    # ==========================================
    # 🎛️ TABBED WORKSPACE WORKFLOW
    # ==========================================
    tab1, tab_planner, tab_grades, tab_ref = st.tabs([
        "📊 Academic Dashboard",
        "🗓️ Enrollment Planner",
        "📝 Student Grade Record",
        "📚 Curriculum Reference"
    ])
    
    # --------------------------------------------------
    # TAB 1: ACADEMIC DASHBOARD
    # --------------------------------------------------
    with tab1:
        st.subheader("Academic Status Overview")
        
        # Display cards
        card_col1, card_col2, card_col3, card_col4 = st.columns(4)
        with card_col1:
            st.markdown(f"""
                <div class="metric-card">
                    <p style="margin:0; font-size: 0.9rem; color: #555;">Completed Units</p>
                    <h2 style="margin:0; color:#006633; font-weight:bold;">{summary['completed_units']} <span style="font-size:1rem; color:#888;">/ 171</span></h2>
                </div>
            """, unsafe_allow_html=True)
        with card_col2:
            st.markdown(f"""
                <div class="metric-card">
                    <p style="margin:0; font-size: 0.9rem; color: #555;">Remaining Units</p>
                    <h2 style="margin:0; color:#006633; font-weight:bold;">{summary['remaining_units']}</h2>
                </div>
            """, unsafe_allow_html=True)
        with card_col3:
            st.markdown(f"""
                <div class="gold-metric-card">
                    <p style="margin:0; font-size: 0.9rem; color: #555;">Cumulative GWA</p>
                    <h2 style="margin:0; color:#db9d00; font-weight:bold;">{summary['gwa']:.3f}</h2>
                </div>
            """, unsafe_allow_html=True)
        with card_col4:
            st.markdown(f"""
                <div class="metric-card">
                    <p style="margin:0; font-size: 0.9rem; color: #555;">Incompletes (INCs)</p>
                    <h2 style="margin:0; color:#006633; font-weight:bold;">{summary['inc_count']}</h2>
                </div>
            """, unsafe_allow_html=True)

        # Progress bars for level-by-level completion
        st.subheader("Progress by Year Level")
        for level in ["1st Year", "2nd Year", "3rd Year", "4th Year"]:
            completed = summary["completed_units_by_level"][level]
            total = summary["total_units_by_level"][level]
            pct = (completed / total) if total > 0 else 0.0
            
            progress_col1, progress_col2 = st.columns([1, 6])
            with progress_col1:
                st.write(f"**{level}**")
            with progress_col2:
                st.progress(pct, text=f"{completed} / {total} units completed ({pct*100:.1f}%)")

    # --------------------------------------------------
    # TAB 2: ENROLLMENT PLANNER
    # --------------------------------------------------
    with tab_planner:
        st.subheader("Prerequisite & Co-requisite Advisor")
        st.write("Plan and check eligibility for the following semester's scheduling:")
        
        planned_courses = st.multiselect("Select courses you plan to enroll in next:", options=list(CURRICULUM.keys()))
        
        if planned_courses:
            checks_ok = True
            eligibility_list = []
            
            # Map of already passed courses
            passed_courses = {code for code, details in CURRICULUM.items() 
                              if evaluate_course_status({
                                  "att1_grade": summary["grades_map"].get(code, {}).get("att1_grade", ""),
                                  "att2_grade": summary["grades_map"].get(code, {}).get("att2_grade", ""),
                                  "att3_grade": summary["grades_map"].get(code, {}).get("att3_grade", "")
                              })["status"] == "Passed"}
            
            for code in planned_courses:
                details = CURRICULUM[code]
                prereqs = details["prereq"]
                coreqs = details["coreq"]
                
                # Check standing prerequisites
                prereq_met = True
                failed_reasons = []
                
                for req in prereqs:
                    if req == "2nd Year Standing" and summary["completed_units"] < 45:
                        prereq_met = False
                        failed_reasons.append("Requires 2nd Year Standing (minimum 45 completed units)")
                    elif req == "3rd Year Standing" and summary["completed_units"] < 100:
                        prereq_met = False
                        failed_reasons.append("Requires 3rd Year Standing (minimum 100 completed units)")
                    elif req == "4th Year Standing" and summary["completed_units"] < 153:
                        prereq_met = False
                        failed_reasons.append("Requires 4th Year Standing (minimum 153 completed units)")
                    elif req not in ["2nd Year Standing", "3rd Year Standing", "4th Year Standing"] and req not in passed_courses:
                        prereq_met = False
                        failed_reasons.append(f"Prerequisite course {req} ({CURRICULUM[req]['name']}) is not completed")
                        
                # Check co-requisites
                coreq_met = True
                for req in coreqs:
                    if req not in passed_courses and req not in planned_courses:
                        coreq_met = False
                        failed_reasons.append(f"Co-requisite course {req} ({CURRICULUM[req]['name']}) must be taken simultaneously or previously")
                        
                if prereq_met and coreq_met:
                    eligibility_list.append({"Course": code, "Status": "✅ ELIGIBLE", "Remarks": "All requirements satisfied"})
                else:
                    checks_ok = False
                    eligibility_list.append({"Course": code, "Status": "❌ INELIGIBLE", "Remarks": " | ".join(failed_reasons)})
            
            # Display results in structured table
            el_df = pd.DataFrame(eligibility_list)
            st.table(el_df)
            
            if checks_ok:
                st.success("🎉 Excellent! Your proposed schedule is 100% compliant with prerequisites!")
            else:
                st.error("🚨 Warning: You have chosen courses for which prerequisites/co-requisites have not been met.")

    # --------------------------------------------------
    # TAB 3: STUDENT GRADE RECORD
    # --------------------------------------------------
    with tab_grades:
        st.subheader("Academic Records Editor")
        st.write("Update and audit your grade records. Please remember to click **Save Changes to Cloud** below after editing!")
        
        # Build initial dataframe for editing
        table_rows = []
        for code, details in CURRICULUM.items():
            g_rec = summary["grades_map"].get(code, {})
            table_rows.append({
                "Course Code": code,
                "Description": details["name"],
                "Units": details["units"],
                "Year Level": details["year"],
                "Semester": details["sem"],
                "Attempt 1 Term": g_rec.get("att1_term", ""),
                "Attempt 1 Grade": g_rec.get("att1_grade", ""),
                "Attempt 2 Term": g_rec.get("att2_term", ""),
                "Attempt 2 Grade": g_rec.get("att2_grade", ""),
                "Attempt 3 Term": g_rec.get("att3_term", ""),
                "Attempt 3 Grade": g_rec.get("att3_grade", "")
            })
            
        initial_df = pd.DataFrame(table_rows)
        
        # Config options for dropdown editors
        edited_df = st.data_editor(
            initial_df,
            column_config={
                "Course Code": st.column_config.TextColumn("Course Code", disabled=True),
                "Description": st.column_config.TextColumn("Description", disabled=True),
                "Units": st.column_config.NumberColumn("Units", disabled=True),
                "Year Level": st.column_config.TextColumn("Year Level", disabled=True),
                "Semester": st.column_config.TextColumn("Semester", disabled=True),
                "Attempt 1 Term": st.column_config.SelectboxColumn("Attempt 1 Term", options=SEMESTERS),
                "Attempt 1 Grade": st.column_config.SelectboxColumn("Attempt 1 Grade", options=GRADES),
                "Attempt 2 Term": st.column_config.SelectboxColumn("Attempt 2 Term", options=SEMESTERS),
                "Attempt 2 Grade": st.column_config.SelectboxColumn("Attempt 2 Grade", options=GRADES),
                "Attempt 3 Term": st.column_config.SelectboxColumn("Attempt 3 Term", options=SEMESTERS),
                "Attempt 3 Grade": st.column_config.SelectboxColumn("Attempt 3 Grade", options=GRADES)
            },
            num_rows="fixed",
            use_container_width=True,
            key="grades_grid"
        )
        
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # Save Button to persist edited df to Google Sheet database
        if st.button("💾 Save Changes to Cloud", key="save_cloud_btn"):
            changed_rows_count = 0
            with st.spinner("Synchronizing changes with Google Sheets..."):
                for idx, row in edited_df.iterrows():
                    code = row["Course Code"]
                    init_row = initial_df.loc[initial_df["Course Code"] == code].iloc[0]
                    
                    # Verify if row has differences
                    has_diff = (
                        row["Attempt 1 Term"] != init_row["Attempt 1 Term"] or
                        row["Attempt 1 Grade"] != init_row["Attempt 1 Grade"] or
                        row["Attempt 2 Term"] != init_row["Attempt 2 Term"] or
                        row["Attempt 2 Grade"] != init_row["Attempt 2 Grade"] or
                        row["Attempt 3 Term"] != init_row["Attempt 3 Term"] or
                        row["Attempt 3 Grade"] != init_row["Attempt 3 Grade"]
                    )
                    
                    if has_diff:
                        payload = {
                            "student_id": active_student_id,
                            "course_code": code,
                            "grades": {
                                "att1_grade": row["Attempt 1Grade"] if "Attempt 1Grade" in row else row["Attempt 1 Grade"],
                                "att1_term": row["Attempt 1 Term"],
                                "att2_grade": row["Attempt 2Grade"] if "Attempt 2Grade" in row else row["Attempt 2 Grade"],
                                "att2_term": row["Attempt 2 Term"],
                                "att3_grade": row["Attempt 3Grade"] if "Attempt 3Grade" in row else row["Attempt 3 Grade"],
                                "att3_term": row["Attempt 3 Term"]
                            }
                        }
                        res = call_api("save_grade", payload)
                        if res.get("success"):
                            changed_rows_count += 1
                        else:
                            st.error(f"Error saving {code}: {res.get('error')}")
                            
            if changed_rows_count > 0:
                st.success(f"Successfully synchronized {changed_rows_count} updated course records with Google Sheets!")
                st.rerun()
            else:
                st.info("No modifications detected to synchronize.")

    # --------------------------------------------------
    # TAB 4: CURRICULUM REFERENCE
    # --------------------------------------------------
    with tab_ref:
        st.subheader("BSCE Master Curriculum Reference")
        st.write("Browse courses, prerequisites, and unit distributions:")
        
        # Filter options
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            filt_year = st.selectbox("Filter by Year Level:", options=["All Year Levels", "1st Year", "2nd Year", "3rd Year", "4th Year"])
        with filter_col2:
            filt_sem = st.selectbox("Filter by Semester:", options=["All Semesters", "1st Semester", "2nd Semester", "Summer"])
            
        # Build curriculum df
        ref_rows = []
        for code, details in CURRICULUM.items():
            if filt_year != "All Year Levels" and details["year"] != filt_year:
                continue
            if filt_sem != "All Semesters" and details["sem"] != filt_sem:
                continue
                
            ref_rows.append({
                "Course Code": code,
                "Description": details["name"],
                "Units": details["units"],
                "Year Level": details["year"],
                "Semester": details["sem"],
                "Prerequisites": ", ".join(details["prereq"]) if details["prereq"] else "None",
                "Co-requisites": ", ".join(details["coreq"]) if details["coreq"] else "None"
            })
            
        ref_df = pd.DataFrame(ref_rows)
        if not ref_df.empty:
            st.dataframe(ref_df, use_container_width=True, hide_index=True)
        else:
            st.info("No courses found matching selected filters.")

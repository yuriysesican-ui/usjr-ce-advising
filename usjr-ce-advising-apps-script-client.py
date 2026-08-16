import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import requests

# Set page configuration
st.set_page_config(
    page_title="USJ-R Civil Engineering Advising Portal",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 SYSTEM THEMING & CUSTOM CSS (GREEN & GOLD)
# ==========================================
# USJ-R Official Colors: Forest Green (#006633) & Athletic Gold (#FFCC00)
st.markdown("""
<style>
    .reportview-container {
        background-color: #f4f6f9;
    }
    .sidebar .sidebar-content {
        background-color: #006633;
        color: white;
    }
    h1, h2, h3 {
        color: #006633;
    }
    .stButton>button {
        background-color: #006633;
        color: white;
        border-radius: 5px;
        border: 1px solid #006633;
    }
    .stButton>button:hover {
        background-color: #FFCC00;
        color: #006633;
        border: 1px solid #FFCC00;
    }
    .status-badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🗄️ MASTER CURRICULUM DATABASE (73 COURSES)
# ==========================================
CURRICULUM = {
    # Year 1 - Semester 1
    "GE-PC": {"name": "Purposive Communication", "units": 3, "year": "1st Year", "sem": "1st Sem", "prereq": [], "coreq": []},
    "GE-USELF": {"name": "Understanding the Self", "units": 3, "year": "1st Year", "sem": "1st Sem", "prereq": [], "coreq": []},
    "GE-MATH": {"name": "Mathematics in the Modern World", "units": 3, "year": "1st Year", "sem": "1st Sem", "prereq": [], "coreq": []},
    "CHEM111": {"name": "Chemistry for Engineers", "units": 3, "year": "1st Year", "sem": "1st Sem", "prereq": [], "coreq": []},
    "CHEM111L": {"name": "Chemistry for Engineers Lab", "units": 1, "year": "1st Year", "sem": "1st Sem", "prereq": [], "coreq": []},
    "MATH111": {"name": "Calculus 1", "units": 3, "year": "1st Year", "sem": "1st Sem", "prereq": [], "coreq": []},
    "CE111": {"name": "Civil Engineering Orientation", "units": 2, "year": "1st Year", "sem": "1st Sem", "prereq": [], "coreq": []},
    "NSTP1": {"name": "National Service Training Program 1", "units": 3, "year": "1st Year", "sem": "1st Sem", "prereq": [], "coreq": []},
    "PE1": {"name": "Physical Education 1", "units": 2, "year": "1st Year", "sem": "1st Sem", "prereq": [], "coreq": []},
    "RELE1": {"name": "Religious Education 1", "units": 3, "year": "1st Year", "sem": "1st Sem", "prereq": [], "coreq": []},

    # Year 1 - Semester 2
    "GE-STS": {"name": "Science, Technology, and Society", "units": 3, "year": "1st Year", "sem": "2nd Sem", "prereq": [], "coreq": []},
    "GE-ART": {"name": "Art Appreciation", "units": 3, "year": "1st Year", "sem": "2nd Sem", "prereq": [], "coreq": []},
    "PHYS121": {"name": "Physics for Engineers", "units": 3, "year": "1st Year", "sem": "2nd Sem", "prereq": ["MATH111"], "coreq": []},
    "PHYS121L": {"name": "Physics for Engineers Lab", "units": 1, "year": "1st Year", "sem": "2nd Sem", "prereq": ["MATH111"], "coreq": []},
    "MATH121": {"name": "Calculus 2", "units": 3, "year": "1st Year", "sem": "2nd Sem", "prereq": ["MATH111"], "coreq": []},
    "ESC121": {"name": "Computer-Aided Drafting", "units": 1, "year": "1st Year", "sem": "2nd Sem", "prereq": [], "coreq": []},
    "NSTP2": {"name": "National Service Training Program 2", "units": 3, "year": "1st Year", "sem": "2nd Sem", "prereq": ["NSTP1"], "coreq": []},
    "PE2": {"name": "Physical Education 2", "units": 2, "year": "1st Year", "sem": "2nd Sem", "prereq": ["PE1"], "coreq": []},
    "RELE2": {"name": "Religious Education 2", "units": 3, "year": "1st Year", "sem": "2nd Sem", "prereq": ["RELE1"], "coreq": []},

    # Year 2 - Semester 1
    "GE-CW": {"name": "The Contemporary World", "units": 3, "year": "2nd Year", "sem": "1st Sem", "prereq": [], "coreq": []},
    "MATH211": {"name": "Differential Equations", "units": 3, "year": "2nd Year", "sem": "1st Sem", "prereq": ["MATH121"], "coreq": []},
    "ESC211": {"name": "Engineering Economics", "units": 3, "year": "2nd Year", "sem": "1st Sem", "prereq": ["MATH121"], "coreq": []},
    "ESC212": {"name": "Statics of Rigid Bodies", "units": 3, "year": "2nd Year", "sem": "1st Sem", "prereq": ["PHYS121", "MATH121"], "coreq": []},
    "CE211": {"name": "Surveying 1 (Elementary Surveying)", "units": 3, "year": "2nd Year", "sem": "1st Sem", "prereq": ["MATH121"], "coreq": []},
    "CE211L": {"name": "Surveying 1 Lab", "units": 1, "year": "2nd Year", "sem": "1st Sem", "prereq": ["MATH121"], "coreq": []},
    "PE3": {"name": "Physical Education 3", "units": 2, "year": "2nd Year", "sem": "1st Sem", "prereq": ["PE2"], "coreq": []},
    "RELE3": {"name": "Religious Education 3", "units": 3, "year": "2nd Year", "sem": "1st Sem", "prereq": ["RELE2"], "coreq": []},

    # Year 2 - Semester 2
    "GE-RHIST": {"name": "Readings in Philippine History", "units": 3, "year": "2nd Year", "sem": "2nd Sem", "prereq": [], "coreq": []},
    "MATH221": {"name": "Numerical Solutions / Advanced Math", "units": 3, "year": "2nd Year", "sem": "2nd Sem", "prereq": ["MATH211"], "coreq": []},
    "ESC221": {"name": "Dynamics of Rigid Bodies", "units": 2, "year": "2nd Year", "sem": "2nd Sem", "prereq": ["ESC212"], "coreq": []},
    "ESC222": {"name": "Mechanics of Deformable Bodies", "units": 3, "year": "2nd Year", "sem": "2nd Sem", "prereq": ["ESC212"], "coreq": []},
    "CE221": {"name": "Surveying 2 (Higher Surveying)", "units": 3, "year": "2nd Year", "sem": "2nd Sem", "prereq": ["CE211"], "coreq": []},
    "CE221L": {"name": "Surveying 2 Lab", "units": 1, "year": "2nd Year", "sem": "2nd Sem", "prereq": ["CE211L"], "coreq": []},
    "CE222": {"name": "Construction Materials and Testing", "units": 2, "year": "2nd Year", "sem": "2nd Sem", "prereq": ["ESC212"], "coreq": []},
    "CE222L": {"name": "Construction Materials Lab", "units": 1, "year": "2nd Year", "sem": "2nd Sem", "prereq": ["ESC212"], "coreq": []},
    "PE4": {"name": "Physical Education 4", "units": 2, "year": "2nd Year", "sem": "2nd Sem", "prereq": ["PE3"], "coreq": []},
    "RELE4": {"name": "Religious Education 4", "units": 3, "year": "2nd Year", "sem": "2nd Sem", "prereq": ["RELE3"], "coreq": []},

    # Year 3 - Semester 1
    "GE-LIT": {"name": "Literature of the Philippines", "units": 3, "year": "3rd Year", "sem": "1st Sem", "prereq": [], "coreq": []},
    "CE311": {"name": "Structural Theory", "units": 3, "year": "3rd Year", "sem": "1st Sem", "prereq": ["ESC222"], "coreq": []},
    "CE311L": {"name": "Structural Analysis Lab", "units": 1, "year": "3rd Year", "sem": "1st Sem", "prereq": ["ESC222"], "coreq": []},
    "CE312": {"name": "Fluid Mechanics", "units": 3, "year": "3rd Year", "sem": "1st Sem", "prereq": ["ESC221", "ESC222"], "coreq": []},
    "CE312L": {"name": "Fluid Mechanics Lab", "units": 1, "year": "3rd Year", "sem": "1st Sem", "prereq": ["ESC221", "ESC222"], "coreq": []},
    "CE313": {"name": "Soil Mechanics 1", "units": 3, "year": "3rd Year", "sem": "1st Sem", "prereq": ["ESC222"], "coreq": []},
    "CE313L": {"name": "Soil Mechanics Lab", "units": 1, "year": "3rd Year", "sem": "1st Sem", "prereq": ["ESC222"], "coreq": []},
    "CE314": {"name": "Transportation Engineering", "units": 3, "year": "3rd Year", "sem": "1st Sem", "prereq": ["CE221"], "coreq": []},
    "CE315": {"name": "Building Systems Design", "units": 2, "year": "3rd Year", "sem": "1st Sem", "prereq": ["ESC121"], "coreq": []},

    # Year 3 - Semester 2
    "GE-ETHICS": {"name": "Ethics", "units": 3, "year": "3rd Year", "sem": "2nd Sem", "prereq": [], "coreq": []},
    "CE321": {"name": "Design of Reinforced Concrete Members", "units": 3, "year": "3rd Year", "sem": "2nd Sem", "prereq": ["CE311"], "coreq": []},
    "CE322": {"name": "Hydraulics", "units": 3, "year": "3rd Year", "sem": "2nd Sem", "prereq": ["CE312"], "coreq": []},
    "CE322L": {"name": "Hydraulics Lab", "units": 1, "year": "3rd Year", "sem": "2nd Sem", "prereq": ["CE312L"], "coreq": []},
    "CE323": {"name": "Soil Mechanics 2 (Foundation Engineering)", "units": 3, "year": "3rd Year", "sem": "2nd Sem", "prereq": ["CE313"], "coreq": []},
    "CE324": {"name": "Principles of Highway and Railroad Eng.", "units": 3, "year": "3rd Year", "sem": "2nd Sem", "prereq": ["CE314"], "coreq": []},
    "CE325": {"name": "Construction Occupational Safety & Health", "units": 2, "year": "3rd Year", "sem": "2nd Sem", "prereq": ["CE222"], "coreq": []},
    "CE326": {"name": "Hydrology", "units": 2, "year": "3rd Year", "sem": "2nd Sem", "prereq": ["CE312"], "coreq": []},

    # Year 3 - Summer
    "CE331": {"name": "CE Practicum / Internship (240 Hours)", "units": 3, "year": "3rd Year", "sem": "Summer", "prereq": ["CE321", "CE323"], "coreq": []},

    # Year 4 - Semester 1
    "RIZAL": {"name": "Life and Works of Rizal", "units": 3, "year": "4th Year", "sem": "1st Sem", "prereq": [], "coreq": []},
    "CE411": {"name": "Design of Steel Structures", "units": 3, "year": "4th Year", "sem": "1st Sem", "prereq": ["CE311"], "coreq": []},
    "CE412": {"name": "Water Resources Engineering", "units": 3, "year": "4th Year", "sem": "1st Sem", "prereq": ["CE322"], "coreq": []},
    "CE413": {"name": "Quantity Surveying and Estimating", "units": 2, "year": "4th Year", "sem": "1st Sem", "prereq": ["CE315"], "coreq": ["CE414"]},
    "CE414": {"name": "Construction Methods and Project Mgt.", "units": 3, "year": "4th Year", "sem": "1st Sem", "prereq": ["CE325"], "coreq": []},
    "CE414L": {"name": "Project Management Software Lab", "units": 1, "year": "4th Year", "sem": "1st Sem", "prereq": ["CE325"], "coreq": []},
    "CE415": {"name": "CE Project 1 (Thesis/Capstone)", "units": 2, "year": "4th Year", "sem": "1st Sem", "prereq": ["CE321", "CE323", "CE324"], "coreq": []},
    "CEE411": {"name": "CE Elective 1 (Structural Design)", "units": 3, "year": "4th Year", "sem": "1st Sem", "prereq": ["CE321"], "coreq": []},
    "CEE412": {"name": "CE Elective 2 (Geotechnical Eng.)", "units": 3, "year": "4th Year", "sem": "1st Sem", "prereq": ["CE323"], "coreq": []},

    # Year 4 - Semester 2
    "GE-TAX": {"name": "Income Taxation and Agrarian Reform", "units": 3, "year": "4th Year", "sem": "2nd Sem", "prereq": [], "coreq": []},
    "CE421": {"name": "CE Laws, Contracts, and Ethics", "units": 2, "year": "4th Year", "sem": "2nd Sem", "prereq": ["CE414"], "coreq": []},
    "CE422": {"name": "CE Project 2 (Thesis Defense)", "units": 2, "year": "4th Year", "sem": "2nd Sem", "prereq": ["CE415"], "coreq": []},
    "CE423": {"name": "Bridge Engineering", "units": 3, "year": "4th Year", "sem": "2nd Sem", "prereq": ["CE411", "CE321"], "coreq": []},
    "CE424": {"name": "Earthquake Engineering", "units": 3, "year": "4th Year", "sem": "2nd Sem", "prereq": ["CE311"], "coreq": []},
    "CEE423": {"name": "CE Elective 3 (Water Resources Design)", "units": 3, "year": "4th Year", "sem": "2nd Sem", "prereq": ["CE412"], "coreq": []},
    "CEE424": {"name": "CE Elective 4 (Transportation Design)", "units": 3, "year": "4th Year", "sem": "2nd Sem", "prereq": ["CE324"], "coreq": []}
}

SEMESTERS_LIST = ["", "1sem24-25", "2sem24-25", "sum24-25", "1sem25-26", "2sem25-26", "sum25-26", "1sem26-27", "2sem26-27", "sum26-27"]
GRADES_LIST = ["", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "3.0", "5.0", "INC", "W"]

# ==========================================
# 🗄️ GOOGLE APPS SCRIPT WEB API CONNECTOR
# ==========================================
def call_db_api(action, payload):
    """Makes a direct HTTP POST request to the Google Apps Script Web App."""
    if "database_url" not in st.secrets:
        st.error("Configuration error: 'st.secrets has no key \"database_url\". Please check Streamlit Secrets.")
        st.stop()
    
    url = st.secrets["database_url"]
    full_payload = {"action": action, **payload}
    try:
        response = requests.post(url, json=full_payload)
        if response.status_code == 401:
            st.error("Authentication Error: 401 Unauthorized. Make sure who has access is set to 'Anyone'!")
            return {"success": False, "error": "Unauthorized (401)"}
        elif response.status_code != 200:
            st.error(f"Database error! Status code: {response.status_code}")
            return {"success": False, "error": f"Server error {response.status_code}"}
        return response.json()
    except Exception as e:
        st.error(f"Failed to connect to spreadsheet database: {str(e)}")
        return {"success": False, "error": str(e)}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(student_id, name, password):
    pwd_hash = hash_password(password)
    return call_db_api("register", {
        "student_id": student_id,
        "name": name,
        "password_hash": pwd_hash
    })

def authenticate_user(student_id, password):
    pwd_hash = hash_password(password)
    return call_db_api("login", {
        "student_id": student_id,
        "password_hash": pwd_hash
    })

def get_student_grades(student_id):
    res = call_db_api("get_grades", {"student_id": student_id})
    if res.get("success"):
        return res.get("grades", [])
    return []

def save_student_grade(student_id, code, att1_g, att1_t, att2_g, att2_t, att3_g, att3_t):
    return call_db_api("save_grade", {
        "student_id": student_id,
        "course_code": code,
        "grades": {
            "att1_grade": att1_g, "att1_term": att1_t,
            "att2_grade": att2_g, "att2_term": att2_t,
            "att3_grade": att3_g, "att3_term": att3_t
        }
    })

def update_student_profile_summary(student_id, standing, gwa, units):
    return call_db_api("update_profile", {
        "student_id": student_id,
        "standing": standing,
        "gwa": gwa,
        "units": units
    })

def get_all_registered_students():
    res = call_db_api("get_all_students", {})
    if res.get("success"):
        return res.get("students", [])
    return []

def get_all_inc_marks():
    res = call_db_api("get_all_inc_marks", {})
    if res.get("success"):
        return res.get("inc_marks", [])
    return []

def get_sequence_bottlenecks(gateways):
    res = call_db_api("get_sequence_bottlenecks", {"gateways": gateways})
    if res.get("success"):
        return res.get("bottlenecks", {})
    return {}

# Initialize session states
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_profile" not in st.session_state:
    st.session_state["user_profile"] = None
if "is_chairman" not in st.session_state:
    st.session_state["is_chairman"] = False
if "loaded_student_by_adviser" not in st.session_state:
    st.session_state["loaded_student_by_adviser"] = None

# Sidebar Authentication Layout
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e0/USJ-R_Seal.svg", width=100)
    st.markdown("### USJ-R CE Advising System")
    
    if not st.session_state["authenticated"]:
        auth_mode = st.radio("Choose Action", ["Login", "Register"])
        student_id_input = st.text_input("Student ID")
        password_input = st.text_input("Password", type="password")
        
        if auth_mode == "Register":
            full_name_input = st.text_input("Full Name (e.g. Juan dela Cruz)")
            if st.button("Create Account"):
                if student_id_input and password_input and full_name_input:
                    reg_res = register_user(student_id_input, full_name_input, password_input)
                    if reg_res.get("success"):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error(f"Registration error: {reg_res.get('error')}")
                else:
                    st.warning("Please fill in all registration fields!")
        else:
            if st.button("Login"):
                if student_id_input == "chairman1947" and password_input == "RecoletosCE":
                    st.session_state["authenticated"] = True
                    st.session_state["is_chairman"] = True
                    st.session_state["user_profile"] = {"student_id": "chairman1947", "name": "CE Department Chairperson", "standing": "Chairman", "gwa": 0.0, "units": 0}
                    st.rerun()
                elif student_id_input and password_input:
                    login_res = authenticate_user(student_id_input, password_input)
                    if login_res.get("success"):
                        st.session_state["authenticated"] = True
                        st.session_state["is_chairman"] = False
                        st.session_state["user_profile"] = login_res.get("user")
                        st.rerun()
                    else:
                        st.error(f"Login error: {login_res.get('error')}")
                else:
                    st.warning("Please enter your ID and password!")
    else:
        st.success(f"Logged in as:\n**{st.session_state['user_profile']['name']}**")
        if st.session_state["is_chairman"]:
            st.info("🛡️ Administrator Mode Enabled")
            
            students_list = get_all_registered_students()
            if students_list:
                s_options = {f"{s['student_id']} - {s['name']}": s for s in students_list}
                selected_s_str = st.selectbox("Select Student to Advise/View", ["-- Select Student --"] + list(s_options.keys()))
                if selected_s_str != "-- Select Student --":
                    st.session_state["loaded_student_by_adviser"] = s_options[selected_s_str]
                else:
                    st.session_state["loaded_student_by_adviser"] = None
            else:
                st.warning("No students registered yet.")
        
        if st.button("Log Out"):
            st.session_state["authenticated"] = False
            st.session_state["is_chairman"] = False
            st.session_state["user_profile"] = None
            st.session_state["loaded_student_by_adviser"] = None
            st.rerun()

# ==========================================
# 🏛️ BRAND HEADER PANEL (WITH LOGO & LABELS)
# ==========================================
st.markdown("""
<div style='display: flex; align-items: center; background-color: #006633; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
    <div style='flex: 1; text-align: center; color: #FFCC00; font-family: sans-serif;'>
        <h2 style='margin: 0; color: #FFCC00;'>UNIVERSITY OF SAN JOSE - RECOLETOS</h2>
        <h4 style='margin: 5px 0 0 0; color: white;'>Department of Civil Engineering Advising Portal</h4>
    </div>
</div>
""", unsafe_allow_html=True)

# Select active student context
active_student = None
if st.session_state["authenticated"]:
    if st.session_state["is_chairman"] and st.session_state["loaded_student_by_adviser"]:
        active_student = st.session_state["loaded_student_by_adviser"]
    elif not st.session_state["is_chairman"]:
        active_student = st.session_state["user_profile"]

if not active_student:
    if st.session_state["is_chairman"]:
        st.warning("👈 Please select a student from the sidebar dropdown to view their dashboard and plan.")
        
        # CHAIRPERSON EXCLUSIVE VIEWS
        st.markdown("### 🛡️ Chairperson Global Insights")
        insight_tab1, insight_tab2, insight_tab3 = st.tabs(["📋 Registered Students", "⚠️ Active INC Marks", "⚙️ Sequence Bottlenecks"])
        
        with insight_tab1:
            all_s = get_all_registered_students()
            if all_s:
                df_all = pd.DataFrame(all_s)
                df_all.columns = ["Student ID", "Full Name", "Academic Standing", "Cumulative GWA", "Completed Units"]
                st.dataframe(df_all, use_container_width=True)
            else:
                st.info("No registered students found.")
                
        with insight_tab2:
            all_incs = get_all_inc_marks()
            if all_incs:
                df_incs = pd.DataFrame(all_incs)
                st.dataframe(df_incs[["student_id", "name", "course_code"]], use_container_width=True)
            else:
                st.success("Clean slate! No active INC grades found across the department.")
                
        with insight_tab3:
            gateways = ["MATH111", "MATH121", "ESC212", "ESC222", "CE311", "CE312", "CE313"]
            b_data = get_sequence_bottlenecks(gateways)
            if b_data:
                for code, students in b_data.items():
                    st.markdown(f"**{code} - {CURRICULUM[code]['name']} ({len(students)} students blocked)**")
                    if students:
                        st.write(", ".join(students))
                    else:
                        st.write("None")
                    st.markdown("---")
    else:
        st.info("🔑 Please Login or Register in the sidebar to access your academic planner.")
else:
    active_student_id = active_student["student_id"]
    active_student_name = active_student["name"]

    # ==========================================
    # 🔄 REAL-TIME DATA STATE SYNCHRONIZER
    # ==========================================
    db_grades = get_student_grades(active_student_id)
    grades_dict = {}
    for g in db_grades:
        grades_dict[g["course_code"]] = {
            "att1_g": g.get("att1_grade", ""), "att1_t": g.get("att1_term", ""),
            "att2_g": g.get("att2_grade", ""), "att2_t": g.get("att2_term", ""),
            "att3_g": g.get("att3_grade", ""), "att3_t": g.get("att3_term", "")
        }

    # ==========================================
    # 🧮 LOGICAL CALCULATION FUNCTIONS (GROUNDED)
    # ==========================================
    def evaluate_course_status(attempts):
        active_g = ""
        for g in [attempts["att1_g"], attempts["att2_g"], attempts["att3_g"]]:
            if g != "":
                active_g = g
        
        if active_g == "":
            return "None"
        if active_g in ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "3.0"]:
            return "Passed"
        if active_g == "INC":
            return "INC"
        if active_g == "W":
            return "W"
        if active_g == "5.0":
            return "Failed"
        return "Ongoing"

    # Resolve course status map
    course_status_map = {}
    gwa_points_sum = 0.0
    gwa_units_sum = 0.0
    completed_units_by_level = {"1st Year": 0, "2nd Year": 0, "3rd Year": 0, "4th Year": 0}
    total_units_by_level = {"1st Year": 0, "2nd Year": 0, "3rd Year": 0, "4th Year": 0}

    for code, details in CURRICULUM.items():
        total_units_by_level[details["year"]] += details["units"]
        attempts = grades_dict.get(code, {"att1_g": "", "att1_t": "", "att2_g": "", "att2_t": "", "att3_g": "", "att3_t": ""})
        status = evaluate_course_status(attempts)
        course_status_map[code] = status
        
        last_g = ""
        for g in [attempts["att1_g"], attempts["att2_g"], attempts["att3_g"]]:
            if g != "":
                last_g = g
        if last_g and last_g not in ["INC", "W", ""]:
            gwa_points_sum += float(last_g) * details["units"]
            gwa_units_sum += details["units"]
            
        if status == "Passed":
            completed_units_by_level[details["year"]] += details["units"]

    total_completed_units = sum(completed_units_by_level.values())
    total_curriculum_units = sum(total_units_by_level.values())
    remaining_curriculum_units = total_curriculum_units - total_completed_units
    cumulative_gwa = round(gwa_points_sum / gwa_units_sum, 3) if gwa_units_sum > 0 else 0.0
    active_inc_count = sum(1 for code, status in course_status_map.items() if status == "INC")

    if total_completed_units >= 153:
        academic_standing_level = "4th Year"
    elif total_completed_units >= 100:
        academic_standing_level = "3rd Year"
    elif total_completed_units >= 45:
        academic_standing_level = "2nd Year"
    else:
        academic_standing_level = "1st Year"

    # Sync calculated values back to spreadsheet roster
    update_student_profile_summary(active_student_id, academic_standing_level, cumulative_gwa, total_completed_units)

    def is_prereq_satisfied(prereqs, status_map, standing):
        for req in prereqs:
            if status_map.get(req, "None") != "Passed":
                return False
        return True

    # ==========================================
    # 🎛️ TABBED SYSTEM CONTAINER
    # ==========================================
    tabs_to_render = ["📊 Academic Dashboard", "🗓️ Enrollment Planner", "📝 Student Grade Record", "📚 Curriculum Reference"]
    tab_widgets = st.tabs(tabs_to_render)

    # --------------------------------------------------
    # TAB 1: ACADEMIC DASHBOARD
    # --------------------------------------------------
    with tab_widgets[0]:
        st.markdown(f"### Welcome back, **{active_student_name}**! (ID: {active_student_id})")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Academic Year Level", academic_standing_level)
        with col2:
            st.metric("Cumulative GWA", f"{cumulative_gwa:.3f}" if cumulative_gwa > 0 else "N/A")
        with col3:
            st.metric("Completed Units", f"{total_completed_units} / {total_curriculum_units}")
        with col4:
            st.metric("Active INC Grades", active_inc_count)

        st.markdown("#### Year Level Completion Breakdown")
        for lvl, comp in completed_units_by_level.items():
            tot = total_units_by_level[lvl]
            pct = int((comp / tot) * 100) if tot > 0 else 0
            st.write(f"**{lvl}**: {comp} / {tot} Units ({pct}%)")
            st.progress(pct / 100.0)

    # --------------------------------------------------
    # TAB 2: ENROLLMENT PLANNER
    # --------------------------------------------------
    with tab_widgets[1]:
        st.markdown("### 🗓️ Smart Enrollment Planner (A.Y. 2026-2027)")
        st.info("Choose the courses you want to enroll in. The planner automatically verifies all pre-requisites against your spreadsheet history.")
        
        st.markdown("#### Available Plan Selection")
        eligible_courses = []
        for code, details in CURRICULUM.items():
            curr_status = course_status_map.get(code, "None")
            if curr_status != "Passed":
                prereq_ok = is_prereq_satisfied(details["prereq"], course_status_map, academic_standing_level)
                if prereq_ok:
                    eligible_courses.append(code)
        
        if eligible_courses:
            col_sel1, col_sel2 = st.columns([2, 1])
            with col_sel1:
                selections = st.multiselect("Select Courses for Your Enrollment Sandbox", eligible_courses, format_func=lambda x: f"{x} - {CURRICULUM[x]['name']} ({CURRICULUM[x]['units']} Units)")
            with col_sel2:
                total_plan_units = sum(CURRICULUM[s]["units"] for s in selections)
                st.metric("Planned Units", f"{total_plan_units} / 24 Max")
                if total_plan_units > 24:
                    st.error("⚠️ Overload warning! You have exceeded the maximum of 24 units.")
            
            if selections:
                st.markdown("##### 📑 Selected Sandbox Schedule")
                plan_df = pd.DataFrame([{
                    "Course Code": s,
                    "Course Name": CURRICULUM[s]["name"],
                    "Units": CURRICULUM[s]["units"],
                    "Year-Level Recommended": CURRICULUM[s]["year"],
                    "Recommended Semester": CURRICULUM[s]["sem"]
                } for s in selections])
                st.table(plan_df)
        else:
            st.success("Congratulations! You have completed all courses in the USJ-R Civil Engineering curriculum.")

    # --------------------------------------------------
    # TAB 3: STUDENT GRADE RECORD
    # --------------------------------------------------
    with tab_widgets[2]:
        st.markdown("### 📝 Grade Record Bulk Editor")
        st.warning("Changes made here are written instantly and securely back to your Google Sheet database.")
        
        selected_edit_course = st.selectbox("Select Course to Record Grade", ["-- Select Course --"] + list(CURRICULUM.keys()))
        if selected_edit_course != "-- Select Course --":
            details = CURRICULUM[selected_edit_course]
            st.markdown(f"**Editing: {selected_edit_course} - {details['name']}** ({details['units']} Units)")
            
            current_grades = grades_dict.get(selected_edit_course, {"att1_g": "", "att1_t": "", "att2_g": "", "att2_t": "", "att3_g": "", "att3_t": ""})
            
            col_att1, col_att2, col_att3 = st.columns(3)
            with col_att1:
                st.markdown("**First Attempt**")
                att1_g_input = st.selectbox("Grade #1", GRADES_LIST, index=GRADES_LIST.index(current_grades["att1_g"]))
                att1_t_input = st.selectbox("Term #1", SEMESTERS_LIST, index=SEMESTERS_LIST.index(current_grades["att1_t"]))
            with col_att2:
                st.markdown("**Second Attempt**")
                att2_g_input = st.selectbox("Grade #2", GRADES_LIST, index=GRADES_LIST.index(current_grades["att2_g"]))
                att2_t_input = st.selectbox("Term #2", SEMESTERS_LIST, index=SEMESTERS_LIST.index(current_grades["att2_t"]))
            with col_att3:
                st.markdown("**Third Attempt**")
                att3_g_input = st.selectbox("Grade #3", GRADES_LIST, index=GRADES_LIST.index(current_grades["att3_g"]))
                att3_t_input = st.selectbox("Term #3", SEMESTERS_LIST, index=SEMESTERS_LIST.index(current_grades["att3_t"]))
            
            if st.button("💾 Commit Grade to Database"):
                save_res = save_student_grade(active_student_id, selected_edit_course, att1_g_input, att1_t_input, att2_g_input, att2_t_input, att3_g_input, att3_t_input)
                if save_res.get("success"):
                    st.success(f"Successfully committed grades for {selected_edit_course}!")
                    st.rerun()
                else:
                    st.error(f"Failed to save grade: {save_res.get('error')}")

    # --------------------------------------------------
    # TAB 4: CURRICULUM REFERENCE
    # --------------------------------------------------
    with tab_widgets[3]:
        st.markdown("### 📚 Curriculum & Prerequisite Map")
        
        ref_data = []
        for code, details in CURRICULUM.items():
            ref_data.append({
                "Code": code,
                "Course Name": details["name"],
                "Units": details["units"],
                "Year recommendation": details["year"],
                "Semester recommendation": details["sem"],
                "Prerequisites": ", ".join(details["prereq"]) if details["prereq"] else "None"
            })
        
        df_ref = pd.DataFrame(ref_data)
        st.dataframe(df_ref, use_container_width=True)

import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set page configuration
st.set_page_config(
    page_title="USJ-R Civil Engineering Advising App",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 SYSTEM THEMING & CUSTOM CSS (GREEN & GOLD)
# ==========================================
# USJ-R Official Colors: Forest Green (#006633) & Athletic Gold (#FFCC00)
st.markdown("""
<style>
    :root {
        --primary-color: #006633;
        --secondary-color: #FFCC00;
        --bg-color: #F4F6F4;
    }
    
    /* Style headers */
    .header-container {
        background: linear-gradient(135deg, #006633 0%, #004d26 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 25px;
        border-left: 8px solid #FFCC00;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        color: #FFFFFF;
        letter-spacing: 0.5px;
    }
    .header-subtitle {
        font-size: 1.2rem;
        color: #FFCC00;
        margin: 5px 0 0 0;
        font-weight: 600;
        letter-spacing: 1px;
    }
    .header-dept {
        font-size: 0.95rem;
        color: #E6F2EB;
        margin: 2px 0 0 0;
        font-style: italic;
    }
    
    /* Info boxes and stats */
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border-top: 4px solid #006633;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #006633;
    }
    .metric-lbl {
        font-size: 0.85rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Visual Semester Cards */
    .sem-card-green {
        background-color: #E6F2EB;
        border: 1.5px solid #006633;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .sem-card-yellow {
        background-color: #FFFCE6;
        border: 1.5px solid #FFCC00;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .sem-card-grey {
        background-color: #F2F2F7;
        border: 1.5px solid #D1D1D6;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* Sidebar branding */
    .sidebar-brand {
        text-align: center;
        padding: 10px;
        margin-bottom: 15px;
        background-color: #E6F2EB;
        border-radius: 8px;
        border-left: 4px solid #006633;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🗄️ MASTER CURRICULUM DATABASE (73 COURSES)
# ==========================================
CURRICULUM = {
    "EM 1A1": {"desc": "Engineering Calculus 1", "units": 3, "prereq": "None", "coreq": "None", "term": "1st Year, Sem 1"},
    "NS 1A1": {"desc": "Chemistry for Engineers (Lec)", "units": 3, "prereq": "None", "coreq": "None", "term": "1st Year, Sem 1"},
    "NS 1A2": {"desc": "Chemistry for Engineers (Lab)", "units": 1, "prereq": "None", "coreq": "NS 1A1", "term": "1st Year, Sem 1"},
    "CE 1A1": {"desc": "Civil Engineering Orientation", "units": 2, "prereq": "None", "coreq": "None", "term": "1st Year, Sem 1"},
    "ES 1": {"desc": "Engineering Drawing and Plans", "units": 2, "prereq": "None", "coreq": "None", "term": "1st Year, Sem 1"},
    "GE STS": {"desc": "Science, Technology, Engineering and Society", "units": 3, "prereq": "None", "coreq": "None", "term": "1st Year, Sem 1"},
    "ReEd 1": {"desc": "Initium Fidei: An Introduction to Doing Catholic Theology", "units": 3, "prereq": "None", "coreq": "None", "term": "1st Year, Sem 1"},
    "PE 1": {"desc": "Physical Education 1", "units": 2, "prereq": "None", "coreq": "None", "term": "1st Year, Sem 1"},
    "NSTP 1": {"desc": "Civic Welfare Training Service 11/ROTC 11", "units": 3, "prereq": "None", "coreq": "None", "term": "1st Year, Sem 1"},
    "GUIDANCE 1": {"desc": "Adjustment to College Life Phase 1", "units": 1, "prereq": "None", "coreq": "None", "term": "1st Year, Sem 1"},
    
    "EM 1B1": {"desc": "Engineering Calculus 2", "units": 3, "prereq": "EM 1A1", "coreq": "None", "term": "1st Year, Sem 2"},
    "NS 1B1": {"desc": "Physics for Engineers (Lec)", "units": 3, "prereq": "EM 1A1", "coreq": "EM 1B1", "term": "1st Year, Sem 2"},
    "NS 1B2": {"desc": "Physics for Engineers (Lab)", "units": 1, "prereq": "EM 1A1", "coreq": "NS 1B1, EM 1B1", "term": "1st Year, Sem 2"},
    "ES 2": {"desc": "Computer-Aided Drafting", "units": 2, "prereq": "ES 1", "coreq": "None", "term": "1st Year, Sem 2"},
    "ReEd 2": {"desc": "Written That You May Believe: An Introduction to Biblical Exegesis", "units": 3, "prereq": "ReEd 1", "coreq": "None", "term": "1st Year, Sem 2"},
    "GE MMW": {"desc": "Mathematics in the Modern World", "units": 3, "prereq": "None", "coreq": "None", "term": "1st Year, Sem 2"},
    "GE UTS": {"desc": "Understanding the Self", "units": 3, "prereq": "None", "coreq": "None", "term": "1st Year, Sem 2"},
    "PE 2": {"desc": "Physical Education 2", "units": 2, "prereq": "PE 1", "coreq": "None", "term": "1st Year, Sem 2"},
    "NSTP 2": {"desc": "Civic Welfare Training Service 12/ROTC 12", "units": 3, "prereq": "NSTP 1", "coreq": "None", "term": "1st Year, Sem 2"},
    "GUIDANCE 2": {"desc": "Adjustment to College Life Phase 2", "units": 1, "prereq": "None", "coreq": "None", "term": "1st Year, Sem 2"},
    
    "EM 2A1": {"desc": "Differential Equations", "units": 3, "prereq": "EM 1B1", "coreq": "None", "term": "2nd Year, Sem 1"},
    "ES 3": {"desc": "Statics of Rigid Bodies", "units": 3, "prereq": "EM 1B1, NS 1B1", "coreq": "None", "term": "2nd Year, Sem 1"},
    "CE 2A1": {"desc": "Fundamentals of Surveying", "units": 4, "prereq": "ES 1", "coreq": "None", "term": "2nd Year, Sem 1"},
    "ES 6": {"desc": "Engineering Economics", "units": 3, "prereq": "2nd Year Standing", "coreq": "None", "term": "2nd Year, Sem 1"},
    "ES 14": {"desc": "Environmental Science and Engineering", "units": 3, "prereq": "NS 1A1", "coreq": "None", "term": "2nd Year, Sem 1"},
    "EP 1": {"desc": "English Proficiency Level 1", "units": 3, "prereq": "None", "coreq": "None", "term": "2nd Year, Sem 1"},
    "PE 3": {"desc": "Physical Education 3", "units": 2, "prereq": "PE 2", "coreq": "None", "term": "2nd Year, Sem 1"},
    "ReEd 3": {"desc": "Our Restless Hearts: An Introduction to Doing Catholic Morality", "units": 3, "prereq": "ReEd 2", "coreq": "None", "term": "2nd Year, Sem 1"},
    
    "GE TCW": {"desc": "The Contemporary World", "units": 3, "prereq": "None", "coreq": "None", "term": "2nd Year, Sem 2"},
    "ES 4": {"desc": "Dynamics of Rigid Bodies", "units": 2, "prereq": "ES 3", "coreq": "None", "term": "2nd Year, Sem 2"},
    "ES 10": {"desc": "Mechanics of Deformable Bodies", "units": 4, "prereq": "ES 3", "coreq": "None", "term": "2nd Year, Sem 2"},
    "CE 2B1": {"desc": "Highway and Railroad Engineering", "units": 3, "prereq": "CE 2A1", "coreq": "None", "term": "2nd Year, Sem 2"},
    "CE Tech": {"desc": "Civil Engineering Technology 1", "units": 1, "prereq": "None", "coreq": "None", "term": "2nd Year, Sem 2"},
    "GE PC": {"desc": "Purposive Communication", "units": 3, "prereq": "None", "coreq": "None", "term": "2nd Year, Sem 2"},
    "ES 9": {"desc": "Computer Fundamentals and Programming", "units": 2, "prereq": "None", "coreq": "None", "term": "2nd Year, Sem 2"},
    "PE 4": {"desc": "Physical Education 4", "units": 2, "prereq": "PE 3", "coreq": "None", "term": "2nd Year, Sem 2"},
    "ReEd 4": {"desc": "A Call to Action: An Introduction to Catholic Social Thought", "units": 3, "prereq": "ReEd 3", "coreq": "None", "term": "2nd Year, Sem 2"},
    
    "CE 2S1": {"desc": "Geology for Civil Engineers", "units": 2, "prereq": "NS 1A1", "coreq": "None", "term": "2nd Year, Summer"},
    "CE 2S2": {"desc": "Construction Materials and Testing", "units": 3, "prereq": "ES 10", "coreq": "None", "term": "2nd Year, Summer"},
    "GE AA": {"desc": "Art Appreciation", "units": 3, "prereq": "None", "coreq": "None", "term": "2nd Year, Summer"},
    
    "CE 3A1": {"desc": "Structural Theory", "units": 4, "prereq": "ES 10", "coreq": "None", "term": "3rd Year, Sem 1"},
    "CE 3A2": {"desc": "Numerical Solutions to CE Problems", "units": 3, "prereq": "EM 2A1", "coreq": "None", "term": "3rd Year, Sem 1"},
    "CE 3A3": {"desc": "Building Systems Design", "units": 3, "prereq": "ES 1, ES 2", "coreq": "None", "term": "3rd Year, Sem 1"},
    "AC 3A1": {"desc": "Engineering Utilities 1", "units": 3, "prereq": "NS 1B1, NS 1B2", "coreq": "None", "term": "3rd Year, Sem 1"},
    "AC 3A2": {"desc": "Engineering Utilities 2", "units": 3, "prereq": "NS 1B1, NS 1B2", "coreq": "None", "term": "3rd Year, Sem 1"},
    "EDA 1CE": {"desc": "Engineering Data Analysis for CE", "units": 3, "prereq": "3rd Year Standing", "coreq": "None", "term": "3rd Year, Sem 1"},
    "ES 7": {"desc": "Engineering Management", "units": 2, "prereq": "3rd Year Standing", "coreq": "None", "term": "3rd Year, Sem 1"},
    "EfCOM": {"desc": "Effective Communication and Human Relations", "units": 3, "prereq": "GE PC", "coreq": "None", "term": "3rd Year, Sem 1"},
    
    "CE 3B1": {"desc": "Quantity Surveying", "units": 2, "prereq": "CE 3A3, CE 2S2", "coreq": "None", "term": "3rd Year, Sem 2"},
    "CE 3B2": {"desc": "Principles of Steel Design", "units": 3, "prereq": "CE 3A1, CE 2S2", "coreq": "None", "term": "3rd Year, Sem 2"},
    "CE 3B3": {"desc": "Principles of Reinforced/Prestressed Concrete", "units": 4, "prereq": "CE 3A1, CE 2S2", "coreq": "None", "term": "3rd Year, Sem 2"},
    "CE 3B4": {"desc": "Hydrology", "units": 2, "prereq": "3rd Year Standing", "coreq": "CE 3B5", "term": "3rd Year, Sem 2"},
    "CE 3B5": {"desc": "Hydraulics", "units": 5, "prereq": "ES 4, ES 10", "coreq": "None", "term": "3rd Year, Sem 2"},
    "CE 3B6": {"desc": "Geotechnical Engineering 1 (Soil Mechanics)", "units": 4, "prereq": "ES 10, CE 2S1", "coreq": "None", "term": "3rd Year, Sem 2"},
    "CE 3B7": {"desc": "Principles of Transportation Engineering", "units": 3, "prereq": "CE 2B1", "coreq": "None", "term": "3rd Year, Sem 2"},
    "GE ET": {"desc": "Ethics", "units": 3, "prereq": "None", "coreq": "None", "term": "3rd Year, Sem 2"},
    
    "OJT": {"desc": "CE Industry Immersion (OJT) - 240 hours", "units": 3, "prereq": "4th Year Standing", "coreq": "None", "term": "3rd Year, Summer"},
    
    "CE 4A1": {"desc": "CE Project 1", "units": 2, "prereq": "4th Year Standing", "coreq": "None", "term": "4th Year, Sem 1"},
    "CE 4A2": {"desc": "Integrated Course 1 for CE", "units": 3, "prereq": "4th Year Standing", "coreq": "None", "term": "4th Year, Sem 1"},
    "CE 4A3": {"desc": "Construction Method and Project Management", "units": 3, "prereq": "4th Year Standing", "coreq": "None", "term": "4th Year, Sem 1"},
    "CE Elec 1": {"desc": "Professional Course - Specialized 1", "units": 3, "prereq": "4th Year Standing", "coreq": "None", "term": "4th Year, Sem 1"},
    "CE Elec 2": {"desc": "Professional Course - Specialized 2", "units": 3, "prereq": "4th Year Standing", "coreq": "None", "term": "4th Year, Sem 1"},
    "CE Elec 3": {"desc": "Professional Course - Specialized 3", "units": 3, "prereq": "4th Year Standing", "coreq": "None", "term": "4th Year, Sem 1"},
    "GE EPM": {"desc": "Eastern Philosophy", "units": 3, "prereq": "None", "coreq": "None", "term": "4th Year, Sem 1"},
    "ES 12": {"desc": "Technopreneurship 101", "units": 3, "prereq": "4th Year Standing", "coreq": "None", "term": "4th Year, Sem 1"},
    
    "CE 4B1": {"desc": "CE Project 2", "units": 2, "prereq": "CE 4A1", "coreq": "None", "term": "4th Year, Sem 2"},
    "CE 4B2": {"desc": "CE Law, Ethics and Contracts", "units": 2, "prereq": "4th Year Standing", "coreq": "None", "term": "4th Year, Sem 2"},
    "CE 4B3": {"desc": "Integrated Course 2 for CE", "units": 3, "prereq": "4th Year Standing", "coreq": "None", "term": "4th Year, Sem 2"},
    "CE 4B4": {"desc": "Integrated Course 3 for CE", "units": 3, "prereq": "4th Year Standing", "coreq": "None", "term": "4th Year, Sem 2"},
    "CE Elec 4": {"desc": "Professional Course - Specialized 4", "units": 3, "prereq": "4th Year Standing", "coreq": "None", "term": "4th Year, Sem 2"},
    "CE Elec 5": {"desc": "Professional Course - Specialized 5", "units": 3, "prereq": "4th Year Standing", "coreq": "None", "term": "4th Year, Sem 2"},
    "Rizal": {"desc": "Life and Works of Dr Jose Rizal", "units": 3, "prereq": "None", "coreq": "None", "term": "4th Year, Sem 2"},
    "GE RPH": {"desc": "Readings in Philippine History", "units": 3, "prereq": "None", "coreq": "None", "term": "4th Year, Sem 2"}
}

SEMESTERS_LIST = ["", "1sem24-25", "2sem24-25", "sum24-25", "1sem25-26", "2sem25-26", "sum25-26", "1sem26-27", "2sem26-27", "sum26-27"]
GRADES_LIST = ["", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "3.0", "5.0", "INC", "W"]

# ==========================================
# 🗄️ GOOGLE SHEETS CONNECTION UTILITIES
# ==========================================
@st.cache_resource
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    gcp_info = dict(st.secrets["gcp_service_account"])
    if "private_key" in gcp_info:
        gcp_info["private_key"] = gcp_info["private_key"].replace("\\\\n", chr(10)).replace("\\n", chr(10))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_info, scope)
    return gspread.authorize(creds)

def get_worksheets():
    client = get_gspread_client()
    sh = client.open_by_key(st.secrets["spreadsheet_key"])
    return sh.worksheet("Student_Roster"), sh.worksheet("Student_Grades")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(student_id, name, password):
    try:
        ws_roster, ws_grades = get_worksheets()
        all_roster = ws_roster.get_all_values()
        
        # Check if exists
        for r in all_roster[1:]:
            if r[0] == student_id:
                return False, "Student ID already registered."
        
        pwd_hash = hash_password(password)
        # Append roster row: student_id, name, password_hash, standing, gwa, units
        ws_roster.append_row([student_id, name, pwd_hash, "1st Year", 0.0, 0])
        
        # Pre-populate blank curriculum records in Student_Grades
        bulk_rows = []
        for code in CURRICULUM.keys():
            bulk_rows.append([student_id, code, "", "", "", "", "", ""])
        ws_grades.append_rows(bulk_rows)
        
        return True, "Account successfully registered! You can now log in."
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def authenticate_user(student_id, password):
    try:
        ws_roster, _ = get_worksheets()
        all_roster = ws_roster.get_all_values()
        
        pwd_hash = hash_password(password)
        for r in all_roster[1:]:
            if r[0] == student_id and r[2] == pwd_hash:
                r_padded = r + [""] * (6 - len(r))
                standing = r_padded[3] if r_padded[3] else "1st Year"
                try:
                    gwa = float(r_padded[4]) if r_padded[4] else 0.0
                except:
                    gwa = 0.0
                try:
                    units = int(r_padded[5]) if r_padded[5] else 0
                except:
                    units = 0
                return True, {
                    "student_id": r_padded[0],
                    "name": r_padded[1],
                    "standing": standing,
                    "gwa": gwa,
                    "units": units
                }
        return False, "Invalid Student ID or Password."
    except Exception as e:
        return False, f"Authentication error: {str(e)}"

def get_student_grades(student_id):
    try:
        _, ws_grades = get_worksheets()
        all_vals = ws_grades.get_all_values()
        
        grades_dict = {}
        for r in all_vals[1:]:
            if r[0] == student_id:
                code = r[1]
                row_padded = r + [""] * (8 - len(r))
                grades_dict[code] = [
                    (row_padded[2], row_padded[3]),
                    (row_padded[4], row_padded[5]),
                    (row_padded[6], row_padded[7])
                ]
        # Fallback for missing courses
        for code in CURRICULUM.keys():
            if code not in grades_dict:
                grades_dict[code] = [("", ""), ("", ""), ("", "")]
        return grades_dict
    except Exception as e:
        st.error(f"Error fetching grades: {str(e)}")
        return {code: [("", ""), ("", ""), ("", "")] for code in CURRICULUM.keys()}

def save_student_grade(student_id, code, att1_g, att1_t, att2_g, att2_t, att3_g, att3_t):
    try:
        _, ws_grades = get_worksheets()
        all_vals = ws_grades.get_all_values()
        
        row_idx = -1
        for idx, r in enumerate(all_vals):
            if r[0] == student_id and r[1] == code:
                row_idx = idx + 1
                break
                
        row_data = [student_id, code, att1_g, att1_t, att2_g, att2_t, att3_g, att3_t]
        if row_idx != -1:
            ws_grades.update(f"C{row_idx}:H{row_idx}", [[att1_g, att1_t, att2_g, att2_t, att3_g, att3_t]])
        else:
            ws_grades.append_row(row_data)
    except Exception as e:
        st.error(f"Error saving grade: {str(e)}")

def update_student_profile_summary(student_id, standing, gwa, units):
    try:
        ws_roster, _ = get_worksheets()
        all_roster = ws_roster.get_all_values()
        
        row_idx = -1
        for idx, r in enumerate(all_roster):
            if r[0] == student_id:
                row_idx = idx + 1
                break
        if row_idx != -1:
            ws_roster.update(f"D{row_idx}:F{row_idx}", [[standing, gwa, units]])
    except:
        pass

def get_all_registered_students():
    try:
        ws_roster, _ = get_worksheets()
        all_roster = ws_roster.get_all_values()
        
        roster_list = []
        for r in all_roster[1:]:
            r_padded = r + [""] * (6 - len(r))
            try:
                gwa_val = float(r_padded[4]) if r_padded[4] else 0.0
            except:
                gwa_val = 0.0
            try:
                units_val = int(r_padded[5]) if r_padded[5] else 0
            except:
                units_val = 0
            roster_list.append({
                "student_id": r_padded[0],
                "name": r_padded[1],
                "standing": r_padded[3] if r_padded[3] else "1st Year",
                "gwa": gwa_val,
                "units": units_val
            })
        return roster_list
    except Exception as e:
        st.error(f"Error fetching roster directory: {str(e)}")
        return []

# ==========================================
# 👥 AUTHENTICATION STATE & SESSIONS
# ==========================================
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
    st.markdown("""
    <div class="sidebar-brand">
        <h4 style="margin: 0; color: #006633; font-weight: 800;">USJ-R ADVISING</h4>
        <small style="color: #666; font-weight: bold;">BSCE 2022 Prospectus</small>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state["authenticated"] and not st.session_state["is_chairman"]:
        auth_mode = st.radio("Access Mode", ["Log In", "Register Account", "Chairman Access"])
        
        if auth_mode == "Log In":
            st.subheader("🔑 Student Login")
            s_id = st.text_input("Student ID", key="login_id")
            s_pwd = st.text_input("Password", type="password", key="login_pwd")
            if st.button("Log In", use_container_width=True):
                success, data = authenticate_user(s_id, s_pwd)
                if success:
                    st.session_state["authenticated"] = True
                    st.session_state["user_profile"] = data
                    st.session_state["is_chairman"] = False
                    st.session_state["loaded_student_by_adviser"] = None
                    st.success(f"Welcome back, {data['name']}!")
                    st.rerun()
                else:
                    st.error(data)
                    
        elif auth_mode == "Register Account":
            st.subheader("📝 Register Student Profile")
            reg_id = st.text_input("Student ID", key="reg_id")
            reg_name = st.text_input("Full Name", key="reg_name")
            reg_pwd = st.text_input("Password", type="password", key="reg_pwd")
            if st.button("Create Profile", use_container_width=True):
                if not reg_id or not reg_name or not reg_pwd:
                    st.error("Please fill in all registration fields.")
                else:
                    success, msg = register_user(reg_id, reg_name, reg_pwd)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                        
        elif auth_mode == "Chairman Access":
            st.subheader("👑 Advisor Bypass")
            bypass_code = st.text_input("Department Passcode", type="password")
            if st.button("Bypass", use_container_width=True):
                if bypass_code == "USJR-CE-CHAIR":
                    st.session_state["authenticated"] = True
                    st.session_state["is_chairman"] = True
                    st.session_state["user_profile"] = {"student_id": "CHAIRMAN", "name": "Department Chairman"}
                    st.success("Welcome, Chairman!")
                    st.rerun()
                else:
                    st.error("Incorrect departmental access code.")
    else:
        # User is logged in
        st.markdown(f"""
        <div style="background-color: #E6F2EB; padding: 15px; border-radius: 8px; border-left: 4px solid #006633; margin-bottom: 15px;">
            <p style="margin: 0; color: #006633; font-weight: bold; font-size: 0.85rem;">Active User</p>
            <h4 style="margin: 0; color: #006633; font-weight: 800;">{st.session_state['user_profile']['name']}</h4>
            <p style="margin: 0; color: #666; font-size: 0.8rem; font-weight: bold;">ID: {st.session_state['user_profile']['student_id']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # If adviser is logged in, show student switcher
        if st.session_state["is_chairman"]:
            st.markdown("---")
            st.subheader("👥 Student Records Directory")
            roster = get_all_registered_students()
            if roster:
                roster_choices = {f"{r['student_id']} - {r['name']}": r for r in roster}
                selected_choice = st.selectbox("Select Student Profile", list(roster_choices.keys()))
                if selected_choice:
                    st.session_state["loaded_student_by_adviser"] = roster_choices[selected_choice]
            else:
                st.warning("No registered students found in database.")
                
        if st.button("Log Out / Reset Session", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user_profile"] = None
            st.session_state["is_chairman"] = False
            st.session_state["loaded_student_by_adviser"] = None
            # Clear all local bulk buffers
            keys_to_clear = [k for k in st.session_state.keys() if "editor" in k or "grade_df_data" in k or "planner_df" in k]
            for k in keys_to_clear:
                del st.session_state[k]
            st.rerun()

# ==========================================
# 🏛️ BRAND HEADER PANEL (WITH LOGO & LABELS)
# ==========================================
header_col1, header_col2 = st.columns([1, 6])
with header_col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #006633 0%, #FFCC00 100%); width: 85px; height: 85px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 8px rgba(0,0,0,0.15); margin-top: 10px;">
        <span style="color: white; font-size: 2rem; font-weight: 900; letter-spacing: -1px;">CE</span>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    st.markdown("""
    <div style="margin-top: 5px;">
        <h4 style="margin: 0; color: #006633; font-weight: 900; letter-spacing: 0.5px;">UNIVERSITY OF SAN JOSE - RECOLETOS</h4>
        <h2 style="margin: 0 0 2px 0; color: #004d26; font-weight: 800; font-size: 1.8rem; line-height: 1.2;">Student Academic Advising and Planning Portal</h2>
        <div style="background-color: #FFCC00; height: 3px; width: 100%; border-radius: 2px; margin-top: 4px; margin-bottom: 4px;"></div>
        <p style="margin: 0; color: #8c7300; font-size: 0.85rem; font-weight: 800; letter-spacing: 1px;">CIVIL ENGINEERING DEPARTMENT • BSCE 2022 CURRICULUM</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 10px; margin-bottom: 25px; border: 0.5px solid #E6F2EB;' />", unsafe_allow_html=True)

# Determine who is the active student profile to load
active_student = None
if st.session_state["authenticated"]:
    if st.session_state["is_chairman"]:
        active_student = st.session_state["loaded_student_by_adviser"]
    else:
        active_student = st.session_state["user_profile"]

if not active_student:
    st.info("👋 Welcome! Please Log In or Register a Student Profile in the sidebar to begin.")
    st.stop()

active_student_id = active_student["student_id"]
active_student_name = active_student["name"]

# ==========================================
# 🔄 REAL-TIME DATA STATE SYNCHRONIZER
# ==========================================
student_grades = get_student_grades(active_student_id)

# Synchronize updates from Student Grade Record Tab 3 (Bulk editor callback)
bulk_editor_key = f"bulk_editor_{active_student_id}"
if bulk_editor_key in st.session_state and st.session_state[bulk_editor_key] is not None:
    edits = st.session_state[bulk_editor_key].get("edited_rows", {})
    if edits:
        # Load the temp dataframe in memory to translate indexes back to course codes
        temp_list = []
        for code, details in CURRICULUM.items():
            temp_list.append({
                "Code": code,
                "att1_g": student_grades[code][0][0], "att1_t": student_grades[code][0][1],
                "att2_g": student_grades[code][1][0], "att2_t": student_grades[code][1][1],
                "att3_g": student_grades[code][2][0], "att3_t": student_grades[code][2][1],
            })
        temp_df = pd.DataFrame(temp_list)
        
        # Apply changes and write to database
        for idx, changes in edits.items():
            idx = int(idx)
            code = temp_df.loc[idx, "Code"]
            
            # Read existing
            att1_g, att1_t = student_grades[code][0]
            att2_g, att2_t = student_grades[code][1]
            att3_g, att3_t = student_grades[code][2]
            
            if "Att 1 Grade" in changes: att1_g = str(changes["Att 1 Grade"])
            if "Att 1 Term" in changes: att1_t = str(changes["Att 1 Term"])
            if "Att 2 Grade" in changes: att2_g = str(changes["Att 2 Grade"])
            if "Att 2 Term" in changes: att2_t = str(changes["Att 2 Term"])
            if "Att 3 Grade" in changes: att3_g = str(changes["Att 3 Grade"])
            if "Att 3 Term" in changes: att3_t = str(changes["Att 3 Term"])
            
            save_student_grade(active_student_id, code, att1_g, att1_t, att2_g, att2_t, att3_g, att3_t)
            
        # Re-fetch updated records
        student_grades = get_student_grades(active_student_id)

# ==========================================
# 🧮 LOGICAL CALCULATION FUNCTIONS (GROUNDED)
# ==========================================
def evaluate_course_status(attempts):
    # Evaluates the active status of a subject
    # Passed, Failed, INC, W, or Not Taken
    last_grade = ""
    for grade, term in reversed(attempts):
        if grade != "":
            last_grade = grade
            break
            
    if last_grade == "":
        return "Not Taken"
    elif last_grade in ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "3.0"]:
        return "Passed"
    elif last_grade == "INC":
        return "INC"
    elif last_grade == "W":
        return "Withdrawn"
    else:
        return "Failed"

# Process states for all 73 subjects
course_status_map = {}
gwa_points_sum = 0.0
gwa_units_sum = 0.0
completed_units_by_level = {"1st Year": 0, "2nd Year": 0, "3rd Year": 0, "4th Year": 0}
total_units_by_level = {"1st Year": 0, "2nd Year": 0, "3rd Year": 0, "4th Year": 0}

for code, details in CURRICULUM.items():
    attempts = student_grades[code]
    status = evaluate_course_status(attempts)
    course_status_map[code] = status
    
    # Calculate GWA for passed/failed numerical items (excluding INC, W, and Blank)
    # Check most recent attempt grade
    recent_grade = ""
    for grade, term in reversed(attempts):
        if grade != "":
            recent_grade = grade
            break
            
    if recent_grade != "" and recent_grade not in ["INC", "W"]:
        try:
            g_val = float(recent_grade)
            gwa_points_sum += g_val * details["units"]
            gwa_units_sum += details["units"]
        except:
            pass
            
    # Track units completed by level
    lvl = details["term"].split(",")[0]
    if status == "Passed":
        completed_units_by_level[lvl] = completed_units_by_level.get(lvl, 0) + details["units"]
    total_units_by_level[lvl] = total_units_by_level.get(lvl, 0) + details["units"]

total_completed_units = sum(completed_units_by_level.values())
total_curriculum_units = sum(total_units_by_level.values())
remaining_curriculum_units = total_curriculum_units - total_completed_units
cumulative_gwa = round(gwa_points_sum / gwa_units_sum, 3) if gwa_units_sum > 0 else 0.0

active_inc_count = sum(1 for code, status in course_status_map.items() if status == "INC")

# Determine Year Standing level based on completed units
if total_completed_units >= 153:
    academic_standing_level = "4th Year"
elif total_completed_units >= 100:
    academic_standing_level = "3rd Year"
elif total_completed_units >= 45:
    academic_standing_level = "2nd Year"
else:
    academic_standing_level = "1st Year"

# Update profile in DB summary table
update_student_profile_summary(active_student_id, academic_standing_level, cumulative_gwa, total_completed_units)

# ==========================================
# 🎛️ TABBED SYSTEM CONTAINER
# ==========================================
tabs_to_render = ["📊 Academic Dashboard", "🗓️ Enrollment Planner", "📝 Student Grade Record", "📚 Curriculum Reference"]
if st.session_state["is_chairman"]:
    tabs_to_render.append("👑 Chairman & Faculty Portal")

tab_widgets = st.tabs(tabs_to_render)

# Helper function to evaluate prerequisite completion
def is_prereq_satisfied(prereq_str, status_map, current_standing):
    if prereq_str == "None":
        return True
    
    # Check standing restrictions
    if "Standing" in prereq_str:
        req_standing = prereq_str.split(" ")[0] # "2nd", "3rd", "4th"
        standings_hierarchy = {"1st Year": 1, "2nd Year": 2, "3rd Year": 3, "4th Year": 4}
        return standings_hierarchy.get(current_standing, 1) >= standings_hierarchy.get(req_standing + " Year", 1)
        
    # Split comma requirements
    reqs = [r.strip() for r in prereq_str.replace(",", " ").split() if r.strip()]
    for r in reqs:
        if status_map.get(r, "Not Taken") != "Passed":
            return False
    return True

# Helper function to check co-requisite rules
def is_coreq_satisfied(coreq_str, status_map, planner_selections):
    if coreq_str == "None":
        return True
    reqs = [r.strip() for r in coreq_str.replace(",", " ").split() if r.strip()]
    for r in reqs:
        # Satisfied if passed previously, or selected in active planner rows
        if status_map.get(r, "Not Taken") == "Passed" or r in planner_selections:
            continue
        return False
    return True

# --------------------------------------------------
# TAB 1: ACADEMIC DASHBOARD
# --------------------------------------------------
with tab_widgets[0]:
    st.markdown("### 📈 Student Academic Standing & Statistics")
    
    # 3-Column Profile Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-lbl">Academic Year Standing</p>
            <h1 class="metric-val">{academic_standing_level}</h1>
            <p style="margin:0; font-size: 0.8rem; color: #666; font-weight: bold;">{total_completed_units} / {total_curriculum_units} Units Passed</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-lbl">Cumulative GWA (Attempts)</p>
            <h1 class="metric-val">{cumulative_gwa:.3f}</h1>
            <p style="margin:0; font-size: 0.8rem; color: #666; font-weight: bold;">Josenian Scale (1.0 to 3.0)</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        status_color = "#006633" if active_inc_count == 0 else "#FFCC00"
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-lbl">Active INC Marks</p>
            <h1 class="metric-val" style="color: {status_color};">{active_inc_count}</h1>
            <p style="margin:0; font-size: 0.8rem; color: #666; font-weight: bold;">Must remove within 1 Year</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 🗺️ VISUAL SEMESTER PROGRESS GRID
    st.markdown("### 🗺️ Visual Semester Progress Grid")
    
    # Map out the 10 distinct prospectus terms
    terms_definition = [
        {"name": "1st Year, Sem 1", "title": "First Year, 1st Semester"},
        {"name": "1st Year, Sem 2", "title": "First Year, 2nd Semester"},
        {"name": "2nd Year, Sem 1", "title": "Second Year, 1st Semester"},
        {"name": "2nd Year, Sem 2", "title": "Second Year, 2nd Semester"},
        {"name": "2nd Year, Summer", "title": "Second Year, Summer"},
        {"name": "3rd Year, Sem 1", "title": "Third Year, 1st Semester"},
        {"name": "3rd Year, Sem 2", "title": "Third Year, 2nd Semester"},
        {"name": "3rd Year, Summer", "title": "Third Year, Summer (OJT)"},
        {"name": "4th Year, Sem 1", "title": "Fourth Year, 1st Semester"},
        {"name": "4th Year, Sem 2", "title": "Fourth Year, 2nd Semester"}
    ]
    
    # Render progress grid as 2-column list of responsive cards
    grid_col1, grid_col2 = st.columns(2)
    for index, term_item in enumerate(terms_definition):
        term_code = term_item["name"]
        term_title = term_item["title"]
        
        # Filter curriculum items in this term
        term_courses = {code: details for code, details in CURRICULUM.items() if details["term"] == term_code}
        term_total_count = len(term_courses)
        term_passed_count = sum(1 for code in term_courses.keys() if course_status_map[code] == "Passed")
        
        # Determine status cards and styles
        if term_passed_count == term_total_count and term_total_count > 0:
            card_class = "sem-card-green"
            badge = "🟢"
            status_lbl = "Completed (100%)"
            fill_pct = 100
        elif term_passed_count > 0:
            card_class = "sem-card-yellow"
            badge = "🟡"
            status_lbl = f"In Progress ({term_passed_count} / {term_total_count} Passed)"
            fill_pct = int((term_passed_count / term_total_count) * 100)
        else:
            card_class = "sem-card-grey"
            badge = "⚪"
            status_lbl = "Upcoming / Locked (0%)"
            fill_pct = 0
            
        card_html = f"""
        <div class="{card_class}">
            <div style="font-weight: bold; font-size: 1.05rem; display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; color: #333;">
                <span>{term_title}</span>
                <span>{badge}</span>
            </div>
            <div style="font-size: 0.85rem; color: #555; margin-bottom: 8px; font-weight: bold;">
                {status_lbl}
            </div>
            <div style="background-color: #D1D1D6; height: 8px; border-radius: 4px; overflow: hidden; width: 100%;">
                <div style="background-color: {'#006633' if card_class=='sem-card-green' else '#FFCC00' if card_class=='sem-card-yellow' else '#8E8E93'}; width: {fill_pct}%; height: 100%; border-radius: 4px;"></div>
            </div>
        </div>
        """
        
        if index % 2 == 0:
            with grid_col1:
                st.markdown(card_html, unsafe_allow_html=True)
        else:
            with grid_col2:
                st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 🚧 CRITICAL ACADEMIC PATHWAY BOTTLENECKS
    st.markdown("### 🚧 CRITICAL ACADEMIC PATHWAY BOTTLENECKS")
    st.info("The pipelines below map out major civil engineering pathways. Instantly evaluates eligibility to prevent delayed graduation.")
    
    # Pre-calculate sequence matrices
    sequences = {
        "Mechanics Sequence (Prerequisite Chain: ES 3 ➔ ES 10 ➔ CE 3A1)": [
            {"code": "ES 3", "role": "Gateway Block"},
            {"code": "ES 10", "role": "Intermediate Block"},
            {"code": "CE 3A1", "role": "Design Block"}
        ],
        "Structural Design Sequence (Prerequisite Chain: CE 3A1 & CE 2S2 ➔ Concrete/Steel Design)": [
            {"code": "CE 3A1", "role": "Gateway Analysis"},
            {"code": "CE 2S2", "role": "Gateway Testing"},
            {"code": "CE 3B2", "role": "Steel Design"},
            {"code": "CE 3B3", "role": "Concrete Design"}
        ],
        "Geotechnical Sequence (Prerequisite Chain: ES 10 & CE 2S1 ➔ Soil Mechanics)": [
            {"code": "ES 10", "role": "Gateway Mechanics"},
            {"code": "CE 2S1", "role": "Gateway Geology"},
            {"code": "CE 3B6", "role": "Geotechnical 1"}
        ],
        "Hydraulics Sequence (Prerequisite Chain: ES 4 & ES 10 ➔ Hydraulics)": [
            {"code": "ES 4", "role": "Gateway Dynamics"},
            {"code": "ES 10", "role": "Gateway Mechanics"},
            {"code": "CE 3B5", "role": "Hydraulics"}
        ]
    }
    
    for seq_name, items in sequences.items():
        with st.expander(f"📁 {seq_name}", expanded=True):
            seq_data = []
            for item in items:
                code = item["code"]
                role = item["role"]
                desc = CURRICULUM[code]["desc"]
                status = course_status_map[code]
                
                # Assign visual status alerts
                if status == "Passed":
                    alert = "🟢 Eligible / Cleared"
                elif status == "INC":
                    alert = "🟡 Incomplete Mark (Restricted)"
                elif status == "Failed":
                    alert = "🔴 Prerequisite Failure"
                else:
                    alert = "⚪ Prerequisite Locked (Not Taken)"
                    
                seq_data.append({
                    "Course Code": code,
                    "Course Description": desc,
                    "Curriculum Role": role,
                    "Academic Status": status,
                    "Advising Clearance": alert
                })
            
            sdf = pd.DataFrame(seq_data)
            
            # Apply styling colors
            def style_clearance_matrix(val):
                if "🟢" in val:
                    return 'background-color: #E6F2EB; color: #006633; font-weight: bold;'
                elif "🔴" in val:
                    return 'background-color: #FCE8E6; color: #C5221F; font-weight: bold;'
                elif "🟡" in val:
                    return 'background-color: #FEF7E0; color: #B06000; font-weight: bold;'
                return 'background-color: #F1F3F4; color: #5F6368;'
                
            sdf_styler = sdf.style
            if hasattr(sdf_styler, "map"):
                styled_df = sdf_styler.map(style_clearance_matrix, subset=["Advising Clearance"])
            else:
                styled_df = sdf_styler.applymap(style_clearance_matrix, subset=["Advising Clearance"])
                
            st.dataframe(
                styled_df,
                hide_index=True,
                use_container_width=True
            )

# --------------------------------------------------
# TAB 2: ENROLLMENT PLANNER
# --------------------------------------------------
with tab_widgets[1]:
    st.markdown("### 🗓️ Semestral Enrollment Planner")
    st.write("Plan and simulate next term's schedule to verify prerequisite and co-requisite rules before official enrollment.")
    
    planner_editor_key = f"planner_editor_{active_student_id}"
    
    # Maintain planner selections in session state
    if f'planner_df_{active_student_id}' not in st.session_state:
        st.session_state[f'planner_df_{active_student_id}'] = pd.DataFrame([
            {"Course Code": ""} for _ in range(12)
        ])
        
    planner_df = st.session_state[f'planner_df_{active_student_id}']
    
    # Process user dropdown inputs inside editor
    if planner_editor_key in st.session_state and st.session_state[planner_editor_key] is not None:
        edits = st.session_state[planner_editor_key].get("edited_rows", {})
        for row_idx, change in edits.items():
            row_idx = int(row_idx)
            if "Course Code" in change:
                planner_df.loc[row_idx, "Course Code"] = change["Course Code"]
        st.session_state[f'planner_df_{active_student_id}'] = planner_df
        
    # Get active selections
    selected_codes = [c for c in planner_df["Course Code"].values if c != ""]
    
    # Evaluate metadata and validation remarks for planner rows
    processed_planner = []
    total_planner_units = 0
    
    for idx in range(12):
        code = planner_df.loc[idx, "Course Code"]
        if code == "":
            processed_planner.append({
                "Course Code": "",
                "Description": "",
                "Units": "",
                "Prerequisites": "",
                "Co-Requisites": "",
                "Advising Status": "",
                "Validation Remarks": ""
            })
        else:
            details = CURRICULUM[code]
            desc = details["desc"]
            units = details["units"]
            prereq = details["prereq"]
            coreq = details["coreq"]
            
            total_planner_units += units
            
            # 1. Prerequisite Validation
            prereq_ok = is_prereq_satisfied(prereq, course_status_map, academic_standing_level)
            
            # 2. Co-requisite Validation
            coreq_ok = is_coreq_satisfied(coreq, course_status_map, selected_codes)
            
            # Already completed checker
            is_passed = course_status_map.get(code, "Not Taken") == "Passed"
            
            if is_passed:
                status_alert = "Already Passed"
                remarks = "🟢 This subject has already been successfully passed in your ledger."
            elif not prereq_ok:
                status_alert = "Disapproved"
                remarks = f"🔴 Deficient in prerequisite: {prereq}."
            elif not coreq_ok:
                status_alert = "Coreq Deficient"
                remarks = f"🟡 Requires concurrent co-requisite: {coreq}."
            else:
                status_alert = "Approved"
                remarks = "🟢 Cleared! Student is eligible for enrollment."
                
            processed_planner.append({
                "Course Code": code,
                "Description": desc,
                "Units": units,
                "Prerequisites": prereq,
                "Co-Requisites": coreq,
                "Advising Status": status_alert,
                "Validation Remarks": remarks
            })
            
    pdf = pd.DataFrame(processed_planner)
    
    # Display schedule planner with locked styles
    st.markdown("##### 📝 Simulated Term Schedule Grid (12 Rows)")
    
    # Formatting helper for cell background
    def style_planner_tab(row):
        styles = [''] * len(row)
        # First column (Course Code) is editable -> Pure White
        styles[0] = 'background-color: #FFFFFF; color: #000000;'
        # System calculated columns -> Soft Green
        for i in range(1, len(row)):
            styles[i] = 'background-color: #E6F2EB; color: #003311;'
            
        # If the row has an advising status, color that column specifically
        status_val = row["Advising Status"]
        if status_val == "Approved":
            styles[5] = 'background-color: #C2E7D9; color: #005a36; font-weight: bold;'
        elif status_val == "Disapproved":
            styles[5] = 'background-color: #FAD2CF; color: #a51d1a; font-weight: bold;'
        elif status_val == "Coreq Deficient":
            styles[5] = 'background-color: #FDE8BB; color: #8a5700; font-weight: bold;'
            
        return styles

    # Sort choices of dropdown course code selector
    choices_list = [""] + sorted(list(CURRICULUM.keys()))
    
    edited_planner_df = st.data_editor(
        pdf.style.apply(style_planner_tab, axis=1),
        key=planner_editor_key,
        column_config={
            "Course Code": st.column_config.SelectboxColumn(
                width=80,
                options=choices_list,
                required=False
            ),
            "Description": st.column_config.TextColumn(width=160, disabled=True),
            "Units": st.column_config.NumberColumn(width=50, disabled=True),
            "Prerequisites": st.column_config.TextColumn(width=110, disabled=True),
            "Co-Requisites": st.column_config.TextColumn(width=110, disabled=True),
            "Advising Status": st.column_config.TextColumn(width=110, disabled=True),
            "Validation Remarks": st.column_config.TextColumn(width=280, disabled=True)
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Stats footer for planner
    col_u1, col_u2 = st.columns([4, 1])
    with col_u2:
        st.markdown(f"""
        <div style="background-color: #006633; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-top: 5px;">
            <small style="text-transform: uppercase; font-size: 0.65rem; font-weight: bold; letter-spacing: 0.5px;">Simulated Load</small>
            <h3 style="margin:0; font-weight: 800; color: #FFCC00;">{total_planner_units} Units</h3>
        </div>
        """, unsafe_allow_html=True)

# --------------------------------------------------
# TAB 3: STUDENT GRADE RECORD
# --------------------------------------------------
with tab_widgets[2]:
    st.markdown("### 📝 Josenian Active Student Grade Ledger")
    st.write("Input, modify, or update student grade histories. Calculated values directly compile into the Academic Dashboard in real-time.")
    
    # Structure prospectus items in chronological order for editing
    grade_rows = []
    for code, details in CURRICULUM.items():
        attempts = student_grades[code]
        grade_rows.append({
            "Course": code,
            "Regular Term": details["term"],
            "Description": details["desc"],
            "Units": details["units"],
            "Prerequisites": details["prereq"],
            "Co-Requisites": details["coreq"],
            "Att 1 Grade": attempts[0][0],
            "Att 1 Term": attempts[0][1],
            "Att 2 Grade": attempts[1][0],
            "Att 2 Term": attempts[1][1],
            "Att 3 Grade": attempts[2][0],
            "Att 3 Term": attempts[2][1]
        })
        
    gdf = pd.DataFrame(grade_rows)
    
    # Custom shading formatting for the ledger
    def style_ledger_matrix(row):
        styles = [''] * len(row)
        # Non-editable descriptors (Columns 0 to 5) -> Soft Green
        for i in range(6):
            styles[i] = 'background-color: #E6F2EB; color: #003311;'
        # Editable Input values (Attempts) -> Pure White
        for i in range(6, len(row)):
            styles[i] = 'background-color: #FFFFFF; color: #000000;'
        return styles
        
    # Render interactive data editor
    edited_grades_df = st.data_editor(
        gdf.style.apply(style_ledger_matrix, axis=1),
        key=bulk_editor_key,
        column_config={
            "Course": st.column_config.TextColumn(width=80, disabled=True),
            "Regular Term": st.column_config.TextColumn(width=65, disabled=True),
            "Description": st.column_config.TextColumn(width=160, disabled=True),
            "Units": st.column_config.NumberColumn(width=50, disabled=True),
            "Prerequisites": st.column_config.TextColumn(width=110, disabled=True),
            "Co-Requisites": st.column_config.TextColumn(width=110, disabled=True),
            
            "Att 1 Grade": st.column_config.SelectboxColumn(options=GRADES_LIST, width=80),
            "Att 1 Term": st.column_config.SelectboxColumn(options=SEMESTERS_LIST, width=85),
            "Att 2 Grade": st.column_config.SelectboxColumn(options=GRADES_LIST, width=80),
            "Att 2 Term": st.column_config.SelectboxColumn(options=SEMESTERS_LIST, width=85),
            "Att 3 Grade": st.column_config.SelectboxColumn(options=GRADES_LIST, width=80),
            "Att 3 Term": st.column_config.SelectboxColumn(options=SEMESTERS_LIST, width=85)
        },
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# TAB 4: CURRICULUM REFERENCE
# --------------------------------------------------
with tab_widgets[3]:
    st.markdown("### 📚 BSCE 2022 Curriculum Prospectus Reference")
    st.write("Browse academic courses and pre/co-requisite rules classified chronologically by semester.")
    
    # Sort courses into groupings
    semester_groups = [
        {"code": "1st Year, Sem 1", "title": "First Year, 1st Semester"},
        {"code": "1st Year, Sem 2", "title": "First Year, 2nd Semester"},
        {"code": "2nd Year, Sem 1", "title": "Second Year, 1st Semester"},
        {"code": "2nd Year, Sem 2", "title": "Second Year, 2nd Semester"},
        {"code": "2nd Year, Summer", "title": "Second Year, Summer"},
        {"code": "3rd Year, Sem 1", "title": "Third Year, 1st Semester"},
        {"code": "3rd Year, Sem 2", "title": "Third Year, 2nd Semester"},
        {"code": "3rd Year, Summer", "title": "Third Year, Summer (OJT)"},
        {"code": "4th Year, Sem 1", "title": "Fourth Year, 1st Semester"},
        {"code": "4th Year, Sem 2", "title": "Fourth Year, 2nd Semester"}
    ]
    
    for g in semester_groups:
        g_code = g["code"]
        g_title = g["title"]
        
        # Pull subjects matching code
        grouped_courses = []
        for code, details in CURRICULUM.items():
            if details["term"] == g_code:
                grouped_courses.append({
                    "Course Code": code,
                    "Description": details["desc"],
                    "Units": details["units"],
                    "Prerequisites": details["prereq"],
                    "Co-Requisites": details["coreq"]
                })
        
        g_df = pd.DataFrame(grouped_courses)
        g_units = sum(g_df["Units"].values)
        
        with st.expander(f"📁 {g_title} ({g_units} Total Units)", expanded=False):
            st.dataframe(
                g_df.style.set_properties(**{'background-color': '#E6F2EB', 'color': '#003311'}),
                use_container_width=True,
                hide_index=True
            )

# --------------------------------------------------
# TAB 5: CHAIRMAN PORTAL (Gated Tab)
# --------------------------------------------------
if st.session_state["is_chairman"]:
    with tab_widgets[4]:
        st.markdown("""
        <div style="background-color: #FFFCE6; padding: 15px; border-radius: 8px; border-left: 4px solid #FFCC00; margin-bottom: 20px;">
            <h4 style="margin: 0; color: #8a5700; font-weight: bold;">👑 Advisor & Chairperson Administration Panel</h4>
            <p style="margin: 0; color: #555; font-size: 0.85rem;">This master portal compiles analytics across all registered student profiles in the Google Sheets database.</p>
        </div>
        """, unsafe_allow_html=True)
        
        all_students = get_all_registered_students()
        
        if not all_students:
            st.info("No student accounts have been registered in the database yet.")
        else:
            # 1. Institutional KPIs
            c_col1, c_col2, c_col3, c_col4 = st.columns(4)
            total_registered = len(all_students)
            avg_gwa = np.mean([s["gwa"] for s in all_students if s["gwa"] > 0]) if any(s["gwa"] > 0 for s in all_students) else 0.0
            total_passed_units = sum(s["units"] for s in all_students)
            
            with c_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-lbl">Total Registered Students</p>
                    <h1 class="metric-val">{total_registered}</h1>
                </div>
                """, unsafe_allow_html=True)
            with c_col2:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-lbl">Department Avg GWA</p>
                    <h1 class="metric-val">{avg_gwa:.3f}</h1>
                </div>
                """, unsafe_allow_html=True)
            with c_col3:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-lbl">Total Completed Units</p>
                    <h1 class="metric-val">{total_passed_units}</h1>
                </div>
                """, unsafe_allow_html=True)
            with c_col4:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-lbl">Active Roster Status</p>
                    <h1 class="metric-val" style="color:#006633;">HEALTHY</h1>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 2. Complete Roster Sheet
            st.markdown("#### 📋 Complete Student Directory and Academic Standing")
            roster_df = pd.DataFrame(all_students)
            st.dataframe(
                roster_df.style.set_properties(**{'background-color': '#E6F2EB', 'color': '#003311'}),
                column_config={
                    "student_id": "Student ID",
                    "name": "Full Student Name",
                    "standing": "Curriculum Standing",
                    "gwa": "Cumulative GWA",
                    "units": "Completed Units"
                },
                use_container_width=True,
                hide_index=True
            )
            
            # 3. Dynamic Failure/INC Tracker
            st.markdown("#### 🔍 Active Incomplete (INC) Marks Tracker")
            inc_tracking_list = []
            
            # Query all grades across the entire database to find INC marks
            try:
                _, ws_grades = get_worksheets()
                all_grades = ws_grades.get_all_values()
                
                student_grades_map = {}
                for row in all_grades[1:]:
                    row_padded = row + [""] * (8 - len(row))
                    s_id = row_padded[0]
                    c_code = row_padded[1]
                    attempts = [
                        (row_padded[2], row_padded[3]),
                        (row_padded[4], row_padded[5]),
                        (row_padded[6], row_padded[7])
                    ]
                    if s_id not in student_grades_map:
                        student_grades_map[s_id] = {}
                    student_grades_map[s_id][c_code] = attempts
            except Exception as e:
                st.error(f"Error fetching administrative grade data: {str(e)}")
                student_grades_map = {}
            
            for s in all_students:
                s_id = s["student_id"]
                s_name = s["name"]
                s_grades_dict = student_grades_map.get(s_id, {})
                
                for c_code, attempts in s_grades_dict.items():
                    # Check if most recent attempt is an INC
                    last_grade = ""
                    last_term = ""
                    for g, t in reversed(attempts):
                        if g != "":
                            last_grade = g
                            last_term = t
                            break
                    if last_grade == "INC":
                        inc_tracking_list.append({
                            "Student ID": s_id,
                            "Student Name": s_name,
                            "Course Code": c_code,
                            "Incomplete Term": last_term,
                            "Prerequisites": CURRICULUM.get(c_code, {}).get("prereq", "None"),
                            "Co-Requisites": CURRICULUM.get(c_code, {}).get("coreq", "None")
                        })
                    
            if inc_tracking_list:
                inc_df = pd.DataFrame(inc_tracking_list)
                st.dataframe(
                    inc_df.style.set_properties(**{'background-color': '#FFFCE6', 'color': '#8a5700'}),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("🎉 Excellent! There are currently no active incomplete (INC) marks in the database.")
                
            # 4. Aggregated Pipeline Bottlenecks
            st.markdown("#### 📊 Aggregated Sequence Bottlenecks")
            st.write("Aggregated count of students blocked at critical gateway prerequisites across your department database.")
            
            gateways = ["ES 3", "ES 10", "CE 3A1", "ES 4", "CE 2S1", "CE 2S2"]
            gateway_stats = []
            
            for g_code in gateways:
                blocked_students = []
                for s in all_students:
                    s_id = s["student_id"]
                    s_grades_dict = student_grades_map.get(s_id, {})
                    g_attempts = s_grades_dict.get(g_code, [])
                    
                    last_g = ""
                    for g, t in reversed(g_attempts):
                        if g != "":
                            last_g = g
                            break
                    if last_g in ["5.0", "W", "INC", ""] or last_g is None:
                        blocked_students.append(s["name"])
                            
                gateway_stats.append({
                    "Prerequisite Gateway": g_code,
                    "Course Name": CURRICULUM[g_code]["desc"],
                    "Blocked Student Count": len(blocked_students),
                    "Affected Student List": ", ".join(blocked_students) if blocked_students else "None"
                })
                
            gate_df = pd.DataFrame(gateway_stats)
            st.dataframe(
                gate_df.style.set_properties(**{'background-color': '#FCE8E6', 'color': '#a51d1a'}),
                use_container_width=True,
                hide_index=True
            )

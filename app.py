import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from fpdf import FPDF
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

# Database setup
Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    type = Column(String)
    phase = Column(String)
    department = Column(String)
    budget = Column(Float)
    actual_cost = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    execution_progress = Column(Float, default=0.0)
    risk_level = Column(String, default="Low")
    goals = Column(Text, default="")
    stakeholders = Column(Text, default="")
    initial_risks = Column(Text, default="")
    resources = Column(Text, default="")
    milestones = Column(Text, default="")
    team_size = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    name = Column(String)
    status = Column(String, default="Not Started")
    due_date = Column(DateTime)
    project = relationship("Project", back_populates="tasks")

Project.tasks = relationship("Task", order_by=Task.id, back_populates="project")

engine = create_engine('sqlite:///bt_app.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

# Initialize session state for centralized project management
if 'session' not in st.session_state:
    st.session_state['session'] = Session()

if 'selected_project' not in st.session_state:
    st.session_state['selected_project'] = None

if 'project_data' not in st.session_state:
    st.session_state['project_data'] = {}

session = st.session_state['session']

# Streamlit Config
st.set_page_config(
    page_title="BT Project Management",
    page_icon="C:/Users/brajb/OneDrive/Desktop/coding development/New BT app/Black and Purple Gradient Modern Futuristic Rocket Icon Tech Logo (1).png",
    layout="wide"
)

# Sidebar for navigation with larger logo
st.sidebar.image("C:/Users/brajb/OneDrive/Desktop/coding development/New BT app/Black and Purple Gradient Modern Futuristic Rocket Icon Tech Logo (1).png", width=250)
st.sidebar.title("Navigation")

# Categorized navigation options
categories = {
    "Home": ["Home"],
    "Project Management": ["Dashboard", "Project Management", "Risk Management", "Resource Management", "Time Tracking and Billing"],
    "Reporting": ["Reporting", "Project Portfolio Management"],
    "Stakeholders": ["Client and Stakeholder Management", "Knowledge Management"],
    "Compliance and Governance": ["Compliance and Governance", "Gamification"],
    "Continuous Improvement": ["Continuous Improvement", "AI-Powered Task Recommendations"],
    "Settings": ["Mobile Access and Notifications", "Customizable Dashboards and Dark Mode", "Advanced Scheduling"]
}

selected_category = st.sidebar.selectbox("Select Category", list(categories.keys()))
option = st.sidebar.radio("Choose a Module", categories[selected_category])

# Project Templates
project_templates = {
    "Turnaround Project": {"goals": "Increase efficiency by 20%", "stakeholders": "Ops, Finance", "initial_risks": "High initial cost"},
    "Digitization": {"goals": "Automate 50% of manual processes", "stakeholders": "IT, Ops", "initial_risks": "Integration with legacy systems"},
    "Special Project": {"goals": "Launch new product line", "stakeholders": "Marketing, R&D", "initial_risks": "Market acceptance"},
    "New Technology Research and Implementation": {"goals": "Research and implement AI solutions", "stakeholders": "IT, R&D", "initial_risks": "Rapid tech changes"}
}

# Project Phase Options
project_phases = ["None", "Scoping", "Validation", "Trial", "Rollout", "Money Step"]

# Department Options
departments = ["None", "Automation", "Maintenance", "Quality", "QMS", "Stores", "TPD", 
               "IE", "HR", "Sustainability", "Project", "MIS", "Business Analytics (BI)", 
               "Business transformation", "Finance", "Compliance"]

def apply_template(template_name):
    template = project_templates.get(template_name, {})
    return template.get('goals', ''), template.get('stakeholders', ''), template.get('initial_risks', '')

def load_project_data(selected_project):
    project = session.query(Project).filter_by(name=selected_project).first()
    if project:
        st.session_state['project_data'] = {
            'id': project.id,
            'name': project.name,
            'type': project.type,
            'phase': project.phase,
            'department': project.department,
            'budget': project.budget,
            'actual_cost': project.actual_cost,
            'roi': project.roi,
            'execution_progress': project.execution_progress,
            'risk_level': project.risk_level,
            'goals': project.goals,
            'stakeholders': project.stakeholders,
            'initial_risks': project.initial_risks,
            'resources': project.resources,
            'milestones': project.milestones,
            'team_size': project.team_size,
            'created_at': project.created_at
        }
    return project

def save_project_data():
    project = load_project_data(st.session_state['selected_project'])
    if project:
        project.name = st.session_state['project_data']['name']
        project.type = st.session_state['project_data']['type']
        project.phase = st.session_state['project_data']['phase']
        project.department = st.session_state['project_data']['department']
        project.budget = st.session_state['project_data']['budget']
        project.actual_cost = st.session_state['project_data']['actual_cost']
        project.roi = st.session_state['project_data']['roi']
        project.execution_progress = st.session_state['project_data']['execution_progress']
        project.risk_level = st.session_state['project_data']['risk_level']
        project.goals = st.session_state['project_data']['goals']
        project.stakeholders = st.session_state['project_data']['stakeholders']
        project.initial_risks = st.session_state['project_data']['initial_risks']
        project.resources = st.session_state['project_data']['resources']
        project.milestones = st.session_state['project_data']['milestones']
        project.team_size = st.session_state['project_data']['team_size']
        session.commit()

def select_project():
    projects = session.query(Project).all()
    project_names = [project.name for project in projects]
    selected_project = st.sidebar.selectbox("Select Project", project_names)

    if selected_project:
        st.session_state['selected_project'] = selected_project
        load_project_data(selected_project)

select_project()

# Home Page with Full-Screen GIF and Welcome Note
def home():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("C:/Users/brajb/OneDrive/Desktop/coding development/New BT app/Kaizen (3).gif");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("Welcome to BT Project Management App")
    st.write("This app is your one-stop solution for managing projects, resources, risks, and much more!")

def dashboard():
    st.title("Dashboard Overview")
    
    st.subheader("Project Status Summary")
    
    projects = session.query(Project).all()
    if not projects:
        st.warning("No projects found. Please add a new project.")
        return

    project_data = {
        "Project": [project.name for project in projects],
        "Status": ["On Track" if project.execution_progress >= 80 else "Delayed" if project.execution_progress >= 50 else "At Risk" for project in projects],
        "Completion": [project.execution_progress for project in projects]
    }
    df = pd.DataFrame(project_data)
    st.table(df)

    st.subheader("Completion Rates")
    completion_fig = px.bar(df, x="Project", y="Completion", color="Status", title="Project Completion Rates")
    st.plotly_chart(completion_fig)

    st.subheader("Project Distribution by Type")
    type_counts = df["Project"].groupby([project.type for project in projects]).count().reset_index(name="Count")
    type_fig = px.pie(type_counts, values="Count", names="index", title="Project Distribution by Type")
    st.plotly_chart(type_fig)

    st.subheader("Project Distribution by Department")
    department_counts = df["Project"].groupby([project.department for project in projects]).count().reset_index(name="Count")
    department_fig = px.pie(department_counts, values="Count", names="index", title="Project Distribution by Department")
    st.plotly_chart(department_fig)

    st.subheader("Project Distribution by Phase")
    phase_counts = df["Project"].groupby([project.phase for project in projects]).count().reset_index(name="Count")
    phase_fig = px.pie(phase_counts, values="Count", names="index", title="Project Distribution by Phase")
    st.plotly_chart(phase_fig)

def project_management():
    st.title("Project Management")
    
    # Add a new project
    st.subheader("Add a New Project")
    new_project_name = st.text_input("Project Name (Unique)")
    new_project_type = st.selectbox("Project Type", project_templates.keys())
    new_project_phase = st.selectbox("Project Phase", project_phases)
    new_project_department = st.selectbox("Department", departments)
    new_project_budget = st.number_input("Budget", min_value=0.0)

    if st.button("Add Project"):
        if not new_project_name or session.query(Project).filter_by(name=new_project_name).first():
            st.error("Project name must be unique and not empty.")
        else:
            new_project = Project(
                name=new_project_name,
                type=new_project_type,
                phase=new_project_phase,
                department=new_project_department,
                budget=new_project_budget,
                actual_cost=0.0,
                roi=0.0,
                execution_progress=0.0,
                risk_level="Low"
            )
            session.add(new_project)
            session.commit()
            st.success(f"Project '{new_project_name}' added successfully.")

    # Update an existing project
    st.subheader("Update an Existing Project")
    update_project_name = st.selectbox("Select a Project to Update", [p.name for p in session.query(Project).all()])
    update_project = session.query(Project).filter_by(name=update_project_name).first()
    if update_project:
        new_phase = st.selectbox("Update Phase", project_phases, index=project_phases.index(update_project.phase))
        new_department = st.selectbox("Update Department", departments, index=departments.index(update_project.department))
        new_budget = st.number_input("Update Budget", value=update_project.budget)

        if st.button("Update Project"):
            update_project.phase = new_phase
            update_project.department = new_department
            update_project.budget = new_budget
            session.commit()
            st.success(f"Project '{update_project_name}' updated successfully.")

    # Delete a project
    st.subheader("Delete a Project")
    delete_project_name = st.selectbox("Select a Project to Delete", [p.name for p in session.query(Project).all()])
    if st.button("Delete Project"):
        delete_project = session.query(Project).filter_by(name=delete_project_name).first()
        if delete_project:
            session.delete(delete_project)
            session.commit()
            st.success(f"Project '{delete_project_name}' deleted successfully.")

def risk_management():
    st.title("Risk Management")
    
    projects = session.query(Project).all()
    if not projects:
        st.warning("No projects found. Please add a new project.")
        return
    
    # Risk Management Data
    risk_data = {
        "Risk": ["Risk 1", "Risk 2", "Risk 3"],
        "Probability": [0.3, 0.5, 0.7],
        "Impact": [0.4, 0.6, 0.8]
    }
    df = pd.DataFrame(risk_data)
    
    st.subheader("Risk Probability and Impact Tracking")
    risk_fig = px.scatter(df, x="Probability", y="Impact", size="Impact", color="Risk", title="Risk Probability and Impact")
    st.plotly_chart(risk_fig)
    
    st.subheader("Add a New Risk")
    new_risk = st.text_input("Risk Name")
    new_prob = st.slider("Probability", 0.0, 1.0, 0.5)
    new_impact = st.slider("Impact", 0.0, 1.0, 0.5)
    if st.button("Add Risk"):
        df = df.append({"Risk": new_risk, "Probability": new_prob, "Impact": new_impact}, ignore_index=True)
        st.success(f"Risk '{new_risk}' added successfully.")

def resource_management():
    st.title("Resource Management")
    
    projects = session.query(Project).all()
    if not projects:
        st.warning("No projects found. Please add a new project.")
        return
    
    # Resource Allocation Data
    resources = {
        "Resource": ["Resource A", "Resource B", "Resource C"],
        "Allocated to": ["Project A", "Project B", "Project C"],
        "Availability": [80, 50, 30]
    }
    df = pd.DataFrame(resources)
    
    st.subheader("Resource Allocation")
    st.table(df)
    
    st.subheader("Manage Resource Allocation")
    resource_name = st.selectbox("Select a Resource", df["Resource"])
    new_allocation = st.selectbox("Allocate to Project", [project.name for project in projects])
    new_availability = st.slider("Resource Availability", 0, 100, 80)
    if st.button("Update Allocation"):
        df.loc[df["Resource"] == resource_name, ["Allocated to", "Availability"]] = [new_allocation, new_availability]
        st.success(f"Resource '{resource_name}' updated successfully.")

def time_tracking_and_billing():
    st.title("Time Tracking and Billing")
    
    projects = session.query(Project).all()
    if not projects:
        st.warning("No projects found. Please add a new project.")
        return
    
    # Log hours for a project
    st.subheader("Log Hours")
    project = st.selectbox("Select Project", [project.name for project in projects])
    hours = st.number_input("Hours Worked", 0, 100)
    rate = st.number_input("Hourly Rate", 0.0, 1000.0)
    if st.button("Log Hours"):
        total_cost = hours * rate
        st.success(f"Logged {hours} hours for '{project}'. Total Cost: ${total_cost:.2f}")

def reporting():
    st.title("Generate Reports")
    
    projects = session.query(Project).all()
    if not projects:
        st.warning("No projects found. Please add a new project.")
        return
    
    st.subheader("Project Reports")
    project = st.selectbox("Select Project for Report", [project.name for project in projects])
    report_type = st.selectbox("Select Report Type", ["Progress Report", "Financial Report", "Risk Report"])
    
    if st.button("Generate Report"):
        st.success(f"{report_type} for '{project}' generated successfully.")

def project_portfolio_management():
    st.title("Project Portfolio Management")
    
    projects = session.query(Project).all()
    if not projects:
        st.warning("No projects found. Please add a new project.")
        return
    
    # Example of portfolio overview
    portfolio_data = {
        "Portfolio": [project.name for project in projects],
        "Projects": [project.name for project in projects],
        "Budget": [project.budget for project in projects]
    }
    df = pd.DataFrame(portfolio_data)
    
    st.subheader("Portfolio Overview")
    portfolio_fig = px.bar(df, x="Portfolio", y="Budget", title="Portfolio Budget Allocation")
    st.plotly_chart(portfolio_fig)

def client_and_stakeholder_management():
    st.title("Client and Stakeholder Management")
    
    projects = session.query(Project).all()
    if not projects:
        st.warning("No projects found. Please add a new project.")
        return
    
    # Manage client communication and stakeholder plans
    st.subheader("Client Communication")
    client_name = st.text_input("Client Name")
    communication_plan = st.text_area("Communication Plan")
    if st.button("Save Communication Plan"):
        st.success(f"Communication Plan for '{client_name}' saved successfully.")
    
    st.subheader("Stakeholder Management")
    stakeholder_name = st.text_input("Stakeholder Name")
    stakeholder_plan = st.text_area("Stakeholder Plan")
    if st.button("Save Stakeholder Plan"):
        st.success(f"Stakeholder Plan for '{stakeholder_name}' saved successfully.")

def knowledge_management():
    st.title("Knowledge Management")
    
    projects = session.query(Project).all()
    if not projects:
        st.warning("No projects found. Please add a new project.")
        return
    
    st.subheader("Upload Project Documents")
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)
    for uploaded_file in uploaded_files:
        st.write("Uploaded:", uploaded_file.name)
    
    st.subheader("Document Library")
    # Example documents list
    documents = ["Doc1.pdf", "Doc2.pdf", "SOP1.docx"]
    st.write(documents)

def compliance_and_governance():
    st.title("Compliance and Governance")
    
    projects = session.query(Project).all()
    if not projects:
        st.warning("No projects found. Please add a new project.")
        return
    
    st.subheader("Track Compliance Tasks")
    compliance_task = st.text_input("Compliance Task")
    due_date = st.date_input("Due Date")
    if st.button("Add Compliance Task"):
        st.success(f"Compliance Task '{compliance_task}' added successfully.")
    
    st.subheader("Governance Overview")
    # Example governance overview
    governance_data = {"Task": ["Task A", "Task B"], "Status": ["Completed", "Pending"]}
    df = pd.DataFrame(governance_data)
    st.table(df)

def gamification():
    st.title("Gamification")
    
    projects = session.query(Project).all()
    if not projects:
        st.warning("No projects found. Please add a new project.")
        return
    
    st.subheader("Track Achievements")
    achievements = ["Milestone 1", "Milestone 2", "Milestone 3"]
    st.write(achievements)
    
    st.subheader("Add New Achievement")
    new_achievement = st.text_input("Achievement Name")
    if st.button("Add Achievement"):
        achievements.append(new_achievement)
        st.success(f"Achievement '{new_achievement}' added successfully.")

def continuous_improvement():
    st.title("Continuous Improvement")
    
    projects = session.query(Project).all()
    if not projects:
        st.warning("No projects found. Please add a new project.")
        return
    
    st.subheader("Log Continuous Improvement Initiatives")
    improvement = st.text_input("Improvement Initiative")
    description = st.text_area("Description")
    if st.button("Log Initiative"):
        st.success(f"Initiative '{improvement}' logged successfully.")
    
    st.subheader("View Improvement Log")
    # Example improvement log
    improvement_log = {"Initiative": ["Improve A", "Improve B"], "Status": ["In Progress", "Completed"]}
    df = pd.DataFrame(improvement_log)
    st.table(df)

def ai_powered_task_recommendations():
    st.title("AI-Powered Task Recommendations")
    
    projects = session.query(Project).all()
    if not projects:
        st.warning("No projects found. Please add a new project.")
        return
    
    st.subheader("Task Prioritization")
    # Example AI-powered task recommendations
    tasks = {"Task": ["Task 1", "Task 2", "Task 3"], "Priority": [0.9, 0.7, 0.8]}
    df = pd.DataFrame(tasks)
    df = df.sort_values(by="Priority", ascending=False)
    st.table(df)
    
    st.subheader("AI Task Recommendations")
    task = st.text_input("Enter Task Description")
    if st.button("Get Recommendations"):
        st.write("AI suggests the following priority for the task: High")

def mobile_access_and_notifications():
    st.title("Mobile Access and Notifications")
    
    st.subheader("Enable Mobile Access")
    st.write("Mobile access enabled for all users.")
    
    st.subheader("Configure Notifications")
    notifications = ["Project Updates", "Task Reminders", "Deadline Alerts"]
    selected_notifications = st.multiselect("Select Notifications to Receive", notifications)
    if st.button("Save Notifications"):
        st.success("Notifications preferences saved successfully.")

def customizable_dashboards_and_dark_mode():
    st.title("Customizable Dashboards and Dark Mode")
    
    st.subheader("Customize Your Dashboard")
    st.write("Select widgets to display on your dashboard.")
    
    st.subheader("Toggle Dark Mode")
    dark_mode = st.checkbox("Enable Dark Mode")
    if dark_mode:
        st.write("Dark mode enabled.")
    else:
        st.write("Dark mode disabled.")

def advanced_scheduling():
    st.title("Advanced Scheduling")
    
    projects = session.query(Project).all()
    if not projects:
        st.warning("No projects found. Please add a new project.")
        return
    
    st.subheader("Event Scheduling")
    event = st.text_input("Event Name")
    event_date = st.date_input("Event Date")
    if st.button("Schedule Event"):
        st.success(f"Event '{event}' scheduled for {event_date} successfully.")
    
    st.subheader("Calendar Integration")
    st.write("All events are integrated with the project calendar.")

# Module selection based on user input
if option == "Home":
    home()

elif option == "Dashboard":
    dashboard()

elif option == "Project Management":
    project_management()

elif option == "Risk Management":
    risk_management()

elif option == "Resource Management":
    resource_management()

elif option == "Time Tracking and Billing":
    time_tracking_and_billing()

elif option == "Reporting":
    reporting()

elif option == "Project Portfolio Management":
    project_portfolio_management()

elif option == "Client and Stakeholder Management":
    client_and_stakeholder_management()

elif option == "Knowledge Management":
    knowledge_management()

elif option == "Compliance and Governance":
    compliance_and_governance()

elif option == "Gamification":
    gamification()

elif option == "Continuous Improvement":
    continuous_improvement()

elif option == "AI-Powered Task Recommendations":
    ai_powered_task_recommendations()

elif option == "Mobile Access and Notifications":
    mobile_access_and_notifications()

elif option == "Customizable Dashboards and Dark Mode":
    customizable_dashboards_and_dark_mode()

elif option == "Advanced Scheduling":
    advanced_scheduling()

# Closing session
session.close()

# ============================================================
# NG NIGERIA INCIDENTS ANALYSIS DASHBOARD
# ============================================================

# Import the libraries we need
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

# Configure the appearance of the Streamlit page
st.set_page_config(
    page_title="NG Nigeria Incidents Dashboard",
    page_icon="🇳🇬",
    layout="wide"
)


# ============================================================
# 2. LOAD THE DATA
# ============================================================

# Get the folder where this app.py file is located
BASE_DIR = Path(__file__).parent

# Locate the incidents.csv file
DATA_FILE = BASE_DIR / "incidents.csv"

# Read the CSV file
df = pd.read_csv(DATA_FILE)


# ============================================================
# 3. CLEAN COLUMN NAMES
# ============================================================

# Remove spaces before and after column names
df.columns = df.columns.str.strip()

# Replace multiple spaces with a single space
df.columns = df.columns.str.replace(
    r"\s+",
    " ",
    regex=True
)


# ============================================================
# 4. STANDARDIZE ORIGINAL COLUMN NAMES
# ============================================================

# Rename columns if different spellings are found
rename_columns = {}

for column in df.columns:

    clean_column = column.strip().lower()

    if clean_column == "identifier":
        rename_columns[column] = "Identifier"

    elif clean_column == "title":
        rename_columns[column] = "Title"

    elif clean_column == "start date":
        rename_columns[column] = "Start date"

    elif clean_column == "end date":
        rename_columns[column] = "End date"

    elif clean_column == "number of deaths":
        rename_columns[column] = "Number of deaths"

    elif clean_column == "incident type":
        rename_columns[column] = "Incident Type"

    elif clean_column == "state":
        rename_columns[column] = "State"


df = df.rename(columns=rename_columns)


# ============================================================
# 5. CHECK REQUIRED ORIGINAL COLUMNS
# ============================================================

required_columns = [
    "Identifier",
    "Title",
    "Start date",
    "End date",
    "Number of deaths"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        "The following required columns are missing from the dataset: "
        + ", ".join(missing_columns)
    )

    st.write("Columns found in the CSV:")
    st.write(df.columns.tolist())

    st.stop()


# ============================================================
# 6. CONVERT DATE COLUMNS
# ============================================================

# Convert Start date into a proper datetime format
df["Start date"] = pd.to_datetime(
    df["Start date"],
    errors="coerce"
)

# Convert End date into a proper datetime format
df["End date"] = pd.to_datetime(
    df["End date"],
    errors="coerce"
)


# ============================================================
# 7. CLEAN NUMBER OF DEATHS
# ============================================================

# Make sure Number of deaths is numeric
df["Number of deaths"] = pd.to_numeric(
    df["Number of deaths"],
    errors="coerce"
)


# ============================================================
# 8. REMOVE INVALID ROWS
# ============================================================

# Remove records missing important information
df = df.dropna(
    subset=[
        "Identifier",
        "Title",
        "Start date",
        "End date",
        "Number of deaths"
    ]
)


# ============================================================
# 9. CREATE YEAR COLUMN
# ============================================================

# Extract the year from Start date
df["Year"] = df["Start date"].dt.year


# ============================================================
# 10. CREATE MONTH COLUMN
# ============================================================

# Extract the month number
df["Month"] = df["Start date"].dt.month


# ============================================================
# 11. CREATE MONTH NAME COLUMN
# ============================================================

# Extract the month name
df["Month Name"] = df["Start date"].dt.month_name()


# ============================================================
# 12. CREATE DAY OF WEEK COLUMN
# ============================================================

# Extract the day of the week
df["Day of Week"] = df["Start date"].dt.day_name()


# ============================================================
# 13. CREATE STATE COLUMN
# ============================================================

# List of Nigerian states and FCT
states = [
    "Abia",
    "Adamawa",
    "Akwa Ibom",
    "Anambra",
    "Bauchi",
    "Bayelsa",
    "Benue",
    "Borno",
    "Cross River",
    "Delta",
    "Ebonyi",
    "Edo",
    "Ekiti",
    "Enugu",
    "Gombe",
    "Imo",
    "Jigawa",
    "Kaduna",
    "Kano",
    "Katsina",
    "Kebbi",
    "Kogi",
    "Kwara",
    "Lagos",
    "Nasarawa",
    "Niger",
    "Ogun",
    "Ondo",
    "Osun",
    "Oyo",
    "Plateau",
    "Rivers",
    "Sokoto",
    "Taraba",
    "Yobe",
    "Zamfara",
    "FCT",
    "Abuja"
]


# Function for extracting state from the title
def extract_state(title):

    # Convert title to text
    title = str(title)

    # Check every state
    for state in states:

        # Check whether the state appears in the title
        if state.lower() in title.lower():

            return state

    # Return Unknown if no state is found
    return "Unknown"


# If State does not already exist, create it
if "State" not in df.columns:

    df["State"] = df["Title"].apply(extract_state)

else:

    # Fill missing states using the title
    df["State"] = df["State"].fillna(
        df["Title"].apply(extract_state)
    )


# ============================================================
# 14. CREATE INCIDENT TYPE COLUMN
# ============================================================

# The titles in the dataset commonly follow this format:
#
# Auto Crash, Ogun
# Stray Bullets, Sokoto
# Lightning Kills Herder, Kaduna
#
# Therefore, the incident type is the part before the state.


def extract_incident_type(title):

    # Convert title to text
    title = str(title).strip()

    # Split the title at the final comma
    if "," in title:

        incident_type = title.rsplit(",", 1)[0].strip()

        return incident_type

    # If there is no comma, use the title itself
    return title


# If Incident Type does not exist, create it
if "Incident Type" not in df.columns:

    df["Incident Type"] = df["Title"].apply(
        extract_incident_type
    )

else:

    # Fill missing incident types from Title
    df["Incident Type"] = df["Incident Type"].fillna(
        df["Title"].apply(extract_incident_type)
    )


# ============================================================
# 15. CREATE INCIDENT DURATION
# ============================================================

# Calculate the difference between End date and Start date
df["Incident Duration (days)"] = (
    df["End date"] - df["Start date"]
).dt.days


# ============================================================
# 16. FINAL CLEANING
# ============================================================

# Replace negative duration values with zero
df.loc[
    df["Incident Duration (days)"] < 0,
    "Incident Duration (days)"
] = 0


# Remove any remaining missing values in important columns
df = df.dropna(
    subset=[
        "Identifier",
        "Title",
        "Start date",
        "End date",
        "Number of deaths",
        "Year",
        "Month",
        "Month Name",
        "Day of Week",
        "Incident Type",
        "State",
        "Incident Duration (days)"
    ]
)


# ============================================================
# 17. DASHBOARD TITLE
# ============================================================

st.title("🇳🇬 NG Nigeria Incidents Analysis Dashboard")

st.write(
    """
    This dashboard provides an interactive analysis of incidents
    recorded across Nigeria. It allows users to explore incidents,
    deaths, states, incident types and trends over time.
    """
)


# ============================================================
# 18. SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Dashboard Filters")


# ------------------------------
# State filter
# ------------------------------

state_options = sorted(
    df["State"].dropna().unique().tolist()
)

selected_state = st.sidebar.selectbox(
    "Select State",
    ["All"] + state_options
)


# ------------------------------
# Incident type filter
# ------------------------------

incident_options = sorted(
    df["Incident Type"].dropna().unique().tolist()
)

selected_incident = st.sidebar.selectbox(
    "Select Incident Type",
    ["All"] + incident_options
)


# ------------------------------
# Year filter
# ------------------------------

year_options = sorted(
    df["Year"].dropna().unique().tolist()
)

selected_year = st.sidebar.selectbox(
    "Select Year",
    ["All"] + year_options
)


# ============================================================
# 19. APPLY FILTERS
# ============================================================

# Create a copy of the cleaned dataset
filtered_df = df.copy()


# Apply State filter
if selected_state != "All":

    filtered_df = filtered_df[
        filtered_df["State"] == selected_state
    ]


# Apply Incident Type filter
if selected_incident != "All":

    filtered_df = filtered_df[
        filtered_df["Incident Type"] == selected_incident
    ]


# Apply Year filter
if selected_year != "All":

    filtered_df = filtered_df[
        filtered_df["Year"] == selected_year
    ]


# ============================================================
# 20. KEY PERFORMANCE INDICATORS
# ============================================================

st.subheader("Key Statistics")


# Total incidents
total_incidents = len(filtered_df)


# Total deaths
total_deaths = filtered_df["Number of deaths"].sum()


# Number of states
total_states = filtered_df["State"].nunique()


# Average deaths
if total_incidents > 0:

    average_deaths = filtered_df[
        "Number of deaths"
    ].mean()

else:

    average_deaths = 0


# Display four KPI cards
col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Incidents",
        f"{total_incidents:,}"
    )


with col2:

    st.metric(
        "Total Deaths",
        f"{int(total_deaths):,}"
    )


with col3:

    st.metric(
        "States Affected",
        total_states
    )


with col4:

    st.metric(
        "Average Deaths",
        f"{average_deaths:.2f}"
    )


# ============================================================
# 21. INCIDENTS OVER TIME
# ============================================================

st.subheader("Incidents Over Time")


# Group incidents by year
yearly_incidents = (
    filtered_df
    .groupby("Year")
    .size()
    .reset_index(name="Number of Incidents")
)


# Create line chart
fig_year = px.line(
    yearly_incidents,
    x="Year",
    y="Number of Incidents",
    markers=True,
    title="Number of Incidents by Year"
)


st.plotly_chart(
    fig_year,
    use_container_width=True
)


# ============================================================
# 22. DEATHS OVER TIME
# ============================================================

st.subheader("Deaths Over Time")


# Group deaths by year
yearly_deaths = (
    filtered_df
    .groupby("Year")["Number of deaths"]
    .sum()
    .reset_index()
)


# Create line chart
fig_deaths = px.line(
    yearly_deaths,
    x="Year",
    y="Number of deaths",
    markers=True,
    title="Number of Deaths by Year"
)


st.plotly_chart(
    fig_deaths,
    use_container_width=True
)


# ============================================================
# 23. INCIDENTS BY STATE
# ============================================================

st.subheader("Incidents by State")


# Count incidents in each state
state_counts = (
    filtered_df["State"]
    .value_counts()
    .reset_index()
)


# Rename columns
state_counts.columns = [
    "State",
    "Number of Incidents"
]


# Sort by number of incidents
state_counts = state_counts.sort_values(
    "Number of Incidents",
    ascending=False
)


# Create bar chart
fig_state = px.bar(
    state_counts,
    x="State",
    y="Number of Incidents",
    title="Number of Incidents by State"
)


st.plotly_chart(
    fig_state,
    use_container_width=True
)


# ============================================================
# 24. INCIDENT TYPES
# ============================================================

st.subheader("Top Incident Types")


# Count incident types
incident_counts = (
    filtered_df["Incident Type"]
    .value_counts()
    .reset_index()
)


# Rename columns
incident_counts.columns = [
    "Incident Type",
    "Number of Incidents"
]


# Select the top 15 incident types
top_incidents = incident_counts.head(15)


# Create horizontal bar chart
fig_incidents = px.bar(
    top_incidents,
    x="Number of Incidents",
    y="Incident Type",
    orientation="h",
    title="Top 15 Incident Types"
)


st.plotly_chart(
    fig_incidents,
    use_container_width=True
)


# ============================================================
# 25. MONTHLY ANALYSIS
# ============================================================

st.subheader("Monthly Incident Trend")


# Group incidents by month
monthly_incidents = (
    filtered_df
    .groupby("Month")["Identifier"]
    .count()
    .reset_index(name="Number of Incidents")
)


# Create month name
monthly_incidents["Month Name"] = (
    pd.to_datetime(
        monthly_incidents["Month"],
        format="%m"
    ).dt.month_name()
)


# Sort by month number
monthly_incidents = monthly_incidents.sort_values(
    "Month"
)


# Create chart
fig_month = px.bar(
    monthly_incidents,
    x="Month Name",
    y="Number of Incidents",
    title="Incidents by Month"
)


st.plotly_chart(
    fig_month,
    use_container_width=True
)


# ============================================================
# 26. DAY OF WEEK ANALYSIS
# ============================================================

st.subheader("Incidents by Day of the Week")


# Count incidents by day
day_counts = (
    filtered_df["Day of Week"]
    .value_counts()
    .reset_index()
)


# Rename columns
day_counts.columns = [
    "Day of Week",
    "Number of Incidents"
]


# Create bar chart
fig_day = px.bar(
    day_counts,
    x="Day of Week",
    y="Number of Incidents",
    title="Incidents by Day of the Week"
)


st.plotly_chart(
    fig_day,
    use_container_width=True
)


# ============================================================
# 27. DATA TABLE
# ============================================================

st.subheader("Incident Records")


# Display selected columns
display_columns = [
    "Identifier",
    "Title",
    "Start date",
    "End date",
    "Number of deaths",
    "Year",
    "Month Name",
    "Day of Week",
    "Incident Type",
    "State",
    "Incident Duration (days)"
]


st.dataframe(
    filtered_df[display_columns],
    use_container_width=True
)


# ============================================================
# 28. DOWNLOAD FILTERED DATA
# ============================================================

st.subheader("Download Data")


# Convert filtered data into CSV
csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")


# Create download button
st.download_button(
    label="Download Filtered Data",
    data=csv_data,
    file_name="filtered_nigeria_incidents.csv",
    mime="text/csv"
)


# ============================================================
# 29. FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "NG Nigeria Incidents Analysis Dashboard | "
    "Built with Python, Pandas, Plotly and Streamlit"
)
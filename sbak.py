import streamlit as st
import pandas as pd
import re
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="SMS Expense Tracker", layout="wide")

# ---------- Helper Functions ----------
def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def log_action(username, action, details=""):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "username": username,
        "action": action,
        "details": details
    }
    df_log = pd.DataFrame([log_entry])
    with open(r"audit_log.csv", "a") as f:
        df_log.to_csv(f, header=f.tell() == 0, index=False)

def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def get_user_data_file(username):
    return f"data_{username}.csv"

# ---------- Load Admin Data ----------
@st.cache_data
def load_main_data():
    df = pd.read_csv(r"s1.csv")
    df.columns = df.columns.str.strip().str.lower()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

main_data = load_main_data()

# Extract unique users and set passwords
user_creds = {
    "sakshi": "123",
    "akanksha": "098",
    "kirti": "456",
    "bhumika": "678",
    "admin": "admin"
}

# ---------- Login/Register ----------
login_option = st.sidebar.selectbox("Choose Option", ["Login", "New User Registration"])
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

user_authenticated = False

if login_option == "Login":
    if st.sidebar.button("Login"):
        if user_creds.get(username) == password:
            user_authenticated = True
            log_action(username, "Login")
        else:
            st.sidebar.error("Invalid credentials")

elif login_option == "New User Registration":
    if st.sidebar.button("Register"):
        if username in user_creds:
            st.sidebar.error("User already exists")
        elif username and password:
            # Register user and create new data file
            user_creds[username] = password
            df_new = pd.DataFrame(columns=main_data.columns)
            df_new.to_csv(get_user_data_file(username), index=False)
            st.sidebar.success("Registration successful. Please log in.")
            log_action(username, "Registered")
        else:
            st.sidebar.warning("Please enter valid username and password")

# ---------- Main App ----------
if user_authenticated:
    st.title("📊 SMS Expense Tracker")
    st.markdown("Analyze your spending by filtering uploaded expenses.")

    if username == "admin":
        df = main_data.copy()
    else:
        user_file = get_user_data_file(username)
        if os.path.exists(user_file):
            df = pd.read_csv(user_file)
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        else:
            df = main_data[main_data['paid by'].str.lower() == username.lower()].copy()

    # Sidebar filters
    st.sidebar.header("Filter Options")
    start = st.sidebar.date_input("Start Date", df['date'].min().date() if not df.empty else datetime.today().date())
    end = st.sidebar.date_input("End Date", df['date'].max().date() if not df.empty else datetime.today().date())
    filtered = df[(df['date'] >= pd.to_datetime(start)) & (df['date'] <= pd.to_datetime(end))]

    filter_map = {
        "category": "Category",
        "subcategory": "Subcategory",
        "payment method": "Payment Method",
        "account used": "Account Used",
        "currency": "Currency",
        "paid by": "Paid By",
        "split with": "Split With",
        "settled": "Settled",
        "recurring": "Recurring",
        "frequency": "Frequency",
        "bill/receipt attached": "Bill/Receipt Attached",
        "tags": "Tags",
        "budget category": "Budget Category",
        "location": "Location"
    }

    for col in filter_map:
        if filter_map[col].lower() in df.columns:
            options = df[filter_map[col].lower()].dropna().unique()
            selected = st.sidebar.multiselect(filter_map[col], options)
            if selected:
                filtered = filtered[filtered[filter_map[col].lower()].isin(selected)]

    if not filtered.empty:
        log_action(username, "Viewed Data", f"From {start} to {end}")
        st.subheader("Summary")
        col1, col2 = st.columns(2)
        col1.metric("Total Spent", f"₹{filtered['amount'].sum():,.2f}")
        col2.metric("Transactions", len(filtered))

        st.subheader("Category Breakdown")
        if 'category' in filtered.columns:
            pie_data = filtered.groupby("category")["amount"].sum().reset_index()
            st.plotly_chart(px.pie(pie_data, names='category', values='amount'))

        st.subheader("Spending Over Time")
        time_series = filtered.groupby(filtered['date'].dt.date)['amount'].sum()
        st.line_chart(time_series)

        st.subheader("Transactions")
        st.dataframe(filtered)

        st.download_button("Download Filtered CSV", convert_df(filtered), "filtered_expenses.csv", "text/csv")
        log_action(username, "Download", "Filtered CSV downloaded")
    else:
        st.warning("No records match your filters.")

import streamlit as st
import pandas as pd
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
    with open("audit_log.csv", "a") as f:
        df_log.to_csv(f, header=f.tell() == 0, index=False)

def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def get_user_data_file(username):
    return f"data_{username}.csv"

@st.cache_data
def load_main_data():
    df = pd.read_csv(r"data_with_users.csv")
    df.columns = df.columns.str.strip().str.lower()
    df['date'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    return df

main_data = load_main_data()

# ---------- Credentials ----------
user_creds = {
    "sakshi": "123",
    "akanksha": "098",
    "kirti": "456",
    "bhumika": "678",
    "admin": "admin"
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ---------- Login/Register ----------
if not st.session_state.authenticated:
    login_option = st.sidebar.selectbox("Choose Option", ["Login", "New User Registration"])
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if login_option == "Login":
        if st.sidebar.button("Login"):
            if user_creds.get(username) == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                log_action(username, "Login")
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials")

    elif login_option == "New User Registration":
        if st.sidebar.button("Register"):
            if username in user_creds:
                st.sidebar.error("User already exists")
            elif username and password:
                user_creds[username] = password
                df_new = pd.DataFrame(columns=main_data.columns)
                df_new.to_csv(get_user_data_file(username), index=False)
                st.sidebar.success("Registration successful. Please log in.")
                log_action(username, "Registered")
            else:
                st.sidebar.warning("Please enter valid username and password")

# ---------- Main App ----------
if st.session_state.authenticated:
    username = st.session_state.username
    st.title("📊 SMS Expense Tracker")
    st.subheader(f"Welcome, {username}!")

    if st.button("Log Out"):
        log_action(username, "Log Out")
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()

    if username == "admin":
        df = main_data.copy()
    else:
        user_file = get_user_data_file(username)
        if os.path.exists(user_file):
            df = pd.read_csv(user_file)
            df.columns = df.columns.str.strip().str.lower()
            df['date'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        else:
            df = main_data[main_data['paid by'].str.lower() == username.lower()].copy()

    # Sidebar Filters
    st.sidebar.header("📅 Filter Options")
    start = st.sidebar.date_input("Start Date", df['date'].min().date())
    end = st.sidebar.date_input("End Date", df['date'].max().date())
    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime(end)
    filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    filters = {
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

    for col_key, label in filters.items():
        if col_key in filtered.columns:
            options = sorted(filtered[col_key].dropna().unique().tolist())
            if col_key == "location":
                extra_locations = ["Pune", "Mumbai", "Nashik", "Delhi", "Nagpur", "Bangalore"]
                options = sorted(set(options + extra_locations))
            selected = st.sidebar.multiselect(f"{label}", options)
            if selected:
                filtered = filtered[filtered[col_key].isin(selected)]

    if not filtered.empty:
        log_action(username, "Viewed Data", f"From {start_date.date()} to {end_date.date()}")
        st.subheader("Summary")
        col1, col2 = st.columns(2)
        col1.metric("Total Spent", f"₹{filtered['amount'].sum():,.2f}")
        col2.metric("Transactions", len(filtered))

        st.subheader("Category Breakdown")
        if 'category' in filtered.columns:
            pie_data = filtered.groupby("category")["amount"].sum().reset_index()
            st.plotly_chart(px.pie(pie_data, names='category', values='amount'))

        st.subheader("Spending Over Time")
        if 'date' in filtered.columns:
            time_series = filtered.groupby(filtered['date'].dt.date)['amount'].sum()
            st.line_chart(time_series)

        st.subheader("Transactions")
        st.dataframe(filtered)

        st.download_button("Download Filtered CSV", convert_df(filtered), "filtered_expenses.csv", "text/csv")
        log_action(username, "Download", "Filtered CSV downloaded")
    else:
        st.warning("⚠ No records match your filters.")

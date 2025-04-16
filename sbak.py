import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="SMS Expense Tracker", layout="wide")

CSV_PATH = r"s1.csv"

# ---------- Load Data ----------
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    df.columns = df.columns.str.strip().str.lower()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

# ---------- Save Data ----------
def save_data(df):
    df.to_csv(CSV_PATH, index=False)

# ---------- Login & Sign Up ----------
def authenticate():
    st.sidebar.title("Account Access")
    choice = st.sidebar.radio("Select", ["Login", "Sign Up"])

    if choice == "Sign Up":
        st.sidebar.subheader("Create New Account")
        new_user = st.sidebar.text_input("New Username")
        new_pass = st.sidebar.text_input("New Password", type="password")

        if st.sidebar.button("Register"):
            df = load_data()
            if new_user in df['username'].values:
                st.sidebar.error("Username already exists.")
            else:
                new_entry = {
                    "username": new_user,
                    "password": new_pass,
                    "usertype": "user",
                    "date": pd.NaT,
                    "amount": 0
                }
                for col in df.columns:
                    if col not in new_entry:
                        new_entry[col] = pd.NA
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(df)
                st.sidebar.success("Account created. Please log in.")
                st.rerun()

        return None, None

    else:
        st.sidebar.subheader("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")

        df = load_data()
        creds = df.dropna(subset=['username', 'password'])[['username', 'password', 'usertype']].drop_duplicates()

        match = creds[(creds['username'] == username) & (creds['password'] == password)]
        if st.sidebar.button("Login"):
            if not match.empty:
                usertype = match.iloc[0]['usertype']
                return username, usertype
            else:
                st.sidebar.error("Invalid credentials")

    return None, None

# ---------- Helper Functions ----------
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# ---------- Main App ----------
def app(username, usertype):
    st.title("📊 SMS Expense Tracker")
    st.markdown("Analyze your spending by filtering uploaded expenses.")

    df = load_data()

    # Filter data: users see only their entries, admin sees everything
    if usertype != "admin":
        df = df[df['paid by'].str.strip().str.lower() == username.lower()]

    # Sidebar filters
    st.sidebar.header("Filter Options")
    start = st.sidebar.date_input("Start Date", df['date'].min().date())
    end = st.sidebar.date_input("End Date", df['date'].max().date())
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
    else:
        st.warning("No records match your filters.")

# ---------- Run App ----------
username, usertype = authenticate()
if username:
    app(username, usertype)

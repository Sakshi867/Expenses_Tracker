import streamlit as st
import pandas as pd
import re
import plotly.express as px
from datetime import datetime

# ✅ Set app to mobile-friendly layout
st.set_page_config(page_title="Expense Tracker", layout="wide", initial_sidebar_state="collapsed")

# ✅ Hide Streamlit header, menu, and footer
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# ---------- Load Data ----------
@st.cache_data
def load_data():
    df = pd.read_csv(r"Modified_Expenses_with_Login.csv")
    df.columns = df.columns.str.strip().str.lower()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

data = load_data()
user_creds = dict(zip(data['username'], data['password']))

# ---------- Login ----------
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if user_creds.get(username) == password:
        return True
    elif username and password:
        st.sidebar.error("Invalid credentials")
    return False

# ---------- Helper Functions ----------
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# ---------- Main App ----------
def app():
    st.markdown("<h2 style='text-align: center;'>💸 SMS Expense Tracker</h2>", unsafe_allow_html=True)
    st.markdown("Analyze your spending by filtering uploaded expenses.")

    df = data.copy()

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
        st.dataframe(filtered, use_container_width=True)

        st.download_button("Download Filtered CSV", convert_df(filtered), "filtered_expenses.csv", "text/csv", use_container_width=True)
    else:
        st.warning("No records match your filters.")

# ---------- Run App ----------
if login():
    app()

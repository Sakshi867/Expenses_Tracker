# 📱 SMS Expense Tracker

A lightweight expense tracker built with **Streamlit** that parses SMS messages to extract and organize financial transactions. This app supports **user login**, **data filtering**, and reads data from a **CSV file**, offering a simple and effective solution for managing your expenses.



## 🚀 Features

- 🔐 **User Authentication**  
  Simple login system to manage access.

- 📄 **CSV-Based Storage**  
  Reads transaction data from a structured CSV file (e.g., extracted SMS messages).

- 🔍 **Filtering Options**  
  Filter transactions by date, category, amount, and more.

- 📊 **Summarized Reports**  
  Automatically calculates totals, averages, and other insights.

- 🌐 **Web UI with Streamlit**  
  Fast and interactive user interface built with Streamlit.


## 🗃️ CSV Format

Make sure your CSV file has the following columns:

```csv
Date, Description, Amount, Category
2025-04-01, POS 1234 Debit Card Purchase, 250.00, Shopping
2025-04-02, UPI Transfer to XYZ, 1500.00, Transfer
...

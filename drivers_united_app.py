import streamlit as st
import pandas as pd

st.set_page_config(page_title="Drivers United", layout="wide")

st.title("🚛 Drivers United Dashboard")

# -----------------------
# SESSION STATE STORAGE
# -----------------------
if "loads" not in st.session_state:
    st.session_state.loads = pd.DataFrame(columns=[
        "Pickup", "Drop", "Miles", "Rate", "CPM", "Status"
    ])

if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=[
        "Category", "Amount"
    ])

# -----------------------
# ADD LOAD
# -----------------------
st.header("➕ Add Load")

col1, col2 = st.columns(2)

with col1:
    pickup = st.text_input("Pickup City")
    miles = st.number_input("Miles", min_value=0)

with col2:
    drop = st.text_input("Drop City")
    rate = st.number_input("Rate ($)", min_value=0)

if st.button("Add Load"):
    if miles > 0:
        cpm = round(rate / miles, 2)
    else:
        cpm = 0

    new_row = pd.DataFrame([{
        "Pickup": pickup,
        "Drop": drop,
        "Miles": miles,
        "Rate": rate,
        "CPM": cpm,
        "Status": "Booked"
    }])

    st.session_state.loads = pd.concat(
        [st.session_state.loads, new_row],
        ignore_index=True
    )

    st.success("Load added!")

# -----------------------
# LOAD TABLE
# -----------------------
st.header("📦 Active Loads")

st.dataframe(st.session_state.loads, use_container_width=True)

# -----------------------
# ADD EXPENSE
# -----------------------
st.header("⛽ Add Expense")

col3, col4 = st.columns(2)

with col3:
    category = st.selectbox("Category", ["Fuel", "Repair", "Toll", "Other"])

with col4:
    amount = st.number_input("Amount ($)", min_value=0)

if st.button("Add Expense"):
    new_expense = pd.DataFrame([{
        "Category": category,
        "Amount": amount
    }])

    st.session_state.expenses = pd.concat(
        [st.session_state.expenses, new_expense],
        ignore_index=True
    )

    st.success("Expense added!")

# -----------------------
# EXPENSE TABLE
# -----------------------
st.header("💸 Expenses")

st.dataframe(st.session_state.expenses, use_container_width=True)

# -----------------------
# DASHBOARD METRICS
# -----------------------
st.header("📊 Summary")

total_revenue = st.session_state.loads["Rate"].sum()
total_expense = st.session_state.expenses["Amount"].sum()
profit = total_revenue - total_expense

avg_cpm = 0
if not st.session_state.loads.empty:
    avg_cpm = round(st.session_state.loads["CPM"].mean(), 2)

colA, colB, colC, colD = st.columns(4)

colA.metric("Revenue", f"${total_revenue}")
colB.metric("Expenses", f"${total_expense}")
colC.metric("Profit", f"${profit}")
colD.metric("Avg CPM", avg_cpm)
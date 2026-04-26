import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Drivers United", layout="wide")

st.title("🚛 Drivers United Dashboard")

DATA_FILE = "data.csv"
EXPENSE_FILE = "expenses.csv"

# -----------------------
# LOAD DATA
# -----------------------
if os.path.exists(DATA_FILE):
    loads = pd.read_csv(DATA_FILE)
else:
    loads = pd.DataFrame(columns=["Pickup","Drop","Miles","Rate","CPM","Status"])

if os.path.exists(EXPENSE_FILE):
    expenses = pd.read_csv(EXPENSE_FILE)
else:
    expenses = pd.DataFrame(columns=["Category","Amount"])

# -----------------------
# SAVE FUNCTIONS
# -----------------------
def save_loads():
    loads.to_csv(DATA_FILE, index=False)

def save_expenses():
    expenses.to_csv(EXPENSE_FILE, index=False)

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
    cpm = round(rate / miles, 2) if miles > 0 else 0

    new_row = pd.DataFrame([{
        "Pickup": pickup,
        "Drop": drop,
        "Miles": miles,
        "Rate": rate,
        "CPM": cpm,
        "Status": "Booked"
    }])

    loads = pd.concat([loads, new_row], ignore_index=True)
    save_loads()
    st.success("Load saved!")

# -----------------------
# LOAD TABLE
# -----------------------
st.header("📦 Loads")

if not loads.empty:
    for i in range(len(loads)):
        colA, colB, colC = st.columns([4,2,2])

        colA.write(f"{loads.loc[i,'Pickup']} → {loads.loc[i,'Drop']} | ${loads.loc[i,'Rate']}")

        status = colB.selectbox(
            "Status",
            ["Booked","In Transit","Delivered","Paid"],
            index=["Booked","In Transit","Delivered","Paid"].index(loads.loc[i,"Status"]),
            key=f"status_{i}"
        )

        if status != loads.loc[i,"Status"]:
            loads.loc[i,"Status"] = status
            save_loads()

# -----------------------
# INVOICE GENERATOR
# -----------------------
st.header("🧾 Generate Invoice")

if not loads.empty:
    load_choice = st.selectbox("Select Load", loads.index)

    selected = loads.loc[load_choice]

    st.write("### Invoice Preview")
    st.write(f"Pickup: {selected['Pickup']}")
    st.write(f"Drop: {selected['Drop']}")
    st.write(f"Rate: ${selected['Rate']}")

    invoice_text = f"""
    DRIVERS UNITED INVOICE

    Pickup: {selected['Pickup']}
    Drop: {selected['Drop']}
    Rate: ${selected['Rate']}
    """

    st.download_button(
        label="Download Invoice",
        data=invoice_text,
        file_name="invoice.txt"
    )

# -----------------------
# ADD EXPENSE
# -----------------------
st.header("⛽ Add Expense")

col3, col4 = st.columns(2)

with col3:
    category = st.selectbox("Category", ["Fuel","Repair","Toll","Other"])

with col4:
    amount = st.number_input("Amount ($)", min_value=0)

if st.button("Add Expense"):
    new_expense = pd.DataFrame([{
        "Category": category,
        "Amount": amount
    }])

    expenses = pd.concat([expenses, new_expense], ignore_index=True)
    save_expenses()
    st.success("Expense saved!")

# -----------------------
# EXPENSE TABLE
# -----------------------
st.header("💸 Expenses")

st.dataframe(expenses, use_container_width=True)

# -----------------------
# DASHBOARD
# -----------------------
st.header("📊 Summary")

total_revenue = loads["Rate"].sum()
total_expense = expenses["Amount"].sum()
profit = total_revenue - total_expense
avg_cpm = round(loads["CPM"].mean(),2) if not loads.empty else 0

colA, colB, colC, colD = st.columns(4)

colA.metric("Revenue", f"${total_revenue}")
colB.metric("Expenses", f"${total_expense}")
colC.metric("Profit", f"${profit}")
colD.metric("Avg CPM", avg_cpm)

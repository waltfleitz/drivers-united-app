import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Drivers United", layout="wide")

DATA_FILE = "database.json"

# -----------------------
# LOAD DATABASE
# -----------------------
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        db = json.load(f)
else:
    db = {}

def save_db():
    with open(DATA_FILE, "w") as f:
        json.dump(db, f, indent=2)

# -----------------------
# DRIVER LOGIN
# -----------------------
st.sidebar.title("Driver Login")

driver = st.sidebar.text_input("Enter Driver Name")

if not driver:
    st.warning("Enter your name to begin")
    st.stop()

if driver not in db:
    db[driver] = {
        "loads": [],
        "expenses": []
    }
    save_db()

st.sidebar.success(f"Logged in as {driver}")

st.title(f"🚛 Drivers United — {driver}")

# -----------------------
# TABS
# -----------------------
tab1, tab2, tab3, tab4 = st.tabs(["📦 Loads", "⛽ Expenses", "🧾 Invoice", "📊 Dashboard"])

# =======================
# LOADS TAB (UPDATED)
# =======================
with tab1:
    st.subheader("Add Load")

    col1, col2 = st.columns(2)

    with col1:
        pickup_city = st.text_input("Pickup City")
        pickup_business = st.text_input("Pickup Business Name")
        miles = st.number_input("Miles", min_value=0)

    with col2:
        drop_city = st.text_input("Drop City")
        drop_business = st.text_input("Drop Business Name")
        rate = st.number_input("Rate", min_value=0)

    if st.button("Add Load"):
        cpm = round(rate / miles, 2) if miles > 0 else 0

        db[driver]["loads"].append({
            "Pickup City": pickup_city,
            "Pickup Business": pickup_business,
            "Drop City": drop_city,
            "Drop Business": drop_business,
            "Miles": miles,
            "Rate": rate,
            "CPM": cpm,
            "Status": "Booked"
        })
        save_db()
        st.success("Load saved!")

    st.subheader("Your Loads")

    loads_df = pd.DataFrame(db[driver]["loads"])

    if not loads_df.empty:
        for i in range(len(loads_df)):
            colA, colB = st.columns([4,2])

            colA.write(
                f"{loads_df.loc[i,'Pickup Business']} ({loads_df.loc[i,'Pickup City']}) → "
                f"{loads_df.loc[i,'Drop Business']} ({loads_df.loc[i,'Drop City']}) | "
                f"${loads_df.loc[i,'Rate']}"
            )

            status = colB.selectbox(
                "Status",
                ["Booked","In Transit","Delivered","Paid"],
                index=["Booked","In Transit","Delivered","Paid"].index(loads_df.loc[i,"Status"]),
                key=f"{driver}_status_{i}"
            )

            db[driver]["loads"][i]["Status"] = status
            save_db()

# =======================
# EXPENSES TAB
# =======================
with tab2:
    st.subheader("Add Expense")

    col1, col2, col3 = st.columns(3)

    with col1:
        category = st.selectbox("Category", ["Fuel","Repair","Toll","Insurance","Other"])

    with col2:
        amount = st.number_input("Amount", min_value=0)

    with col3:
        notes = st.text_input("Notes")

    if st.button("Add Expense"):
        db[driver]["expenses"].append({
            "Category": category,
            "Amount": amount,
            "Notes": notes
        })
        save_db()
        st.success("Expense saved!")

    st.subheader("Edit Expenses")

    if db[driver]["expenses"]:
        for i, exp in enumerate(db[driver]["expenses"]):
            colA, colB, colC, colD = st.columns([2,2,3,1])

            new_cat = colA.selectbox(
                "Category",
                ["Fuel","Repair","Toll","Insurance","Other"],
                index=["Fuel","Repair","Toll","Insurance","Other"].index(exp["Category"]),
                key=f"{driver}_cat_{i}"
            )

            new_amt = colB.number_input(
                "Amount",
                value=int(exp["Amount"]),
                key=f"{driver}_amt_{i}"
            )

            new_notes = colC.text_input(
                "Notes",
                value=exp.get("Notes", ""),
                key=f"{driver}_notes_{i}"
            )

            if colD.button("❌", key=f"{driver}_del_{i}"):
                db[driver]["expenses"].pop(i)
                save_db()
                st.rerun()

            if (
                new_cat != exp["Category"] or
                new_amt != exp["Amount"] or
                new_notes != exp.get("Notes", "")
            ):
                db[driver]["expenses"][i]["Category"] = new_cat
                db[driver]["expenses"][i]["Amount"] = new_amt
                db[driver]["expenses"][i]["Notes"] = new_notes
                save_db()

# =======================
# INVOICE TAB (UPDATED)
# =======================
with tab3:
    st.subheader("Generate Invoice")

    loads_df = pd.DataFrame(db[driver]["loads"])

    if not loads_df.empty:
        idx = st.selectbox("Select Load", loads_df.index)

        selected = loads_df.loc[idx]

        st.write("### Invoice Preview")
        st.write(f"Pickup: {selected['Pickup Business']} ({selected['Pickup City']})")
        st.write(f"Drop: {selected['Drop Business']} ({selected['Drop City']})")
        st.write(f"Rate: ${selected['Rate']}")

        invoice_text = f"""
DRIVERS UNITED INVOICE

Driver: {driver}

Pickup: {selected['Pickup Business']} ({selected['Pickup City']})
Drop: {selected['Drop Business']} ({selected['Drop City']})
Rate: ${selected['Rate']}
"""

        st.download_button(
            label="Download Invoice",
            data=invoice_text,
            file_name="invoice.txt"
        )

# =======================
# DASHBOARD TAB
# =======================
with tab4:
    st.subheader("Summary")

    loads_df = pd.DataFrame(db[driver]["loads"])
    expenses_df = pd.DataFrame(db[driver]["expenses"])

    total_revenue = loads_df["Rate"].sum() if not loads_df.empty else 0
    total_expense = expenses_df["Amount"].sum() if not expenses_df.empty else 0
    profit = total_revenue - total_expense
    avg_cpm = round(loads_df["CPM"].mean(), 2) if not loads_df.empty else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Revenue", f"${total_revenue}")
    col2.metric("Expenses", f"${total_expense}")
    col3.metric("Profit", f"${profit}")
    col4.metric("Avg CPM", avg_cpm)

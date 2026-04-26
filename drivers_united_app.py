import streamlit as st
import pandas as pd
import json
import os
from datetime import date

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
# LOADS TAB (FULL EDITABLE)
# =======================
with tab1:
    st.subheader("Add Load")

    col1, col2 = st.columns(2)

    with col1:
        load_date = st.date_input("Date", value=date.today())

        pickup_business = st.text_input("Pickup Business")
        pickup_city = st.text_input("Pickup City")
        pickup_state = st.text_input("Pickup State")
        pickup_zip = st.text_input("Pickup ZIP")

    with col2:
        drop_business = st.text_input("Drop Business")
        drop_city = st.text_input("Drop City")
        drop_state = st.text_input("Drop State")
        drop_zip = st.text_input("Drop ZIP")

        miles = st.number_input("Miles", min_value=0)
        rate = st.number_input("Rate", min_value=0)

    if st.button("Add Load"):
        cpm = round(rate / miles, 2) if miles > 0 else 0

        db[driver]["loads"].append({
            "Date": str(load_date),
            "Pickup Business": pickup_business,
            "Pickup City": pickup_city,
            "Pickup State": pickup_state,
            "Pickup ZIP": pickup_zip,
            "Drop Business": drop_business,
            "Drop City": drop_city,
            "Drop State": drop_state,
            "Drop ZIP": drop_zip,
            "Miles": miles,
            "Rate": rate,
            "CPM": cpm,
            "Status": "Booked"
        })
        save_db()
        st.success("Load saved!")

    st.subheader("Edit Loads")

    if db[driver]["loads"]:
        for i, load in enumerate(db[driver]["loads"]):
            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                new_date = col1.text_input("Date", value=load["Date"], key=f"d_{i}")

                new_pb = col1.text_input("Pickup Business", value=load["Pickup Business"], key=f"pb_{i}")
                new_pc = col1.text_input("Pickup City", value=load["Pickup City"], key=f"pc_{i}")
                new_ps = col1.text_input("Pickup State", value=load["Pickup State"], key=f"ps_{i}")
                new_pz = col1.text_input("Pickup ZIP", value=load["Pickup ZIP"], key=f"pz_{i}")

            with col2:
                new_db = col2.text_input("Drop Business", value=load["Drop Business"], key=f"db_{i}")
                new_dc = col2.text_input("Drop City", value=load["Drop City"], key=f"dc_{i}")
                new_ds = col2.text_input("Drop State", value=load["Drop State"], key=f"ds_{i}")
                new_dz = col2.text_input("Drop ZIP", value=load["Drop ZIP"], key=f"dz_{i}")

                new_miles = col2.number_input("Miles", value=int(load["Miles"]), key=f"m_{i}")
                new_rate = col2.number_input("Rate", value=int(load["Rate"]), key=f"r_{i}")

                status = col2.selectbox(
                    "Status",
                    ["Booked","In Transit","Delivered","Paid"],
                    index=["Booked","In Transit","Delivered","Paid"].index(load["Status"]),
                    key=f"s_{i}"
                )

            if st.button("❌ Delete Load", key=f"del_{i}"):
                db[driver]["loads"].pop(i)
                save_db()
                st.rerun()

            # Auto-save changes
            updated = {
                "Date": new_date,
                "Pickup Business": new_pb,
                "Pickup City": new_pc,
                "Pickup State": new_ps,
                "Pickup ZIP": new_pz,
                "Drop Business": new_db,
                "Drop City": new_dc,
                "Drop State": new_ds,
                "Drop ZIP": new_dz,
                "Miles": new_miles,
                "Rate": new_rate,
                "CPM": round(new_rate / new_miles, 2) if new_miles > 0 else 0,
                "Status": status
            }

            if updated != load:
                db[driver]["loads"][i] = updated
                save_db()

# =======================
# EXPENSES TAB (UNCHANGED)
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
                key=f"cat_{i}"
            )

            new_amt = colB.number_input("Amount", value=int(exp["Amount"]), key=f"amt_{i}")
            new_notes = colC.text_input("Notes", value=exp.get("Notes",""), key=f"note_{i}")

            if colD.button("❌", key=f"expdel_{i}"):
                db[driver]["expenses"].pop(i)
                save_db()
                st.rerun()

            if (new_cat != exp["Category"] or new_amt != exp["Amount"] or new_notes != exp.get("Notes","")):
                db[driver]["expenses"][i] = {
                    "Category": new_cat,
                    "Amount": new_amt,
                    "Notes": new_notes
                }
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

        st.write(f"Pickup: {selected['Pickup Business']} ({selected['Pickup City']}, {selected['Pickup State']} {selected['Pickup ZIP']})")
        st.write(f"Drop: {selected['Drop Business']} ({selected['Drop City']}, {selected['Drop State']} {selected['Drop ZIP']})")
        st.write(f"Rate: ${selected['Rate']}")

        file_name = f"{selected['Pickup Business']}_to_{selected['Drop Business']}.txt"

        invoice_text = f"""
DRIVERS UNITED INVOICE

Driver: {driver}
Date: {selected['Date']}

Pickup:
{selected['Pickup Business']}
{selected['Pickup City']}, {selected['Pickup State']} {selected['Pickup ZIP']}

Drop:
{selected['Drop Business']}
{selected['Drop City']}, {selected['Drop State']} {selected['Drop ZIP']}

Rate: ${selected['Rate']}
"""

        st.download_button(
            label="Download Invoice",
            data=invoice_text,
            file_name=file_name
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

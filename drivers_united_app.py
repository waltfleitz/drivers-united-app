import streamlit as st
import pandas as pd
import json
import os
from datetime import date, datetime

st.set_page_config(page_title="ARISE Distribution", layout="wide")

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

def safe_get(d, key, default=""):
    return d[key] if key in d else default

# -----------------------
# BRAND HEADER
# -----------------------
st.markdown("""
# 🚛 ARISE Distribution
### Hotshot Trucking — Fast. Reliable. On Time.
""")

st.markdown("---")

# -----------------------
# DRIVER LOGIN
# -----------------------
st.sidebar.title("Driver Login")

driver = st.sidebar.text_input("Driver Name", value="Joshua Smith")

if not driver:
    st.warning("Enter your name")
    st.stop()

if driver not in db:
    db[driver] = {"loads": [], "expenses": []}
    save_db()

# Sidebar Contact Info
st.sidebar.markdown("### Driver Info")
st.sidebar.write("📞 502-396-6192")
st.sidebar.write("📍 Borden, Indiana")
st.sidebar.write("✉️ arisedistribution26@gmail.com")

st.sidebar.success(f"Logged in as {driver}")

# -----------------------
# TABS
# -----------------------
tab1, tab2, tab3, tab4 = st.tabs(["📦 Loads", "⛽ Expenses", "🧾 Invoice", "📊 Dashboard"])

# =======================
# LOADS TAB
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
        rate = st.number_input("Customer Rate", min_value=0)
        cost = st.number_input("Driver Cost", min_value=0)

    if st.button("Add Load"):
        cpm = round(rate / miles, 2) if miles > 0 else 0
        profit = rate - cost

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
            "Cost": cost,
            "Profit": profit,
            "CPM": cpm,
            "Status": "Booked",
            "Paid": "No"
        })
        save_db()
        st.success("Load saved!")

    st.subheader("Active Loads")

    for i, load in enumerate(db[driver]["loads"]):
        st.markdown("---")

        st.markdown(f"""
**{safe_get(load,'Pickup Business')} ({safe_get(load,'Pickup City')}, {safe_get(load,'Pickup State')} {safe_get(load,'Pickup ZIP')})**  
➡️  
**{safe_get(load,'Drop Business')} ({safe_get(load,'Drop City')}, {safe_get(load,'Drop State')} {safe_get(load,'Drop ZIP')})**
""")

        col1, col2, col3 = st.columns(3)

        new_rate = col1.number_input("Rate", value=int(safe_get(load,"Rate",0)), key=f"r_{i}")
        new_cost = col2.number_input("Cost", value=int(safe_get(load,"Cost",0)), key=f"c_{i}")

        status = col3.selectbox(
            "Status",
            ["Booked","In Transit","Delivered","Paid"],
            index=["Booked","In Transit","Delivered","Paid"].index(safe_get(load,"Status","Booked")),
            key=f"s_{i}"
        )

        paid = col3.selectbox(
            "Paid",
            ["No","Yes"],
            index=["No","Yes"].index(safe_get(load,"Paid","No")),
            key=f"p_{i}"
        )

        profit = new_rate - new_cost

        db[driver]["loads"][i]["Rate"] = new_rate
        db[driver]["loads"][i]["Cost"] = new_cost
        db[driver]["loads"][i]["Profit"] = profit
        db[driver]["loads"][i]["Status"] = status
        db[driver]["loads"][i]["Paid"] = paid

        save_db()

# =======================
# EXPENSES
# =======================
with tab2:
    st.subheader("Expenses")

    category = st.selectbox("Category", ["Fuel","Repair","Toll","Insurance","Other"])
    amount = st.number_input("Amount", min_value=0)

    if st.button("Add Expense"):
        db[driver]["expenses"].append({"Category": category, "Amount": amount})
        save_db()
        st.success("Expense added")

    st.dataframe(pd.DataFrame(db[driver]["expenses"]))

# =======================
# INVOICE
# =======================
with tab3:
    st.subheader("Invoice")

    loads_df = pd.DataFrame(db[driver]["loads"])

    if not loads_df.empty:
        idx = st.selectbox("Select Load", loads_df.index)
        selected = loads_df.loc[idx]

        st.write(f"### {selected['Pickup Business']} ➝ {selected['Drop Business']}")
        st.write(f"Rate: ${selected['Rate']}")

        invoice = f"""
ARISE DISTRIBUTION
Hotshot Trucking

Driver: {driver}
Date: {selected['Date']}

Pickup:
{selected['Pickup Business']}
{selected['Pickup City']}, {selected['Pickup State']} {selected['Pickup ZIP']}

Drop:
{selected['Drop Business']}
{selected['Drop City']}, {selected['Drop State']} {selected['Drop ZIP']}

Total: ${selected['Rate']}
"""

        st.download_button("Download Invoice", invoice,
            file_name=f"{selected['Pickup Business']}_to_{selected['Drop Business']}.txt")

# =======================
# DASHBOARD
# =======================
with tab4:
    st.subheader("Business Overview")

    loads_df = pd.DataFrame(db[driver]["loads"])

    if not loads_df.empty:
        revenue = loads_df["Rate"].sum()
        cost = loads_df["Cost"].sum()
        profit = loads_df["Profit"].sum()

        col1, col2, col3 = st.columns(3)

        col1.metric("Revenue", f"${revenue}")
        col2.metric("Cost", f"${cost}")
        col3.metric("Profit", f"${profit}")

        # Aging
        today = datetime.today()

        def aging(d):
            try:
                days = (today - datetime.strptime(d, "%Y-%m-%d")).days
                if days <= 30: return "0-30"
                elif days <= 60: return "31-60"
                else: return "60+"
            except:
                return "Unknown"

        loads_df["Aging"] = loads_df["Date"].apply(aging)

        st.dataframe(loads_df[["Pickup Business","Drop Business","Rate","Paid","Aging"]])

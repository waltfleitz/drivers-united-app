import streamlit as st
import pandas as pd
import json
import os
from datetime import date, datetime

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
# SAFE GET (prevents crashes)
# -----------------------
def safe_get(d, key, default=""):
    return d[key] if key in d else default

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
        rate = st.number_input("Rate", min_value=0)
        cost = st.number_input("Cost (what you pay driver)", min_value=0)

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

    st.subheader("Edit Loads")

    for i, load in enumerate(db[driver]["loads"]):
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            new_date = col1.text_input("Date", value=safe_get(load,"Date"), key=f"d_{i}")
            new_pb = col1.text_input("Pickup Business", value=safe_get(load,"Pickup Business"), key=f"pb_{i}")
            new_pc = col1.text_input("Pickup City", value=safe_get(load,"Pickup City"), key=f"pc_{i}")
            new_ps = col1.text_input("Pickup State", value=safe_get(load,"Pickup State"), key=f"ps_{i}")
            new_pz = col1.text_input("Pickup ZIP", value=safe_get(load,"Pickup ZIP"), key=f"pz_{i}")

        with col2:
            new_db = col2.text_input("Drop Business", value=safe_get(load,"Drop Business"), key=f"db_{i}")
            new_dc = col2.text_input("Drop City", value=safe_get(load,"Drop City"), key=f"dc_{i}")
            new_ds = col2.text_input("Drop State", value=safe_get(load,"Drop State"), key=f"ds_{i}")
            new_dz = col2.text_input("Drop ZIP", value=safe_get(load,"Drop ZIP"), key=f"dz_{i}")

            new_miles = col2.number_input("Miles", value=int(safe_get(load,"Miles",0)), key=f"m_{i}")
            new_rate = col2.number_input("Rate", value=int(safe_get(load,"Rate",0)), key=f"r_{i}")
            new_cost = col2.number_input("Cost", value=int(safe_get(load,"Cost",0)), key=f"c_{i}")

            status = col2.selectbox(
                "Status",
                ["Booked","In Transit","Delivered","Paid"],
                index=["Booked","In Transit","Delivered","Paid"].index(safe_get(load,"Status","Booked")),
                key=f"s_{i}"
            )

            paid = col2.selectbox(
                "Paid",
                ["No","Yes"],
                index=["No","Yes"].index(safe_get(load,"Paid","No")),
                key=f"paid_{i}"
            )

        if st.button("❌ Delete Load", key=f"del_{i}"):
            db[driver]["loads"].pop(i)
            save_db()
            st.rerun()

        profit = new_rate - new_cost

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
            "Cost": new_cost,
            "Profit": profit,
            "CPM": round(new_rate / new_miles, 2) if new_miles > 0 else 0,
            "Status": status,
            "Paid": paid
        }

        db[driver]["loads"][i] = updated
        save_db()

# =======================
# EXPENSES TAB
# =======================
with tab2:
    st.subheader("Expenses")

    expenses_df = pd.DataFrame(db[driver]["expenses"])
    st.dataframe(expenses_df)

# =======================
# INVOICE TAB
# =======================
with tab3:
    st.subheader("Invoice")

    loads_df = pd.DataFrame(db[driver]["loads"])

    if not loads_df.empty:
        idx = st.selectbox("Select Load", loads_df.index)
        selected = loads_df.loc[idx]

        st.write(f"{selected['Pickup Business']} → {selected['Drop Business']}")
        st.write(f"Rate: ${selected['Rate']}")

        st.download_button(
            "Download Invoice",
            data=str(selected),
            file_name=f"{selected['Pickup Business']}_to_{selected['Drop Business']}.txt"
        )

# =======================
# DASHBOARD TAB
# =======================
with tab4:
    st.subheader("Dashboard")

    loads_df = pd.DataFrame(db[driver]["loads"])

    if not loads_df.empty:
        total_revenue = loads_df["Rate"].sum()
        total_cost = loads_df["Cost"].sum()
        total_profit = loads_df["Profit"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Revenue", f"${total_revenue}")
        col2.metric("Cost", f"${total_cost}")
        col3.metric("Profit", f"${total_profit}")

        # Aging
        st.subheader("Aging")

        today = datetime.today()

        def aging_bucket(d):
            try:
                days = (today - datetime.strptime(d, "%Y-%m-%d")).days
                if days <= 30:
                    return "0-30"
                elif days <= 60:
                    return "31-60"
                else:
                    return "60+"
            except:
                return "Unknown"

        loads_df["Aging"] = loads_df["Date"].apply(aging_bucket)

        st.dataframe(loads_df[["Pickup Business","Drop Business","Rate","Paid","Aging"]])

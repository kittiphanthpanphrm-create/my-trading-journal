import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Trading Journal", layout="wide")

CSV_FILE = "trades.csv"

# โหลดข้อมูลเดิม
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=[
        "Date", "Symbol", "Direction", "Session", "Setup",
        "Entry", "Exit", "Lot", "PnL ($)", "RR", "Result", "Chart Link", "Notes"
    ])

st.title("📈 Trading Journal (บันทึกการเทรด)")

# สรุปสถิติรวม
if not df.empty:
    total_trades = len(df)
    total_pnl = df["PnL ($)"].sum()
    wins = len(df[df["Result"] == "WIN"])
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("จำนวนไม้ทั้งหมด", f"{total_trades} ไม้")
    col2.metric("กำไร/ขาดทุนรวม", f"${total_pnl:,.2f}")
    col3.metric("จำนวนไม้ชนะ", f"{wins} ไม้")
    col4.metric("Win Rate", f"{win_rate:.1f}%")

st.markdown("---")

# ฟอร์มบันทึก
st.subheader("➕ บันทึกไม้ใหม่")
with st.form("trade_form", clear_on_submit=True):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        trade_date = st.date_input("วันที่", value=date.today())
        symbol = st.selectbox("Symbol", ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD", "US30", "NAS100", "อื่นๆ"])
    with c2:
        direction = st.selectbox("Direction", ["BUY", "SELL"])
        session = st.selectbox("Session", ["Asian", "London", "NY AM", "NY PM"])
    with c3:
        setup = st.selectbox("Setup", ["Liquidity Sweep + OB", "FVG + Inducement", "Break of Structure", "Wyckoff Setup", "Retail Trap", "อื่นๆ"])
        result = st.selectbox("ผลลัพธ์", ["WIN", "LOSS", "BE"])
    with c4:
        lot = st.number_input("Lot Size", min_value=0.01, value=0.10, step=0.01)
        pnl = st.number_input("กำไร/ขาดทุน ($)", value=0.0, step=10.0)

    c5, c6, c7 = st.columns(3)
    with c5:
        entry_price = st.number_input("ราคาเข้า (Entry)", value=0.0, format="%.2f")
    with c6:
        exit_price = st.number_input("ราคาออก (Exit)", value=0.0, format="%.2f")
    with c7:
        rr = st.number_input("R:R", value=1.0, step=0.5)

    chart_url = st.text_input("ลิงก์รูปชาร์ต (TradingView Snapshot)")
    notes = st.text_area("บันทึกอารมณ์ / หมายเหตุ")

    submitted = st.form_submit_button("💾 บันทึกข้อมูล", use_container_width=True)

    if submitted:
        new_data = {
            "Date": str(trade_date),
            "Symbol": symbol,
            "Direction": direction,
            "Session": session,
            "Setup": setup,
            "Entry": entry_price,
            "Exit": exit_price,
            "Lot": lot,
            "PnL ($)": pnl,
            "RR": rr,
            "Result": result,
            "Chart Link": chart_url,
            "Notes": notes
        }
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
        st.rerun()

st.subheader("📋 ประวัติการเทรดทั้งหมด")
if not df.empty:
    st.dataframe(df.iloc[::-1], use_container_width=True)
else:
    st.info("ยังไม่มีข้อมูลการเทรด กรอกแบบฟอร์มด้านบนเพื่อเริ่มบันทึก")

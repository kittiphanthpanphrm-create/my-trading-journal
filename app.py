import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Trading Journal", layout="centered")

CSV_FILE = "trades.csv"

# โหลดหรือสร้างโครงสร้างข้อมูล
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["เวลา", "สินทรัพย์", "ผลลัพธ์", "R:R"])

st.title("📈 Trading Journal")

# ฟอร์มบันทึกข้อมูลแบบกระชับ
with st.form("quick_trade_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        trade_time = st.text_input("เวลา", value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        symbol = st.selectbox("สินทรัพย์ที่เทรด", ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD", "US30", "NAS100", "อื่นๆ"])
        
    with col2:
        result = st.selectbox("ผลลัพธ์", ["WIN", "LOSS", "BE"])
        rr = st.number_input("R:R", value=1.0, step=0.5, format="%.2f")

    submitted = st.form_submit_button("💾 บันทึก", use_container_width=True)

    if submitted:
        new_row = {
            "เวลา": trade_time,
            "สินทรัพย์": symbol,
            "ผลลัพธ์": result,
            "R:R": rr
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success("บันทึกสำเร็จ!")
        st.rerun()

st.markdown("---")

# แสดงประวัติการเทรด
st.subheader("📋 ประวัติการเทรด")
if not df.empty:
    st.dataframe(df.iloc[::-1], use_container_width=True)
else:
    st.info("ยังไม่มีข้อมูล กรอกด้านบนเพื่อเริ่มบันทึก")

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests

st.set_page_config(page_title="Trading Journal", layout="centered")

CSV_FILE = "trades.csv"
IMAGE_DIR = "trade_images"

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

columns = ["เวลา", "สินทรัพย์", "ระบบเทรด", "ผลลัพธ์", "R:R", "รูปภาพชาร์ต"]

if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    for col in columns:
        if col not in df.columns:
            df[col] = ""
else:
    df = pd.DataFrame(columns=columns)

def download_tv_image(url: str) -> str:
    """ดาวน์โหลดรูปจากลิงก์ TradingView มาเก็บในเซิร์ฟเวอร์โดยตรง"""
    url = url.strip()
    if not url:
        return ""
    
    # แปลงลิงก์หน้าเว็บให้เป็นลิงก์ไฟล์รูปภาพ .png
    if "tradingview.com/x/" in url:
        snap_id = url.rstrip("/").split("/")[-1]
        direct_url = f"https://s3.tradingview.com/snapshots/{snap_id[0].lower()}/{snap_id}.png"
    else:
        direct_url = url
        
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(direct_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            filename = f"tv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            local_path = os.path.join(IMAGE_DIR, filename)
            with open(local_path, "wb") as f:
                f.write(resp.content)
            return local_path
    except Exception:
        pass
    return url

st.title("📈 Trading Journal")

with st.form("trade_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        trade_time = st.text_input("เวลา", value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        symbol = st.selectbox("สินทรัพย์ที่เทรด", ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD", "US30", "NAS100", "อื่นๆ"])
        strategy = st.selectbox("ระบบเทรด", ["ไวคอฟ (Wyckoff)", "โฟโลเทรน (Follow Trend)", "อื่นๆ"])
        
    with col2:
        result = st.selectbox("ผลลัพธ์", ["WIN", "LOSS", "BE"])
        rr = st.number_input("R:R", value=1.0, step=0.5, format="%.2f")

    chart_input = st.text_input("🔗 วางลิงก์รูป TradingView (https://www.tradingview.com/x/...)")
    uploaded_image = st.file_uploader("หรือเลือกไฟล์จากเครื่อง (ถ้ามี)", type=["png", "jpg", "jpeg"])

    submitted = st.form_submit_button("💾 บันทึก", use_container_width=True)

    if submitted:
        saved_img_path = ""
        
        # กรณีอัปโหลดไฟล์ตรงๆ
        if uploaded_image is not None:
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_image.name}"
            saved_img_path = os.path.join(IMAGE_DIR, filename)
            with open(saved_img_path, "wb") as f:
                f.write(uploaded_image.getbuffer())
        # กรณีวางลิงก์ TradingView
        elif chart_input.strip() != "":
            with st.spinner("กำลังดึงรูปภาพจาก TradingView..."):
                saved_img_path = download_tv_image(chart_input)

        new_row = {
            "เวลา": trade_time,
            "สินทรัพย์": symbol,
            "ระบบเทรด": strategy,
            "ผลลัพธ์": result,
            "R:R": rr,
            "รูปภาพชาร์ต": saved_img_path
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success("บันทึกข้อมูลเรียบร้อย!")
        st.rerun()

st.markdown("---")

st.subheader("📋 ประวัติการเทรด")
if not df.empty:
    for idx, row in df.iloc[::-1].iterrows():
        header_text = f"🔹 {row['เวลา']} | {row['สินทรัพย์']} | {row['ระบบเทรด']} | ผลลัพธ์: {row['ผลลัพธ์']} (R:R: {row['R:R']})"
        with st.expander(header_text):
            c_left, c_right = st.columns([1, 2])
            with c_left:
                st.write(f"**เวลา:** {row['เวลา']}")
                st.write(f"**สินทรัพย์:** {row['สินทรัพย์']}")
                st.write(f"**ระบบเทรด:** {row['ระบบเทรด']}")
                st.write(f"**ผลลัพธ์:** {row['ผลลัพธ์']}")
                st.write(f"**R:R:** {row['R:R']}")
            with c_right:
                img_path = str(row["รูปภาพชาร์ต"]).strip()
                if img_path and os.path.exists(img_path):
                    st.image(img_path, caption="ชาร์ตประกอบการเทรด", use_container_width=True)
                elif img_path.startswith("http"):
                    st.image(img_path, caption="ชาร์ตจากลิงก์", use_container_width=True)
                else:
                    st.caption("ไม่มีรูปภาพแนบ")
else:
    st.info("ยังไม่มีข้อมูล กรอกฟอร์มด้านบนเพื่อเริ่มบันทึก")

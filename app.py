import streamlit as st
import pandas as pd
from datetime import datetime
import os

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

def get_direct_chart_url(url: str) -> str:
    """แปลงลิงก์ Snapshot ของ TradingView ให้กลายเป็น URL ไฟล์รูปภาพตรงๆ"""
    url = url.strip()
    if not url:
        return ""
    if "tradingview.com/x/" in url:
        # ตัดเอา Snapshot ID เช่น https://www.tradingview.com/x/ABC12345/ -> ABC12345
        parts = url.rstrip("/").split("/")
        snap_id = parts[-1]
        return f"https://s3.tradingview.com/snapshots/{snap_id[0].lower()}/{snap_id}.png"
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

    chart_input = st.text_input("🔗 วางลิงก์รูป TradingView (กดปุ่มกล้อง -> Copy link to image)")
    uploaded_image = st.file_uploader("หรือเลือกไฟล์จากเครื่อง (ถ้ามี)", type=["png", "jpg", "jpeg"])

    submitted = st.form_submit_button("💾 บันทึก", use_container_width=True)

    if submitted:
        image_ref = ""
        if uploaded_image is not None:
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_image.name}"
            image_path = os.path.join(IMAGE_DIR, filename)
            with open(image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())
            image_ref = image_path
        elif chart_input.strip() != "":
            image_ref = get_direct_chart_url(chart_input)

        new_row = {
            "เวลา": trade_time,
            "สินทรัพย์": symbol,
            "ระบบเทรด": strategy,
            "ผลลัพธ์": result,
            "R:R": rr,
            "รูปภาพชาร์ต": image_ref
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
                raw_img = str(row["รูปภาพชาร์ต"]).strip()
                img_url = get_direct_chart_url(raw_img)
                
                if img_url.startswith("http://") or img_url.startswith("https://"):
                    st.image(img_url, caption="ชาร์ต TradingView", use_container_width=True)
                elif img_url and os.path.exists(img_url):
                    st.image(img_url, caption="ชาร์ตประกอบการเทรด", use_container_width=True)
                else:
                    st.caption("ไม่มีรูปภาพแนบ")
else:
    st.info("ยังไม่มีข้อมูล กรอกฟอร์มด้านบนเพื่อเริ่มบันทึก")

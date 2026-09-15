import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

st.set_page_config(page_title="Trading Dashboard & Journal", layout="wide")

CSV_FILE = "trades.csv"
IMAGE_DIR = "trade_images"

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

columns = ["id", "เวลา", "สินทรัพย์", "ระบบเทรด", "ผลลัพธ์", "R:R", "รูปภาพชาร์ต"]

def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if "id" not in df.columns:
            df["id"] = [str(i) for i in range(len(df))]
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        df["id"] = df["id"].astype(str)
        return df
    return pd.DataFrame(columns=columns)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# แปลงรูปภาพเป็น Base64 เพื่อให้คลิกเปิดดูขนาดจริง 4K ในแท็บใหม่ได้
def get_image_base64_url(img_path):
    with open(img_path, "rb") as f:
        data = f.read()
    ext = img_path.split(".")[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    encoded = base64.b64encode(data).decode()
    return f"data:{mime};base64,{encoded}"

df = load_data()

# ==============================================================================
# โหมดดูภาพขนาดใหญ่พร้อมระบบซูม (Ultra HD Viewer)
# ==============================================================================
if st.session_state.get("view_fullscreen_img"):
    img_info = st.session_state["view_fullscreen_img"]
    
    col_btn1, col_btn2, col_zoom = st.columns([1.5, 2, 2.5])
    with col_btn1:
        if st.button("🔙 ✖ ปิดรูปภาพ / กลับหน้าหลัก", use_container_width=True):
            st.session_state["view_fullscreen_img"] = None
            st.rerun()

    if os.path.exists(img_info["path"]):
        img_data_url = get_image_base64_url(img_info["path"])
        with col_btn2:
            st.markdown(
                f'<a href="{img_data_url}" target="_blank" style="text-decoration:none;">'
                f'<button style="width:100%;height:38px;background-color:#0284c7;color:white;border:none;border-radius:6px;cursor:pointer;font-weight:bold;">'
                f'↗️ เปิดรูปต้นฉบับ 4K ในแท็บใหม่ (คลิกซูมได้)</button></a>',
                unsafe_allow_html=True
            )
        with col_zoom:
            zoom_level = st.slider("🔍 ขยายขนาดภาพ (Zoom Level)", min_value=100, max_value=300, value=150, step=10, format="%d%%")

        st.subheader(f"🔍 ชาร์ต: {img_info['title']}")
        
        # กล่องแสดงผลแบบมี Scrollbar เลื่อนซ้ายขวาได้อิสระ ไม่บีบตัวหนังสือ
        st.markdown(
            f"""
            <div style="width: 100%; overflow-x: auto; overflow-y: auto; border: 1px solid #334155; border-radius: 8px; padding: 10px; background: #0f172a;">
                <img src="{img_data_url}" style="width: {zoom_level}%; max-width: none; height: auto; display: block;" />
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error("ไม่พบไฟล์รูปภาพ")
    
    st.stop()

# ==============================================================================
# ส่วนที่ 1: แดชบอร์ดและกราฟสถิติการเทรด
# ==============================================================================
st.title("📊 Trading Performance Dashboard")

if df.empty:
    st.info("💡 ยังไม่มีข้อมูลการเทรดในระบบ เลื่อนลงไปด้านล่างเพื่อบันทึกไม้แรก")
else:
    df_calc = df.copy()
    df_calc["R:R"] = pd.to_numeric(df_calc["R:R"], errors="coerce").fillna(0.0)

    def calc_net_r(row):
        res = str(row["ผลลัพธ์"]).upper()
        if res == "WIN":
            return row["R:R"]
        elif res == "LOSS":
            return -1.0
        return 0.0

    df_calc["Net_R"] = df_calc.apply(calc_net_r, axis=1)
    df_calc["Cumulative_R"] = df_calc["Net_R"].cumsum()

    total_trades = len(df_calc)
    wins = len(df_calc[df_calc["ผลลัพธ์"] == "WIN"])
    losses = len(df_calc[df_calc["ผลลัพธ์"] == "LOSS"])
    bes = len(df_calc[df_calc["ผลลัพธ์"] == "BE"])
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
    total_r = df_calc["Net_R"].sum()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("จำนวนไม้ทั้งหมด", f"{total_trades} ไม้")
    m2.metric("Win Rate", f"{win_rate:.1f} %")
    m3.metric("ผลรวม R รวมสะสม", f"{total_r:+.2f} R")
    m4.metric("สัดส่วน (W / L / BE)", f"{wins} / {losses} / {bes}")

    st.write("")

    c_chart1, c_chart2 = st.columns([2, 1])
    with c_chart1:
        st.subheader("📈 กราฟการเติบโตของพอร์ต (Cumulative R:R Curve)")
        chart_data = df_calc[["เวลา", "Cumulative_R"]].set_index("เวลา")
        st.line_chart(chart_data)

    with c_chart2:
        st.subheader("🎯 สัดส่วนผลลัพธ์ & ระบบเทรด")
        strat_summary = df_calc.groupby("ระบบเทรด").agg(
            จำนวนไม้=("id", "count"),
            Rรวม=("Net_R", "sum")
        ).reset_index()
        st.dataframe(strat_summary, use_container_width=True, hide_index=True)
        st.bar_chart(df_calc["ผลลัพธ์"].value_counts())

st.divider()

# ==============================================================================
# ส่วนที่ 2: บันทึกการเทรด และ ประวัติจัดการข้อมูล
# ==============================================================================
tab_new, tab_history = st.tabs(["📝 บันทึกการเทรดใหม่", "📋 ประวัติการเทรดและจัดการ (แก้ไข/ลบ)"])

with tab_new:
    st.subheader("📝 บันทึกการเทรดใหม่")
    with st.form("new_trade_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            trade_time = st.text_input("เวลา", value=datetime.now().strftime("%Y-%m-%d %H:%M"))
            symbol = st.selectbox("สินทรัพย์ที่เทรด", ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD", "US30", "NAS100", "อื่นๆ"])
            strategy = st.selectbox("ระบบเทรด", ["ไวคอฟ (Wyckoff)", "โฟโลเทรน (Follow Trend)", "อื่นๆ"])
        with col2:
            result = st.selectbox("ผลลัพธ์", ["WIN", "LOSS", "BE"])
            rr = st.number_input("R:R", value=1.0, step=0.5, format="%.2f")
            uploaded_image = st.file_uploader("📷 แนบรูปภาพชาร์ต (PNG, JPG)", type=["png", "jpg", "jpeg"])

        submitted = st.form_submit_button("💾 บันทึกการเทรด", use_container_width=True)

        if submitted:
            image_path = ""
            new_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
            if uploaded_image is not None:
                ext = uploaded_image.name.split(".")[-1]
                filename = f"{new_id}.{ext}"
                image_path = os.path.join(IMAGE_DIR, filename)
                with open(image_path, "wb") as f:
                    f.write(uploaded_image.getbuffer())

            new_row = {
                "id": new_id,
                "เวลา": trade_time,
                "สินทรัพย์": symbol,
                "ระบบเทรด": strategy,
                "ผลลัพธ์": result,
                "R:R": rr,
                "รูปภาพชาร์ต": image_path
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("✅ บันทึกข้อมูลเรียบร้อย!")
            st.rerun()

with tab_history:
    st.subheader("📋 รายการประวัติการเทรดทั้งหมด")
    if df.empty:
        st.info("ยังไม่มีประวัติการเทรด")
    else:
        st.write(f"จำนวนทั้งหมด: **{len(df)}** ไม้")

        for idx, row in df.iloc[::-1].iterrows():
            trade_id = str(row["id"])
            box_title = f"ไม้ {row['เวลา']} | {row['สินทรัพย์']} | {row['ระบบเทรด']} | ผลลัพธ์: {row['ผลลัพธ์']} (R:R: {row['R:R']})"
            
            with st.expander(box_title):
                c1, c2 = st.columns([1, 1])
                
                with c1:
                    st.write(f"**รหัสอ้างอิง:** `{trade_id}`")
                    st.write(f"**เวลา:** {row['เวลา']}")
                    st.write(f"**สินทรัพย์:** {row['สินทรัพย์']}")
                    st.write(f"**ระบบเทรด:** {row['ระบบเทรด']}")
                    st.write(f"**ผลลัพธ์:** {row['ผลลัพธ์']}")
                    st.write(f"**R:R:** {row['R:R']}")

                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("✏️ แก้ไขข้อมูล", key=f"btn_edit_{trade_id}", use_container_width=True):
                            st.session_state[f"editing_{trade_id}"] = True

                    with btn_col2:
                        if st.button("🗑️ ลบรายการ", key=f"btn_del_{trade_id}", use_container_width=True):
                            if row["รูปภาพชาร์ต"] and os.path.exists(str(row["รูปภาพชาร์ต"])):
                                try:
                                    os.remove(str(row["รูปภาพชาร์ต"]))
                                except Exception:
                                    pass
                            df = df[df["id"] != trade_id]
                            save_data(df)
                            st.success("ลบรายการเรียบร้อย!")
                            st.rerun()

                with c2:
                    img_path = str(row["รูปภาพชาร์ต"]).strip()
                    if img_path and os.path.exists(img_path):
                        st.image(img_path, caption="รูปชาร์ตประกอบ", use_container_width=True)
                        if st.button("🔍 ดูภาพขยายเต็มจอ", key=f"view_img_{trade_id}", use_container_width=True):
                            st.session_state["view_fullscreen_img"] = {
                                "path": img_path,
                                "title": f"{row['สินทรัพย์']} | {row['ระบบเทรด']} | {row['ผลลัพธ์']} ({row['เวลา']})"
                            }
                            st.rerun()
                    else:
                        st.caption("ไม่มีรูปภาพแนบสำหรับไม้นี้")

                if st.session_state.get(f"editing_{trade_id}", False):
                    st.markdown("---")
                    st.write("**📝 ฟอร์มแก้ไขข้อมูล:**")
                    with st.form(key=f"form_edit_{trade_id}"):
                        e_time = st.text_input("เวลา", value=row["เวลา"])
                        
                        symbol_list = ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD", "US30", "NAS100", "อื่นๆ"]
                        s_idx = symbol_list.index(row["สินทรัพย์"]) if row["สินทรัพย์"] in symbol_list else len(symbol_list)-1
                        e_symbol = st.selectbox("สินทรัพย์", symbol_list, index=s_idx)

                        strat_list = ["ไวคอฟ (Wyckoff)", "โฟโลเทรน (Follow Trend)", "อื่นๆ"]
                        strat_idx = strat_list.index(row["ระบบเทรด"]) if row["ระบบเทรด"] in strat_list else len(strat_list)-1
                        e_strategy = st.selectbox("ระบบเทรด", strat_list, index=strat_idx)

                        res_list = ["WIN", "LOSS", "BE"]
                        res_idx = res_list.index(row["ผลลัพธ์"]) if row["ผลลัพธ์"] in res_list else 0
                        e_result = st.selectbox("ผลลัพธ์", res_list, index=res_idx)

                        e_rr = st.number_input("R:R", value=float(row["R:R"]) if str(row["R:R"]).replace(".","",1).isdigit() else 1.0, step=0.5)

                        save_edit = st.form_submit_button("💾 ยืนยันการแก้ไข", use_container_width=True)
                        if save_edit:
                            df.loc[df["id"] == trade_id, "เวลา"] = e_time
                            df.loc[df["id"] == trade_id, "สินทรัพย์"] = e_symbol
                            df.loc[df["id"] == trade_id, "ระบบเทรด"] = e_strategy
                            df.loc[df["id"] == trade_id, "ผลลัพธ์"] = e_result
                            df.loc[df["id"] == trade_id, "R:R"] = e_rr
                            save_data(df)
                            st.session_state[f"editing_{trade_id}"] = False
                            st.success("อัปเดตข้อมูลสำเร็จ!")
                            st.rerun()

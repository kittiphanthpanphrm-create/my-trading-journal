import streamlit as st
import pandas as pd
from datetime import datetime
import zoneinfo
import re
import os
import base64

st.set_page_config(page_title="Trading Dashboard & Journal", layout="wide")

TH_TZ = zoneinfo.ZoneInfo("Asia/Bangkok")

def get_now_th():
    return datetime.now(TH_TZ)

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

def get_image_base64_url(img_path):
    with open(img_path, "rb") as f:
        data = f.read()
    ext = img_path.split(".")[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    encoded = base64.b64encode(data).decode()
    return f"data:{mime};base64,{encoded}"

# ฟังก์ชันดึงชั่วโมงจากข้อความเวลาที่ผู้ใช้บันทึกจริง
def extract_hour_range(time_str):
    if not time_str or pd.isna(time_str):
        return "ไม่ระบุเวลา"
    val = str(time_str).strip()
    
    # พยายามแปลงแบบ datetime ปกติ
    try:
        dt = pd.to_datetime(val)
        h = dt.hour
        return f"{h:02d}:00 - {(h+1)%24:02d}:00"
    except Exception:
        pass

    # หากมีรูปแบบเช่น 08:30 หรือ 8:00 หรือ 08.30
    match = re.search(r'(\b\d{1,2})[:.](\d{2})', val)
    if match:
        h = int(match.group(1))
        if 0 <= h <= 23:
            return f"{h:02d}:00 - {(h+1)%24:02d}:00"
            
    # กรณีพิมพ์แค่เลขชั่วโมงเดี่ยวๆ เช่น 8 หรือ 08
    match_single = re.search(r'\b(\d{1,2})\b', val)
    if match_single:
        h = int(match_single.group(1))
        if 0 <= h <= 23:
            return f"{h:02d}:00 - {(h+1)%24:02d}:00"

    return "ไม่ระบุเวลา"

def render_donut_chart(win_rate, loss_rate, be_rate, title="WIN RATE"):
    c = 251.2
    dash_w = (win_rate / 100) * c
    dash_l = (loss_rate / 100) * c
    dash_be = (be_rate / 100) * c

    off_w = 0.0
    off_l = -dash_w
    off_be = -(dash_w + dash_l)

    return f"""
    <div style="background:#1e293b; border:1px solid #475569; border-radius:12px; padding:18px; text-align:center;">
        <svg width="170" height="170" viewBox="0 0 100 100" style="transform: rotate(-90deg); border-radius: 50%;">
            <circle cx="50" cy="50" r="40" fill="transparent" stroke="#334155" stroke-width="15" />
            <circle cx="50" cy="50" r="40" fill="transparent" stroke="#22c55e" stroke-width="15"
                    stroke-dasharray="{dash_w} {c}" stroke-dashoffset="{off_w}" />
            <circle cx="50" cy="50" r="40" fill="transparent" stroke="#ef4444" stroke-width="15"
                    stroke-dasharray="{dash_l} {c}" stroke-dashoffset="{off_l}" />
            <circle cx="50" cy="50" r="40" fill="transparent" stroke="#eab308" stroke-width="15"
                    stroke-dasharray="{dash_be} {c}" stroke-dashoffset="{off_be}" />
        </svg>
        <div style="margin-top:-108px; margin-bottom:40px;">
            <span style="font-size:24px; font-weight:900; color:#ffffff;">{win_rate:.1f}%</span><br>
            <span style="font-size:11px; color:#cbd5e1; font-weight:700;">{title}</span>
        </div>
        <div style="display:flex; justify-content:center; gap:12px; font-size:12px; font-weight:700; margin-top:15px;">
            <span style="color:#22c55e;">● ชนะ ({win_rate:.0f}%)</span>
            <span style="color:#ef4444;">● แพ้ ({loss_rate:.0f}%)</span>
            <span style="color:#eab308;">● เสมอ ({be_rate:.0f}%)</span>
        </div>
    </div>
    """

# สไตล์
st.markdown(
    """
    <style>
    label[data-testid="stWidgetLabel"] p {
        color: #0f172a !important;
        font-size: 15px !important;
        font-weight: 700 !important;
    }
    .header-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #475569;
        border-left: 8px solid #f97316;
        border-radius: 12px;
        padding: 18px 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.35);
    }
    .header-box h1 {
        color: #ffffff !important;
        font-size: 26px !important;
        font-weight: 800 !important;
        margin: 0 !important;
    }
    .header-box p {
        color: #cbd5e1 !important;
        font-size: 14px !important;
        margin: 6px 0 0 0 !important;
    }
    .section-title {
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #475569;
        border-left: 6px solid #f97316;
        border-radius: 8px;
        padding: 12px 20px;
        color: #ffffff !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        margin: 18px 0 14px 0;
    }
    .metric-card {
        background: #1e293b;
        border: 1px solid #475569;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
        margin-bottom: 12px;
    }
    .metric-label {
        color: #cbd5e1 !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        margin-bottom: 6px;
    }
    .metric-value {
        color: #fb923c !important;
        font-size: 28px !important;
        font-weight: 900 !important;
        line-height: 1.2;
    }
    .strategy-card {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .strategy-header {
        font-size: 20px;
        font-weight: 800;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .stat-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #1e293b;
        font-size: 15px;
    }
    .stat-row:last-child {
        border-bottom: none;
    }
    .stat-label {
        color: #94a3b8;
        font-weight: 600;
    }
    .stat-val {
        color: #f8fafc;
        font-weight: 800;
    }
    .trade-card {
        background: #0f172a !important;
        padding: 16px 20px !important;
        border-radius: 10px !important;
        border: 1px solid #334155 !important;
        margin-bottom: 12px !important;
    }
    .trade-card p {
        color: #f8fafc !important;
        font-size: 15px !important;
        margin: 6px 0 !important;
    }
    .trade-card b {
        color: #94a3b8 !important;
        font-weight: 700 !important;
        display: inline-block;
        width: 100px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

df = load_data()

# โหมดดูภาพขยาย
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
                f'<button style="width:100%;height:38px;background-color:#ea580c;color:white;border:none;border-radius:6px;cursor:pointer;font-weight:bold;">'
                f'↗️ เปิดรูปต้นฉบับในแท็บใหม่</button></a>',
                unsafe_allow_html=True
            )
        with col_zoom:
            zoom_level = st.slider("🔍 ขยายขนาดภาพ", min_value=100, max_value=300, value=150, step=10, format="%d%%")

        st.markdown(f'<div class="section-title">🔍 ตรวจสอบชาร์ต: {img_info["title"]}</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="width: 100%; overflow: auto; border: 2px solid #334155; border-radius: 10px; padding: 12px; background: #0b1120;">
                <img src="{img_data_url}" style="width: {zoom_level}%; max-width: none; height: auto; display: block;" />
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error("ไม่พบไฟล์รูปภาพ")
    st.stop()

st.markdown(
    """
    <div class="header-box">
        <h1>📊 TRADING PERFORMANCE DASHBOARD & JOURNAL</h1>
        <p>ระบบวิเคราะห์และแสดงผลตามช่วงเวลาที่กดบันทึกการเทรดจริง</p>
    </div>
    """,
    unsafe_allow_html=True
)

if df.empty:
    st.info("💡 ขณะนี้ยังไม่มีข้อมูลบันทึกในระบบ คุณสามารถเริ่มกรอกบันทึกไม้แรกได้ที่กล่องด้านล่างนี้เลยครับ")
else:
    df_calc = df.copy()
    df_calc["R:R"] = pd.to_numeric(df_calc["R:R"], errors="coerce").fillna(0.0)

    # นำเวลาที่ผู้ใช้บันทึกจริงมาแปลงเป็นช่วงเวลา 1 ชั่วโมง
    df_calc["ช่วงเวลา_1ชม"] = df_calc["เวลา"].apply(extract_hour_range)

    def calc_net_r(row):
        res = str(row["ผลลัพธ์"]).upper()
        if res == "WIN":
            return row["R:R"]
        elif res == "LOSS":
            return -1.0
        return 0.0

    df_calc["Net_R"] = df_calc.apply(calc_net_r, axis=1)
    df_calc = df_calc.sort_values(by="เวลา", ascending=True).reset_index(drop=True)
    df_calc["Cumulative_R"] = df_calc["Net_R"].cumsum()

    total_trades = len(df_calc)
    wins = len(df_calc[df_calc["ผลลัพธ์"] == "WIN"])
    losses = len(df_calc[df_calc["ผลลัพธ์"] == "LOSS"])
    bes = len(df_calc[df_calc["ผลลัพธ์"] == "BE"])
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
    total_r = df_calc["Net_R"].sum()

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f'<div class="metric-card"><div class="metric-label">จำนวนไม้ทั้งหมด</div><div class="metric-value">{total_trades} ไม้</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="metric-label">Win Rate รวม</div><div class="metric-value">{win_rate:.1f} %</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="metric-label">ผลรวม R สะสมรวม</div><div class="metric-value">{total_r:+.2f} R</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-card"><div class="metric-label">สัดส่วนรวม (ชนะ / แพ้ / เสมอ)</div><div class="metric-value" style="font-size:24px;">{wins} / {losses} / {bes}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">⚖️ สถิติและแผนภูมิอัตราชนะแยกตามระบบ</div>', unsafe_allow_html=True)

    def get_strat_metrics(name_keyword):
        sub = df_calc[df_calc["ระบบเทรด"].str.contains(name_keyword, case=False, na=False)]
        t = len(sub)
        w = len(sub[sub["ผลลัพธ์"] == "WIN"])
        l = len(sub[sub["ผลลัพธ์"] == "LOSS"])
        b = len(sub[sub["ผลลัพธ์"] == "BE"])
        wr = (w / t * 100) if t > 0 else 0.0
        lr = (l / t * 100) if t > 0 else 0.0
        br = (b / t * 100) if t > 0 else 0.0
        nr = sub["Net_R"].sum() if t > 0 else 0.0
        return t, w, l, b, wr, lr, br, nr

    w_t, w_w, w_l, w_b, w_wr, w_lr, w_br, w_nr = get_strat_metrics("ไวคอฟ")
    f_t, f_w, f_l, f_b, f_wr, f_lr, f_br, f_nr = get_strat_metrics("โฟโลเทรน")

    col_w_box, col_w_chart, col_f_box, col_f_chart = st.columns([1.3, 1, 1.3, 1])

    with col_w_box:
        st.markdown(
            f"""
            <div class="strategy-card" style="border-left: 6px solid #38bdf8; height: 100%;">
                <div class="strategy-header" style="color: #38bdf8;">📘 ไวคอฟ (Wyckoff)</div>
                <div class="stat-row"><span class="stat-label">จำนวนไม้:</span><span class="stat-val">{w_t} ไม้</span></div>
                <div class="stat-row"><span class="stat-label">Win Rate:</span><span class="stat-val" style="color:#22c55e; font-size:17px;">{w_wr:.1f}%</span></div>
                <div class="stat-row"><span class="stat-label">ชนะ / แพ้ / เสมอ:</span><span class="stat-val"><span style="color:#22c55e;">{w_w}</span> / <span style="color:#ef4444;">{w_l}</span> / <span style="color:#eab308;">{w_b}</span></span></div>
                <div class="stat-row"><span class="stat-label">Net R สะสม:</span><span class="stat-val" style="color:#fb923c; font-size:17px;">{w_nr:+.2f} R</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_w_chart:
        st.markdown(render_donut_chart(w_wr, w_lr, w_br, "WYCKOFF"), unsafe_allow_html=True)

    with col_f_box:
        st.markdown(
            f"""
            <div class="strategy-card" style="border-left: 6px solid #ec4899; height: 100%;">
                <div class="strategy-header" style="color: #ec4899;">📗 โฟโลเทรน (Follow Trend)</div>
                <div class="stat-row"><span class="stat-label">จำนวนไม้:</span><span class="stat-val">{f_t} ไม้</span></div>
                <div class="stat-row"><span class="stat-label">Win Rate:</span><span class="stat-val" style="color:#22c55e; font-size:17px;">{f_wr:.1f}%</span></div>
                <div class="stat-row"><span class="stat-label">ชนะ / แพ้ / เสมอ:</span><span class="stat-val"><span style="color:#22c55e;">{f_w}</span> / <span style="color:#ef4444;">{f_l}</span> / <span style="color:#eab308;">{f_b}</span></span></div>
                <div class="stat-row"><span class="stat-label">Net R สะสม:</span><span class="stat-val" style="color:#fb923c; font-size:17px;">{f_nr:+.2f} R</span></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_f_chart:
        st.markdown(render_donut_chart(f_wr, f_lr, f_br, "TREND"), unsafe_allow_html=True)

    # ส่วนวิเคราะห์ช่วงเวลา 1 ชั่วโมง
    st.markdown('<div class="section-title">⏰ สถิติการเทรดแยกตามช่วงเวลา (รอบละ 1 ชั่วโมง จากเวลาที่บันทึก)</div>', unsafe_allow_html=True)

    def summarize_hour_group(group):
        tot = len(group)
        w = len(group[group["ผลลัพธ์"] == "WIN"])
        l = len(group[group["ผลลัพธ์"] == "LOSS"])
        b = len(group[group["ผลลัพธ์"] == "BE"])
        wr = (w / tot * 100) if tot > 0 else 0.0
        nr = group["Net_R"].sum()
        return pd.Series({
            "จำนวนไม้": tot,
            "ชนะ (Win)": w,
            "แพ้ (Loss)": l,
            "เสมอ (BE)": b,
            "Win Rate %": f"{wr:.1f}%",
            "Net R": f"{nr:+.2f} R",
            "ชนะ (ไม้)": w,
            "แพ้ (ไม้)": l
        })

    hourly_summary = df_calc.groupby("ช่วงเวลา_1ชม").apply(summarize_hour_group).reset_index()
    hourly_summary = hourly_summary.sort_values(by="ช่วงเวลา_1ชม")

    ch1, ch2 = st.columns([1.6, 1.4])

    with ch1:
        st.write("**📊 แผนภูมิเปรียบเทียบไม้ชนะ และไม้แพ้ในแต่ละชั่วโมง**")
        chart_bar_df = hourly_summary[["ช่วงเวลา_1ชม", "ชนะ (ไม้)", "แพ้ (ไม้)"]].set_index("ช่วงเวลา_1ชม")
        st.bar_chart(chart_bar_df, color=["#22c55e", "#ef4444"])

    with ch2:
        st.write("**📋 ตารางสรุป Win Rate และผลตอบแทนรายชั่วโมง**")
        display_hourly = hourly_summary[["ช่วงเวลา_1ชม", "จำนวนไม้", "ชนะ (Win)", "แพ้ (Loss)", "เสมอ (BE)", "Win Rate %", "Net R"]]
        st.dataframe(display_hourly, use_container_width=True, hide_index=True)

    st.write("")
    st.markdown('<div class="section-title">📈 กราฟการเติบโตของพอร์ต (Cumulative R:R Curve)</div>', unsafe_allow_html=True)
    chart_data = df_calc[["เวลา", "Cumulative_R"]].set_index("เวลา")
    st.line_chart(chart_data)

# ส่วนบันทึกการเทรดใหม่
st.markdown('<div class="section-title">📝 บันทึกการเทรดใหม่</div>', unsafe_allow_html=True)

with st.expander("➕ คลิกเพื่อเปิด / ปิดฟอร์มบันทึกข้อมูลไม้ใหม่", expanded=True):
    with st.form("new_trade_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            trade_time = st.text_input("วัน-เวลาที่เทรด (เช่น 2026-09-15 08:30 หรือพิมพ์เฉพาะเวลา 08:30)", value="")
            symbol = st.selectbox("สินทรัพย์ที่เทรด", ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD", "US30", "NAS100", "อื่นๆ"])
            strategy = st.selectbox("ระบบเทรด", ["ไวคอฟ (Wyckoff)", "โฟโลเทรน (Follow Trend)", "อื่นๆ"])
        with col2:
            result = st.selectbox("ผลลัพธ์", ["WIN", "LOSS", "BE"])
            rr = st.number_input("R:R (ความคุ้มค่า)", value=1.0, step=0.5, format="%.2f")
            uploaded_image = st.file_uploader("📷 แนบรูปภาพชาร์ต (PNG, JPG)", type=["png", "jpg", "jpeg"])

        submitted = st.form_submit_button("💾 ยืนยันบันทึกการเทรด", use_container_width=True)

        if submitted:
            # ถ้าไม่กรอก ให้ใช้เวลาปัจจุบันของไทย
            final_time = trade_time.strip() if trade_time.strip() else get_now_th().strftime("%Y-%m-%d %H:%M")
            
            image_path = ""
            new_id = f"T_{int(datetime.now().timestamp() * 1000)}"
            if uploaded_image is not None:
                ext = uploaded_image.name.split(".")[-1]
                filename = f"{new_id}.{ext}"
                image_path = os.path.join(IMAGE_DIR, filename)
                with open(image_path, "wb") as f:
                    f.write(uploaded_image.getbuffer())

            new_row = {
                "id": new_id,
                "เวลา": final_time,
                "สินทรัพย์": symbol,
                "ระบบเทรด": strategy,
                "ผลลัพธ์": result,
                "R:R": rr,
                "รูปภาพชาร์ต": image_path
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว!")
            st.rerun()

# ประวัติบันทึกการเทรด
st.markdown(f'<div class="section-title">📋 ประวัติบันทึกการเทรดทั้งหมด ({len(df)} ไม้)</div>', unsafe_allow_html=True)

if df.empty:
    st.caption("ยังไม่มีประวัติการเทรด")
else:
    tab_all, tab_wyckoff, tab_trend = st.tabs(["📂 ดูทั้งหมด", "📘 เฉพาะไวคอฟ (Wyckoff)", "📗 เฉพาะโฟโลเทรน (Follow Trend)"])

    def render_trade_list(data_subset, tab_prefix):
        if data_subset.empty:
            st.caption("ไม่มีรายการเทรดในหมวดหมู่นี้")
            return

        for idx, row in data_subset.iloc[::-1].iterrows():
            trade_id = str(row["id"])
            trade_time_val = str(row["เวลา"]).strip()
            badge_color = "#22c55e" if row["ผลลัพธ์"] == "WIN" else ("#ef4444" if row["ผลลัพธ์"] == "LOSS" else "#eab308")
            
            # คำนวณช่วงชั่วโมงจากเวลาที่บันทึก
            hr_range = extract_hour_range(trade_time_val)
            hour_badge = f"⏰ {hr_range}" if hr_range != "ไม่ระบุเวลา" else ""

            box_title = f"ไม้ {trade_time_val}  |  {row['สินทรัพย์']}  |  {row['ระบบเทรด']}  |  {hour_badge}  |  ผลลัพธ์: {row['ผลลัพธ์']} (R:R: {row['R:R']})"
            
            with st.expander(box_title):
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.markdown(
                        f"""
                        <div class="trade-card" style="border-left: 5px solid {badge_color} !important;">
                            <p><b>รหัสอ้างอิง:</b> <code style="color:#fb923c;">{trade_id}</code></p>
                            <p><b>วัน-เวลาที่เทรด:</b> {trade_time_val}</p>
                            <p><b>ช่วงเวลา:</b> <span style="color:#38bdf8; font-weight:bold;">{hour_badge}</span></p>
                            <p><b>สินทรัพย์:</b> {row['สินทรัพย์']}</p>
                            <p><b>ระบบเทรด:</b> {row['ระบบเทรด']}</p>
                            <p><b>ผลลัพธ์:</b> <span style="color:{badge_color}; font-weight:800; font-size:16px;">{row['ผลลัพธ์']}</span></p>
                            <p><b>R:R:</b> {row['R:R']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("✏️ แก้ไขข้อมูล", key=f"btn_edit_{tab_prefix}_{trade_id}", use_container_width=True):
                            st.session_state[f"editing_{tab_prefix}_{trade_id}"] = True
                    with btn_col2:
                        if st.button("🗑️ ลบรายการ", key=f"btn_del_{tab_prefix}_{trade_id}", use_container_width=True):
                            if row["รูปภาพชาร์ต"] and os.path.exists(str(row["รูปภาพชาร์ต"])):
                                try:
                                    os.remove(str(row["รูปภาพชาร์ต"]))
                                except Exception:
                                    pass
                            global df
                            df = df[df["id"] != trade_id]
                            save_data(df)
                            st.success("ลบรายการเรียบร้อย!")
                            st.rerun()

                with c2:
                    img_path = str(row["รูปภาพชาร์ต"]).strip()
                    if img_path and os.path.exists(img_path):
                        st.image(img_path, caption="รูปชาร์ตประกอบ", use_container_width=True)
                        if st.button("🔍 ดูภาพขยายเต็มจอ", key=f"view_img_{tab_prefix}_{trade_id}", use_container_width=True):
                            st.session_state["view_fullscreen_img"] = {
                                "path": img_path,
                                "title": f"{row['สินทรัพย์']} | {row['ระบบเทรด']} | {row['ผลลัพธ์']} ({trade_time_val})"
                            }
                            st.rerun()
                    else:
                        st.caption("ไม่มีรูปภาพแนบสำหรับไม้นี้")

                if st.session_state.get(f"editing_{tab_prefix}_{trade_id}", False):
                    st.markdown("---")
                    st.write("**📝 ฟอร์มแก้ไขข้อมูล:**")
                    with st.form(key=f"form_edit_{tab_prefix}_{trade_id}"):
                        e_time = st.text_input("เวลาที่เทรด (เช่น 2026-09-15 08:30)", value=trade_time_val)
                        
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
                            df.loc[df["id"] == trade_id, "เวลา"] = e_time.strip()
                            df.loc[df["id"] == trade_id, "สินทรัพย์"] = e_symbol
                            df.loc[df["id"] == trade_id, "ระบบเทรด"] = e_strategy
                            df.loc[df["id"] == trade_id, "ผลลัพธ์"] = e_result
                            df.loc[df["id"] == trade_id, "R:R"] = e_rr
                            save_data(df)
                            st.session_state[f"editing_{tab_prefix}_{trade_id}"] = False
                            st.success("อัปเดตข้อมูลสำเร็จ!")
                            st.rerun()

    with tab_all:
        render_trade_list(df, "all")

    with tab_wyckoff:
        df_wyckoff = df[df["ระบบเทรด"].str.contains("ไวคอฟ", case=False, na=False)]
        render_trade_list(df_wyckoff, "wyckoff")

    with tab_trend:
        df_trend = df[df["ระบบเทรด"].str.contains("โฟโลเทรน", case=False, na=False)]
        render_trade_list(df_trend, "trend")

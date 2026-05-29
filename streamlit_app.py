import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
import os
from PIL import Image

st.set_page_config(page_title="Dental Health Tracker", layout="wide")
st.title("🦷 Complete Oral Health Tracker")
st.caption("Track hygiene | Diet | Photos | Systemic Health")

# Create photo folder
PHOTO_DIR = "user_photos"
if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

# Initialize data
if "logs" not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=[
        "Date", "Brushing (1-5)", "Flossing (1-5)", "Sugar_Intake_g",
        "Water_Intake_cups", "Gums_Bleed (0/1)", "Stress_Level (1-10)"
    ])

if "photos" not in st.session_state:
    st.session_state.photos = pd.DataFrame(columns=["Date", "Tooth", "Angle", "Photo_Path"])

# Sidebar - Daily Log
st.sidebar.header("📝 Log Today")
with st.sidebar.form("daily_log"):
    brushing = st.slider("Brushing (1=poor, 5=excellent)", 1, 5, 4)
    flossing = st.slider("Flossing (1=poor, 5=excellent)", 1, 5, 3)
    sugar = st.number_input("Sugar intake (grams)", 0, 150, 25)
    water = st.slider("Water (cups)", 0, 12, 6)
    gums_bleed = st.checkbox("Gums bleed when brushing?")
    stress = st.slider("Stress level (1=low, 10=high)", 1, 10, 5)
    
    submitted = st.form_submit_button("Save Today's Log")
    
    if submitted:
        new_entry = pd.DataFrame([{
            "Date": date.today(),
            "Brushing (1-5)": brushing,
            "Flossing (1-5)": flossing,
            "Sugar_Intake_g": sugar,
            "Water_Intake_cups": water,
            "Gums_Bleed (0/1)": 1 if gums_bleed else 0,
            "Stress_Level (1-10)": stress
        }])
        st.session_state.logs = pd.concat([st.session_state.logs, new_entry], ignore_index=True)
        st.sidebar.success("✅ Saved!")

# Sidebar - Photo Upload
st.sidebar.markdown("---")
st.sidebar.header("📸 Upload Tooth Photo")
with st.sidebar.form("photo_upload"):
    tooth_num = st.number_input("Tooth number (1-32)", 1, 32, 1)
    angle = st.selectbox("Angle", ["Front", "Left", "Right", "Top", "Bottom"])
    photo_file = st.file_uploader("Choose photo", type=["jpg", "jpeg", "png"])
    
    photo_submitted = st.form_submit_button("Upload Photo")
    
    if photo_submitted and photo_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tooth_{tooth_num}_{angle}_{timestamp}.jpg"
        filepath = os.path.join(PHOTO_DIR, filename)
        
        image = Image.open(photo_file)
        image.save(filepath)
        
        new_photo = pd.DataFrame([{
            "Date": date.today(),
            "Tooth": tooth_num,
            "Angle": angle,
            "Photo_Path": filepath
        }])
        st.session_state.photos = pd.concat([st.session_state.photos, new_photo], ignore_index=True)
        st.sidebar.success(f"✅ Photo saved for tooth #{tooth_num}")

# Main Dashboard
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📸 Photos", "📜 History"])

with tab1:
    if len(st.session_state.logs) > 0:
        latest = st.session_state.logs.iloc[-1]
        
        # Calculate scores
        hygiene_score = (latest["Brushing (1-5)"] * 0.5 + latest["Flossing (1-5)"] * 0.5) * 10
        diet_score = max(0, 100 - (latest["Sugar_Intake_g"] * 2))
        health_score = (hygiene_score + diet_score) / 2
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🪥 Hygiene", f"{hygiene_score:.0f}/50")
        col2.metric("🍎 Diet", f"{diet_score:.0f}/100")
        col3.metric("🏆 Overall Health", f"{health_score:.0f}/100")
        
        st.subheader("💡 Recommendations")
        if latest["Gums_Bleed (0/1)"]:
            st.warning("⚠️ Bleeding gums → see a dentist. Link to heart health.")
        if latest["Sugar_Intake_g"] > 25:
            st.info("🍬 High sugar → reduces to <25g/day for better teeth.")
        if latest["Stress_Level (1-10)"] > 7:
            st.info("😫 High stress → affects gum healing. Try deep breathing.")
    else:
        st.info("📋 No data yet. Use the sidebar to log your first day.")

with tab2:
    if len(st.session_state.photos) > 0:
        for _, row in st.session_state.photos.iterrows():
            if os.path.exists(row["Photo_Path"]):
                image = Image.open(row["Photo_Path"])
                st.image(image, caption=f"Tooth #{row['Tooth']} - {row['Angle']} - {row['Date']}")
    else:
        st.info("No photos uploaded yet. Use the sidebar to add photos.")

with tab3:
    if len(st.session_state.logs) > 0:
        st.dataframe(st.session_state.logs)
        csv = st.session_state.logs.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "dental_log.csv", "text/csv")
    else:
        st.write("No history yet.")

st.sidebar.markdown("---")
st.sidebar.info("Track your dental health daily. Photos are saved on the server.")

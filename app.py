import streamlit as st
import pandas as pd

# --- APP TITLE ---
st.set_page_config(page_title="Vibe Coding Starter", page_icon="✨", layout="centered")
st.title("✨ Vibe Coding Starter App")
st.write("Welcome to **Vibe Coding Club**! This is your starter project. Fork it, deploy it, and make it your own.")

# --- FILE UPLOADER ---
st.header("📂 Upload a CSV")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("CSV loaded successfully!")
    st.dataframe(df)

    # Example chart
    st.subheader("📊 Quick Data Preview")
    try:
        st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])
    except:
        st.info("No numeric columns to plot.")

# --- PERSONALIZE SECTION ---
st.header("🎨 Make it Yours")
name = st.text_input("What's your name?")
if name:
    st.write(f"Hi **{name}** 👋 — welcome to your vibe-coded app!")

# --- FOOTER ---
st.markdown("---")
st.caption("Built with ❤️ in Vibe Coding Club")

import streamlit as st
import pandas as pd

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="FuturePath AI Dashboard",
    layout="wide"
)

# =====================================
# FUNCTION: CLEANING & TYPE CONVERSION
# =====================================
def process_dataframe(df):
    """
    Fungsi untuk membersihkan nama kolom dan memastikan tipe data benar.
    """
    # 1. Bersihkan nama kolom
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    
    # 2. Proteksi jika ada sisa Git Conflict di nama kolom
    if any("<<<" in str(col) for col in df.columns):
        st.error("⚠️ Terdeteksi 'Git Merge Conflict' pada file CSV! Harap bersihkan file Anda secara manual.")
        st.stop()

    # 3. Konversi kolom gaji ke angka (PENTING untuk memperbaiki TypeError: agg function failed)
    if "annual_salary_usd" in df.columns:
        # errors='coerce' akan mengubah teks yang bukan angka menjadi NaN agar tidak merusak perhitungan
        df["annual_salary_usd"] = pd.to_numeric(df["annual_salary_usd"], errors='coerce')
        
    return df

# =====================================
# LOAD DATA
# =====================================
# Menggunakan try-except agar jika file tidak ditemukan atau rusak, dashboard tidak blank putih
try:
    df_jobs = pd.read_csv("data/processed/ai_jobs_market_2025_2026_clean.csv")
    df_roles = pd.read_csv("data/processed/it_job_roles_skills_clean.csv")
    df_career = pd.read_csv("data/processed/skill_career_recommendation_clean.csv")

    # Jalankan fungsi pembersihan
    df_jobs = process_dataframe(df_jobs)
    df_roles = process_dataframe(df_roles)
    df_career = process_dataframe(df_career)
    
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    st.stop()

# =====================================
# TITLE
# =====================================
st.title("🚀 FuturePath AI Dashboard")

st.markdown("""
Dashboard interaktif untuk exploratory data analysis (EDA), 
career recommendation insight, dan skill gap analysis.
""")

# =====================================
# SIDEBAR
# =====================================
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Pilih Dashboard",
    [
        "AI Jobs Market",
        "IT Roles & Skills",
        "Career Recommendation"
    ]
)

# =====================================
# DASHBOARD 1: AI JOBS MARKET
# =====================================
if menu == "AI Jobs Market":
    st.header("📊 AI Jobs Market Analysis")

    # SEARCH FOR COLUMN NAMES
    job_title_col = next((col for col in ["job_title", "jobtitle", "job_profession", "profession", "title"] if col in df_jobs.columns), None)

    # METRICS
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Jobs", f"{len(df_jobs):,}")
    with col2:
        val = df_jobs[job_title_col].nunique() if job_title_col else "N/A"
        st.metric("Unique Job Titles", val)
    with col3:
        val = df_jobs["country"].nunique() if "country" in df_jobs.columns else "N/A"
        st.metric("Countries", val)

    st.divider()

    # DATA PREVIEW
    with st.expander("Lihat Dataset Preview"):
        st.dataframe(df_jobs.head(10))

    # VISUALISASI
    c1, c2 = st.columns(2)

    with c1:
        if "experience_level" in df_jobs.columns:
            st.subheader("Experience Level")
            st.bar_chart(df_jobs["experience_level"].value_counts())

    with c2:
        if "job_category" in df_jobs.columns:
            st.subheader("Top 10 Job Categories")
            st.bar_chart(df_jobs["job_category"].value_counts().head(10))

    # SALARY ANALYSIS (Bagian yang tadinya Error)
    if "job_category" in df_jobs.columns and "annual_salary_usd" in df_jobs.columns:
        st.subheader("💰 Average Salary by Job Category (USD)")
        
        # Menghapus data yang kosong (NaN) agar grafik akurat
        salary_df = df_jobs.dropna(subset=["annual_salary_usd"])
        
        salary_by_category = (
            salary_df.groupby("job_category")["annual_salary_usd"]
            .mean()
            .sort_values(ascending=False)
        )
        st.bar_chart(salary_by_category)

    # TOP SKILLS
    if "required_skills" in df_jobs.columns:
        st.subheader("🛠️ Top Required Skills")
        all_skills = df_jobs["required_skills"].fillna("").str.split(r"\s*\|\s*").explode().str.strip()
        top_skills = all_skills[all_skills != ""].value_counts().head(15)
        st.bar_chart(top_skills)

# =====================================
# DASHBOARD 2: IT ROLES
# =====================================
elif menu == "IT Roles & Skills":
    st.header("💻 IT Roles & Skills Analysis")
    st.dataframe(df_roles.head())
    st.subheader("Columns Available")
    st.write(df_roles.columns.tolist())

# =====================================
# DASHBOARD 3: CAREER
# =====================================
elif menu == "Career Recommendation":
    st.header("🎯 Career Recommendation Analysis")
    st.dataframe(df_career.head())
    st.subheader("Columns Available")
    st.write(df_career.columns.tolist())

# =====================================
# FOOTER
# =====================================
st.markdown("---")
st.caption("FuturePath AI Dashboard | Developed by Data Science Team © 2026")
import streamlit as st
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# =========================
# GLOBAL LOGS
# =========================
log = []
report = {}

# =========================
# PAGE CONFIG + STYLE
# =========================
st.set_page_config(page_title="Data Cleaning Tool", layout="wide")

# 🎨 Button Styling
st.markdown("""
    <style>
    .stDownloadButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        border-radius: 10px;
        padding: 10px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# SAFE FILE LOADER
# =========================
def load_file(uploaded_file):
    encodings = ['utf-8', 'latin1', 'cp1252']

    if uploaded_file.name.endswith('.csv'):
        for enc in encodings:
            try:
                df = pd.read_csv(uploaded_file, encoding=enc)
                st.success(f"✅ Loaded with encoding: {enc}")
                return {"sheet1": df}
            except:
                continue
        st.error("❌ Could not read CSV file")
        st.stop()
    else:
        return pd.read_excel(uploaded_file, sheet_name=None)

# =========================
# CLEAN FUNCTIONS
# =========================

def clean_column_names(df):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "", regex=True)
    )

    # Fix empty column names
    new_cols = []
    for i, col in enumerate(df.columns):
        if col == "" or col is None:
            new_cols.append(f"column_{i}")
        else:
            new_cols.append(col)

    df.columns = new_cols
    log.append("✔ Column names standardized")
    return df

def fix_nan_strings(df):
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].replace(["nan", "none", ""], np.nan)
    log.append("✔ Fixed string 'nan'")
    return df

def standardize_text(df):
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip().str.lower()
    log.append("✔ Text standardized")
    return df

def fix_data_types(df):
    for col in df.columns:
        if "id" in col:
            df[col] = df[col].astype(str)
            continue

        temp_col = pd.to_numeric(df[col], errors='coerce')
        if temp_col.notna().sum() > 0:
            df[col] = temp_col

        if "date" in col or "time" in col:
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)

    log.append("✔ Data types fixed")
    return df

def fix_age_column(df):
    if "age" in df.columns:
        df["age"] = pd.to_numeric(df["age"], errors='coerce')
        df["age"].fillna(df["age"].median(), inplace=True)
        df["age"] = df["age"].round().astype(int)
    log.append("✔ Age fixed")
    return df

def fix_salary_column(df):
    if "salary" in df.columns:
        df["salary"] = pd.to_numeric(df["salary"], errors='coerce')
        df["salary"].fillna(df["salary"].median(), inplace=True)
    log.append("✔ Salary cleaned")
    return df

def clean_dates(df):
    if "joining_date" in df.columns:
        df["joining_date"] = pd.to_datetime(df["joining_date"], errors='coerce', dayfirst=True)
        df["joining_date"] = df["joining_date"].dt.strftime('%Y-%m-%d')
    log.append("✔ Dates formatted")
    return df

def handle_missing(df):
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col].fillna(df[col].median(), inplace=True)
        else:
            if not df[col].mode().empty:
                df[col].fillna(df[col].mode()[0], inplace=True)
            else:
                df[col].fillna("unknown", inplace=True)
    log.append("✔ Missing handled")
    return df

def remove_duplicates(df):
    before = len(df)
    df = df.drop_duplicates()
    report['duplicates_removed'] = before - len(df)
    log.append(f"✔ Duplicates removed: {before - len(df)}")
    return df

def fix_invalid_values(df):
    for col in df.select_dtypes(include=['int64', 'float64']).columns:
        df[col] = df[col].apply(lambda x: np.nan if x < 0 else x)
    log.append("✔ Invalid values fixed")
    return df

def handle_outliers(df):
    for col in df.select_dtypes(include=['int64', 'float64']).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        df[col] = np.clip(df[col], Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)
    log.append("✔ Outliers handled")
    return df

def standardize_categories(df):
    if "city" in df.columns:
        df["city"] = df["city"].replace({"mumbay": "mumbai"})
    if "gender" in df.columns:
        df["gender"] = df["gender"].replace({"m": "male", "f": "female"})
    log.append("✔ Categories standardized")
    return df

def remove_noise(df):
    df = df.dropna(axis=1, how='all')
    log.append("✔ Empty columns removed")
    return df

def calculate_quality_score(df):
    total = df.size
    missing = df.isnull().sum().sum()
    return round((1 - missing / total) * 100, 2)

# =========================
# UI
# =========================

st.title("🚀 Automated Data Cleaning Tool")

st.sidebar.header("⚙️ Settings")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file:

    log.clear()
    report.clear()

    sheets = load_file(uploaded_file)
    cleaned_sheets = {}

    for name, df in sheets.items():
        df = clean_column_names(df)
        df = fix_nan_strings(df)
        df = standardize_text(df)
        df = fix_data_types(df)
        df = fix_age_column(df)
        df = fix_salary_column(df)
        df = clean_dates(df)
        df = handle_missing(df)
        df = remove_duplicates(df)
        df = fix_invalid_values(df)
        df = handle_outliers(df)
        df = standardize_categories(df)
        df = remove_noise(df)

        cleaned_sheets[name] = df

    score = np.mean([calculate_quality_score(df) for df in cleaned_sheets.values()])

    col1, col2 = st.columns(2)
    col1.metric("📊 Data Quality Score", f"{score}/100")
    col2.metric("🧹 Duplicates Removed", report.get("duplicates_removed", 0))

    tab1, tab2, tab3 = st.tabs(["📄 Data", "📋 Report", "🧾 Logs"])

    with tab1:
        for name, df in cleaned_sheets.items():
            st.subheader(name)
            st.dataframe(df, use_container_width=True)

    with tab2:
        st.json(report)

    with tab3:
        st.write(log)

    # =========================
    # DOWNLOAD BUTTON (LEFT SIDEBAR)
    # =========================
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Download Cleaned Data")

    output_file = "cleaned_output.xlsx"

    with pd.ExcelWriter(output_file) as writer:
        for name, df in cleaned_sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)

    with open(output_file, "rb") as f:
        st.sidebar.download_button(
            label="⬇️ Download Excel File",
            data=f,
            file_name="cleaned_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

else:
    st.info("👈 Upload a file to start")
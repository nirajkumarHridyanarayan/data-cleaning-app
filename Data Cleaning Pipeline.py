import streamlit as st
import pandas as pd
import numpy as np
import warnings
import csv
warnings.filterwarnings("ignore")

# =========================
# GLOBAL LOGS
# =========================
log = []
report = {}

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Data Cleaning Tool", layout="wide")

# =========================
# SAFE FILE LOADER (FIXED)
# =========================
def load_file(uploaded_file):
    encodings = ['utf-8', 'latin1', 'cp1252']

    if uploaded_file.name.endswith('.csv'):

        for enc in encodings:
            try:
                # 🔥 Detect delimiter
                sample = uploaded_file.read(5000).decode(enc)
                uploaded_file.seek(0)

                delimiter = csv.Sniffer().sniff(sample).delimiter

                df = pd.read_csv(uploaded_file, encoding=enc, delimiter=delimiter)

                # 🚨 STRUCTURE CHECK
                if df.shape[1] < 5:
                    st.warning("⚠️ Detected possible delimiter issue. Trying fallback...")

                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding=enc, delimiter=",")

                st.success(f"✅ Loaded | Encoding: {enc} | Delimiter: '{delimiter}'")
                return {"sheet1": df}, "csv"

            except:
                uploaded_file.seek(0)
                continue

        st.error("❌ Could not correctly parse CSV file")
        st.stop()

    else:
        return pd.read_excel(uploaded_file, sheet_name=None), "excel"

# =========================
# CLEAN FUNCTIONS (SAFE)
# =========================

def clean_column_names(df):
    original_cols = df.columns.tolist()

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "", regex=True)
    )

    # Prevent empty columns
    new_cols = []
    for i, col in enumerate(df.columns):
        if col == "" or col is None:
            new_cols.append(original_cols[i])  # 🔥 KEEP ORIGINAL
        else:
            new_cols.append(col)

    df.columns = new_cols
    log.append("✔ Column names standardized (structure preserved)")
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

    sheets, file_type = load_file(uploaded_file)
    cleaned_sheets = {}

    for name, df in sheets.items():

        # 🚨 FINAL STRUCTURE CHECK
        if df.shape[1] < 5:
            st.error("❌ File structure broken. Please check your file.")
            st.stop()

        df = clean_column_names(df)
        df = fix_nan_strings(df)
        df = standardize_text(df)
        df = fix_data_types(df)
        df = handle_missing(df)
        df = remove_duplicates(df)
        df = remove_noise(df)

        cleaned_sheets[name] = df

    score = np.mean([calculate_quality_score(df) for df in cleaned_sheets.values()])

    col1, col2 = st.columns(2)
    col1.metric("📊 Data Quality Score", f"{score}/100")
    col2.metric("🧹 Duplicates Removed", report.get("duplicates_removed", 0))

    st.divider()

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
    # SMART DOWNLOAD (SAME FORMAT)
    # =========================

    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Download Cleaned Data")

    if file_type == "csv":
        df = list(cleaned_sheets.values())[0]

        csv_data = df.to_csv(index=False).encode('utf-8')

        st.sidebar.download_button(
            "⬇️ Download CSV",
            data=csv_data,
            file_name="cleaned_data.csv",
            mime="text/csv",
            use_container_width=True
        )

    else:
        from io import BytesIO
        buffer = BytesIO()

        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            for name, df in cleaned_sheets.items():
                df.to_excel(writer, sheet_name=name, index=False)

        st.sidebar.download_button(
            "⬇️ Download Excel",
            data=buffer.getvalue(),
            file_name="cleaned_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

else:
    st.info("👈 Upload a file to start")
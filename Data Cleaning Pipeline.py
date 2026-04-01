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
# CLEAN FUNCTIONS
# =========================

def clean_column_names(df):
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "", regex=True)
    )
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

        df[col] = pd.to_numeric(df[col], errors='ignore')

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
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        df[col] = np.clip(df[col], lower, upper)
    log.append("✔ Outliers handled")
    return df

def standardize_categories(df):
    if "city" in df.columns:
        df["city"] = df["city"].replace({"mumbay": "mumbai"})

    if "gender" in df.columns:
        df["gender"] = df["gender"].replace({
            "m": "male", "male": "male",
            "f": "female", "female": "female"
        })

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
# STREAMLIT UI
# =========================

st.set_page_config(page_title="Data Cleaning Tool", layout="wide")

st.title("🚀 Automated Data Cleaning Tool")

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:

    log.clear()
    report.clear()

    # LOAD FILE
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
        sheets = {"sheet1": df}
    else:
        sheets = pd.read_excel(uploaded_file, sheet_name=None)

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

    # DISPLAY
    score = np.mean([calculate_quality_score(df) for df in cleaned_sheets.values()])
    st.metric("📊 Data Quality Score", f"{round(score,2)}/100")

    for name, df in cleaned_sheets.items():
        st.subheader(f"📄 {name}")
        st.dataframe(df.head())

    st.subheader("📋 Report")
    st.json(report)

    st.subheader("🧾 Logs")
    st.write(log)

    # DOWNLOAD
    output_file = "cleaned_output.xlsx"
    with pd.ExcelWriter(output_file) as writer:
        for name, df in cleaned_sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)

    with open(output_file, "rb") as f:
        st.download_button("📥 Download Cleaned Data", f, "cleaned_data.xlsx")
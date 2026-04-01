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
# LOAD FILE
# =========================
def load_file(file_path):
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
            return {"sheet1": df}
        elif file_path.endswith('.xlsx'):
            sheets = pd.read_excel(file_path, sheet_name=None)
            return sheets
        else:
            raise ValueError("Unsupported file format")
    except Exception as e:
        print("❌ Error loading file:", e)
        return None

# =========================
# CLEAN COLUMN NAMES
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

# =========================
# FIX "nan" STRINGS
# =========================
def fix_nan_strings(df):
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].replace(["nan", "none", ""], np.nan)
    log.append("✔ Fixed string 'nan'")
    return df

# =========================
# STANDARDIZE TEXT
# =========================
def standardize_text(df):
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip().str.lower()
    log.append("✔ Text standardized")
    return df

# =========================
# FIX DATA TYPES (SAFE)
# =========================
def fix_data_types(df):
    for col in df.columns:

        # ID should not convert to datetime
        if "id" in col:
            df[col] = df[col].astype(str)
            continue

        df[col] = pd.to_numeric(df[col], errors='ignore')

        if "date" in col or "time" in col:
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)

    log.append("✔ Data types fixed")
    return df

# =========================
# FIX AGE
# =========================
def fix_age_column(df):
    if "age" in df.columns:
        df["age"] = pd.to_numeric(df["age"], errors='coerce')
        median_age = df["age"].median()
        df["age"].fillna(median_age, inplace=True)
        df["age"] = df["age"].round().astype(int)

    log.append("✔ Age fixed (no decimals)")
    return df

# =========================
# FIX SALARY
# =========================
def fix_salary_column(df):
    if "salary" in df.columns:
        df["salary"] = pd.to_numeric(df["salary"], errors='coerce')
        df["salary"].fillna(df["salary"].median(), inplace=True)

    log.append("✔ Salary cleaned")
    return df

# =========================
# CLEAN DATES
# =========================
def clean_dates(df):
    if "joining_date" in df.columns:
        df["joining_date"] = pd.to_datetime(df["joining_date"], errors='coerce', dayfirst=True)
        df["joining_date"] = df["joining_date"].dt.strftime('%Y-%m-%d')

    log.append("✔ Dates formatted")
    return df

# =========================
# HANDLE MISSING
# =========================
def handle_missing(df):
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        else:
            if not df[col].mode().empty:
                df[col] = df[col].fillna(df[col].mode()[0])
            else:
                df[col] = df[col].fillna("unknown")

    log.append("✔ Missing values handled")
    return df

# =========================
# REMOVE DUPLICATES
# =========================
def remove_duplicates(df):
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)

    report['duplicates_removed'] = removed
    log.append(f"✔ Duplicates removed: {removed}")
    return df

# =========================
# FIX INVALID VALUES
# =========================
def fix_invalid_values(df):
    for col in df.select_dtypes(include=['int64', 'float64']).columns:
        df[col] = df[col].apply(lambda x: np.nan if x < 0 else x)
    log.append("✔ Invalid values fixed")
    return df

# =========================
# HANDLE OUTLIERS
# =========================
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

# =========================
# STANDARDIZE CATEGORIES
# =========================
def standardize_categories(df):
    if "city" in df.columns:
        df["city"] = df["city"].replace({
            "mumbay": "mumbai",
            "mumbai": "mumbai",
            "delhi": "delhi"
        })

    if "gender" in df.columns:
        df["gender"] = df["gender"].replace({
            "m": "male",
            "male": "male",
            "f": "female",
            "female": "female"
        })

    log.append("✔ Categories standardized")
    return df

# =========================
# REMOVE NOISE
# =========================
def remove_noise(df):
    df = df.dropna(axis=1, how='all')
    log.append("✔ Empty columns removed")
    return df

# =========================
# QUALITY SCORE
# =========================
def calculate_quality_score(df):
    total = df.size
    missing = df.isnull().sum().sum()
    return round((1 - missing / total) * 100, 2)

# =========================
# MAIN FUNCTION
# =========================
def clean_data(file_path, output_path="cleaned_data.xlsx"):
    global log, report
    log = []
    report = {}

    sheets = load_file(file_path)
    if sheets is None:
        return

    cleaned_sheets = {}

    for name, df in sheets.items():
        print(f"\n🔄 Processing sheet: {name}")

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

    # SAVE FILE
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for name, df in cleaned_sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)

    print(f"\n✅ Cleaned file saved: {output_path}")

    # SCORE
    scores = [calculate_quality_score(df) for df in cleaned_sheets.values()]
    final_score = round(sum(scores) / len(scores), 2)

    print("\n===== DATA CLEANING REPORT =====")
    print(f"📊 Data Quality Score: {final_score}/100")
    print("📋 Report:", report)
    print("🧾 Log:", log)

    return cleaned_sheets


# =========================
# RUN
# =========================
if __name__ == "__main__":
    clean_data("aug_test.csv")   # change file name if needed
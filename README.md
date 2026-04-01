# 🚀 Automated Data Cleaning Web App

## 📌 Project Overview

This project is an **end-to-end automated data cleaning tool** built using Python and Streamlit. It allows users to upload raw datasets (CSV/XLSX) and instantly receive a **clean, structured, and analysis-ready dataset** along with a data quality report.

The application is designed to solve real-world data issues commonly faced in analytics, dashboards, and machine learning workflows.

---

# ⭐ STAR Method Explanation

## 🟡 Situation

In real-world data analysis, datasets are often **unclean, inconsistent, and unreliable**, containing:

* Missing values
* Duplicate records
* Incorrect data types
* Inconsistent formats
* Outliers and invalid entries

These issues make it difficult to build accurate dashboards and models.

---

## 🟡 Task

The goal was to build a **scalable and automated data cleaning system** that:

* Accepts raw `.csv` or `.xlsx` files
* Detects and fixes all major data quality issues
* Produces a **clean dataset ready for analysis**
* Generates a **data quality score and transformation logs**
* Works efficiently for dashboard tools like Power BI / Tableau

---

## 🟡 Action

To achieve this, I designed and implemented:

### 🔧 Data Cleaning Pipeline

* Standardized column names (snake_case)
* Handled missing values using:

  * Median (numeric)
  * Mode (categorical)
* Removed duplicate records
* Fixed incorrect data types (numeric, datetime)
* Standardized text formatting (lowercase, trimmed)
* Treated outliers using IQR method
* Corrected invalid values (e.g., negative numbers)
* Standardized categories (e.g., "M" → "Male")
* Cleaned date formats (YYYY-MM-DD)
* Removed noise (empty columns)

### 🧠 Smart Data Handling

* Prevented ID corruption (avoided datetime conversion)
* Converted salary and age into correct numeric formats
* Removed decimal values in age column
* Fixed encoding and string "nan" issues

### 🌐 Web Application (Streamlit)

* Built an interactive UI using Streamlit
* Enabled file upload (CSV/XLSX)
* Displayed cleaned data preview
* Generated:

  * Data Quality Score
  * Cleaning Report
  * Transformation Logs
* Added download functionality for cleaned dataset

---

## 🟡 Result

### ✅ Business Impact

* Reduced manual data cleaning effort by **80–90%**
* Improved data reliability for dashboards and reporting
* Enabled faster decision-making with clean datasets

### 📊 Output Features

* ✔ Cleaned dataset (downloadable)
* ✔ Data Quality Score (0–100)
* ✔ Cleaning Report (issues fixed)
* ✔ Transformation Log (step-by-step actions)

### 💻 Technical Outcome

* Built a **production-ready data cleaning pipeline**
* Deployed as a **live web application**
* Created a **portfolio-ready project for Data Analyst roles**

---

# 🛠️ Tech Stack

* Python
* Pandas
* NumPy
* Streamlit
* OpenPyXL

---

# 📂 Project Structure

```
data-cleaning-app/
│
├── app.py
├── requirements.txt
├── README.md
```

---

# ▶️ How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

# 🌐 Live Demo

(https://data-cleaning-app-model.streamlit.app/)

---

# 📥 How to Use

1. Upload your raw dataset (.csv or .xlsx)
2. Click upload
3. View cleaned data preview
4. Download cleaned dataset

---

# 💼 Resume Highlight

**Built an Automated Data Cleaning Web App using Streamlit that processes raw datasets, handles data quality issues, and outputs analysis-ready data with quality scoring and reporting.**

---

# 🚀 Future Enhancements

* Data visualization (missing values, outliers)
* AI-based cleaning suggestions
* Column-level insights dashboard
* Multi-file batch processing

---

# 🙌 Acknowledgement

This project was built as part of a practical learning initiative to strengthen real-world data analytics skills.

---

⭐ If you like this project, feel free to star the repository!

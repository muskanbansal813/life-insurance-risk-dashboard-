import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# ----------------- LOGIN SETUP -----------------
USERNAME = "muskan"
PASSWORD = "Muskan@2025"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login to Access Dashboard")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

    st.stop()

# --------------------------
# Page config
st.set_page_config(page_title="Life Insurance Dashboard", layout="centered")

# Enhanced header with color, size, and alignment
st.markdown("""
    <h1 style='text-align: center; color: #1F4E79; font-size: 44px;'>
        📊 Life Insurance Risk Insights
    </h1>
    <p style='text-align: center; font-size: 18px; color: #4B4B4B;'>
        Analyze trends in applicant risk profiles, BMI, age groups, and product categories.
    </p>
    <hr style='border:1px solid #ccc;'>
""", unsafe_allow_html=True)

# Add some vertical space
st.markdown("<br>", unsafe_allow_html=True)

# Section header
st.markdown("""
    <h1 style='text-align: center; color: #1F4E79; font-size: 36px;'>
        🩺 Life Insurance Risk Insights Dashboard
    </h1>
""", unsafe_allow_html=True)

#---------------------Tooltip------------------

st.markdown("""
<div style='
    background-color: #f9f9f9;
    border-left: 6px solid #1F4E79;
    padding: 16px;
    border-radius: 6px;
    margin-bottom: 30px;
'>
    <h4 style='margin-top: 0;'>📌 What is <i>Response Score</i>?</h4>
    <p style='font-size: 15px; line-height: 1.6; color: #333;'>
        The <b>Response Score</b> (also known as <b>Underwriting Risk Score</b>) ranges from <b>1 to 8</b>, where:<br>
        • <b>1</b> = Low risk (healthier, safer to insure)<br>
        • <b>8</b> = High risk (more health concerns, costlier to insure)<br><br>
        This score helps insurers decide on premium rates and approval chances.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------
# Load + Denormalize Data
@st.cache_data
def load_data():
    df = pd.read_csv("insurance data.csv")

    # Denormalize
    df["Actual_Age"] = (df["Ins_Age"] * 72 + 18).round(0)
    df["Actual_BMI"] = (df["BMI"] * 40 + 15).round(1)
    df["Actual_Weight"] = (df["Wt"] * 80 + 40).round(1)

    # BMI Category
    def bmi_category(bmi):
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "Overweight"
        elif bmi < 35:
            return "Obese Class I"
        elif bmi < 40:
            return "Obese Class II"
        else:
            return "Obese Class III"

    df["BMI_Category"] = df["Actual_BMI"].apply(bmi_category)

    # Age Group
    def age_bin(age):
        if age <= 35:
            return "25–35"
        elif age <= 45:
            return "36–45"
        elif age <= 55:
            return "46–55"
        elif age <= 65:
            return "56–65"
        elif age <= 75:
            return "66–75"
        else:
            return "76+"

    df["Age_Group"] = df["Actual_Age"].apply(age_bin)

    return df

df = load_data()

# --------------------------
# Sidebar Filters with "All"
st.sidebar.header("🔎 Filter Options")

bmi_options = ["All"] + sorted(df["BMI_Category"].unique())
age_options = ["All"] + sorted(df["Age_Group"].unique())
product_options = ["All"] + sorted(df["Product_Info_2"].unique())
response_options = ["All"] + sorted(df["Response"].unique())

bmi_filter = st.sidebar.selectbox("BMI Category", bmi_options)
age_filter = st.sidebar.selectbox("Age Group", age_options)
product_filter = st.sidebar.selectbox("Product Info 2", product_options)
response_filter = st.sidebar.selectbox("Response Score", response_options)

df_filtered = df.copy()
if bmi_filter != "All":
    df_filtered = df_filtered[df_filtered["BMI_Category"] == bmi_filter]
if age_filter != "All":
    df_filtered = df_filtered[df_filtered["Age_Group"] == age_filter]
if product_filter != "All":
    df_filtered = df_filtered[df_filtered["Product_Info_2"] == product_filter]
if response_filter != "All":
    df_filtered = df_filtered[df_filtered["Response"] == response_filter]

# --------------------------
# Optional table view
if st.checkbox("📋 Show Filtered Data"):
    st.dataframe(df_filtered.head(20))

# --------------------------
# Chart 1: Applicants Proportion by Risk Score
st.subheader("1️⃣ Applicants Proportion by Risk Score")
count = df_filtered["Response"].value_counts(normalize=True).sort_index()
percent = (count * 100).round(2)
fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(x=percent.index, y=percent.values, ax=ax, palette="Blues_d")
ax.set_ylabel("Percentage (%)")
ax.set_xlabel("Response Score (1–8)")
st.pyplot(fig)

# Chart 2: Applicants Distribution by BMI Category
st.subheader("2️⃣ Applicants Distribution by BMI Category")
bmi_dist = df_filtered["BMI_Category"].value_counts(normalize=True)
bmi_percent = (bmi_dist * 100).round(2).reindex(
    ["Underweight", "Normal", "Overweight", "Obese Class I", "Obese Class II", "Obese Class III"]
)
fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(x=bmi_percent.index, y=bmi_percent.values, palette="Set2", ax=ax)
ax.set_ylabel("Percentage (%)")
ax.set_xlabel("BMI Category")
ax.tick_params(axis="x", rotation=30)
st.pyplot(fig)

# Chart 3: BMI vs Response
st.subheader("3️⃣ BMI vs Response (Boxplot)")
fig, ax = plt.subplots(figsize=(6, 4))
sns.boxplot(x="Response", y="Actual_BMI", data=df_filtered, ax=ax, palette="pastel")
st.pyplot(fig)

# Chart 4: Applicants Count by Age Group
st.subheader("4️⃣ Applicants by Age Group")
age_counts = df_filtered["Age_Group"].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(x=age_counts.index, y=age_counts.values, palette="coolwarm", ax=ax)
ax.set_ylabel("Applicant Count")
st.pyplot(fig)

# Chart 5: Average Response by Product Info 2
st.subheader("5️⃣ Average Risk Score by Product Info 2")
response_mean = df_filtered.groupby("Product_Info_2")["Response"].mean()
fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(x=response_mean.index, y=response_mean.values, ax=ax, palette="viridis")
ax.set_ylabel("Avg Response Score")
ax.set_xlabel("Product Info 2")
st.pyplot(fig)

# Chart 6: BMI vs Age (Hexbin - clearer view)
st.subheader("6️⃣ Average BMI by Age Group")
bmi_avg_age = df_filtered.groupby("Age_Group")["Actual_BMI"].mean().reindex(["25–35", "36–45", "46–55", "56–65", "66–75", "76+"])
fig, ax = plt.subplots(figsize=(6, 4))
bmi_avg_age.plot(kind="line", marker="o", ax=ax, color="#1f77b4")
ax.set_ylabel("Average BMI")
ax.set_xlabel("Age Group")
st.pyplot(fig)



# Chart 7: Response Score by BMI Category
st.subheader("7️⃣ Response Score by BMI Category")
fig, ax = plt.subplots(figsize=(6, 4))
sns.boxplot(x="BMI_Category", y="Response", data=df_filtered, palette="Set1", ax=ax)
ax.tick_params(axis="x", rotation=30)
st.pyplot(fig)

# Chart 8: Applicants Count by Product Info 2
st.subheader("8️⃣ Applicants by Product Info 2")
prod_counts = df_filtered["Product_Info_2"].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(x=prod_counts.index, y=prod_counts.values, palette="Set3", ax=ax)
ax.set_ylabel("Applicants")
ax.set_xlabel("Product Info 2")
st.pyplot(fig)

# Chart 9: Average BMI by Age Group
st.subheader("9️⃣ Average BMI by Age Group")
bmi_by_age = df_filtered.groupby("Age_Group")["Actual_BMI"].mean().reindex(
    ["25–35", "36–45", "46–55", "56–65", "66–75", "76+"]
)
fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(x=bmi_by_age.index, y=bmi_by_age.values, ax=ax, palette="cividis")
ax.set_ylabel("Average BMI")
st.pyplot(fig)

# Chart 10: Heatmap of Response vs BMI Category & Age Group
st.subheader("🔟 Heatmap: Response vs Age Group & BMI Category")
pivot = pd.pivot_table(df_filtered, values="Response", index="BMI_Category", columns="Age_Group", aggfunc="mean")
fig, ax = plt.subplots(figsize=(6, 4))
sns.heatmap(pivot, annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig)


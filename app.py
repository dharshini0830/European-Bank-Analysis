import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="European Bank Customer Churn Analytics",
    page_icon="🏦",
    layout="wide"
)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.title("🏦 European Bank Customer Churn Analytics")
st.markdown(
    """
    **Segmentation-driven analytics dashboard for understanding
    customer churn across geography, demographics and financial profiles.**
    """
)

# ---------------------------------------------------------
# LOAD DATASET
# ---------------------------------------------------------

@st.cache_data
def load_data():

    file_path = "European_Bank_cleaned.csv.xlsx"

    df = pd.read_excel(file_path)

    return df


df = load_data()

# ---------------------------------------------------------
# DATA VALIDATION
# ---------------------------------------------------------

required_columns = [
    "Year",
    "CustomerId",
    "Surname",
    "CreditScore",
    "Geography",
    "Gender",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
    "Exited"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:

    st.error(
        f"Missing columns in dataset: {missing_columns}"
    )

    st.stop()

# ---------------------------------------------------------
# DATA CLEANING
# ---------------------------------------------------------

df = df.copy()

# Remove duplicate customers
df = df.drop_duplicates(subset="CustomerId")

# Remove unnecessary analytical field
# Surname is retained in original data but not used for analysis

# Make sure numerical fields are numeric
numeric_columns = [
    "CreditScore",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
    "Exited"
]

for col in numeric_columns:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# Remove rows with missing target
df = df.dropna(subset=["Exited"])

# ---------------------------------------------------------
# SEGMENTATION
# ---------------------------------------------------------

# AGE SEGMENT

def age_group(age):

    if age < 30:
        return "<30"

    elif age <= 45:
        return "30–45"

    elif age <= 60:
        return "46–60"

    else:
        return "60+"


df["AgeGroup"] = df["Age"].apply(age_group)


# CREDIT SCORE SEGMENT

def credit_group(score):

    if score < 580:
        return "Low"

    elif score < 700:
        return "Medium"

    else:
        return "High"


df["CreditScoreBand"] = df["CreditScore"].apply(
    credit_group
)


# TENURE SEGMENT

def tenure_group(tenure):

    if tenure <= 3:
        return "New"

    elif tenure <= 7:
        return "Mid-term"

    else:
        return "Long-term"


df["TenureGroup"] = df["Tenure"].apply(
    tenure_group
)


# BALANCE SEGMENT

def balance_group(balance):

    if balance == 0:
        return "Zero-balance"

    elif balance < 100000:
        return "Low-balance"

    else:
        return "High-balance"


df["BalanceSegment"] = df["Balance"].apply(
    balance_group
)


# ---------------------------------------------------------
# CHURN LABEL
# ---------------------------------------------------------

df["Churn"] = df["Exited"].map(
    {
        0: "Retained",
        1: "Churned"
    }
)

# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------

st.sidebar.header("🔎 Segment Filters")

geography_filter = st.sidebar.multiselect(
    "Geography",
    options=sorted(df["Geography"].dropna().unique()),
    default=sorted(df["Geography"].dropna().unique())
)

gender_filter = st.sidebar.multiselect(
    "Gender",
    options=sorted(df["Gender"].dropna().unique()),
    default=sorted(df["Gender"].dropna().unique())
)

age_filter = st.sidebar.multiselect(
    "Age Group",
    options=sorted(df["AgeGroup"].unique()),
    default=sorted(df["AgeGroup"].unique())
)

tenure_filter = st.sidebar.multiselect(
    "Tenure Group",
    options=sorted(df["TenureGroup"].unique()),
    default=sorted(df["TenureGroup"].unique())
)

credit_filter = st.sidebar.multiselect(
    "Credit Score",
    options=sorted(df["CreditScoreBand"].unique()),
    default=sorted(df["CreditScoreBand"].unique())
)

balance_filter = st.sidebar.multiselect(
    "Balance Segment",
    options=sorted(df["BalanceSegment"].unique()),
    default=sorted(df["BalanceSegment"].unique())
)

# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------

filtered_df = df[
    (df["Geography"].isin(geography_filter)) &
    (df["Gender"].isin(gender_filter)) &
    (df["AgeGroup"].isin(age_filter)) &
    (df["TenureGroup"].isin(tenure_filter)) &
    (df["CreditScoreBand"].isin(credit_filter)) &
    (df["BalanceSegment"].isin(balance_filter))
]

# ---------------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------------

total_customers = len(filtered_df)

churned_customers = filtered_df["Exited"].sum()

if total_customers > 0:

    churn_rate = (
        churned_customers /
        total_customers
    ) * 100

else:

    churn_rate = 0


retained_customers = (
    total_customers -
    churned_customers
)

# High-value customers
high_value = filtered_df[
    filtered_df["BalanceSegment"] == "High-balance"
]

if len(high_value) > 0:

    high_value_churn_rate = (
        high_value["Exited"].mean()
    ) * 100

else:

    high_value_churn_rate = 0


# Inactive customers
inactive_customers = filtered_df[
    filtered_df["IsActiveMember"] == 0
]

if len(inactive_customers) > 0:

    inactive_churn_rate = (
        inactive_customers["Exited"].mean()
    ) * 100

else:

    inactive_churn_rate = 0

# ---------------------------------------------------------
# KPI DISPLAY
# ---------------------------------------------------------

st.header("📊 Overall Churn Summary")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Customers",
    f"{total_customers:,}"
)

col2.metric(
    "Churned Customers",
    f"{int(churned_customers):,}"
)

col3.metric(
    "Overall Churn Rate",
    f"{churn_rate:.2f}%"
)

col4.metric(
    "High-Value Churn Rate",
    f"{high_value_churn_rate:.2f}%"
)

col5.metric(
    "Inactive Churn Rate",
    f"{inactive_churn_rate:.2f}%"
)

st.divider()

# ---------------------------------------------------------
# CHART 1 — CHURN DISTRIBUTION
# ---------------------------------------------------------

st.header("📌 Churn Distribution")

churn_counts = (
    filtered_df["Churn"]
    .value_counts()
    .reset_index()
)

churn_counts.columns = [
    "Customer Status",
    "Customers"
]

fig1 = px.pie(
    churn_counts,
    names="Customer Status",
    values="Customers",
    hole=0.45,
    title="Retained vs Churned Customers"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# ---------------------------------------------------------
# CHART 2 — GEOGRAPHY
# ---------------------------------------------------------

st.header("🌍 Geography-wise Churn Analysis")

geo_analysis = (
    filtered_df
    .groupby("Geography")
    .agg(
        Customers=("CustomerId", "count"),
        Churned=("Exited", "sum"),
        Churn_Rate=("Exited", "mean")
    )
    .reset_index()
)

geo_analysis["Churn_Rate"] *= 100

fig2 = px.bar(
    geo_analysis,
    x="Geography",
    y="Churn_Rate",
    text="Churn_Rate",
    title="Churn Rate by Geography",
    labels={
        "Churn_Rate": "Churn Rate (%)"
    }
)

fig2.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.dataframe(
    geo_analysis,
    use_container_width=True
)

# ---------------------------------------------------------
# CHART 3 — AGE GROUP
# ---------------------------------------------------------

st.header("👥 Age-wise Churn Comparison")

age_analysis = (
    filtered_df
    .groupby("AgeGroup")
    .agg(
        Customers=("CustomerId", "count"),
        Churned=("Exited", "sum"),
        Churn_Rate=("Exited", "mean")
    )
    .reset_index()
)

age_analysis["Churn_Rate"] *= 100

age_order = [
    "<30",
    "30–45",
    "46–60",
    "60+"
]

age_analysis["AgeGroup"] = pd.Categorical(
    age_analysis["AgeGroup"],
    categories=age_order,
    ordered=True
)

age_analysis = age_analysis.sort_values(
    "AgeGroup"
)

fig3 = px.bar(
    age_analysis,
    x="AgeGroup",
    y="Churn_Rate",
    text="Churn_Rate",
    title="Churn Rate by Age Group",
    labels={
        "Churn_Rate": "Churn Rate (%)"
    }
)

fig3.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# ---------------------------------------------------------
# CHART 4 — TENURE
# ---------------------------------------------------------

st.header("⏳ Tenure-wise Churn Comparison")

tenure_analysis = (
    filtered_df
    .groupby("TenureGroup")
    .agg(
        Customers=("CustomerId", "count"),
        Churned=("Exited", "sum"),
        Churn_Rate=("Exited", "mean")
    )
    .reset_index()
)

tenure_analysis["Churn_Rate"] *= 100

tenure_order = [
    "New",
    "Mid-term",
    "Long-term"
]

tenure_analysis["TenureGroup"] = pd.Categorical(
    tenure_analysis["TenureGroup"],
    categories=tenure_order,
    ordered=True
)

tenure_analysis = tenure_analysis.sort_values(
    "TenureGroup"
)

fig4 = px.bar(
    tenure_analysis,
    x="TenureGroup",
    y="Churn_Rate",
    text="Churn_Rate",
    title="Churn Rate by Tenure Group",
    labels={
        "Churn_Rate": "Churn Rate (%)"
    }
)

fig4.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# ---------------------------------------------------------
# CHART 5 — CREDIT SCORE
# ---------------------------------------------------------

st.header("💳 Credit Score Churn Analysis")

credit_analysis = (
    filtered_df
    .groupby("CreditScoreBand")
    .agg(
        Customers=("CustomerId", "count"),
        Churned=("Exited", "sum"),
        Churn_Rate=("Exited", "mean")
    )
    .reset_index()
)

credit_analysis["Churn_Rate"] *= 100

fig5 = px.bar(
    credit_analysis,
    x="CreditScoreBand",
    y="Churn_Rate",
    text="Churn_Rate",
    title="Churn Rate by Credit Score Band",
    labels={
        "Churn_Rate": "Churn Rate (%)"
    }
)

fig5.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

# ---------------------------------------------------------
# CHART 6 — BALANCE SEGMENT
# ---------------------------------------------------------

st.header("💰 Balance Segment Analysis")

balance_analysis = (
    filtered_df
    .groupby("BalanceSegment")
    .agg(
        Customers=("CustomerId", "count"),
        Churned=("Exited", "sum"),
        Churn_Rate=("Exited", "mean"),
        Total_Balance=("Balance", "sum")
    )
    .reset_index()
)

balance_analysis["Churn_Rate"] *= 100

fig6 = px.bar(
    balance_analysis,
    x="BalanceSegment",
    y="Churn_Rate",
    text="Churn_Rate",
    title="Churn Rate by Balance Segment",
    labels={
        "Churn_Rate": "Churn Rate (%)"
    }
)

fig6.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

# ---------------------------------------------------------
# CHART 7 — GENDER
# ---------------------------------------------------------

st.header("⚥ Gender-based Churn Analysis")

gender_analysis = (
    filtered_df
    .groupby("Gender")
    .agg(
        Customers=("CustomerId", "count"),
        Churned=("Exited", "sum"),
        Churn_Rate=("Exited", "mean")
    )
    .reset_index()
)

gender_analysis["Churn_Rate"] *= 100

fig7 = px.bar(
    gender_analysis,
    x="Gender",
    y="Churn_Rate",
    text="Churn_Rate",
    title="Churn Rate by Gender",
    labels={
        "Churn_Rate": "Churn Rate (%)"
    }
)

fig7.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

st.plotly_chart(
    fig7,
    use_container_width=True
)

# ---------------------------------------------------------
# CHART 8 — ACTIVE MEMBER
# ---------------------------------------------------------

st.header("📱 Engagement vs Churn")

activity_analysis = (
    filtered_df
    .groupby("IsActiveMember")
    .agg(
        Customers=("CustomerId", "count"),
        Churned=("Exited", "sum"),
        Churn_Rate=("Exited", "mean")
    )
    .reset_index()
)

activity_analysis["Member_Status"] = (
    activity_analysis["IsActiveMember"]
    .map(
        {
            0: "Inactive",
            1: "Active"
        }
    )
)

activity_analysis["Churn_Rate"] *= 100

fig8 = px.bar(
    activity_analysis,
    x="Member_Status",
    y="Churn_Rate",
    text="Churn_Rate",
    title="Churn Rate by Member Activity",
    labels={
        "Churn_Rate": "Churn Rate (%)"
    }
)

fig8.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

st.plotly_chart(
    fig8,
    use_container_width=True
)

# ---------------------------------------------------------
# CHART 9 — NUMBER OF PRODUCTS
# ---------------------------------------------------------

st.header("🏦 Product Usage vs Churn")

product_analysis = (
    filtered_df
    .groupby("NumOfProducts")
    .agg(
        Customers=("CustomerId", "count"),
        Churned=("Exited", "sum"),
        Churn_Rate=("Exited", "mean")
    )
    .reset_index()
)

product_analysis["Churn_Rate"] *= 100

fig9 = px.bar(
    product_analysis,
    x="NumOfProducts",
    y="Churn_Rate",
    text="Churn_Rate",
    title="Churn Rate by Number of Products",
    labels={
        "Churn_Rate": "Churn Rate (%)"
    }
)

fig9.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside"
)

st.plotly_chart(
    fig9,
    use_container_width=True
)

# ---------------------------------------------------------
# HIGH VALUE CUSTOMER EXPLORER
# ---------------------------------------------------------

st.header("💎 High-Value Customer Churn Explorer")

high_value_df = filtered_df[
    filtered_df["Balance"] >=
    filtered_df["Balance"].quantile(0.75)
]

st.write(
    f"High-value customers are defined as customers "
    f"whose balance is in the top 25% of the selected data."
)

hv_col1, hv_col2, hv_col3 = st.columns(3)

hv_col1.metric(
    "High-Value Customers",
    f"{len(high_value_df):,}"
)

hv_col2.metric(
    "High-Value Churners",
    f"{int(high_value_df['Exited'].sum()):,}"
)

hv_col3.metric(
    "High-Value Churn Rate",
    f"{high_value_df['Exited'].mean() * 100:.2f}%"
)

# ---------------------------------------------------------
# HIGH VALUE GEOGRAPHY
# ---------------------------------------------------------

if len(high_value_df) > 0:

    hv_geo = (
        high_value_df
        .groupby("Geography")
        .agg(
            Customers=("CustomerId", "count"),
            Churned=("Exited", "sum"),
            Churn_Rate=("Exited", "mean"),
            Balance=("Balance", "sum")
        )
        .reset_index()
    )

    hv_geo["Churn_Rate"] *= 100

    fig10 = px.bar(
        hv_geo,
        x="Geography",
        y="Churn_Rate",
        text="Churn_Rate",
        title="High-Value Customer Churn by Geography",
        labels={
            "Churn_Rate": "Churn Rate (%)"
        }
    )

    fig10.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    st.plotly_chart(
        fig10,
        use_container_width=True
    )

# ---------------------------------------------------------
# FINANCIAL RISK
# ---------------------------------------------------------

st.header("💵 Financial Risk from Churn")

churned_df = filtered_df[
    filtered_df["Exited"] == 1
]

total_churned_balance = churned_df["Balance"].sum()

average_churned_balance = (
    churned_df["Balance"].mean()
    if len(churned_df) > 0
    else 0
)

average_churned_salary = (
    churned_df["EstimatedSalary"].mean()
    if len(churned_df) > 0
    else 0
)

risk_col1, risk_col2, risk_col3 = st.columns(3)

risk_col1.metric(
    "Balance of Churned Customers",
    f"€{total_churned_balance:,.0f}"
)

risk_col2.metric(
    "Average Churner Balance",
    f"€{average_churned_balance:,.0f}"
)

risk_col3.metric(
    "Average Churner Salary",
    f"€{average_churned_salary:,.0f}"
)

# ---------------------------------------------------------
# GEOGRAPHY + AGE INTERACTION
# ---------------------------------------------------------

st.header("🌍 Geography × Age Interaction")

interaction = (
    filtered_df
    .groupby(
        ["Geography", "AgeGroup"]
    )
    .agg(
        Customers=("CustomerId", "count"),
        Churned=("Exited", "sum"),
        Churn_Rate=("Exited", "mean")
    )
    .reset_index()
)

interaction["Churn_Rate"] *= 100

fig11 = px.density_heatmap(
    interaction,
    x="AgeGroup",
    y="Geography",
    z="Churn_Rate",
    text_auto=".2f",
    title="Churn Rate: Geography × Age Group",
    labels={
        "Churn_Rate": "Churn Rate (%)"
    }
)

st.plotly_chart(
    fig11,
    use_container_width=True
)

# ---------------------------------------------------------
# CUSTOMER DATA
# ---------------------------------------------------------

st.header("📋 Filtered Customer Data")

display_columns = [
    "CustomerId",
    "Geography",
    "Gender",
    "Age",
    "AgeGroup",
    "CreditScore",
    "CreditScoreBand",
    "Tenure",
    "TenureGroup",
    "Balance",
    "BalanceSegment",
    "NumOfProducts",
    "IsActiveMember",
    "EstimatedSalary",
    "Churn"
]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True
)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "European Bank Customer Churn Analytics | "
    "Segmentation-driven banking analytics project"
)
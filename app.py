from pathlib import Path

import pandas as pd
import plotly.express as px
from flask import Flask, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "European_Bank_cleaned.csv.xlsx"
app = Flask(__name__)


def age_group(age):
    if age < 30:
        return "<30"
    if age <= 45:
        return "30-45"
    if age <= 60:
        return "46-60"
    return "60+"


def credit_group(score):
    if score < 580:
        return "Low"
    if score < 700:
        return "Medium"
    return "High"


def tenure_group(tenure):
    if tenure <= 3:
        return "New"
    if tenure <= 7:
        return "Mid-term"
    return "Long-term"


def balance_group(balance):
    if balance == 0:
        return "Zero-balance"
    if balance < 100000:
        return "Low-balance"
    return "High-balance"


def load_data():
    data = pd.read_excel(DATA_FILE).drop_duplicates(subset="CustomerId").copy()
    numeric_columns = [
        "CreditScore", "Age", "Tenure", "Balance", "NumOfProducts",
        "HasCrCard", "IsActiveMember", "EstimatedSalary", "Exited",
    ]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.dropna(subset=["Exited"])
    data["AgeGroup"] = data["Age"].apply(age_group)
    data["CreditScoreBand"] = data["CreditScore"].apply(credit_group)
    data["TenureGroup"] = data["Tenure"].apply(tenure_group)
    data["BalanceSegment"] = data["Balance"].apply(balance_group)
    data["Churn"] = data["Exited"].map({0: "Retained", 1: "Churned"})
    return data


DATA = load_data()
FILTERS = {
    "geography": ("Geography", "Geography"),
    "gender": ("Gender", "Gender"),
    "age": ("AgeGroup", "Age Group"),
    "tenure": ("TenureGroup", "Tenure Group"),
    "credit": ("CreditScoreBand", "Credit Score"),
    "balance": ("BalanceSegment", "Balance Segment"),
}


def selected_filters():
    selected = {}
    for key, (column, _) in FILTERS.items():
        values = request.args.getlist(key)
        selected[key] = values or sorted(DATA[column].dropna().astype(str).unique())
    return selected


def chart_html(figure):
    return figure.to_html(full_html=False, include_plotlyjs=False, config={"displayModeBar": False})


def rate_chart(data, group, title, order=None):
    if data.empty:
        return ""
    analysis = data.groupby(group).agg(
        Customers=("CustomerId", "count"),
        Churned=("Exited", "sum"),
        Churn_Rate=("Exited", "mean"),
    ).reset_index()
    analysis["Churn_Rate"] *= 100
    if order:
        analysis[group] = pd.Categorical(analysis[group], categories=order, ordered=True)
        analysis = analysis.sort_values(group)
    figure = px.bar(analysis, x=group, y="Churn_Rate", text="Churn_Rate", title=title,
                    labels={"Churn_Rate": "Churn Rate (%)"})
    figure.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    return chart_html(figure)


@app.get("/")
def dashboard():
    selected = selected_filters()
    filtered = DATA.copy()
    for key, (column, _) in FILTERS.items():
        filtered = filtered[filtered[column].astype(str).isin(selected[key])]

    total = len(filtered)
    churned = int(filtered["Exited"].sum()) if total else 0
    high_value = filtered[filtered["BalanceSegment"] == "High-balance"]
    inactive = filtered[filtered["IsActiveMember"] == 0]
    churn_rate = (churned / total * 100) if total else 0
    high_value_rate = high_value["Exited"].mean() * 100 if len(high_value) else 0
    inactive_rate = inactive["Exited"].mean() * 100 if len(inactive) else 0

    churn_counts = filtered["Churn"].value_counts().rename_axis("Status").reset_index(name="Customers")
    pie = px.pie(churn_counts, names="Status", values="Customers", hole=0.45,
                 title="Retained vs Churned Customers")
    charts = {
        "churn": chart_html(pie),
        "geography": rate_chart(filtered, "Geography", "Churn Rate by Geography"),
        "age": rate_chart(filtered, "AgeGroup", "Churn Rate by Age Group", ["<30", "30-45", "46-60", "60+"]),
        "tenure": rate_chart(filtered, "TenureGroup", "Churn Rate by Tenure Group", ["New", "Mid-term", "Long-term"]),
        "credit": rate_chart(filtered, "CreditScoreBand", "Churn Rate by Credit Score Band"),
        "balance": rate_chart(filtered, "BalanceSegment", "Churn Rate by Balance Segment"),
        "gender": rate_chart(filtered, "Gender", "Churn Rate by Gender"),
        "activity": rate_chart(filtered.assign(Member_Status=filtered["IsActiveMember"].map({0: "Inactive", 1: "Active"})), "Member_Status", "Churn Rate by Member Activity"),
        "products": rate_chart(filtered, "NumOfProducts", "Churn Rate by Number of Products"),
    }

    high_value_df = filtered[filtered["Balance"] >= filtered["Balance"].quantile(0.75)] if total else filtered
    high_value_geo = rate_chart(high_value_df, "Geography", "High-Value Customer Churn by Geography")
    churned_df = filtered[filtered["Exited"] == 1]
    interaction = filtered.groupby(["Geography", "AgeGroup"]).agg(
        Customers=("CustomerId", "count"), Churned=("Exited", "sum"), Churn_Rate=("Exited", "mean")
    ).reset_index()
    interaction["Churn_Rate"] *= 100
    heatmap = px.density_heatmap(interaction, x="AgeGroup", y="Geography", z="Churn_Rate",
                                 title="Churn Rate: Geography x Age Group", labels={"Churn_Rate": "Churn Rate (%)"})

    display_columns = ["CustomerId", "Geography", "Gender", "Age", "AgeGroup", "CreditScore",
                       "CreditScoreBand", "Tenure", "TenureGroup", "Balance", "BalanceSegment",
                       "NumOfProducts", "IsActiveMember", "EstimatedSalary", "Churn"]
    table = filtered[display_columns].head(500).to_html(index=False, classes="data-table", border=0)
    options = {key: {"label": label, "values": sorted(DATA[column].dropna().astype(str).unique())}
               for key, (column, label) in FILTERS.items()}
    return render_template(
        "index.html", selected=selected, options=options, charts=charts, high_value_geo=high_value_geo,
        heatmap=chart_html(heatmap), table=table, total=total, churned=churned,
        churn_rate=churn_rate, high_value_rate=high_value_rate, inactive_rate=inactive_rate,
        high_value_count=len(high_value_df), high_value_churners=int(high_value_df["Exited"].sum()) if len(high_value_df) else 0,
        high_value_balance_rate=high_value_df["Exited"].mean() * 100 if len(high_value_df) else 0,
        total_churned_balance=churned_df["Balance"].sum(), average_churned_balance=churned_df["Balance"].mean() if len(churned_df) else 0,
        average_churned_salary=churned_df["EstimatedSalary"].mean() if len(churned_df) else 0,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# European Bank Customer Churn Analytics

## Project Description




## Objectives

* Measure the overall customer churn rate.
* Identify high-risk customer segments.
* Analyze churn across European regions.
* Compare churn across age, gender, credit score, and tenure.
* Analyze churn among high-value customers.
* Understand the relationship between customer engagement and churn.
* Provide actionable insights through an interactive dashboard.

## Dataset

The project uses a European banking customer dataset containing customer-level information.

### Main Features

| Feature         | Description                 |
| --------------- | --------------------------- |
| CustomerId      | Unique customer identifier  |
| Surname         | Customer surname            |
| CreditScore     | Customer creditworthiness   |
| Geography       | Customer country            |
| Gender          | Customer gender             |
| Age             | Customer age                |
| Tenure          | Years with the bank         |
| Balance         | Account balance             |
| NumOfProducts   | Number of banking products  |
| HasCrCard       | Credit card ownership       |
| IsActiveMember  | Customer activity indicator |
| EstimatedSalary | Estimated annual salary     |
| Exited          | Customer churn indicator    |

## Technologies Used

* Python
* Pandas
* NumPy
* Plotly
* Flask
* Scikit-learn
* Matplotlib
* Seaborn
* Excel

## Methodology

### 1. Data Ingestion & Validation

* Load the banking customer dataset.
* Validate data types and required fields.
* Check missing values and duplicate customers.
* Verify the churn indicator.

### 2. Data Cleaning

* Remove duplicate customer records.
* Handle missing values.
* Remove non-analytical fields from analysis.
* Convert categorical variables for segmentation.

### 3. Customer Segmentation

Customers are segmented based on:

* **Geography:** France, Spain, Germany
* **Age:** <30, 30–45, 46–60, 60+
* **Credit Score:** Low, Medium, High
* **Tenure:** New, Mid-term, Long-term
* **Balance:** Zero-balance, Low-balance, High-balance

### 4. Churn Analysis

The project analyzes:

* Overall churn rate
* Segment-wise churn rate
* Geography-wise churn
* Age-wise churn
* Gender-based churn
* Tenure-wise churn
* Credit-score-based churn
* Engagement vs churn
* Product usage vs churn
* High-value customer churn

### 5. High-Value Customer Analysis

Customers in the top 25% of account balance are treated as high-value customers. Their churn rate, geography, balance, and financial profile are analyzed to identify potential financial risk.

## Key Performance Indicators

* **Overall Churn Rate**
* **Segment Churn Rate**
* **High-Value Churn Ratio**
* **Geographic Risk Index**
* **Engagement Drop Indicator**

## Web Dashboard

The Flask web dashboard provides:

* Overall churn summary
* KPI cards
* Churn distribution
* Geography-wise analysis
* Age-wise comparison
* Tenure analysis
* Credit score analysis
* Balance segment analysis
* Gender analysis
* Engagement analysis
* Product usage analysis
* High-value customer explorer
* Financial risk analysis
* Geography × Age interaction
* Customer-level filtered data

## Project Structure

```text
European_Bank_Churn_Project/
│
├── European_Bank_cleaned.csv.xlsx
├── app.py
├── eda.py
├── requirements.txt
├── README.md
└── screenshots/
```

## Installation

Clone or download the project and navigate to the project directory.

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment on Windows:

```bash
venv\Scripts\activate
```

Install the required libraries:

```bash
pip install -r requirements.txt
```

## Run the Application

Start the Flask dashboard using:

```bash
python app.py
```

The application will open in the browser at:

```text
http://localhost:5000
```

## Deploy on Render

The repository includes `render.yaml` and can be deployed as a Python web service:

1. Open [Render](https://render.com/) and choose **New Web Service**.
2. Connect the `dharshini0830/European-Bank-Analysis` GitHub repository.
3. Render will use the included build and start commands.
4. Deploy the service and open the generated public URL.

## Free HTTPS Deployment on Hugging Face Spaces

If Render requests payment verification, use a free Docker Space instead:

1. Open [Hugging Face Spaces](https://huggingface.co/spaces) and choose **Create new Space**.
2. Choose **Docker**, set the Space to **Public**, and create it.
3. Upload the project files, including `Dockerfile`, `app.py`, `templates/`, `requirements.txt`, and `European_Bank_cleaned.csv.xlsx`.
4. Wait for the build to finish. The public HTTPS URL will be:
	`https://<your-hugging-face-username>-<space-name>.hf.space`

## Expected Outcome

The system provides segmentation-based insights into customer churn and helps identify high-risk customer groups, geographic differences, engagement patterns, and potential financial exposure from customer attrition.

## Future Scope

* Machine learning-based churn prediction
* Customer churn probability scoring
* Automated retention recommendations
* Real-time banking data integration
* Advanced customer lifetime value analysis
* Automated alerts for high-risk customers

## Conclusion

The European Bank Customer Churn Analytics project transforms customer-level banking data into actionable segmentation insights, enabling data-driven understanding of churn and supporting targeted customer retention strategies.

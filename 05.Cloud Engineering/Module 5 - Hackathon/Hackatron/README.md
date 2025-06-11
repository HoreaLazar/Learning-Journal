# cloud_engineering_hackatron

📌 Project Overview
A UK Road Safety dashboard using Streamlit and Azure SQL, deployed via Azure App Service.

🗂️ Dataset
Source: UK Road Safety (from Kaggle or Azure SQL).

Preparation: Cleaned missing values, converted date formats, cast number types.

Stored in: Azure SQL DB Traffic_Accidents_2019_Leeds.

⚙️ Tech Stack
Streamlit, pandas, matplotlib, pyodbc

Azure App Service

Azure SQL Database

Azure Monitor + Cost Management

🧱 Features
Interactive dashboard with filters

Casualty severity bar chart

Daily trend line chart

Map of accidents by coordinates

Monitoring + budget alerts

🧹 Challenges
SQL connection timeout (HYT00) – solved by increasing timeout in connection string

Data type errors – fixed with .astype(int) and proper datetime parsing

🔧 Monitoring & Budget
Alerts set for:

CPU usage

Response time

Health check

Budget: £100/month with alert

Auto-scaling set to manual (limited by B1 plan)

📂 GitHub Repo
Link to your repository (if public):
https://github.com/your-name/uk-road-safety-dashboard

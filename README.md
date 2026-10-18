# AgriServe: A Farmer Records and Government Assistance Tracking System

AgriServe is a research prototype designed to help barangay agricultural offices and Municipal Agriculture Office personnel organize farmer records, manage farm profiles, evaluate assistance applications, and track the distribution of government agricultural support.

## 🚀 Live Prototype

The system is deployed and accessible online via Render:
**Live URL:** [https://agriserve.onrender.com]

_(Note: Because this is hosted on a free tier, the server may take 30-50 seconds to wake up if it has been inactive for a while. Please be patient on the first load)._

## ✨ Core Features

- **Role-Based Authentication:** Separate dashboards and permissions for Farmers, Agricultural Officers, and Administrators.
- **Farmer Profiling & Multi-Farm Management:** Farmers can manage their personal data and register multiple farms, recording crops and logging agricultural losses (e.g., typhoon or pest damage).
- **Assistance Program Management:** Admins can create official assistance programs (e.g., RCEF, PCIC) with specific allocation limits.
- **Application Workflow:** Farmers can apply for programs; Officers can review, approve, or reject applications with documented reasons.
- **Preliminary Assessment Scoring:** An integrated rubric scoring engine to help officers calculate priority scores based on agricultural data.
- **Data Analytics & Export:** Admins have access to a live Chart.js dashboard and can export all system data to a formatted Excel (.xlsx) file.
- **Automated Notifications (Code implemented):** The system is coded to automatically send an email to the farmer when their application is approved or rejected using Flask-Mail.

## 🛠️ Tech Stack

- **Backend:** Python 3.13, Flask 3.1.3, SQLAlchemy
- **Database:** MySQL (Cloud hosted on Aiven, Local via XAMPP)
- **Frontend:** HTML5, CSS3, Bootstrap 5, Chart.js
- **Deployment:** Render
- **Email Integration:** Flask-Mail (Gmail SMTP)

## 💻 How to Run Locally

If you wish to run this project on your local machine:

1. Clone the repository.
2. Create a virtual environment: `python -m venv .venv`
3. Activate it (Windows): `.\.venv\Scripts\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file in the root directory and add your local database link and secret key:
   ```env
   FLASK_APP=run.py
   SECRET_KEY=your_secret_key
   DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/agriserve
   ```

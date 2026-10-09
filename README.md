# AI-Driven Career & Skill Gap Analyzer

A Streamlit web application that helps users understand how their current skills match the requirements of selected career roles. It calculates a skill-readiness score, identifies missing skills, scans resumes for listed skills, and creates a personalized four-week learning roadmap.

**Project alignment:** UN Sustainable Development Goal 8 — Decent Work and Economic Growth  
**Context:** AICTE – IBM SkillsBuild

## Features

- **User accounts:** Register, log in, and log out.
- **Password security:** Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes.
- **Career skill-gap analysis:** Compare selected skills against six role benchmarks:
  - Data Analyst
  - Machine Learning Engineer
  - Full-Stack Developer
  - Cloud Architect
  - Cybersecurity Analyst
  - DevOps Engineer
- **Readiness dashboard:** View your match percentage, readiness label, matched skills, and missing skills.
- **Visual reports:** Interactive gauge and radar charts display skill coverage.
- **Resume scanner:** Upload a PDF or TXT resume, or paste resume text, to detect skills mentioned in it.
- **Learning roadmap:** Generate a four-week plan based on skills missing for the selected role, and download the plan as a text file.
- **Profile and progress:** Save skills, change your password, and review previous analysis scores.
- **Local database:** SQLite stores user profiles and analysis history.

## Tech Stack

- Python
- Streamlit
- SQLite
- Pandas
- Plotly
- pypdf (optional dependency for PDF resume reading)

## Project Structure

```text
.
├── app.py             # Streamlit app, authentication, analysis, and UI
├── requirements.txt   # Python dependencies
├── config.toml        # Streamlit theme and browser settings
├── career_app.db      # Local SQLite database (created/updated by the app)
└── README.md          # Project documentation
```

> **Note:** Do not commit a database containing real user data to a public repository. The app creates its database in the working directory when it starts.

## Requirements

- Python 3.9 or newer (recommended)
- pip
- A web browser

## Installation and Setup

### 1. Clone or download the project

If the project is hosted on GitHub:

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_PROJECT_FOLDER>
```

Alternatively, download the project files and open the folder in VS Code.

### 2. Create a virtual environment (recommended)

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the application

From the project folder, run:

```bash
streamlit run app.py
```

Streamlit will display a local URL in the terminal, usually `http://localhost:8501`. Open it in your browser.

## How to Use

1. Open the app and select **Login / Register** from the sidebar.
2. Create an account using your name, email, and a password of at least six characters, or log in to an existing account.
3. On the **Dashboard**, choose a target role and select the skills you already have.
4. Select **Analyze my skill gap** to see your readiness score, matched skills, and missing skills.
5. Open **Learning Roadmap** to view the four-week learning plan generated from the analysis.
6. Open **Resume Scanner** to upload a PDF/TXT resume or paste resume text, then compare detected skills with a target role.
7. In **Profile**, save your skills, review your analysis history, or change your password.

## How the Readiness Score Works

The score is calculated from the number of required skills selected by the user that match the role's built-in benchmark:

```text
Readiness score = (Matched required skills / Total required skills) × 100
```

The displayed status is based on the following thresholds:

- **80–100%:** Placement ready
- **50–79%:** Getting there
- **0–49%:** Early stage

This is a simple benchmark-based estimate, not a guarantee of job placement. The benchmark lists are defined in `app.py` and may not represent every employer's requirements.

## Resume Scanner Notes

- The scanner searches for configured skill names and aliases in resume text.
- PDF extraction requires the `pypdf` package.
- Scanned/image-only PDFs may not produce extractable text unless OCR is added.
- Skill detection is keyword-based; it does not verify proficiency or understand the full context of a resume.
- Review the detected skills before relying on the results.

## Data and Security Notes

- User records and analysis history are stored in the local `career_app.db` SQLite database.
- Passwords are hashed using PBKDF2-HMAC-SHA256 with a per-user random salt.
- Keep the database private if it contains personal information.
- For a public deployment, review authentication, session handling, database access, secrets management, HTTPS, and privacy requirements before using real user data.
- The app currently uses a local SQLite database; a multi-user hosted deployment may require a managed database and additional security controls.

## Configuration

The `.streamlit/config.toml` file can define the Streamlit theme. The supplied configuration uses a dark theme with saffron as the primary accent.

If your configuration file is named `config.toml`, place it at:

```text
.streamlit/config.toml
```

Streamlit automatically reads configuration from that location when starting the app.

## Troubleshooting

**`streamlit` command not found**

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

**PDF resume is not being read**

```bash
python -m pip install pypdf
```

Then restart the app. You can also paste the resume text directly.

**Database or login issues**

- Make sure the app can write to its project directory.
- Keep `career_app.db` in the directory from which you run the app.
- Do not delete the database if you want to preserve existing accounts and history.

## Future Improvements

- Add more job roles and editable skill benchmarks.
- Support OCR for scanned resumes.
- Recommend learning resources for each missing skill.
- Add export options for reports.
- Improve deployment-ready authentication and persistent database support.

## License

No license has been specified yet. Add a `LICENSE` file before distributing the project publicly.

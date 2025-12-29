# 🛡️ Phishing Email Detection Agent

An intelligent, local-first AI agent that connects to your Gmail, analyzes emails for phishing risks, and provides a clear security dashboard. It combines heuristic analysis (technical checks) with semantic analysis (AI/BERT) to detect sophisticated threats.



## 🚀 Features

-   **Privacy Focused**: Runs locally on your machine.
-   **Dual Analysis Engine**:
    -   **Technical**: Checks for Spoofing (SPF/DKIM), Excessive Redirects, URL Shorteners, and Domain Consistency.
    -   **Semantic**: Uses `BERT` (AI) to detect urgency, coercion, and financial requests in the text.
-   **Smart Dashboard**: View risk scores (0-100) and detailed analysis for every email.
-   **False Positive Reduction**: Intelligent whitelist for matched sender/destination domains (e.g., Marketing emails).

---

## 🛠️ Installation

### Prerequisites
-   Python 3.8+
-   A Gmail Account

### 1. Clone & Install
```bash
git clone https://github.com/your-username/PhishingEmail.git
cd PhishingEmail
pip install -r requirements.txt
```

---

## 🔑 Setup Guide (Bring Your Own Keys)

Since this tool accesses your private Gmail data, you must create your own "App Credentials" in Google Cloud. This keeps your data safe and private.

### Step 1: Create a Google Cloud Project
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Click **"Select a Project"** (top left) -> **"New Project"**.
3.  Name it `PhishingAgent` and click **Create**.

### Step 2: Enable Gmail API
1.  In the Dashboard, search for **"Gmail API"** in the top search bar.
2.  Click **Gmail API** -> **Enable**.

### Step 3: Configure Consent Screen
1.  Go to **APIs & Services** -> **OAuth consent screen**.
2.  Select **External** -> **Create**.
3.  **App Information**:
    -   App Name: `PhishingAgent`
    -   User Support Email: (Your email)
    -   Developer Contact Info: (Your email)
4.  Click **Save and Continue** until you reach **Test Users**.
5.  **Criticial Step**: Click **"+ ADD USERS"** and add **YOUR OWN GMAIL ADDRESS**.
    -   *Why?* Since the app is in "Testing" mode, it will only work for users you explicitly list here.

### Step 4: Create Credentials
1.  Go to **APIs & Services** -> **Credentials**.
2.  Click **"+ CREATE CREDENTIALS"** -> **OAuth Client ID**.
3.  **Application Type**: Select **Desktop App**.
4.  Name: `PhishingAgent-Desktop`.
5.  Click **Create**.
6.  **Download JSON**: Look for the pop-up or the list entry. Click the **Download Icon ⬇️** (Download JSON).
7.  **Rename & Move**:
    -   Rename the file to `credentials.json`.
    -   Move it into the `phishing_agent/` folder of this project.

---

## ▶️ Running the Agent

1.  Start the application:
    ```bash
    python3 phishing_agent/main.py
    ```

2.  **First Run**:
    -   A browser window will open asking you to Login to Google.
    -   **Warning**: You will see a "Google hasn't verified this app" warning. This is expected because *you* created the app for yourself.
    -   Click **Advanced** -> **"Go to PhishingAgent (unsafe)"** to proceed.
    -   Grant the requested permissions (Read-only access to Gmail).

3.  **View Dashboard**:
    -   Open your browser to: `http://localhost:8000/report.html`
    -   The agent will check for new emails every 30 seconds.

## ⚠️ Privacy Note
This application downloads emails to your local machine (`database/queue.json`) for analysis. **No data is sent to any external server** other than Google (for authentication) and the local AI model inference.

# 🛡️ PhishingEmail: AI-Powered Local Phishing Defense

**PhishingEmail** is a privacy-first, local cyber-defense agent that protects your inbox without sending your private emails to the cloud. By running entirely on your machine, it combines heuristic technical analysis with a fine-tuned BERT model to detect sophisticated phishing, BEC (Business Email Compromise), and social engineering attacks.

---

## � Key Features

| Feature | Description |
| :--- | :--- |
| **🔒 Privacy First** | Zero data exfiltration. Analyses run locally on your CPU/GPU. Emails are stored in a local JSON database. |
| **🧠 AI Brain** | Uses a fine-tuned BERT model (`bert-finetuned-phishing`) to detect psychological manipulation and urgency. |
| **⚡ Worst-Link Logic** | Cross-correlates technical failures (SPF/DKIM) with semantic urgency to detect advanced attacks. |
| **🕸️ Deep Inspection** | Unmasks URL shorteners and traces redirect chains to reveal true destinations. |
| **🛡️ Anti-Obfuscation** | Normalizes zero-width characters and homoglyphs used to bypass traditional filters. |
| **� Live Dashboard** | Real-time, auto-refreshing HTML dashboard to visualize threats and analysis results. |

---

## �️ Installation

### Prerequisites
- **Python 3.8+**
- **Gmail Account** (for API access)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/PhishingEmail.git
cd PhishingEmail
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download AI Model (Optional but Recommended)
Pre-download the BERT model to ensure offline capability and faster startup.
```bash
python3 phishing_agent/download_model.py
```
*If skipped, the agent will attempt to download the model from HuggingFace on the first run.*

---

## 🔑 Configuration: Bring Your Own Keys (BYOK)

Because this tool respects your privacy, it does not use a shared cloud server. You must provide your own Google API credentials.

### Step 1: Create a Google Cloud Project
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Click **"Select a Project"** (top left) -> **"New Project"**.
3.  Name it `PhishingAgent` and click **Create**.

### Step 2: Enable Gmail API
1.  In the dashboard search bar, type **"Gmail API"**.
2.  Click **Gmail API** -> **Enable**.

### Step 3: Configure Request Consent
1.  Go to **APIs & Services** -> **OAuth consent screen**.
2.  Select **External** -> **Create**.
3.  **App Information**:
    -   App Name: `PhishingAgent`
    -   User Support Email: (Your email)
    -   Developer Contact Info: (Your email)
4.  Click **Save and Continue** until you reach **Test Users**.
5.  **Critical**: Click **"+ ADD USERS"** and add **YOUR OWN GMAIL ADDRESS**.
    -   *Why?* In "Testing" mode, the app only works for users explicitly listed here.

### Step 4: Generate Credentials
1.  Go to **APIs & Services** -> **Credentials**.
2.  Click **"+ CREATE CREDENTIALS"** -> **OAuth Client ID**.
3.  **Application Type**: Select **Desktop App**.
4.  Name: `PhishingAgent-Desktop`.
5.  Click **Create**.
6.  **Download JSON**: Click the **Download Icon ⬇️** (Download JSON).
7.  **Rename & Move**:
    -   Rename the file to `credentials.json`.
    -   Move it into the `phishing_agent/` folder:
        ```text
        PhishingEmail/
        ├── phishing_agent/
        │   ├── credentials.json  <-- Place here
        │   └── ...
        └── ...
        ```

---

## ▶️ Usage

### Start the Agent
```bash
python3 phishing_agent/main.py
```

### First Run Authentication
1.  A browser window will open asking you to login to Google.
2.  **Warning**: You will see "Google hasn't verified this app". This is expected because *you* created the app.
3.  Click **Advanced** -> **"Go to PhishingAgent (unsafe)"**.
4.  Grant the read-only Gmail permissions.

### View the Dashboard
Once running, the agent starts a local web server. Open your browser to:
**[http://localhost:8000/report.html](http://localhost:8000/report.html)**

The dashboard auto-refreshes every 10 seconds to show new emails and their risk verdicts.

---

## 🧩 Architecture

The agent employs a **Dual-Engine Architecture**:

1.  **Technical Agent (The Shield)**
    -   Validates SPF, DKIM, and DMARC records.
    -   Detects "Reply-To" mismatches and display name spoofing.
    -   Sandbox-simulates URLs to check for dead links or malicious tarpits.

2.  **Semantic Agent (The Brain)**
    -   **Intent Scanner**: Regex-based heuristics for urgency, credential theft, and financial demands.
    -   **BERT Inference**: Uses `bert-finetuned-phishing` to classify email content.
    -   **Trust Override**: If technical checks pass perfectly (clean auth), AI "hallucinations" (false positives) are suppressed to reduce noise.

---

## ⚠️ Privacy & Security Note
-   **Local Storage**: Emails are downloaded to `database/queue.json`.
-   **API Access**: The tool requires `https://www.googleapis.com/auth/gmail.readonly`.
-   **Data Traffic**: No email content is sent to third-party servers. All AI inference happens locally.

---

## 📝 License
This project is open-source. Please check the repository for license details.

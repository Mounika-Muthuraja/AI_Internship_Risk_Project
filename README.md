# 🎯 AI-Powered Internship Risk Detection System

## 📌 Overview

The AI-Powered Internship Risk Detection System analyzes internship offer documents to identify potential scam indicators.

It extracts content from PDF or TXT files, evaluates risk factors using an AI model, and automatically sends alert emails through workflow automation.

The system helps students quickly assess whether an internship offer may be risky before proceeding.

## 🎯 Objective

Many internship scams involve:

* Registration fees
* Unverified companies
* Unofficial communication channels (WhatsApp/Telegram only)
* Lack of clear stipend details

This project aims to:

* Extract internship offer content from documents
* Detect risk signals using AI
* Generate structured analysis output
* Automate alert emails using n8n

## ⚙️ How It Works

### 1️⃣ Document Upload

* User uploads a **PDF or TXT file**
* Text is extracted using:

  * `PDFPlumber` (for PDFs)
  * Direct file reading (for TXT)
* Extracted content is displayed for verification

### 2️⃣ AI Risk Analysis

User asks a question such as:

> “Is this internship genuine?”

The system sends the document + question to an AI model (via OpenRouter API).

The model returns structured JSON:

```json
{
  "stipend_clarity": "Clear | Unclear",
  "registration_fee": "Yes | No",
  "company_verification": "Verified | Unverified",
  "communication_channel": "Official | Unofficial",
  "risk_level": "Low | Medium | High",
  "risk_reason": "string",
  "summary": "string"
}
```

This ensures transparency and structured interpretation.

### 3️⃣ Risk Visualization

Based on AI output, the system displays:

* **Risk Level:** High / Medium / Low
* **Reason:** Explanation of detected risk factors
* **Summary:** Concise overall evaluation

Visual indicators:

* ⚠️ Red alert for High Risk
* ✅ Green indicator for Low Risk
  
### 4️⃣ Email Automation (n8n + Gmail)

User enters recipient email → clicks **Send Alert**

The workflow:

1. AI JSON is parsed
2. Email body is generated dynamically (HTML format)
3. n8n triggers Gmail
4. Email status displayed in Streamlit

Example alert email includes:

* Risk level
* Reason
* Summary
* User’s original question
* Warning message (if High risk)

## 🏗 System Architecture

User Upload
     ↓
Streamlit App
     ↓
Text Extraction (PDFPlumber)
     ↓
OpenRouter API (GPT-4o-mini)
     ↓
Structured JSON Output
     ↓
Risk Display in UI
     ↓
n8n Workflow Trigger
     ↓
Gmail Alert Sent

## 🛠️ Technologies Used

| Category        | Tools                            |
| --------------- | -------------------------------- |
| Frontend        | Streamlit                        |
| Backend         | Python                           |
| AI Model        | GPT-4o-mini (via OpenRouter API) |
| Text Extraction | PDFPlumber                       |
| Automation      | n8n                              |
| Email Service   | Gmail                            |

## 🔍 Key Features

* PDF & TXT document support
* AI-based structured risk classification
* JSON-based transparent analysis
* Automated email alerts
* HTML formatted report emails
* Persistent session results in UI

## 🧪 Testing & Observations

The system was tested using internship samples containing:

* Registration fee requests
* Missing stipend information
* Unverified company names
* Unofficial communication channels

Results:

* High-risk offers were correctly flagged
* Clear reasoning provided in JSON output
* Email automation executed successfully via n8n

## 📈 Possible Enhancements

* Add company verification API integration
* Deploy on cloud (Render / Streamlit Cloud)
* Add scam keyword scoring system
* Multi-language document support
* Risk history dashboard

## 📌 Conclusion

This project demonstrates practical integration of:

* Document processing
* AI-based structured reasoning
* Workflow automation
* Email alert systems

It combines web interface development, API integration, and automation tools to address a real-world student safety problem.


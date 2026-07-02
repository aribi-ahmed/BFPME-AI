<div align="center">

<!-- Animated Title -->
<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&pause=1000&background=08080800&width=435&lines=BFPME+AI+Agent" alt="Typing SVG" /></a>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white"/>
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-0D7377?style=flat-square&logo=checkmarx&logoColor=white"/>
  <img src="https://img.shields.io/badge/Language-French%20%7C%20Tunisian%20Banking-blue?style=flat-square"/>
  <img src="https://img.shields.io/badge/Failsafe-100%25%20Offline%20Capable-brightgreen?style=flat-square"/>
</p>

<br/>

> **An AI-powered document processing assistant for BFPME credit risk officers evaluating SME loan applications and business plans (_Plans d'affaires_) in Tunisia.**

<br/>

---

</div>

## 🎯 What is BFPME AI Credit Agent?

The **Banque de Financement des Petites et Moyennes Entreprises (BFPME)** is Tunisia's specialized bank for SME financing. Credit risk officers must manually analyze dense business plans to extract key financial data and assess loan viability.

This tool **automates that process** — upload any business plan (`.txt` or `.pdf`), and the app instantly extracts all critical Tunisian financial variables, visualizes the investment structure, and lets you interrogate the document through a smart AI chatbot.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 📊 Tab 1 — Executive Dashboard
- Auto-extracted KPI cards (Coût Total, Crédit BFPME, TRI, VAN, Délai de Récupération, Emplois)
- Automatic **risk rating** (FAIBLE / MODÉRÉ / ÉLEVÉ) based on TRI and payback period
- Financial projections table (An 1 → An 3)
- Raw document text viewer

</td>
<td width="50%">

### 📈 Tab 2 — Financial Visualizations
- **Donut chart** — Financing structure breakdown (Apport, FOPRODI, SICAR, BFPME)
- **Bar chart** — Investment vs. financing comparison
- **CA Evolution** — Revenue projections over 3 years
- **TRI Gauge** — Internal rate of return vs. cost of capital
- **Guarantee Coverage** chart vs. BFPME credit

</td>
</tr>
<tr>
<td width="50%">

### 🤖 Tab 3 — AI Chatbot
- Quick-question chips for instant answers
- **Live mode:** GPT-4o powered contextual responses
- **Failsafe mode:** Semantic rule-based dictionary with banking-grade answers
- Covers: risks, TRI, VAN, guarantees, payback, employment, recommendations

</td>
<td width="50%">

### ⚙️ Sidebar Controls
- 📂 File uploader (`.txt` / `.pdf`)
- 🔑 Optional OpenAI API key input
- 🟢 / 🟡 Live engine status indicator
- 🌿 One-click **sample project** loader (Agritech Sidi Bouzid)

</td>
</tr>
</table>

---

## 🔄 Dual-Engine Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  BFPME AI Credit Agent                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   Document Input (.txt / .pdf / Sample)                 │
│              │                                          │
│              ▼                                          │
│   ┌──────────────────────┐                              │
│   │   API Key Present?   │                              │
│   └──────────────────────┘                              │
│         │          │                                    │
│        YES         NO                                   │
│         │          │                                    │
│         ▼          ▼                                    │
│   🟢 GPT-4o    🟡 Smart-Parsing Engine                 │
│   Extraction   (Regex + Fallback Data)                  │
│         │          │                                    │
│         └────┬─────┘                                    │
│              ▼                                          │
│   ┌─────────────────────┐                               │
│   │  Structured Output  │                               │
│   │  (KPIs + Metadata)  │                               │
│   └─────────────────────┘                               │
│              │                                          │
│    ┌─────────┼──────────┐                               │
│    ▼         ▼          ▼                               │
│  Tab 1     Tab 2      Tab 3                             │
│ Dashboard  Charts   Chatbot                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🏦 Extracted Financial Variables

| Variable | Description |
|---|---|
| `Raison Sociale / Secteur` | Company name and sector |
| `Coût Total de l'Investissement` | Total project cost (mDT) |
| `Apport Personnel du Promoteur` | Promoter's personal contribution (mDT) |
| `Dotation FOPRODI / Prime ZDR` | State grant / regional prime (mDT) |
| `Participation SICAR` | Regional investment company share (mDT) |
| `Crédit BFPME` | BFPME loan amount requested (mDT) |
| `Emplois permanents à créer` | Permanent jobs to be created |
| `TRI` | Internal Rate of Return (%) |
| `VAN` | Net Present Value (mDT) |
| `Délai de Récupération` | Payback period (years) |

---

## 🚀 Quick Start

### Option 1 — Streamlit Community Cloud (Recommended)

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your fork, set **Main file:** `main.py`
4. Click **Deploy** ✅

---

### Option 2 — Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/aribi-ahmed/BFPME-AI.git
cd BFPME-AI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run main.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🔑 OpenAI API Key (Optional)

The app works **100% offline** without any API key using the Smart-Parsing Engine.

To enable GPT-4o for dynamic extraction and the live chatbot:
1. Get a key at [platform.openai.com](https://platform.openai.com)
2. Paste it into the sidebar field — it is **never stored or transmitted** beyond your session

| Mode | API Key | Extraction | Chatbot |
|---|---|---|---|
| 🟢 **Live LLM Engine** | ✅ Required | GPT-4o structured output | GPT-4o conversational |
| 🟡 **Smart-Parsing (Failsafe)** | ❌ Not needed | Regex + rule-based | Semantic dictionary |

---

## 📁 Project Structure

```
bfpme-ai-agent/
│
├── main.py                  # 🧠 Full application (single file)
├── requirements.txt         # 📦 Python dependencies
├── .streamlit/
│   └── config.toml          # ⚙️  Server & theme configuration
└── README.md                # 📖 You are here
```

---

## 🛠️ Tech Stack

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,github" height="40"/>
</p>

| Technology | Role |
|---|---|
| **Python 3.11** | Runtime |
| **Streamlit** | Web UI framework |
| **Plotly** | Interactive financial charts |
| **OpenAI (v1.0+)** | LLM extraction & chatbot |
| **pypdf** | PDF text extraction |
| **pandas** | Data tables |

---

## 🌿 Sample Project — Agritech Sidi Bouzid

No file to upload? Click **"🌿 Charger Projet Sample"** in the sidebar to instantly load a realistic Tunisian agri-food project:

- **Sector:** Tomato processing (concentré, pelées, jus)
- **Location:** Zone Industrielle, Sidi Bouzid (ZDR)
- **Total Investment:** 2,850 mDT
- **BFPME Credit:** 1,567 mDT (55%)
- **Jobs Created:** 45 permanent positions
- **TRI:** 18.4% | **VAN:** 650 mDT | **Payback:** 6.8 years

---

## 🔒 Security

- ✅ XSRF protection enabled
- ✅ Document-derived values are HTML-escaped before rendering
- ✅ API key handled in-memory only, never logged or stored
- ✅ File deduplication via SHA-256 content hash
- ✅ PDF parsing isolated in try/except with graceful fallback

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push and open a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

<div align="center">

<br/>

**Built for BFPME credit risk officers 🏦 • Made in Tunisia 🇹🇳**

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=14&duration=4000&pause=1000&color=0D7377&center=true&vCenter=true&width=500&lines=Analyse+intelligente+des+plans+d'affaires;Smart+Parsing+%2B+GPT-4o+%7C+100%25+Failsafe;Open+Source+%E2%80%94+Deploy+in+2+minutes" alt="Footer typing" />

</div>

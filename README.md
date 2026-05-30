# 🔍 Job Listings Search Engine
### Data Mining Lab Project — Inverted Index + TF-IDF Ranking

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![NLTK](https://img.shields.io/badge/NLTK-3.x-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20UI-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-yellow)

A fully custom search engine built **from scratch** over a corpus of **100 tech job listings**. No Elasticsearch. No Whoosh. Just pure Python — an inverted index, TF-IDF ranking, boolean retrieval, and a Google-style Streamlit web interface.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [Web UI (Bonus)](#-web-ui-bonus)
- [▶ Run UI in Google Colab](#-run-ui-in-google-colab-no-install-needed)
- [Example Queries](#-example-queries)
- [Index Statistics](#-index-statistics)
- [Tech Stack](#-tech-stack)

---

## 🧠 Overview

This project implements a **specialized search engine** for job listings as part of a Data Mining lab assignment. The goal was to understand the fundamentals of information retrieval by building every component from the ground up:

| Component | Implementation |
|---|---|
| Text Preprocessing | Tokenization, stopword removal, Porter stemming |
| Indexing | Inverted Index with term frequency + positional data |
| Ranking | TF-IDF scoring (smoothed with +1 IDF) |
| Retrieval | Boolean AND / OR query modes |
| Interface | Jupyter notebook widget + Streamlit web app |

---

## ✨ Features

- **100 real-world job listings** across tech and non-tech domains (Python, ML, DevOps, Design, etc.)
- **Inverted index** built from scratch — maps each term to its posting list (doc IDs, frequencies, positions)
- **TF-IDF ranking** — results sorted by relevance, not just keyword presence
- **AND / OR boolean modes** — strict intersection vs. broad union retrieval
- **Smart snippets** — context-aware excerpt anchored near the first query term hit
- **Index statistics** — term frequency distribution, vocabulary size, avg document length
- **Interactive Jupyter widget** (`ipywidgets`) for in-notebook searching
- **Streamlit Web UI** — Google-style interface with live search, result cards, and tag badges

---

## 📁 Project Structure

```
job-search-engine/
│
├── Job_Search_Engine_100.ipynb   # Main notebook (solution code)
├── app.py                        # Streamlit web UI (bonus)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## ⚙️ How It Works

### 1. Preprocessing (`preprocess()`)

Each document's title + description is cleaned before indexing:

```
raw text  →  lowercase  →  tokenize  →  remove stopwords  →  Porter stem  →  tokens
```

Example: `"Machine Learning Engineer"` → `['machin', 'learn', 'engin']`

### 2. Inverted Index

The index maps every stemmed term to a posting list:

```python
{
  "python": {
    1: {"frequency": 3, "positions": [2, 11, 19]},
    2: {"frequency": 5, "positions": [1, 4, 7, 12, 20]},
    ...
  }
}
```

Tracks:
- **Document frequency (DF)** — how many docs contain the term
- **Term frequency (TF)** — how often it appears in each doc
- **Positions** — for potential phrase queries

### 3. TF-IDF Ranking

$$\text{score}(d, q) = \sum_{t \in q} \text{TF}(t, d) \times \text{IDF}(t)$$

Where:
- $\text{TF}(t, d) = \text{freq}(t, d) \ / \ \text{doc\_length}(d)$
- $\text{IDF}(t) = \log\left(\frac{N+1}{df(t)+1}\right) + 1$ (smoothed to avoid zero)

### 4. Query Processing

| Mode | Logic | Use Case |
|---|---|---|
| `OR` | Union of posting lists | Broad, exploratory search |
| `AND` | Intersection of posting lists | Precise, narrow results |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/job-search-engine.git
cd job-search-engine

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download NLTK data (done automatically on first run, or manually)
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
```

### `requirements.txt`

```
nltk
streamlit
ipywidgets
jupyter
```

---

## 💻 Usage

### Option 1: Jupyter Notebook

```bash
jupyter notebook Job_Search_Engine_100.ipynb
```

Run all cells top to bottom (`Runtime > Run All`). Use the interactive widget in **Cell 12** to search live.

### Option 2: Streamlit Web App

```bash
streamlit run app.py
```

Opens a Google-style search interface in your browser at `http://localhost:8501`.

---

## 🌐 Web UI (Bonus)

The Streamlit app (`app.py`) provides a polished search interface:

- Clean search bar — type any tech keyword
- **OR / AND** mode toggle
- Adjustable **Top K** results slider
- Result cards showing: job title, company, location, TF-IDF score, snippet, and tag badges
- Index statistics panel in the sidebar

---

## ▶ Run UI in Google Colab (No Install Needed)

> **No Python setup required.** Anyone can run the Web UI directly in the browser using Google Colab — just follow these 4 steps.

### Step 1 — Open a new Colab notebook
Go to [colab.research.google.com](https://colab.research.google.com) → **New notebook**

### Step 2 — Upload `app.py`
In the **left sidebar**, click the 📁 folder icon → click the ⬆️ upload button → select `app.py` from this repo.

### Step 3 — Run these 3 cells in order

**Cell 1 — Install libraries**
```python
!pip install streamlit nltk pyngrok -q
```

**Cell 2 — Download NLTK data**
```python
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
print("NLTK ready ✅")
```

**Cell 3 — Launch the app and get your live link**
```python
from pyngrok import ngrok
import subprocess, time

proc = subprocess.Popen(
    ["streamlit", "run", "app.py",
     "--server.port=8501",
     "--server.headless=true",
     "--server.enableCORS=false",
     "--server.enableXsrfProtection=false"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

time.sleep(4)

public_url = ngrok.connect(8501)
print("✅ Your app is live at:", public_url)
```

### Step 4 — Click the link
After ~5 seconds you'll see:
```
✅ Your app is live at: https://xxxx.ngrok-free.app
```
Click it — the Google-style Job Search UI opens in a new tab. The link is shareable with anyone.

> **Note:** The link stays alive as long as your Colab session is running. If it expires, just re-run Cell 3.

---

## 🔎 Example Queries

| Query | Mode | What you get |
|---|---|---|
| `python developer` | OR | All jobs mentioning Python OR development roles |
| `machine learning python` | AND | Jobs requiring BOTH ML and Python skills |
| `android` | OR | Android-specific mobile developer roles |
| `cloud aws kubernetes` | AND | DevOps / cloud roles needing all three skills |
| `data remote` | OR | Remote data science / engineering jobs |
| `security penetration` | AND | Cybersecurity and ethical hacking roles |

---

## 📊 Index Statistics

After building the index over 100 documents:

| Metric | Value |
|---|---|
| Total Documents | 100 |
| Unique Indexed Terms | ~350+ |
| Average Document Length | ~35 tokens |
| Top Term | `python`, `data`, `experi` (stemmed) |

---

## 🛠 Tech Stack

| Tool | Purpose |
|---|---|
| Python 3 | Core language |
| NLTK | Stopword list, Porter Stemmer |
| `re` | Tokenization (regex) |
| `math` | IDF calculation |
| `ipywidgets` | In-notebook interactive UI |
| Streamlit | Web application interface |
| Jupyter Notebook | Development & demonstration environment |

---

## 📋 Assignment Context

Built for a **Data Mining Lab** assignment requiring:
- Custom inverted index (no search libraries)
- Boolean retrieval (AND / OR)
- TF-IDF ranking
- Domain: Job Listings
- Language: Python only (NumPy, Pandas, NLTK allowed)

The Streamlit web UI was developed as **bonus work** to demonstrate a Google-style search experience.

---

## 👤 Author

**Anona Ayshi Rozario**  
Department of CSE
University of Information Technology and Sciences (UITS)

---

*Built from scratch — no Elasticsearch, no Whoosh, no shortcuts.*

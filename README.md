# 🎓 Faculty LeadGen Tool

An intelligent **faculty lead generation and scoring system** built with **Streamlit**.
It scrapes staff/faculty pages, extracts contact details, verifies emails with Hunter.io, scores leads based on academic title, and provides interactive dashboards for analysis.
Additionally, it includes **ML-powered predictive lead scoring** to identify the most promising contacts.

---

## 🌐 Live Demo

🔗 **Deployed App**: [LeadGen Tool on Streamlit Cloud](https://scriptpy-qijtnowamhp6c59e2xysx6.streamlit.app/)

---



## ✨ Features

* 🔍 **Web Scraping** – Extracts name, title, phone, and email from staff directory pages.
* 📧 **Email Verification** – Uses [Hunter.io API](https://hunter.io/) to check email validity.
* 🎯 **Lead Scoring System** – Scores leads based on:

  * Academic Title weight
  * Email validity
  * Domain credibility (`.edu` / `.org` preferred)
* 📊 **Interactive Dashboard** – Visualize lead distribution, email validity, top job titles, phone availability, etc.
* 🤖 **Predictive Analytics** – Machine learning model (Random Forest) to estimate engagement probability.
* 📥 **Export Options** – Download all leads or top 10 leads as CSV.

---

## 🛠️ Tech Stack

* [Python](https://www.python.org/)
* [Streamlit](https://streamlit.io/) – UI & dashboard
* [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) – Web scraping
* [Pandas](https://pandas.pydata.org/) – Data wrangling
* [Altair](https://altair-viz.github.io/) – Data visualization
* [Scikit-learn](https://scikit-learn.org/) – Machine learning (predictive scoring)
* [Hunter.io API](https://hunter.io/) – Email verification

---

## ⚙️ Setup & Installation

### 1. Clone this repository

```bash
git clone https://github.com/harivardhan888/leadgen-tool.git
cd leadgen-tool
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up API key

You’ll need a **Hunter.io API key**. Create a `.env` file (or edit directly in the script):

```bash
HUNTER_API_KEY=your_hunter_api_key_here
```

### 5. Run the app

```bash
streamlit run script.py
```

---

## 🚀 Usage

1. Enter the **URL of a staff directory page** in the text input.

   * ⚠️ Note: The current code is written for sites that use `div.col-sm-3.col-xs-6` with `div.name`, `div.title`, etc.
   * For **other sites** (e.g., [UARK Directory](https://cied.uark.edu/directory/?utm_source=chatgpt.com)), you’ll need to update the HTML tags in `scrape_leads()` inside `script.py`.

2. Adjust **scoring weights** in the sidebar (Title, Email Validity, Domain).

3. Click **Generate Leads**.

4. Explore:

   * Summary metrics
   * Lead table with scores
   * Top 10 ranked leads
   * Export CSVs
   * Interactive charts
   * Predictive lead scoring

---

## 📊 Example Outputs

* Lead summary metrics (valid, invalid, missing emails).
* Color-coded lead scores.
* Charts for score distribution, job titles, email status, phone availability.
* Predicted engagement probability.

---

## 📝 To-Do / Future Improvements

* Support multiple university websites with different HTML structures.
* Integrate LinkedIn scraping for richer profiles.
* Add email sending (campaign integration).
* Deploy to **Streamlit Cloud** or **Heroku**.

---

## 👨‍💻 Author

* Developed by **Hari Vardhan Reddy Kummetha**.
* Open for contributions & suggestions!

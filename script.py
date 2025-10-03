import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import altair as alt
import time


# ACADEMIC TITLE SCORING
# ---------------------------
ACADEMIC_TITLE_SCORES = {
    "Dean": 100,
    "Professor of": 90,                  # e.g., Professor of Gifted Education
    "Professor": 85,                     # covers just "Professor"
    "Associate Professor": 75,
    "Assistant Professor": 65,
    "Clinical Professor": 60,            # Clinical Assistant/Assoc Professor
    "Teaching Professor": 55,            # Teaching Assistant/Associate Professor
    "Instructor": 50,
    "Lecturer": 45,                      # Adjunct Lecturer too
    "Adjunct Lecturer": 40,
    "Intern": 20                         # Assistant Teaching Professor & Intern Liaison
}

MAX_LEADS = 100
HUNTER_API_KEY = "82c0e9dc776c62b4ee95df3bac7cf7357c39458a"


# ---------------------------
# SCRAPE LEADS
# ---------------------------
def scrape_leads(url):
    leads = []
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        st.error(f"Failed to fetch URL: {e}")
        return leads

    soup = BeautifulSoup(response.text, 'html.parser')

    people = soup.find_all("div", class_="col-sm-3 col-xs-6")

    for person in people:
        # Extract Name
        name_tag = person.find("div", class_="name")
        name = name_tag.text.strip() if name_tag else "Unknown"

        # Extract Title
        title_tag = person.find("div", class_="title")
        title = title_tag.text.strip() if title_tag else "Unknown"

        # Extract Phone
        phone_tag = person.find("div", class_="phone")
        phone = phone_tag.text.strip() if phone_tag else ""

        # Extract Email
        email_tag = person.find("div", class_="email")
        email = ""
        if email_tag and email_tag.find("a", href=True):
            email = email_tag.find("a")['href'].replace("mailto:", "").strip()

        leads.append({
            "Name": name,
            "Title": title,
            "Phone": phone,
            "Email": email
        })

        if len(leads) >= MAX_LEADS:
            break

    return leads


# ---------------------------
# HUNTER.IO EMAIL VERIFICATION
# ---------------------------
def verify_email_api(email):
    if not email:
        return False
    url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={HUNTER_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        status = data.get('data', {}).get('status', 'unknown')
        return status == "valid"
    except:
        return False


# ---------------------------
# LEAD SCORING
# ---------------------------
def score_lead(lead, weights=None):
    if weights is None:
        weights = {"title": 50, "email": 30, "domain": 20}

    score = 0
    title = lead['Title'].lower()

    # Title-based scoring (find best match)
    for keyword, base_score in ACADEMIC_TITLE_SCORES.items():
        if keyword.lower() in title:
            score += base_score
            break  # first match is enough

    # Email validity check
    if verify_email_api(lead['Email']):
        score += weights["email"]

    # Domain scoring (.edu/.org > .com in academia)
    if lead['Email']:
        domain = lead['Email'].split('@')[-1]
        if domain.endswith(".edu") or domain.endswith(".org"):
            score += weights["domain"]

    lead['Score'] = score
    return lead


# ---------------------------
# STREAMLIT UI
# ---------------------------
st.set_page_config(page_title="LeadGen Tool", layout="wide")
st.title("Faculty LeadGen Tool")

# URL Input
url_input = st.text_input("Enter URL of staff page or directory:")

# Custom scoring weights
st.sidebar.header("Scoring Weights")
title_w = st.sidebar.slider("Job Title Weight", 0, 100, 50)
email_w = st.sidebar.slider("Email Validity Weight", 0, 100, 30)
domain_w = st.sidebar.slider("Domain Weight", 0, 100, 20)
weights = {"title": title_w, "email": email_w, "domain": domain_w}

# Scrape button
if st.button("Generate Leads"):
    if not url_input:
        st.warning("Please enter a URL.")
    else:
        with st.spinner("Scraping and scoring leads..."):
            raw_leads = scrape_leads(url_input)
            if not raw_leads:
                st.warning("No leads found or scraping failed.")
            else:
                # Deduplicate by email
                df = pd.DataFrame(raw_leads).drop_duplicates(subset=["Email"])

                # Score leads
                scored_leads = []
                for _, lead in df.iterrows():
                    lead_dict = lead.to_dict()
                    lead_dict = score_lead(lead_dict, weights)
                    # Add validation status
                    if not lead_dict["Email"]:
                        lead_dict["Email Status"] = "Missing"
                    elif verify_email_api(lead_dict["Email"]):
                        lead_dict["Email Status"] = "Valid"
                    else:
                        lead_dict["Email Status"] = "Invalid"
                    scored_leads.append(lead_dict)
                    time.sleep(1)

                df = pd.DataFrame(scored_leads).sort_values(by="Score", ascending=False)

                # ---------------------------
                # Summary Metrics
                # ---------------------------
                st.subheader("📌 Lead Summary")
                total_leads = len(df)
                valid_count = (df["Email Status"] == "Valid").sum()
                invalid_count = (df["Email Status"] == "Invalid").sum()
                missing_count = (df["Email Status"] == "Missing").sum()

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Leads", total_leads)
                col2.metric("Valid Emails ✅", valid_count)
                col3.metric("Fake Emails ❌", invalid_count)
                col4.metric("Missing Emails ⚠️", missing_count)

                # ---------------------------
                # Leads Table
                # ---------------------------
                st.subheader("All Leads")

                def color_score(val):
                    if val >= 80:
                        return 'color: green'
                    elif val >= 50:
                        return 'color: orange'
                    else:
                        return 'color: red'

                st.dataframe(df.style.applymap(color_score, subset=['Score']))

                # ---------------------------
                # Top 10 Leads
                # ---------------------------
                st.subheader("Top 10 Leads")
                st.dataframe(df.head(10))

                # ---------------------------
                # Export CSV
                # ---------------------------
                csv_all = df.to_csv(index=False).encode('utf-8')
                csv_top10 = df.head(10).to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download All Leads CSV", data=csv_all, file_name="all_leads.csv")
                st.download_button("📥 Download Top 10 Leads CSV", data=csv_top10, file_name="top10_leads.csv")

                # ---------------------------
                # Dashboard / Visuals
                # ---------------------------
                st.subheader("📊 Dashboard")

                # 1. Lead Score Distribution
                st.markdown("### Lead Score Distribution")
                score_chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('Score:Q', bin=alt.Bin(maxbins=10)),
                    y='count()',
                    tooltip=['count()']
                ).properties(width=600, height=300)
                st.altair_chart(score_chart)

                # 2. Email Status Breakdown
                st.markdown("### Email Status (Valid vs Fake vs Missing)")
                email_counts = df['Email Status'].value_counts().reset_index()
                email_counts.columns = ['Status', 'Count']
                email_chart = alt.Chart(email_counts).mark_arc().encode(
                    theta='Count:Q',
                    color='Status:N',
                    tooltip=['Status', 'Count']
                )
                st.altair_chart(email_chart)

                # 3. Top Job Titles
                st.markdown("### Top Job Titles")
                title_counts = df['Title'].value_counts().reset_index().head(10)
                title_counts.columns = ['Title', 'Count']
                title_chart = alt.Chart(title_counts).mark_bar().encode(
                    x=alt.X('Count:Q'),
                    y=alt.Y('Title:N', sort='-x'),
                    tooltip=['Title', 'Count']
                ).properties(width=600, height=300)
                st.altair_chart(title_chart)

                # 4. Average Score by Title
                st.markdown("### Average Lead Score by Title")
                avg_scores = df.groupby("Title")["Score"].mean().reset_index().sort_values(by="Score", ascending=False).head(10)
                avg_chart = alt.Chart(avg_scores).mark_bar().encode(
                    x=alt.X('Score:Q'),
                    y=alt.Y('Title:N', sort='-x'),
                    tooltip=['Title', 'Score']
                ).properties(width=600, height=300)
                st.altair_chart(avg_chart)

                # 5. Phone Availability
                st.markdown("### Phone Number Availability")
                df['Has Phone'] = df['Phone'].apply(lambda x: "Yes" if x else "No")
                phone_counts = df['Has Phone'].value_counts().reset_index()
                phone_counts.columns = ['Has Phone', 'Count']
                phone_chart = alt.Chart(phone_counts).mark_arc().encode(
                    theta='Count:Q',
                    color='Has Phone:N',
                    tooltip=['Has Phone', 'Count']
                )
                st.altair_chart(phone_chart)


                # ---------------------------
                # 6. Predictive Analytics (ML-based Lead Success Scoring)
                # ---------------------------
                st.subheader("🤖 Predictive Lead Scoring")

                from sklearn.model_selection import train_test_split
                from sklearn.ensemble import RandomForestClassifier

                # Prepare features
                df["Has Email"] = df["Email"].apply(lambda x: 1 if x else 0)
                df["Valid Email"] = df["Email Status"].apply(lambda x: 1 if x == "Valid" else 0)
                df["Domain Type"] = df["Email"].apply(
                    lambda x: "edu" if str(x).endswith(".edu") else ("org" if str(x).endswith(".org") else "other"))

                # Encode domain type
                df["Domain Encoded"] = df["Domain Type"].map({"edu": 2, "org": 1, "other": 0})

                features = df[["Score", "Has Email", "Valid Email", "Domain Encoded"]]
                labels = df["Valid Email"]  # using email validity as proxy for "good lead"

                # Train/test split (only if dataset is big enough)
                if len(df) > 5:
                    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3,
                                                                        random_state=42)
                    model = RandomForestClassifier(random_state=42)
                    model.fit(X_train, y_train)

                    proba = model.predict_proba(features)

                    if proba.shape[1] > 1:
                        df["Engagement Probability"] = proba[:, 1]
                    else:
                        # Only one class in training → set all same probability
                        df["Engagement Probability"] = proba[:, 0]

                    # Show top predicted leads
                    st.markdown("### Top Leads by Predicted Engagement Probability")
                    st.dataframe(df[["Name", "Title", "Email", "Score", "Engagement Probability"]].sort_values(
                        by="Engagement Probability", ascending=False).head(10))

                    # Chart: Engagement probability distribution
                    prob_chart = alt.Chart(df).mark_bar().encode(
                        x=alt.X("Engagement Probability:Q", bin=alt.Bin(maxbins=10)),
                        y="count()",
                        tooltip=["count()"]
                    ).properties(width=600, height=300)
                    st.altair_chart(prob_chart)
                else:
                    st.info("Not enough leads to train predictive model. Try with a larger dataset.")
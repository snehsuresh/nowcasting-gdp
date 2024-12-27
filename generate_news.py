import random
import pandas as pd
from datetime import datetime, timedelta


# Generate random dates between two given dates
def generate_dates(start_date, end_date, n_samples):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return [
        start + timedelta(days=random.randint(0, (end - start).days))
        for _ in range(n_samples)
    ]


# Generate random headlines tied to keywords
def generate_headline(keyword):
    topic_headlines = {
        "GDP": [
            "GDP growth surges",
            "GDP growth declines",
            "GDP growth remains steady",
        ],
        "inflation": [
            "Inflation concerns rise",
            "Inflation rates stabilize",
            "Inflation signals uncertainty",
        ],
        "employment": [
            "Employment rates decline",
            "Job growth improves",
            "Unemployment signals recovery",
        ],
        "recession": [
            "Recession fears deepen",
            "Recession concerns ease",
            "Economic downturn signals recovery",
        ],
        "economic growth": [
            "Economic growth remains robust",
            "Economic growth slows",
            "Economic growth shows resilience",
        ],
        "fiscal policy": [
            "Fiscal policy under scrutiny",
            "Government considers fiscal reforms",
            "Fiscal measures impact economy",
        ],
    }
    return random.choice(topic_headlines[keyword])


# Generate article content tied to keywords
def generate_content(keyword):
    topic_phrases = {
        "GDP": [
            f"The {keyword} shows a significant change due to market conditions.",
            f"Recent data on {keyword} suggests uncertain economic trends.",
            f"Analysts predict that {keyword} will affect upcoming fiscal policies.",
            f"Stakeholders are closely monitoring developments in {keyword}.",
            f"The relationship between {keyword} and global trade remains critical.",
        ],
        "inflation": [
            f"The {keyword} remains a major concern for policymakers.",
            f"Analysts believe {keyword} trends will impact consumer prices.",
            f"Recent data on {keyword} highlights challenges in monetary policy.",
            f"Experts argue that {keyword} may affect wage growth.",
            f"Stakeholders are closely monitoring developments in {keyword}.",
        ],
        "employment": [
            f"The {keyword} is a critical factor in economic recovery.",
            f"Government policies addressing {keyword} are under scrutiny.",
            f"Analysts predict that {keyword} will impact consumer spending.",
            f"Recent trends in {keyword} show a mixed outlook.",
            f"Stakeholders are closely monitoring developments in {keyword}.",
        ],
        "recession": [
            f"The {keyword} remains a looming threat to global markets.",
            f"Recent trends in {keyword} suggest a slow recovery.",
            f"Analysts warn that {keyword} could disrupt fiscal policies.",
            f"Stakeholders are closely monitoring developments in {keyword}.",
            f"Historical data on {keyword} reveals cyclic patterns of recovery.",
        ],
        "economic growth": [
            f"The {keyword} is showing signs of slowing down.",
            f"Government measures to boost {keyword} are under scrutiny.",
            f"Analysts suggest that {keyword} will play a key role in fiscal planning.",
            f"The relationship between {keyword} and inflation is widely debated.",
            f"Recent trends in {keyword} reflect uncertainty in global markets.",
        ],
        "fiscal policy": [
            f"The {keyword} remains a critical tool for economic stabilization.",
            f"Recent measures in {keyword} highlight challenges in governance.",
            f"Stakeholders are debating the impact of {keyword} on economic growth.",
            f"Analysts predict that changes in {keyword} will affect market trends.",
            f"Experts suggest that {keyword} could influence consumer confidence.",
        ],
    }
    num_sentences = random.randint(5, 7)  # Ensure at least 5 sentences per article
    return " ".join(random.choices(topic_phrases[keyword], k=num_sentences))


# Generate synthetic news data ensuring alignment between headline, content, and keyword
def generate_synthetic_news_data(start_date, end_date, n_samples):
    dates = generate_dates(start_date, end_date, n_samples)
    sources = [
        "Reuters",
        "The Wall Street Journal",
        "Financial Times",
        "The Economist",
        "Bloomberg",
    ]
    keywords = [
        "GDP",
        "inflation",
        "employment",
        "recession",
        "economic growth",
        "fiscal policy",
    ]

    # Generate dataset
    data = {
        "Date": dates,
        "Source": random.choices(sources, k=n_samples),
        "Keywords": [random.choice(keywords) for _ in range(n_samples)],
    }

    # Generate headlines and content based on keywords
    data["Headline"] = [generate_headline(kw) for kw in data["Keywords"]]
    data["Content"] = [generate_content(kw) for kw in data["Keywords"]]

    return pd.DataFrame(data)


# Generate 10,000 samples from Jan 2002 to July 2024
news_data = generate_synthetic_news_data("2002-01-01", "2024-07-01", 10000000)

# Save to a CSV file
news_data.to_csv("data/synthetic_news_data.csv", index=False)

print("Synthetic news data saved to 'synthetic_news_data.csv'")

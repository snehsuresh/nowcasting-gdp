import pandas as pd
import spacy
nlp = spacy.load("en_core_web_sm")

# Load Loughran-McDonald Dictionary
def load_loughran_mcdonald_dict(file_path):
    """Loads the Loughran-McDonald Dictionary."""
    lm_dict = pd.read_csv(file_path)
    positive_words = set(lm_dict.loc[lm_dict["Positive"] > 0, "Word"].str.lower())
    negative_words = set(lm_dict.loc[lm_dict["Negative"] > 0, "Word"].str.lower())
    return positive_words, negative_words


# Load the dictionary
positive_words, negative_words = load_loughran_mcdonald_dict("data/LM_dictionary.csv")

# Define topics of interest
topics_of_interest = {
    "economy": ["economy", "economic"],
    "unemployment": ["unemployment", "jobs", "employment"],
    "inflation": ["inflation", "price", "costs"],
    "monetary_policy": [
        "central bank",
        "federal funds",
        "interest rate",
        "monetary policy",
    ],
    "financial_sector": ["bank", "lending", "financial"],
    "manufacturing": ["manufacturing", "industrial production", "factory output"],
}

# Extract relevant sentences
def extract_relevant_sentences(content, toi_keywords, extract_all=False):
    """
    Extract sentences based on the provided flag.

    Parameters:
        content (str): The text content of an article.
        toi_keywords (list): List of keywords related to the topic of interest.
        extract_all (bool): Flag to switch between all sentences and relevant ones.

    Returns:
        list: A list of sentences.
    """
    doc = nlp(content)

    if extract_all:
        # Return all sentences in the article
        return [sentence.text for sentence in doc.sents]
    else:
        # Return only relevant sentences
        relevant_sentences = [
            sentence.text
            for sentence in doc.sents
            if any(keyword in sentence.text.lower() for keyword in toi_keywords)
        ]
        return relevant_sentences
    

# Negation handling
def calculate_sentiment_with_negation(sentence, positive, negative):
    """Calculates sentiment with negation handling."""
    doc = nlp(sentence)
    sentiment_score = 0
    negation = False

    for token in doc:
        word = token.lemma_.lower()

        # Check for negation
        if word in {"not", "no", "never"}:
            negation = True
            continue

        # Apply negation to sentiment words
        if word in positive:
            sentiment_score += -1 if negation else 1
        elif word in negative:
            sentiment_score += 1 if negation else -1

        # Reset negation after punctuation or conjunction
        if token.dep_ in {"punct", "conj"}:
            negation = False

    return sentiment_score

# Tense detection
def detect_tense_and_adjust(sentence, positive, negative):
    """Detects verb tense and adjusts sentiment scores."""
    doc = nlp(sentence)
    sentiment_score = 0

    for token in doc:
        word = token.lemma_.lower()
        tense = token.morph.get("Tense")
        weight = 1  # Default weight for present tense

        if tense == "Past":
            weight = 0.8  # Lower weight for past
        elif tense == "Future":
            weight = 1.2  # Higher weight for future

        if word in positive:
            sentiment_score += weight
        elif word in negative:
            sentiment_score -= weight

    return sentiment_score

# Aspect propagation
def aspect_propagation(sentence, positive, negative):
    """Propagates sentiment using dependency parsing."""
    doc = nlp(sentence)
    sentiment_score = 0

    for token in doc:
        word = token.lemma_.lower()

        # Check if the token is part of the ToI
        if word in positive or word in negative:
            base_score = 1 if word in positive else -1

            # Amplify sentiment based on modifiers (e.g., adjectives, adverbs)
            for child in token.children:
                if child.dep_ in {"amod", "advmod"}:
                    modifier = child.lemma_.lower()
                    if modifier in positive:
                        base_score += 0.5
                    elif modifier in negative:
                        base_score -= 0.5

            sentiment_score += base_score

    return sentiment_score

# Integrated FiGAS sentiment calculator
def calculate_figas_sentiment(sentence, positive, negative):
    """Combines negation handling, tense adjustment, and aspect propagation."""
    # Negation handling
    sentiment_score = calculate_sentiment_with_negation(sentence, positive, negative)

    # Tense detection and adjustment
    sentiment_score += detect_tense_and_adjust(sentence, positive, negative)

    # Aspect propagation
    sentiment_score += aspect_propagation(sentence, positive, negative)

    return sentiment_score

# Filter articles by geographic location

def filter_by_geography(content, us_keywords=["US", "United States", "America"]):
    """Filters content to retain articles mentioning the US and remove irrelevant locations."""
    # doc = nlp(content)
    # return any(
    #     word.lower() in sentence.text.lower()
    #     for word in us_keywords
    #     for sentence in doc.sents
    # )
    return True

def process_dataset(data, positive, negative, topics_of_interest, output_file="figas_sentiment_results_million.csv"):
    """Processes the dataset to compute FiGAS sentiment scores."""
    results = []
    batch_size = 10

    for idx, row in data.iterrows():
        content = row["Content"]
        keywords = row["Keywords"]

        # Filter by geography
        # if not filter_by_geography(content):
        #     continue

        # Extract relevant sentences
        toi_keywords = []
        for topic, keywords_list in topics_of_interest.items():
            if any(kw in keywords for kw in keywords_list):
                toi_keywords.extend(keywords_list)

        relevant_sentences = extract_relevant_sentences(content, toi_keywords)
        # Calculate sentiment scores for each relevant sentence
        sentiment_scores = [
            calculate_figas_sentiment(sentence, positive, negative)
            for sentence in relevant_sentences
        ]

        # Aggregate sentiment
        aggregate_sentiment = (
            sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        )

        results.append(
            {
                "Date": row["Date"],
                "Source": row["Source"],
                "Keywords": keywords,
                "Aggregate_Sentiment": aggregate_sentiment,
            }
        )

        # Print progress after every 10 rows
        if (idx + 1) % batch_size == 0:
            print(f"Processed {idx + 1} rows.")
            # Save to CSV incrementally after every 10 rows
            pd.DataFrame(results).to_csv(output_file, index=False, mode='w', header=True)

    # After the loop, save the remaining data if less than 10 rows were processed at the end
    if len(results) % batch_size != 0:
        pd.DataFrame(results).to_csv(output_file, index=False, mode='w', header=True)

    return pd.DataFrame(results)

# Load the dataset
data = pd.read_csv("data/synthetic_news_data.csv")

# Compute FiGAS sentiment
figas_results = process_dataset(
    data, positive_words, negative_words, topics_of_interest
)

# Final save to CSV
figas_results.to_csv("figas_sentiment_results_million.csv", index=False)

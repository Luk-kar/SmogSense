# Python
import pandas as pd
import re

# Dagster
from dagster import asset, AssetExecutionContext

# Machine Learning and Feature Extraction
from sklearn.feature_extraction.text import TfidfVectorizer

# Import MLflow utilities from your module
from common.utils.model_deployment.stopwords import polish_stopwords

# Common
from common.constants import get_metadata_categories
from common.utils.logging import log_dataframe_info

# Pipeline
from models_deployment.assets.constants import AssetCategories, Groups


@asset(
    group_name=Groups.MODEL_TWITTER_ENGAGEMENT,
    metadata={
        "categories": get_metadata_categories(
            AssetCategories.DATA_PREPROCESSING,
            AssetCategories.SOCIAL_MEDIA,
            AssetCategories.TWITTER_ENGAGEMENT_PREDICTOR,
        )
    },
)
def preprocessed_data(
    context: AssetExecutionContext, extract_twitter_engagement_metrics: pd.DataFrame
) -> dict:
    """
    Calculate engagement, clean tweet text, and vectorize text using TF-IDF.


    The TF-IDF (Term Frequency-Inverse Document Frequency) process converts text into numbers.
    - 'Term Frequency' counts how many times each word appears in a tweet.
    - 'Inverse Document Frequency' scales down the weight of words that are common across many tweets.
    This conversion helps highlight the words that are unique and important in each tweet,
    which in turn can be used as features for building machine learning models.
    """

    data = extract_twitter_engagement_metrics.copy()

    # Define weighted engagement calculation
    def calculate_engagement(row):
        return (
            row["like_count"] * 1
            + row["retweet_count"] * 5
            + row["quote_count"] * 10
            + row["reply_count"] * 3
            + row["view_count"] * 0.001
        )

    data["engagement"] = data.apply(calculate_engagement, axis=1)

    # Clean text: lowercase and remove punctuation
    data["cleaned_text"] = data["text"].apply(
        lambda x: re.sub(r"[^\w\s]", "", x.lower())
    )

    # TF-IDF Vectorization using the Polish stopwords
    # In simple terms, TF-IDF converts each tweet's text into a set of numbers.
    # It calculates how important each word is by considering both its frequency in the tweet
    # and its rarity across all tweets. This helps to focus on words that are particularly significant.
    vectorizer = TfidfVectorizer(stop_words=polish_stopwords, max_features=5000)
    X = vectorizer.fit_transform(data["cleaned_text"])
    y = data["engagement"]

    # Log preview of the processed data for debugging and transparency
    context.log.info(f"TF-IDF Vectorization complete. Matrix shape: {X.shape}")

    log_dataframe_info(context, data, "Processed data")

    # Return all necessary preprocessed data as a dictionary
    return {"df": data, "vectorizer": vectorizer, "X": X, "y": y}

# Dagster
from dagster import asset, AssetExecutionContext


# Common
from common.constants import get_metadata_categories
from common.utils.model_deployment.model import Model

# Pipeline
from models_deployment.assets.constants import AssetCategories, Groups

# Machine Learning and Feature Extraction
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# MlFlow
from mlflow.models import infer_signature

# ML Models
from models_deployment.models import TweetEngage


@asset(
    group_name=Groups.MODEL_TWITTER_ENGAGEMENT,
    metadata={
        "categories": get_metadata_categories(
            AssetCategories.MODEL_TRAINING,
            AssetCategories.SOCIAL_MEDIA,
            AssetCategories.TWITTER_ENGAGEMENT_PREDICTOR,
        )
    },
)
def trained_model(context: AssetExecutionContext, preprocessed_data: dict) -> Model:
    """
    Split the data, train a RandomForestRegressor, and evaluate it.
    """
    X = preprocessed_data["X"]
    y = preprocessed_data["y"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    input_example = X_test[0:1].toarray()
    signature = infer_signature(input_example, model.predict(input_example))

    # Logging important metrics
    context.log.info(f"Training set size: {X_train.shape[0]}")
    context.log.info(f"Test set size: {X_test.shape[0]}")
    context.log.info(
        f"Model: RandomForestRegressor with {model.n_estimators} estimators"
    )
    context.log.info(f"Mean Squared Error (MSE): {mse:.4f}")

    return Model(
        model=model,
        model_name=TweetEngage.MODEL_NAME,
        model_description=TweetEngage.MODEL_DESCRIPTION,
        vectorizer=preprocessed_data["vectorizer"],
        X_test=X_test,
        y_test=y_test,
        mse=mse,
        input_example=input_example,
        signature=signature,
    )

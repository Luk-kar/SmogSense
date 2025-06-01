# Python
import pickle

# Dagster
from dagster import asset, AssetExecutionContext

# Common
from common.utils.model_deployment.mlflow_io import log_and_register_model
from common.constants import get_metadata_categories
from common.utils.model_deployment.model import Model

# Pipeline
from models_deployment.assets.constants import AssetCategories, Groups


@asset(
    group_name=Groups.MODEL_TWITTER_ENGAGEMENT,
    metadata={
        "categories": get_metadata_categories(
            AssetCategories.UPLOAD_MODEL,
            AssetCategories.SOCIAL_MEDIA,
            AssetCategories.TWITTER_ENGAGEMENT_PREDICTOR,
        )
    },
)
def logged_model(context: AssetExecutionContext, trained_model: Model):
    """
    Save the model as a pickle and log it with MLflow.
    """

    # Log useful context details for debugging
    context.log.info(f"Model size in bytes: {len(pickle.dumps(trained_model.model))}")
    context.log.info(
        f"Starting MLflow logging process for model '{trained_model.model_name}'."
    )
    context.log.info(f"Input example type: {type(trained_model.input_example)}")
    try:
        context.log.info(f"Input example shape: {trained_model.input_example.shape}")
    except Exception:
        context.log.info("Input example shape: Not available")
    context.log.info(f"Signature details: {trained_model.signature}")
    context.log.info(f"Model performance metric (MSE): {trained_model.mse}")

    log_and_register_model(trained_model, context)

    context.log.info("Model logged and registered successfully.")

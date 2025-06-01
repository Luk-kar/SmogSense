# Python
import os

# Dagster
from dagster import asset_check, AssetCheckResult, AssetCheckExecutionContext

# MLflow
import mlflow
from mlflow.tracking import MlflowClient
from mlflow.exceptions import MlflowException

# Pipeline
from models_deployment.models import TweetEngage


@asset_check(
    asset="logged_model",
    description="Verifies if the model was passedfully registered in MLflow Model Registry.",
)
def check_model_registered(context: AssetCheckExecutionContext):

    model_name = TweetEngage.MODEL_NAME
    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")

    context.log.info(f"Using MLflow tracking URI: {mlflow_tracking_uri}")
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    client = MlflowClient()

    try:
        # Search for all versions of the model
        versions = client.search_model_versions(f"name='{model_name}'")

        if versions:
            context.log.info(
                f"Found {len(versions)} versions for model '{model_name}'."
            )
            return AssetCheckResult(
                passed=True,
                metadata={
                    "model_name": model_name,
                    "versions": [v.version for v in versions],
                    "latest_version": versions[0].version,
                },
            )
        else:
            context.log.error(f"No registered versions found for model '{model_name}'.")
            return AssetCheckResult(
                passed=False,
                metadata={
                    "message": f"Model '{model_name}' has no registered versions."
                },
            )
    except MlflowException as e:
        context.log.error(f"MLflow error while checking model registration: {str(e)}")
        return AssetCheckResult(
            passed=False,
            metadata={"message": f"MLflow error: {str(e)}"},
        )

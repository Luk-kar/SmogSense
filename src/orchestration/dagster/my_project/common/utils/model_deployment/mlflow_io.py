"""
This module provides utility functions and classes for logging and managing machine learning models with MLflow.
"""

# Python
import os
import socket
import platform

# Dagster
from dagster import AssetExecutionContext

# Third party
import psutil
import mlflow

# MlFlow
from mlflow.tracking import MlflowClient
from mlflow.models import infer_signature
from mlflow.exceptions import MlflowException

from .model import Model


class ModelWrapper(mlflow.pyfunc.PythonModel):
    def __init__(self, model):
        self.model = model

    def predict(self, context, model_input):
        return self.model.predict(model_input)


def log_and_register_model(model: Model, context: AssetExecutionContext = None):
    """
    Log the model with MLflow and register it in the Model Registry.
    """

    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")

    log_endpoint = f"mlflow_tracking_uri: {mlflow_tracking_uri}"
    if context:
        context.log.info(log_endpoint)
    else:
        print(log_endpoint)

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    with mlflow.start_run(run_name="tweet_engage_model") as run:

        log_model(
            model.model,
            model_name=model.model_name,
            input_example=model.input_example,
            signature=model.signature,
            metadata={"mse": model.mse},
        )
        mlflow.log_metric("mse", model.mse)

        register_model(
            model_name=model.model_name,
            registered_model_name=model.model_name,
            description=model.model_description,
        )


def log_model(
    model, model_name, input_example=None, signature=None, metadata=None, params=None
):
    """
    Log the model to MLflow.
    """

    if signature is None and input_example is not None:
        signature = infer_signature(input_example, model.predict(input_example), params)

    wrapped_model = ModelWrapper(model)
    mlflow.pyfunc.log_model(
        python_model=wrapped_model,
        artifact_path=model_name,
        input_example=input_example,
        signature=signature,
        metadata=metadata,
    )


def log_metric(name, value):
    """
    Log a metric to MLflow.
    """
    mlflow.log_metric(name, value)


def log_param(name, value):
    """
    Log a parameter to MLflow.
    """
    mlflow.log_param(name, value)


def log_artifact(file_path, artifact_path=None):
    """
    Log an artifact to MLflow.
    """
    mlflow.log_artifact(file_path, artifact_path=artifact_path)


def set_tag(key, value):
    """
    Set a tag for the current run.
    """
    mlflow.set_tag(key, value)


def register_model(model_name, registered_model_name, description=None, tags=None):
    """
    Register the model in MLflow Model Registry, creating a new version if the model already exists.
    """
    # Get the current run ID
    run_id = mlflow.active_run().info.run_id
    # Build model URI
    model_uri = f"runs:/{run_id}/{model_name}"

    # Create an MlflowClient to interact with the registry
    client = MlflowClient()

    # Check if the model is already registered
    try:
        client.get_registered_model(registered_model_name)  # Check if it exists
        print(
            f"Model {registered_model_name} already exists, registering a new version."
        )
    except MlflowException:
        # If it doesn't exist, register the model
        client.create_registered_model(registered_model_name)
        print(f"Model {registered_model_name} does not exist, creating it.")

    # Create a new version of the registered model
    registered_model_version = client.create_model_version(
        name=registered_model_name, source=model_uri, run_id=run_id
    )

    # Wait until the model version is ready
    import time

    for _ in range(10):
        model_version_details = client.get_model_version(
            name=registered_model_name, version=registered_model_version.version
        )
        if model_version_details.status == "READY":
            break
        time.sleep(1)

    # Add description if provided
    if description:
        client.update_model_version(
            name=registered_model_name,
            version=registered_model_version.version,
            description=description,
        )

    # Add tags if provided
    if tags:
        for key, value in tags.items():
            client.set_model_version_tag(
                name=registered_model_name,
                version=registered_model_version.version,
                key=key,
                value=value,
            )

    print(
        f"Model registered: {registered_model_name}, version: {registered_model_version.version}"
    )


def log_system_metrics():
    """
    Log system metrics to MLflow.
    """
    # Log CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)
    mlflow.log_metric("cpu_usage_percent", cpu_usage)

    # Log memory usage
    memory = psutil.virtual_memory()
    mlflow.log_metric("memory_usage_percent", memory.percent)

    # Log system info as tags
    set_tag("host_name", socket.gethostname())
    set_tag("platform", platform.platform())
    set_tag("python_version", platform.python_version())


def load_latest_model(registered_model_name):
    """
    Load the latest version of a registered model from MLflow Model Registry.
    """
    client = MlflowClient()
    # Get the latest version of the registered model
    latest_versions = client.search_model_versions(f"name='{registered_model_name}'")
    if latest_versions:
        latest_version = max(latest_versions, key=lambda v: int(v.version))
        model_uri = f"models:/{registered_model_name}/{latest_version.version}"
        model = mlflow.pyfunc.load_model(model_uri)
        return model
    else:
        print("No registered model found.")
        return None

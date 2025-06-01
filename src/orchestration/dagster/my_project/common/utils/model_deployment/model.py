# Python
from dataclasses import dataclass
from typing import Any, Optional

# MlFlow
from mlflow.models.signature import ModelSignature


@dataclass
class Model:
    """
    Encapsulated machine learning model with associated metadata.

    Attributes:
        model (Any): The trained ML model (e.g., scikit-learn estimator).
        model_name (str): Name of the model.
        model_description (str): Description of what the model does.
        vectorizer (Optional[Any]): Optional feature extractor or vectorizer.
        X_test (Optional[Any]): Test dataset features.
        y_test (Optional[Any]): Test dataset labels/targets.
        mse (Optional[float]): Mean Squared Error of the model.
        input_example (Optional[Any]): An example input for inference.
        signature (Optional[ModelSignature]): MLflow model signature.
    """

    model: Any
    model_name: str
    model_description: str
    vectorizer: Optional[Any] = None
    X_test: Optional[Any] = None
    y_test: Optional[Any] = None
    mse: Optional[float] = None
    input_example: Optional[Any] = None
    signature: Optional[ModelSignature] = None

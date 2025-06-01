#!/bin/sh

echo "Creating MLflow database tables..."

# Start the MLflow server with substituted variables
mlflow server --host 0.0.0.0 --port 5005 \
  --backend-store-uri postgresql+psycopg2://$MLFLOW_DB_USERNAME:$MLFLOW_DB_PASSWORD@postgres:5432/mlflow \
  --default-artifact-root /mlflow

FROM python:3.8-slim

RUN pip install --upgrade pip

RUN pip install mlflow psycopg2-binary

RUN apt-get update && apt-get install -y curl

EXPOSE 5005

WORKDIR /mlflow

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["/entrypoint.sh"]
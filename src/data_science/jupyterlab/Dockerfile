# Start from the official JupyterLab image
FROM quay.io/jupyter/datascience-notebook:notebook-7.2.2

# Update pip list of packages
RUN pip install --upgrade pip

# Install Dagster, Dagit, and other dependencies
COPY requirements.txt /opt/dagster/app/requirements.txt
RUN pip install -r /opt/dagster/app/requirements.txt

# Install mlflow_io-specific dependencies
COPY data/user_code/requirements-mlflow_io.txt /opt/mlflow_io/requirements-mlflow_io.txt
RUN pip install -r /opt/mlflow_io/requirements-mlflow_io.txt

# Set the PYTHONPATH for accessing the user_code directory
ENV PYTHONPATH="${PYTHONPATH}:/home/jovyan/work/user_code"

# Set the working directory for JupyterLab
WORKDIR /home/jovyan/work

# Set environment variables for JupyterLab
ENV JUPYTER_ENABLE_LAB=yes

# Allow JupyterLab to run as root
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
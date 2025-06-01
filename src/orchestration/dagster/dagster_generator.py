"""
This script generates the `dagster.yaml` configuration file during build time 
to avoid issues with missing the `POSTGRES_HOST_PORT` environment variable at runtime. 
Providing this variable dynamically can lead to errors (the cause unknown), 
causing failures due to a missing configuration. 

Instead of hardcoding the port, this approach ensures that the value is set 
at build time, eliminating the need to manually update it whenever it changes.
It's the safest workaround without too much tinkering with the webserver and daemon configurations.
"""

# Python
from dotenv import load_dotenv
import os

# Third-party
from jinja2 import Environment, FileSystemLoader

# Load environment variables from .env file
load_dotenv()

# Paths
output_folder = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(output_folder))

dagster_yaml_path = os.path.join(output_folder, "dagster.yaml")
template = env.get_template("dagster.yaml.jinja")


def get_int_env(var_name):
    value = os.getenv(var_name)

    if not value:
        raise ValueError(f"Missing or empty environment variable: {var_name}")

    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Environment variable {var_name} must be an integer, got '{value}'"
        )


# Validate and fetch PostgreSQL port
postgres_port = get_int_env("POSTGRES_HOST_PORT")

# Render template with validated environment variable
dagster_yaml = template.render({"POSTGRES_HOST_PORT": postgres_port})

# Write to dagster.yaml
with open(dagster_yaml_path, "w") as f:
    f.write(dagster_yaml)

print(f"dagster.yaml generated successfully at:\n{dagster_yaml_path}!")

"""
This script generates the `workspace.yaml` configuration file during build time  
because the pipeline port environment variables cannot be provided dynamically.  
In this YAML configuration, the port values must be hardcoded, and failing to do so  
would result in missing configuration errors.  

Instead of manually updating the ports, this approach ensures that the values are set  
at build time, eliminating the need to remember and change them whenever they update.  
It's the safest workaround without too much tinkering with the webserver and daemon configurations.  
"""

# Python
import os

# Third-party
from jinja2 import Environment, FileSystemLoader

# Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Paths
output_folder = os.path.dirname(os.path.abspath(__file__))

env = Environment(loader=FileSystemLoader(output_folder))

workspace_yaml_path = os.path.join(output_folder, "workspace.yaml")

template = env.get_template("workspace.yaml.jinja")


def get_int_env(var_name):
    value = os.getenv(var_name)

    # Check if the value is None or an empty string
    if not value:
        raise ValueError(f"Missing or empty environment variable: {var_name}")

    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Environment variable {var_name} must be an integer, got '{value}'"
        )


# Validate and fetch integer values
ports = {
    "AIR_QUALITY_PIPELINE_PORT": get_int_env("AIR_QUALITY_PIPELINE_PORT"),
    "HEALTH_PIPELINE_PORT": get_int_env("HEALTH_PIPELINE_PORT"),
    "SOCIAL_MEDIA_PIPELINE_PORT": get_int_env("SOCIAL_MEDIA_PIPELINE_PORT"),
    "WAREHOUSE_PIPELINE_PORT": get_int_env("WAREHOUSE_PIPELINE_PORT"),
    "TERRITORY_PIPELINE_PORT": get_int_env("TERRITORY_PIPELINE_PORT"),
    "MODELS_PIPELINE_PORT": get_int_env("MODELS_PIPELINE_PORT"),
}

# Render template with validated environment variables
workspace_yaml = template.render(ports)

# Write to workspace.yaml
with open(workspace_yaml_path, "w") as f:
    f.write(workspace_yaml)

print(f"workspace.yaml generated successfully at:\n{workspace_yaml_path}!")

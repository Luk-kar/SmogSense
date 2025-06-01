"""
Jinja2 template is used here to set up the rigid structure of the assets views.

USAGE
-----
1. Test the output of the template by running the script:
   - set the OUTPUT_DIR to OUTPUT_DIR_TEST.
2. Once the template is correct, run the script to generate the views.
   - set the OUTPUT_DIR to OUTPUT_DIR_ASSETS.

DOCUMENTATION
-------------
- https://jinja.palletsprojects.com/en/3.0.x/templates/
"""

# Python
import os

# Third-party
from jinja2 import Environment, FileSystemLoader

FILE_PATH = os.path.abspath(__file__)
FILE_PATH_DIR = os.path.dirname(FILE_PATH)

OUTPUT_DIR_ASSETS = os.path.join(
    "src", "orchestration", "dagster", "my_project", "warehouse", "assets", "views"
)
OUTPUT_DIR_TEST = os.path.join(
    "src",
    "orchestration",
    "dagster",
    "my_project",
    "warehouse",
    "assets",
    "assets_generators",
    "output",
)
OUTPUT_DIR = OUTPUT_DIR_ASSETS

env = Environment(loader=FileSystemLoader(f"{FILE_PATH_DIR}/templates"))
template = env.get_template(f"views_template.jinja")


def get_sql_view_names(directory: str):
    """
    Get a list of SQL view names (without the .sql extension) from a directory.
    """
    return [
        os.path.splitext(file)[0]  # Remove the .sql extension
        for file in os.listdir(directory)  # List all files in the directory
        if file.endswith(".sql")  # Filter for SQL files
    ]


def get_view_directories(base_dir: str):
    """
    Get a list of directories containing SQL views within the base directory.
    """
    return [
        name  # Directory name
        for name in os.listdir(base_dir)  # List all items in the base directory
        if os.path.isdir(os.path.join(base_dir, name))  # Filter for directories only
    ]


def generate_directories_structure(base_dir: str):
    """
    Generate a list of tuples containing directory names and their corresponding SQL view names.
    """
    directories = []

    for folder_name in get_view_directories(base_dir):

        folder_path = os.path.join(base_dir, folder_name)
        sql_views = get_sql_view_names(folder_path)
        directories.append((folder_name, sql_views))

    return directories


# Generate the directory structure
directories = generate_directories_structure(OUTPUT_DIR_ASSETS)

for folder_name, views in directories:

    output = template.render(
        folder_name=folder_name, sql_views=[{"name": v} for v in views]
    )

    with open(
        f"{OUTPUT_DIR}/{folder_name}.py",
        "w",
    ) as f:
        f.write(output)

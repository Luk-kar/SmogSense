"""
Used to set the root path for the tests
"""

# Python
import os
import sys


def set_root_path(sub_dir_level: int = 1):
    """
    Set the root path for the tests
    """

    absolute_root_path = get_absolute_root_path(sub_dir_level)

    current_sys_paths = sys.path

    if absolute_root_path not in current_sys_paths:
        sys.path.insert(0, absolute_root_path)
        print(f"Added {absolute_root_path} to sys.path")


def get_absolute_root_path(sub_dir_level: int = 0):
    """
    Get the absolute root path for the tests
    for the pipeline.
    """
    tests_path = __file__

    if sub_dir_level > 0:
        for level in range(sub_dir_level):
            tests_path = os.path.dirname(tests_path)

    project_path = os.path.abspath(os.path.dirname(tests_path))
    pipeline_path = os.path.join("src", "pipeline")

    absolute_root_path = os.path.abspath(os.path.join(project_path, pipeline_path))
    return absolute_root_path

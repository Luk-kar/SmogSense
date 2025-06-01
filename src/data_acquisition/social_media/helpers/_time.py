"""
This module provides helper functions related to time operations for social media data acquisition.
"""

# Python
import random


def get_random_wait_time():
    """
    Get a random wait time between 6.3 and 9.5 seconds.
    """
    return random.uniform(6.3, 9.5)

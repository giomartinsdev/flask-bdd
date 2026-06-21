"""Shared step imports — pytest-bdd requires step functions to be importable
from the test module that uses the scenario. Importing here keeps step
definitions DRY across feature files."""

from tests.steps.product_steps import *  # noqa: F401, F403

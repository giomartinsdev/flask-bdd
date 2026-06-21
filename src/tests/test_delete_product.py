from pathlib import Path
from pytest_bdd import scenarios
from tests.steps.product_steps import *  # noqa: F401, F403

scenarios(str(Path(__file__).parent / "features" / "delete_product.feature"))

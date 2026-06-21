from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parent / "scripts"


@pytest.fixture(scope="session")
def products_seed(_p_infra):
    """Insert stable data once for the entire k6 session."""
    from products.models import Product

    with _p_infra.seed_session() as s:
        s.add(Product(name="Seed Widget", category="stress", price=9.99, stock=100))


@pytest.mark.stress
def test_products_stress(k6_runner, products_seed):
    result = k6_runner.run(SCRIPTS / "products.js")
    assert result.returncode == 0, "k6 threshold violated — check output above"

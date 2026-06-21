from datetime import date
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parent / "scripts"


@pytest.fixture(scope="session")
def hr_seed(_hr_infra):
    """Insert stable data once for the entire k6 session.

    Returns seeded IDs so the k6 script can reference real records.
    """
    from hr.domain.area.model import Area
    from hr.domain.employee.model import Employee, Role

    with _hr_infra.seed_session() as s:
        area = Area(name="StressEngineering")
        s.add(area)
        s.flush()
        area_id = area.id  # capture while session is still open
        s.add(
            Employee(
                name="Seed User",
                email="seed@stress.test",
                role=Role.SENIOR,
                salary=9000,
                hire_date=date(2020, 1, 1),
                role_since=date(2022, 1, 1),
                area_id=area_id,
            )
        )
    return {"area_id": area_id}


@pytest.mark.stress
def test_employees_stress(k6_runner, hr_seed):
    result = k6_runner.run(
        SCRIPTS / "employees.js",
        extra_env={"SEED_AREA_ID": str(hr_seed["area_id"])},
    )
    assert result.returncode == 0, "k6 threshold violated — check output above"

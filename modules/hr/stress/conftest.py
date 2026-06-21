import os
import sys

_stress_dir = os.path.dirname(os.path.abspath(__file__))
_src_dir = os.path.abspath(os.path.join(_stress_dir, "..", "src"))
_lib_dir = os.path.abspath(os.path.join(_stress_dir, "..", "..", "lib"))
_pytest_bdd_utils = os.path.join(_lib_dir, "pytest-bdd-utils")
_openapi_flask_utils = os.path.join(_lib_dir, "openapi-flask-utils")

for _p in (_src_dir, _pytest_bdd_utils, _openapi_flask_utils):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flask import g
import pytest

import hr.api.areas.blueprint as area_bp_module
import hr.api.employees.blueprint as emp_bp_module
from hr.app import create_app
from hr.application.area_service import AreaApplicationService
from hr.application.employee_service import EmployeeApplicationService
from hr.application.event_bus import EventBus
from hr.db import Base
from hr.domain.area.repository import AreaRepository
from hr.domain.employee.repository import EmployeeRepository
from lib.config import BDDConfig
from lib.fixtures import k6_runner, live_server  # noqa: F401
from lib.infra import BDDInfra

_HR_QUEUE = "hr-events"
_HR_TOPIC = "hr-alerts"


@pytest.fixture(scope="session")
def _hr_config():
    return BDDConfig.from_env(
        db_base=Base,
        db_type="sqlserver",
        sqs_queues=[_HR_QUEUE],
        sns_topics=[_HR_TOPIC],
    )


@pytest.fixture(scope="session")
def _hr_infra(_hr_config):
    infra = BDDInfra.from_config(_hr_config)
    yield infra
    infra.stop()


@pytest.fixture(scope="session")
def flask_app(_hr_infra):
    """Session-scoped Flask app wired to the testcontainer DB.

    Uses Flask g for per-request session tracking so concurrent k6 VUs
    don't race on a shared list (unlike the function-scoped BDD conftest).
    TESTING is intentionally left False so Flask returns proper error
    responses instead of propagating exceptions to the HTTP client.
    """
    app = create_app(db_url=_hr_infra.db_url)

    def _make_bus() -> EventBus:
        return EventBus(
            sqs_client=_hr_infra.sqs,
            sns_client=_hr_infra.sns,
            queue_url=_hr_infra.queue_urls[_HR_QUEUE],
            topic_arn=_hr_infra.topic_arns[_HR_TOPIC],
        )

    def _patched_emp() -> EmployeeApplicationService:
        s = _hr_infra.make_session()
        g.setdefault("_sessions", []).append(s)
        return EmployeeApplicationService(
            employee_repo=EmployeeRepository(s),
            area_repo=AreaRepository(s),
            event_bus=_make_bus(),
        )

    def _patched_area() -> AreaApplicationService:
        s = _hr_infra.make_session()
        g.setdefault("_sessions", []).append(s)
        return AreaApplicationService(
            area_repo=AreaRepository(s),
            employee_repo=EmployeeRepository(s),
            event_bus=_make_bus(),
        )

    @app.teardown_request
    def _cleanup(_: Exception | None = None) -> None:
        for s in g.pop("_sessions", []):
            s.close()

    emp_bp_module._make_service = _patched_emp
    area_bp_module._make_service = _patched_area
    return app

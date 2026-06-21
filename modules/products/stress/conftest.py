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

from lib.config import BDDConfig
from lib.fixtures import k6_runner, live_server  # noqa: F401
from lib.infra import BDDInfra
from products.app import create_app
import products.blueprint as bp_module
from products.db import Base
from products.service import ProductService

_QUEUE = "products-events"
_TOPIC = "products-alerts"
_BUCKET = "products-assets"


@pytest.fixture(scope="session")
def _p_config():
    return BDDConfig.from_env(
        db_base=Base,
        sqs_queues=[_QUEUE],
        sns_topics=[_TOPIC],
        s3_buckets=[_BUCKET],
    )


@pytest.fixture(scope="session")
def _p_infra(_p_config):
    infra = BDDInfra.from_config(_p_config)
    yield infra
    infra.stop()


@pytest.fixture(scope="session")
def flask_app(_p_infra):
    """Session-scoped Flask app wired to the testcontainer DB.

    Uses Flask g for per-request session tracking so concurrent k6 VUs
    don't race on a shared list. TESTING left False for proper HTTP error responses.
    """
    app = create_app(db_url=_p_infra.db_url)

    def _patched() -> ProductService:
        s = _p_infra.make_session()
        g.setdefault("_sessions", []).append(s)
        return ProductService(
            session=s,
            sqs_client=_p_infra.sqs,
            sns_client=_p_infra.sns,
            s3_client=_p_infra.s3,
            sqs_queue_url=_p_infra.queue_urls[_QUEUE],
            sns_topic_arn=_p_infra.topic_arns[_TOPIC],
            s3_bucket=_BUCKET,
        )

    @app.teardown_request
    def _cleanup(_: Exception | None = None) -> None:
        for s in g.pop("_sessions", []):
            s.close()

    bp_module._make_service = _patched
    return app

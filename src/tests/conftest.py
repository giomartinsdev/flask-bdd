import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from lib import BDDConfig
from lib.fixtures import (  # noqa: F401 – re-export for pytest discovery
    bdd_infra, bdd_client, reset_between_tests,
    sqs_client, sns_client, s3_client, sqs_queue_url, db_tables,
)

from app import create_app
from modules.products.models import Base
from modules.products.service import ProductService
import modules.products.blueprint as bp_module

_QUEUE  = "products-events"
_TOPIC  = "products-alerts"
_BUCKET = "products-assets"


@pytest.fixture(scope="session")
def bdd_config():
    return BDDConfig.from_env(
        db_base=Base,
        sqs_queues=[_QUEUE],
        sns_topics=[_TOPIC],
        s3_buckets=[_BUCKET],
    )


@pytest.fixture
def db_tables():
    return ["products"]


@pytest.fixture
def flask_app(bdd_infra):
    app = create_app(db_url=bdd_infra.db_url)
    app.config["TESTING"] = True

    _sessions = []

    def _patched():
        s = bdd_infra.make_session()
        _sessions.append(s)
        return ProductService(
            session=s,
            sqs_client=bdd_infra.sqs,
            sns_client=bdd_infra.sns,
            s3_client=bdd_infra.s3,
            sqs_queue_url=bdd_infra.queue_urls[_QUEUE],
            sns_topic_arn=bdd_infra.topic_arns[_TOPIC],
            s3_bucket=_BUCKET,
        )

    @app.teardown_request
    def _cleanup(_=None):
        for s in _sessions:
            s.close()
        _sessions.clear()

    bp_module._make_service = _patched
    return app

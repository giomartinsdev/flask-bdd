import os
from dataclasses import dataclass, field
from typing import Any, List, Optional


class Images:
    POSTGRES = "postgres:16-alpine"
    LOCALSTACK = "localstack/localstack:3"
    SQLSERVER = "flask-bdd-mssql:latest"


@dataclass
class BDDConfig:
    db_type: str = "postgres"          # "postgres" | "sqlserver"
    sqs_queues: List[str] = field(default_factory=list)
    sns_topics: List[str] = field(default_factory=list)
    s3_buckets: List[str] = field(default_factory=list)
    aws_region: str = "us-east-1"
    db_base: Optional[Any] = None
    db_url: Optional[str] = None
    aws_endpoint: Optional[str] = None
    postgres_image: str = Images.POSTGRES
    sqlserver_image: str = Images.SQLSERVER
    localstack_image: str = Images.LOCALSTACK

    @classmethod
    def from_env(
        cls,
        db_base: Any = None,
        db_type: str = "postgres",
        sqs_queues: List[str] = None,
        sns_topics: List[str] = None,
        s3_buckets: List[str] = None,
    ) -> "BDDConfig":
        """Always starts fresh containers on random host ports.

        Does NOT read DATABASE_URL or AWS_ENDPOINT_URL from the environment —
        those are app-server variables that would pin tests to fixed ports and
        cause conflicts when multiple test sessions run concurrently.
        Use from_ci_env() if pre-provisioned services must be reused.
        """
        return cls(
            db_type=db_type,
            db_base=db_base,
            db_url=None,
            aws_endpoint=None,
            aws_region=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            sqs_queues=sqs_queues or [],
            sns_topics=sns_topics or [],
            s3_buckets=s3_buckets or [],
        )

    @classmethod
    def from_ci_env(
        cls,
        db_base: Any = None,
        db_type: str = "postgres",
        sqs_queues: List[str] = None,
        sns_topics: List[str] = None,
        s3_buckets: List[str] = None,
    ) -> "BDDConfig":
        """Reads DATABASE_URL and AWS_ENDPOINT_URL from the environment.

        Use this only in CI pipelines where the database and LocalStack are
        provisioned externally (e.g. as Docker Compose services with fixed
        service-network hostnames). In local development, use from_env() so
        that testcontainers assigns random host ports automatically.
        """
        return cls(
            db_type=db_type,
            db_base=db_base,
            db_url=os.environ.get("DATABASE_URL"),
            aws_endpoint=os.environ.get("AWS_ENDPOINT_URL"),
            aws_region=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            sqs_queues=sqs_queues or [],
            sns_topics=sns_topics or [],
            s3_buckets=s3_buckets or [],
        )

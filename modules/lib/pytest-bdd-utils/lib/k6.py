import os
from pathlib import Path
import subprocess

from pydantic import BaseModel, Field


class K6Runner(BaseModel):
    """Thin wrapper that invokes k6 as a subprocess with BASE_URL injected.

    Thresholds defined in the script's options block are the SLA gate —
    k6 exits with code 1 when any threshold is breached.

    Usage:
        result = k6_runner.run("scripts/employees.js")
        assert result.returncode == 0, result.stderr
    """

    base_url: str
    extra_env: dict[str, str] = Field(default_factory=dict)

    def run(
        self,
        script: str | Path,
        *,
        vus: int | None = None,
        duration: str | None = None,
        extra_env: dict[str, str] | None = None,
        extra_args: list[str] | None = None,
    ) -> subprocess.CompletedProcess:
        cmd = ["k6", "run"]
        if vus is not None:
            cmd += ["-u", str(vus)]
        if duration is not None:
            cmd += ["-d", duration]
        if extra_args:
            cmd += extra_args
        cmd.append(str(script))
        env = {**os.environ, "BASE_URL": self.base_url, **self.extra_env, **(extra_env or {})}
        return subprocess.run(cmd, env=env, capture_output=False, text=True)

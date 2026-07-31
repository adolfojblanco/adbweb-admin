"""Run the Lighthouse CLI as a subprocess and return a flat report.

The runner is intentionally thin: it shells out to the
``lighthouse`` binary, captures JSON on stdout, and hands the
output to :func:`parse_lighthouse_report`. If the binary is
missing or the run fails, a :class:`LighthouseReport` is returned
with ``error`` populated so the rest of the pipeline can keep
working.
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from dataclasses import asdict

from .parser import LighthouseReport, parse_lighthouse_report

log = logging.getLogger(__name__)


DEFAULT_TIMEOUT_S = 120

# ``--only-categories`` keeps the report small and focuses on what
# we actually persist. The other categories (PWA, etc.) are not
# interesting for SEO auditing.
_LIGHTHOUSE_CMD = [
    "lighthouse",
    "--output=json",
    "--output-path=stdout",
    "--only-categories=performance,accessibility,seo,best-practices",
    "--chrome-flags=--headless --no-sandbox --disable-dev-shm-usage",
    "--quiet",
    "--max-wait-for-load=45000",
]


class LighthouseNotInstalled(RuntimeError):
    """Raised when the ``lighthouse`` binary cannot be located."""


def run_lighthouse(
    url: str, *, timeout: int = DEFAULT_TIMEOUT_S
) -> LighthouseReport:
    """Run Lighthouse for ``url`` and return a parsed report.

    The function never raises for runtime errors: a failed run
    returns a :class:`LighthouseReport` with the ``error`` field
    set. The only exception is :class:`LighthouseNotInstalled`,
    which the service layer can turn into a clear message for the
    operator.
    """
    binary = shutil.which("lighthouse")
    if binary is None:
        raise LighthouseNotInstalled(
            "Lighthouse is not installed. Run `npm install -g lighthouse`."
        )

    cmd = [binary, url, *_LIGHTHOUSE_CMD]
    env = {**os.environ, "CI": "true"}

    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return _error_report(url, f"Lighthouse timed out after {timeout}s")
    except FileNotFoundError as exc:  # pragma: no cover
        raise LighthouseNotInstalled(str(exc)) from exc

    if completed.returncode != 0:
        log.warning(
            "Lighthouse exited with code %s for %s\nstderr: %s",
            completed.returncode, url, completed.stderr[:500],
        )
        return _error_report(
            url,
            completed.stderr.strip() or f"Lighthouse exited with code {completed.returncode}",
        )

    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return _error_report(url, f"Invalid Lighthouse JSON: {exc}")

    return parse_lighthouse_report(url, data)


def _error_report(url: str, error: str) -> LighthouseReport:
    return LighthouseReport(
        url=url,
        final_url=url,
        lighthouse_version="",
        user_agent="",
        performance=None,
        accessibility=None,
        seo=None,
        best_practices=None,
        cls=None,
        lcp=None,
        inp=None,
        fcp=None,
        ttfb=None,
        speed_index=None,
        error=error,
        raw={},
    )


def report_to_dict(report: LighthouseReport) -> dict:
    """Plain dict version used by tests and serializers."""
    return asdict(report)

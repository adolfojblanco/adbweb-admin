"""
Lighthouse integration.

Lighthouse is a Node.js tool, so the Python side drives it as a
subprocess. The CLI accepts JSON output, which :mod:`parser`
turns into a flat :class:`LighthouseReport`.

The dependency is not declared in ``Pipfile`` because it is a
Node package. Install it once with::

    npm install -g lighthouse

or, for a project-local install::

    cd apps/seo/lighthouse
    npm install
    export PATH="$PWD/node_modules/.bin:$PATH"
"""
from .parser import LighthouseReport, parse_lighthouse_report
from .runner import LighthouseNotInstalled, run_lighthouse

__all__ = [
    "LighthouseNotInstalled",
    "LighthouseReport",
    "parse_lighthouse_report",
    "run_lighthouse",
]

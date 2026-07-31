"""Tests for the Lighthouse integration.

The runner is tested by patching ``subprocess.run`` so the suite
stays hermetic: no real Chrome, no real network, no real
Lighthouse binary required.
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase

from apps.seo.lighthouse import (
    LighthouseNotInstalled,
    parse_lighthouse_report,
    run_lighthouse,
)
from apps.seo.lighthouse.runner import report_to_dict
from apps.seo.models import (
    LighthouseResult,
    SEOAudit,
    SEOPage,
    Website,
)
from apps.seo.services import run_lighthouse_for_page


# ---------------------------------------------------------------------- #
# Sample Lighthouse JSON (slimmed down)
# ---------------------------------------------------------------------- #
def _lighthouse_json() -> dict:
    return {
        "lighthouseVersion": "12.0.0",
        "userAgent": "Mozilla/5.0 ...",
        "finalDisplayedUrl": "https://example.com/",
        "requestedUrl": "https://example.com/",
        "categories": {
            "performance": {"score": 0.92},
            "accessibility": {"score": 0.81},
            "seo": {"score": 1.0},
            "best-practices": {"score": 0.75},
        },
        "audits": {
            "cumulative-layout-shift": {"numericValue": 0.05},
            "largest-contentful-paint": {"numericValue": 1234.5},
            "interaction-to-next-paint": {"numericValue": 120.0},
            "first-contentful-paint": {"numericValue": 800.0},
            "server-response-time": {"numericValue": 200.0},
            "speed-index": {"numericValue": 1500.0},
        },
    }


# ---------------------------------------------------------------------- #
# Parser
# ---------------------------------------------------------------------- #
class ParseLighthouseReportTests(SimpleTestCase):
    def test_extracts_scores_and_metrics(self):
        report = parse_lighthouse_report(
            "https://example.com/", _lighthouse_json()
        )
        self.assertEqual(report.performance, 92)
        self.assertEqual(report.accessibility, 81)
        self.assertEqual(report.seo, 100)
        self.assertEqual(report.best_practices, 75)
        self.assertAlmostEqual(report.cls, 0.05)
        self.assertAlmostEqual(report.lcp, 1234.5)
        self.assertAlmostEqual(report.inp, 120.0)
        self.assertAlmostEqual(report.fcp, 800.0)
        self.assertAlmostEqual(report.ttfb, 200.0)
        self.assertAlmostEqual(report.speed_index, 1500.0)
        self.assertEqual(report.lighthouse_version, "12.0.0")
        self.assertEqual(report.final_url, "https://example.com/")
        self.assertIsNone(report.error)

    def test_handles_missing_audits(self):
        data = _lighthouse_json()
        data["audits"] = {}
        report = parse_lighthouse_report("https://example.com/", data)
        for field in ("cls", "lcp", "inp", "fcp", "ttfb", "speed_index"):
            self.assertIsNone(getattr(report, field))

    def test_handles_missing_categories(self):
        data = _lighthouse_json()
        data["categories"] = {}
        report = parse_lighthouse_report("https://example.com/", data)
        for field in ("performance", "accessibility", "seo", "best_practices"):
            self.assertIsNone(getattr(report, field))


# ---------------------------------------------------------------------- #
# Runner (subprocess mocked)
# ---------------------------------------------------------------------- #
def _completed_process(stdout: str, stderr: str = "", code: int = 0):
    cp = MagicMock()
    cp.stdout = stdout
    cp.stderr = stderr
    cp.returncode = code
    return cp


class RunLighthouseTests(SimpleTestCase):
    @patch("apps.seo.lighthouse.runner.shutil.which")
    @patch("apps.seo.lighthouse.runner.subprocess.run")
    def test_returns_parsed_report(self, run, which):
        which.return_value = "/usr/local/bin/lighthouse"
        run.return_value = _completed_process(
            json.dumps(_lighthouse_json())
        )
        report = run_lighthouse("https://example.com/")
        self.assertEqual(report.performance, 92)
        self.assertIsNone(report.error)
        run.assert_called_once()
        called_cmd = run.call_args.args[0]
        self.assertEqual(called_cmd[0], "/usr/local/bin/lighthouse")
        self.assertEqual(called_cmd[1], "https://example.com/")

    @patch("apps.seo.lighthouse.runner.shutil.which", return_value=None)
    def test_raises_when_lighthouse_not_installed(self, which):
        with self.assertRaises(LighthouseNotInstalled):
            run_lighthouse("https://example.com/")

    @patch("apps.seo.lighthouse.runner.shutil.which")
    @patch("apps.seo.lighthouse.runner.subprocess.run")
    def test_swallows_non_zero_exit(self, run, which):
        which.return_value = "/usr/local/bin/lighthouse"
        run.return_value = _completed_process("", "boom", code=2)
        report = run_lighthouse("https://example.com/")
        self.assertIsNotNone(report.error)
        self.assertIn("boom", report.error)
        for field in ("performance", "cls", "lcp"):
            self.assertIsNone(getattr(report, field))

    @patch("apps.seo.lighthouse.runner.shutil.which")
    @patch("apps.seo.lighthouse.runner.subprocess.run")
    def test_handles_invalid_json(self, run, which):
        which.return_value = "/usr/local/bin/lighthouse"
        run.return_value = _completed_process("not json at all")
        report = run_lighthouse("https://example.com/")
        self.assertIsNotNone(report.error)
        self.assertIn("Invalid Lighthouse JSON", report.error)

    @patch("apps.seo.lighthouse.runner.shutil.which")
    @patch("apps.seo.lighthouse.runner.subprocess.run")
    def test_handles_timeout(self, run, which):
        import subprocess
        which.return_value = "/usr/local/bin/lighthouse"
        run.side_effect = subprocess.TimeoutExpired(cmd="lighthouse", timeout=5)
        report = run_lighthouse("https://example.com/", timeout=5)
        self.assertIn("timed out", report.error)

    def test_report_to_dict_round_trip(self):
        report = parse_lighthouse_report("https://example.com/", _lighthouse_json())
        d = report_to_dict(report)
        self.assertEqual(d["performance"], 92)
        self.assertAlmostEqual(d["cls"], 0.05)


# ---------------------------------------------------------------------- #
# Service: persistence
# ---------------------------------------------------------------------- #
class RunLighthouseServiceTests(TestCase):
    def setUp(self):
        self.website = Website.objects.create(name="Demo", domain="demo.com")
        self.audit = SEOAudit.objects.create(
            website=self.website, target_url="https://demo.com/"
        )
        self.page = SEOPage.objects.create(
            audit=self.audit,
            url="https://demo.com/",
            status_code=200,
        )

    @patch("apps.seo.services.run_lighthouse")
    def test_persists_scores_and_metrics(self, run):
        run.return_value = parse_lighthouse_report(
            "https://demo.com/", _lighthouse_json()
        )
        result = run_lighthouse_for_page(self.page.id)

        self.assertEqual(result.performance_score, 92)
        self.assertEqual(result.accessibility_score, 81)
        self.assertEqual(result.seo_score, 100)
        self.assertEqual(result.best_practices_score, 75)
        self.assertAlmostEqual(result.cls, 0.05)
        self.assertAlmostEqual(result.lcp, 1234.5)
        self.assertAlmostEqual(result.inp, 120.0)
        self.assertAlmostEqual(result.fcp, 800.0)
        self.assertAlmostEqual(result.ttfb, 200.0)
        self.assertAlmostEqual(result.speed_index, 1500.0)
        self.assertEqual(result.lighthouse_version, "12.0.0")
        self.assertEqual(result.error_message, "")

        # A fresh LighthouseResult row exists and is linked to the page.
        self.assertEqual(
            LighthouseResult.objects.filter(page=self.page).count(), 1
        )

    @patch("apps.seo.services.run_lighthouse")
    def test_runs_are_appended(self, run):
        run.return_value = parse_lighthouse_report(
            "https://demo.com/", _lighthouse_json()
        )
        run_lighthouse_for_page(self.page.id)
        run_lighthouse_for_page(self.page.id)
        self.assertEqual(
            LighthouseResult.objects.filter(page=self.page).count(), 2
        )

    @patch("apps.seo.services.run_lighthouse")
    def test_persists_error_when_lighthouse_fails(self, run):
        report = parse_lighthouse_report("https://demo.com/", _lighthouse_json())
        report.error = "Lighthouse timed out"
        for f in ("performance", "accessibility", "seo", "best_practices",
                  "cls", "lcp", "inp", "fcp", "ttfb", "speed_index"):
            setattr(report, f, None)
        run.return_value = report

        result = run_lighthouse_for_page(self.page.id)
        self.assertEqual(result.error_message, "Lighthouse timed out")
        self.assertIsNone(result.performance_score)
        self.assertIsNone(result.cls)

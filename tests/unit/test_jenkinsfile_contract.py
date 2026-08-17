"""Protect the CI behaviours that make the repository a Jenkins showcase."""

from pathlib import Path

import pytest

JENKINSFILE = Path(__file__).resolve().parents[2] / "Jenkinsfile"
DEMO_ROOT = JENKINSFILE.parent / "demo_app"


@pytest.mark.unit
def test_pipeline_exposes_expected_build_parameters() -> None:
    pipeline = JENKINSFILE.read_text(encoding="utf-8")

    for parameter in (
        "TEST_SUITE",
        "EXECUTION_TARGET",
        "BROWSER",
        "HEADLESS",
        "WORKERS",
    ):
        assert f"name: '{parameter}'" in pipeline


@pytest.mark.unit
def test_pipeline_publishes_results_even_after_failure() -> None:
    pipeline = JENKINSFILE.read_text(encoding="utf-8")

    assert "post {\n        always {" in pipeline
    assert "junit allowEmptyResults: true" in pipeline
    assert "publishHTML target:" in pipeline
    assert "archiveArtifacts allowEmptyArchive: true" in pipeline
    assert "cleanWs deleteDirs: true" in pipeline


@pytest.mark.unit
def test_cloud_credentials_use_jenkins_binding() -> None:
    pipeline = JENKINSFILE.read_text(encoding="utf-8")

    assert "withCredentials([usernamePassword(" in pipeline
    assert "credentialsId: 'lambdatest-credentials'" in pipeline


@pytest.mark.unit
def test_remote_acceptance_target_is_self_contained() -> None:
    from tests.support.inline_page import build_inline_page

    page = build_inline_page(DEMO_ROOT)

    assert page.startswith("data:text/html;charset=utf-8,")
    assert "styles.css" not in page
    assert "app.js" not in page

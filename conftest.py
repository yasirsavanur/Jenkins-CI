"""pytest CLI, WebDriver lifecycle, and Jenkins-friendly failure evidence."""

from __future__ import annotations

import os
import re
from collections.abc import Generator
from contextlib import suppress
from pathlib import Path

import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

from pipeline_suite.config import SUPPORTED_BROWSERS, SUPPORTED_TARGETS, RunSettings
from pipeline_suite.driver_factory import DriverFactory
from tests.support.demo_server import RunningDemoServer, start_demo_server
from tests.support.inline_page import build_inline_page


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("pipeline acceptance")
    group.addoption(
        "--target",
        choices=SUPPORTED_TARGETS,
        default=os.getenv("TEST_TARGET", "local"),
        help="WebDriver execution target",
    )
    group.addoption(
        "--browser",
        choices=SUPPORTED_BROWSERS,
        default=os.getenv("BROWSER", "chrome"),
    )
    group.addoption("--headed", action="store_true", help="Show a local browser window")
    group.addoption("--base-url", help="Override the acceptance target URL")
    group.addoption("--build-name", default="local development", help="Cloud build label")
    group.addoption("--timeout", type=float, default=10.0, help="Explicit wait timeout")
    group.addoption("--reports-dir", default="reports", help="Failure evidence directory")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"report_{report.when}", report)


@pytest.fixture(scope="session")
def demo_server() -> Generator[RunningDemoServer, None, None]:
    root = Path(__file__).resolve().parent / "demo_app"
    server = start_demo_server(root)
    yield server
    server.close()


@pytest.fixture
def run_settings(request: pytest.FixtureRequest, pytestconfig: pytest.Config) -> RunSettings:
    return RunSettings(
        target=pytestconfig.getoption("--target"),
        browser=pytestconfig.getoption("--browser"),
        headless=not pytestconfig.getoption("--headed"),
        mobile=request.node.get_closest_marker("mobile") is not None,
        test_name=request.node.name,
        build_name=pytestconfig.getoption("--build-name"),
        timeout=pytestconfig.getoption("--timeout"),
        reports_dir=Path(pytestconfig.getoption("--reports-dir")),
    )


@pytest.fixture
def base_url(
    run_settings: RunSettings,
    pytestconfig: pytest.Config,
    request: pytest.FixtureRequest,
) -> str:
    override = pytestconfig.getoption("--base-url")
    if override:
        return override.rstrip("/")
    if run_settings.target == "lambdatest":
        root = Path(__file__).resolve().parent / "demo_app"
        return build_inline_page(root)
    server = request.getfixturevalue("demo_server")
    return server.url


@pytest.fixture
def driver(
    request: pytest.FixtureRequest,
    run_settings: RunSettings,
) -> Generator[WebDriver, None, None]:
    web_driver = DriverFactory(run_settings).create()
    yield web_driver

    report = getattr(request.node, "report_call", None)
    if report and report.failed:
        _save_failure_evidence(web_driver, request.node.nodeid, run_settings.reports_dir)
    if run_settings.target == "lambdatest" and report:
        _set_cloud_status(web_driver, passed=report.passed)
    with suppress(WebDriverException):
        web_driver.quit()


def _save_failure_evidence(driver: WebDriver, node_id: str, reports_dir: Path) -> None:
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", node_id).strip("_")
    reports_dir.mkdir(parents=True, exist_ok=True)
    driver.save_screenshot(str(reports_dir / f"{safe_name}.png"))
    (reports_dir / f"{safe_name}.html").write_text(driver.page_source, encoding="utf-8")


def _set_cloud_status(driver: WebDriver, *, passed: bool) -> None:
    status = "passed" if passed else "failed"
    with suppress(WebDriverException):
        driver.execute_script(f"lambda-status={status}")

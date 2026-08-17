"""Selenium option and credential binding tests without real sessions."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from selenium import webdriver

from pipeline_suite.config import RunSettings
from pipeline_suite.driver_factory import ConfigurationError, DriverFactory


@dataclass
class FakeDriver:
    window_size: tuple[int, int] | None = None
    page_timeout: int | None = None

    def set_window_size(self, width: int, height: int) -> None:
        self.window_size = (width, height)

    def set_page_load_timeout(self, timeout: int) -> None:
        self.page_timeout = timeout


@pytest.mark.unit
def test_local_mobile_session_uses_chrome_emulation(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}
    fake_driver = FakeDriver()

    def create_chrome(*, options):
        captured["options"] = options
        return fake_driver

    monkeypatch.setattr(webdriver, "Chrome", create_chrome)
    settings = RunSettings(browser="chrome", mobile=True)

    driver = DriverFactory(settings).create()

    assert driver is fake_driver
    assert captured["options"].experimental_options["mobileEmulation"] == {"deviceName": "Pixel 5"}
    assert fake_driver.window_size == (1440, 1000)
    assert fake_driver.page_timeout == 45


@pytest.mark.unit
def test_cloud_session_uses_options_and_encoded_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = {}
    fake_driver = FakeDriver()

    def create_remote(*, command_executor, options):
        captured.update(url=command_executor, options=options)
        return fake_driver

    monkeypatch.setattr(webdriver, "Remote", create_remote)
    monkeypatch.setenv("LT_USERNAME", "qa user")
    monkeypatch.setenv("LT_ACCESS_KEY", "key/with?symbols")
    settings = RunSettings(
        target="lambdatest",
        test_name="checkout test",
        build_name="Jenkins #42",
    )

    driver = DriverFactory(settings).create()

    assert driver is fake_driver
    assert captured["url"].startswith("https://qa%20user:key%2Fwith%3Fsymbols@")
    cloud_options = captured["options"].capabilities["LT:Options"]
    assert cloud_options["name"] == "checkout test"
    assert cloud_options["build"] == "Jenkins #42"


@pytest.mark.unit
def test_cloud_session_requires_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LT_USERNAME", raising=False)
    monkeypatch.delenv("LT_ACCESS_KEY", raising=False)

    with pytest.raises(ConfigurationError, match="LT_USERNAME and LT_ACCESS_KEY"):
        DriverFactory(RunSettings(target="lambdatest")).create()

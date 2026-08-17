"""Create local or LambdaTest WebDriver sessions with Selenium 4 options."""

from __future__ import annotations

import os
from urllib.parse import quote, urlsplit, urlunsplit

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver

from pipeline_suite.config import RunSettings

DEFAULT_LT_GRID = "https://hub.lambdatest.com/wd/hub"
MOBILE_EMULATION = {
    "deviceMetrics": {
        "width": 393,
        "height": 851,
        "pixelRatio": 3.0,
        "mobile": True,
        "touch": True,
    },
    "clientHints": {"platform": "Android", "mobile": True},
}


class ConfigurationError(RuntimeError):
    """Raised when a selected execution target is not configured."""


class DriverFactory:
    def __init__(self, settings: RunSettings) -> None:
        self.settings = settings

    def create(self) -> WebDriver:
        options = self._browser_options()
        if self.settings.target == "lambdatest":
            self._add_lambdatest_capabilities(options)
            driver = webdriver.Remote(
                command_executor=self._authenticated_grid_url(),
                options=options,
            )
        elif self.settings.browser == "chrome":
            driver = webdriver.Chrome(options=options)
        else:
            driver = webdriver.Firefox(options=options)

        driver.set_window_size(1440, 1000)
        driver.set_page_load_timeout(45)
        return driver

    def _browser_options(self) -> ChromeOptions | FirefoxOptions:
        if self.settings.browser == "chrome":
            options = ChromeOptions()
            chrome_binary = os.getenv("CHROME_BINARY")
            if chrome_binary:
                options.binary_location = chrome_binary
            if self.settings.headless:
                options.add_argument("--headless=new")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            if self.settings.mobile:
                options.add_experimental_option("mobileEmulation", MOBILE_EMULATION)
        else:
            options = FirefoxOptions()
            if self.settings.headless:
                options.add_argument("-headless")

        options.set_capability("acceptInsecureCerts", True)
        return options

    def _add_lambdatest_capabilities(
        self,
        options: ChromeOptions | FirefoxOptions,
    ) -> None:
        options.browser_version = "latest"
        options.platform_name = os.getenv("LT_PLATFORM", "Windows 11")
        options.set_capability(
            "LT:Options",
            {
                "build": self.settings.build_name,
                "name": self.settings.test_name,
                "project": self.settings.project_name,
                "network": True,
                "video": True,
            },
        )

    @staticmethod
    def _authenticated_grid_url() -> str:
        username = os.getenv("LT_USERNAME")
        access_key = os.getenv("LT_ACCESS_KEY")
        if not username or not access_key:
            raise ConfigurationError("LambdaTest execution requires LT_USERNAME and LT_ACCESS_KEY")

        raw_url = os.getenv("LT_GRID_URL", DEFAULT_LT_GRID)
        parts = urlsplit(raw_url)
        if not parts.hostname:
            raise ConfigurationError(f"Invalid LT_GRID_URL: {raw_url}")
        port = f":{parts.port}" if parts.port else ""
        credentials = f"{quote(username, safe='')}:{quote(access_key, safe='')}@"
        return urlunsplit(
            (parts.scheme, f"{credentials}{parts.hostname}{port}", parts.path, parts.query, "")
        )

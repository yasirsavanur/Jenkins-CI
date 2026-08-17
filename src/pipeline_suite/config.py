"""Validated settings for local and cloud test sessions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SUPPORTED_BROWSERS = ("chrome", "firefox")
SUPPORTED_TARGETS = ("local", "lambdatest")


@dataclass(frozen=True, slots=True)
class RunSettings:
    target: str = "local"
    browser: str = "chrome"
    headless: bool = True
    mobile: bool = False
    test_name: str = "selenium test"
    build_name: str = "local development"
    project_name: str = "Jenkins Selenium Pipeline"
    timeout: float = 10.0
    reports_dir: Path = Path("reports")

    def __post_init__(self) -> None:
        target = self.target.lower()
        browser = self.browser.lower()
        if target not in SUPPORTED_TARGETS:
            raise ValueError(f"Unsupported target '{self.target}'")
        if browser not in SUPPORTED_BROWSERS:
            raise ValueError(f"Unsupported browser '{self.browser}'")
        if self.mobile and browser != "chrome":
            raise ValueError("The mobile profile requires Chrome")
        if self.timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "browser", browser)
        object.__setattr__(self, "reports_dir", Path(self.reports_dir))

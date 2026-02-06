from __future__ import annotations

import os
import pytest
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from config.lt_capabilities import desktop_capabilities, mobile_emulation_capabilities


LT_HUB = "https://{user}:{key}@hub.lambdatest.com/wd/hub"


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing environment variable {name}. "
            "Set LT_USERNAME and LT_ACCESS_KEY before running."
        )
    return value


@pytest.fixture(scope="function")
def driver(request) -> WebDriver:
    username = _require_env("LT_USERNAME")
    access_key = _require_env("LT_ACCESS_KEY")

    test_name = request.node.name
    is_mobile = request.node.get_closest_marker("mobile") is not None

    caps = mobile_emulation_capabilities(test_name) if is_mobile else desktop_capabilities(test_name)
    remote_url = LT_HUB.format(user=username, key=access_key)

    drv = webdriver.Remote(command_executor=remote_url, desired_capabilities=caps)
    drv.set_page_load_timeout(60)
    drv.implicitly_wait(10)

    yield drv

    try:
        drv.quit()
    except Exception:
        pass

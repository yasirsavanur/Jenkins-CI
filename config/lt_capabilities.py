from __future__ import annotations

def desktop_capabilities(test_name: str) -> dict:
    # LambdaTest W3C capabilities (Selenium 4 style)
    # Adjust browser/platform versions as needed.
    return {
        "browserName": "Chrome",
        "browserVersion": "latest",
        "platformName": "Windows 11",
        "LT:Options": {
            "project": "LambdaTest - pytest selenium",
            "build": "local",
            "name": test_name,
            "selenium_version": "4.0.0",
            "w3c": True,
        },
    }


def mobile_emulation_capabilities(test_name: str) -> dict:
    # Lightweight approach: Chrome mobile emulation in a regular Selenium session.
    # This avoids Appium and keeps setup simple.
    return {
        "browserName": "Chrome",
        "browserVersion": "latest",
        "platformName": "Windows 11",
        "goog:chromeOptions": {
            "mobileEmulation": {"deviceName": "Pixel 5"}
        },
        "LT:Options": {
            "project": "LambdaTest - pytest selenium",
            "build": "local",
            "name": test_name,
            "selenium_version": "4.0.0",
            "w3c": True,
        },
    }

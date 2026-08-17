"""Fast validation for build parameter combinations."""

import pytest

from pipeline_suite.config import RunSettings


@pytest.mark.unit
def test_settings_normalise_cli_values() -> None:
    settings = RunSettings(target="LOCAL", browser="FIREFOX", timeout=3)

    assert settings.target == "local"
    assert settings.browser == "firefox"
    assert settings.timeout == 3


@pytest.mark.unit
@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"target": "unknown"}, "Unsupported target"),
        ({"browser": "safari"}, "Unsupported browser"),
        ({"browser": "firefox", "mobile": True}, "requires Chrome"),
        ({"timeout": 0}, "greater than zero"),
    ],
)
def test_settings_reject_invalid_build_parameters(overrides: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        RunSettings(**overrides)

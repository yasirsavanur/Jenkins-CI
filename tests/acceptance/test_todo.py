"""Browser journeys selected by Jenkins build parameters."""

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pipeline_suite.config import RunSettings
from pipeline_suite.pages import TodoPage


@pytest.mark.smoke
@pytest.mark.regression
def test_user_can_add_a_pipeline_task(
    driver: WebDriver,
    base_url: str,
    run_settings: RunSettings,
) -> None:
    todo = TodoPage(driver, base_url, run_settings.timeout)

    todo.load()
    todo.add_task("Publish JUnit results")

    assert todo.has_task("Publish JUnit results")


@pytest.mark.regression
@pytest.mark.parametrize(
    "task",
    ["Archive failure evidence", "Promote a green build"],
)
def test_user_can_complete_a_pipeline_task(
    driver: WebDriver,
    base_url: str,
    run_settings: RunSettings,
    task: str,
) -> None:
    todo = TodoPage(driver, base_url, run_settings.timeout)

    todo.load()
    todo.add_task(task)
    todo.complete_task(task)

    assert "done-true" in todo.task_class(task)


@pytest.mark.mobile
def test_core_flow_works_in_the_mobile_profile(
    driver: WebDriver,
    base_url: str,
    run_settings: RunSettings,
) -> None:
    todo = TodoPage(driver, base_url, run_settings.timeout)

    todo.load()
    todo.add_task("Verify responsive acceptance flow")

    assert todo.has_task("Verify responsive acceptance flow")

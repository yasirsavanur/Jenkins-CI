"""User-level actions for the Todo acceptance target."""

from __future__ import annotations

from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait


def _xpath_literal(value: str) -> str:
    if '"' not in value:
        return f'"{value}"'
    if "'" not in value:
        return f"'{value}'"
    parts = value.split('"')
    return "concat(" + ", '\"', ".join(f'"{part}"' for part in parts) + ")"


class TodoPage:
    INPUT = (By.ID, "sampletodotext")
    ADD_BUTTON = (By.ID, "addbutton")

    def __init__(self, driver: WebDriver, base_url: str, timeout: float = 10.0) -> None:
        self.driver = driver
        self.base_url = base_url if base_url.startswith("data:") else base_url.rstrip("/") + "/"
        self.wait = WebDriverWait(driver, timeout)

    def load(self) -> None:
        target = (
            self.base_url
            if self.base_url.startswith("data:")
            else urljoin(self.base_url, "index.html")
        )
        self.driver.get(target)
        self.wait.until(conditions.element_to_be_clickable(self.INPUT))

    def add_task(self, task: str) -> None:
        field = self.wait.until(conditions.element_to_be_clickable(self.INPUT))
        field.clear()
        field.send_keys(task)
        self.wait.until(conditions.element_to_be_clickable(self.ADD_BUTTON)).click()
        self.wait.until(conditions.visibility_of_element_located(self._task_label(task)))

    def complete_task(self, task: str) -> None:
        self.wait.until(conditions.element_to_be_clickable(self._task_checkbox(task))).click()
        self.wait.until(lambda _driver: "done-true" in self.task_class(task))

    def has_task(self, task: str) -> bool:
        return bool(self.driver.find_elements(*self._task_label(task)))

    def task_class(self, task: str) -> str:
        return self.driver.find_element(*self._task_label(task)).get_attribute("class") or ""

    @staticmethod
    def _task_label(task: str) -> tuple[str, str]:
        text = _xpath_literal(task)
        return By.XPATH, f"//li//span[normalize-space()={text}]"

    @staticmethod
    def _task_checkbox(task: str) -> tuple[str, str]:
        text = _xpath_literal(task)
        return By.XPATH, f"//li[.//span[normalize-space()={text}]]//input[@type='checkbox']"

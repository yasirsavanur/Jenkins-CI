import pytest
from tests._common import run_todo_flow

@pytest.mark.single
@pytest.mark.regression
def test_basic_todo_3(driver):
    run_todo_flow(driver, "Yasir says hello from pytest 3")

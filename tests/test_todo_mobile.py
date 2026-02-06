import pytest
from tests._common import run_todo_flow

@pytest.mark.mobile
@pytest.mark.regression
def test_basic_todo_mobile(driver):
    run_todo_flow(driver, "Yasir says hello from mobile emulation")

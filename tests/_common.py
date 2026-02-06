from selenium.webdriver.common.by import By

URL = "https://lambdatest.github.io/sample-todo-app/"

def run_todo_flow(driver, final_text: str):
    driver.get(URL)

    # Click list items
    driver.find_element(By.NAME, "li1").click()
    driver.find_element(By.NAME, "li2").click()
    driver.find_element(By.NAME, "li3").click()
    driver.find_element(By.NAME, "li4").click()
    driver.find_element(By.NAME, "li5").click()

    # Add new items
    driver.find_element(By.ID, "sampletodotext").send_keys("Yey, Let's add it to list")
    driver.find_element(By.ID, "addbutton").click()

    driver.find_element(By.ID, "sampletodotext").send_keys(final_text)
    driver.find_element(By.ID, "addbutton").click()

    # Assert final item
    # Matches the intent of the Java XPath assert
    element = driver.find_element(By.XPATH, "//span[@class='done-false']")
    assert element.text == final_text

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time

# Start browser
driver = webdriver.Chrome()

driver.get("http://localhost:5173/demo")

time.sleep(3)

actions = ActionChains(driver)

# Move to initial position
actions.move_by_offset(100, 200).perform()

# Straight robotic movement
for i in range(200):
    actions.move_by_offset(5, 0)
    actions.perform()
    time.sleep(0.01)

print("Bot movement completed")

time.sleep(5)
driver.quit()

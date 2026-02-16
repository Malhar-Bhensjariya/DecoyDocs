from selenium import webdriver
import time

driver = webdriver.Chrome()
driver.get("http://localhost:3000/demo")

time.sleep(3)

# Straight robotic movement
for i in range(200):
    driver.execute_script("""
        document.dispatchEvent(new MouseEvent('mousemove', {
            clientX: arguments[0],
            clientY: arguments[1],
            bubbles: true
        }));
    """, 100 + i * 3, 250)

    time.sleep(0.01)

print("Bot finished movement")

time.sleep(5)
driver.quit()

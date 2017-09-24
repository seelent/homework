from selenium import webdriver
import time

driver = webdriver.Firefox()
driver.implicitly_wait(10)

try:
    driver.get('http://127.0.0.1:8080/litecard/admin')
    driver.find_element_by_name('username').send_keys('admin')
    driver.find_element_by_name('password').send_keys('admin')
    driver.find_element_by_name('login').click()
    driver.quit()
except Exception as e:
    print('Something gone wrong: {}'.format(e))
    driver.quit()

import pytest
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

@pytest.fixture
def driver(request):
    wd = webdriver.Firefox()
    print(wd.capabilities)
    request.addfinalizer(wd.quit)
    return wd


def test_example(driver):
    driver.get("http://www.google.com/")
    field = driver.find_element_by_name('q')
    field.send_keys("webdriver")
    field.send_keys(Keys.ENTER)
    WebDriverWait(driver, 10).until(EC.title_is("webdriver - Поиск в Google"))
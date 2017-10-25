from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import re, time

class Page:
    def __init__(self, close=True, write=False, timeout=3, product_limit=3):
        self.starting_page_url = 'http://localhost:8080/litecard/admin/'
        self.total_price = 0
        self.product_links = []
        self.write = write
        self.close_browser = close
        self.capabilities = DesiredCapabilities.CHROME
        self.capabilities['loggingPrefs'] = { 'browser':'ALL' }
        self.driver = webdriver.Chrome(desired_capabilities=self.capabilities)
        self.wait = WebDriverWait(driver=self.driver, timeout=timeout).until
        self.driver.get(self.starting_page_url)
        self.driver.find = self.driver.find_elements_by_css_selector
        self.driver.xfind = self.driver.find_elements_by_xpath
        self.selectors = {
            'body':'body',
            'user_field':'div#box-login [name=username]',
            'password_field':'div#box-login [name=password]',
            'login_button':'div#box-login [name=login]',
            'catalog':'//ul[@id="box-apps-menu"]//a[contains(@href, "catalog")]',
            'products':'//form[@name="catalog_form"]//a[contains(text(), "Rubber Ducks")]',
            'product_rows': '//table[@class="dataTable"]//tr[@class="row"]//a[contains(@href, "product_id")]'
        }


    def authorizate(self):
        user_field = self.wait_n_get('user_field')
        user_field[0].send_keys('admin')
        password_field = self.wait_n_get('password_field')
        password_field[0].send_keys('admin')
        login_button = self.wait_n_get('login_button')
        login_button[0].click()

    def wait_n_get(self, selector):
        #print('\n# Waiting for {}'.format(selector))
        selector = self.selectors[selector]
        if re.search('.*//.*', selector):
            #if self.write:
                #print('# Using xpath selector')
            return self.wait(lambda d: d.xfind('{}'.format(selector)))
        else:
            #if self.write:
                #print('# Using css selector')
            return self.wait(lambda d: d.find('{}'.format(selector)))

    def click_link(self, link):
        self.xfind('//table[@class="dataTable"]//a[contains(@href, "{}")]'.format(link))[0].click()

    def click(self, selector):
        print('\n# Clicking on {}'.format(selector))
        if self.write:
            print('# Used selector: {}'.format(self.selectors[selector]))

        objs = self.wait_n_get(selector)

        if self.write:
            print('# Qty of discovered objs: {}'.format(len(objs)))

        objs[0].click()


    def move_to(self, name):
        self.driver.switch_to.window(self.current_window_dict[name])

    def check_log(self):
        log = self.driver.get_log("browser")
        if len(log)>0:
            for entry in log:
                print("Entry = {}".format(entry))
            raise Exception('Some Entries In Log')


    def __getattr__(self, item):
        if hasattr(self.driver, item):
            return getattr(self.driver, item)
        else:
            raise Exception('Page objeect has not such attribute: {}'.format(item))

    def close(self):
        cur_id = self.driver.current_window_handle
        for i in self.current_window_dict:
            if cur_id == self.current_window_dict[i]:
                print ('Current page: {}'.format(i))
        if self.close_browser:
            self.driver.close()



page = None
try:
    page = Page(close=True, write=True)
    page.authorizate()
    page.click('catalog')
    page.click('products')
    for link in page.wait_n_get('product_rows'):
        link.click()
        page.check_log()
        page.click('catalog')
        page.click('products')
    page.driver.quit()
except Exception as e:
    page.close()
    raise e
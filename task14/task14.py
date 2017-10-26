from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

import re, time

class Page:
    def __init__(self, close=True, write=False, timeout=3, product_limit=3):
        self.starting_page_url = 'http://localhost:8080/litecard/admin/'
        self.total_price = 0
        self.current_window_ids = []
        self.current_window_dict = {}
        self.products_in_cart_qty = 0
        self.product_limit = product_limit
        self.write = write
        self.close_browser = close
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(driver=self.driver, timeout=timeout).until
        self.driver.get(self.starting_page_url)
        self.driver.find = self.driver.find_elements_by_css_selector
        self.driver.xfind = self.driver.find_elements_by_xpath
        self.selectors = {
            'body':'body',
            'user_field':'div#box-login [name=username]',
            'password_field':'div#box-login [name=password]',
            'login_button':'div#box-login [name=login]',
            'countries':'//ul[@id="box-apps-menu"]//a[contains(@href, "countries")]',
            'add_new_country':'//td[@id = "content"]//a[@class="button"][contains(@href, "edit_country")]'
        }

        self.select_variants = [
            'Small',
            'Medium +$2.50',
            'Large +$5'
        ]

    def authorizate(self):
        user_field = self.wait_n_get('user_field')
        user_field[0].send_keys('admin')
        password_field = self.wait_n_get('password_field')
        password_field[0].send_keys('admin')
        login_button = self.wait_n_get('login_button')
        login_button[0].click()

    def click_all_links(self):
        self.link_parts = self.xfind('//form[@method="post"]//a[not(contains(@id,"hint"))]')
        print('Link qty: {}'.format(len(self.link_parts)))
        for link in self.link_parts:
            self.current_window_ids = []
            self.current_window_dict = {}
            self.remember_new_window_as('main')
            link.click()
            self.remember_new_window_as('new_link')
            self.move_to('new_link')
            self.wait_n_get('body')
            self.close()
            self.move_to('main')

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

    def click(self, selector):
        print('\n# Clicking on {}'.format(selector))
        if self.write:
            print('# Used selector: {}'.format(self.selectors[selector]))

        objs = self.wait_n_get(selector)

        if self.write:
            print('# Qty of discovered objs: {}'.format(len(objs)))

        objs[0].click()


    def select(self, selector, text, raise_on_fail=False):
        print('\n# Selecting {} from {}'.format(text, selector))
        if self.write:
            print('# Used selector: {}'.format(self.selectors[selector]))
        for variant in self.select_variants:
            if re.search('.*{}.*'.format(text), variant):
                text = variant
                print('# I\'ll use {} from select menu'.format(text))
                break
            else:
                'There\'s NO suitable variant'
        try:
            Select(self.wait_n_get(selector)[0]).select_by_visible_text(text)
        except Exception as e:
            if raise_on_fail:
                raise e
            else:
                print(e)
                pass

    def remember(self, selector, save_text_to=None):
        print('\n# Remembering {}'.format(selector))
        element = self.wait_n_get(selector)[0]
        setattr(self, selector, element)
        if save_text_to is not None:
            setattr(self, save_text_to, element.get_attribute('textContent'))

    def wait_refreshing(self, page_element, old_value=None, absence_is_ok=False):
        #print('\n# Waiting fo refresh of {}'.format(page_element))
        try:
            if old_value != None:
                init_value = getattr(self, old_value)
                while True:
                    current_value = self.wait_n_get(page_element)[0].get_attribute('textContent')
                    if current_value != init_value:
                        break
            else:
                self.wait(EC.staleness_of(self.wait_n_get(page_element)[0]))
                self.wait_n_get(page_element)

        except Exception as e:
            print('# {} is absent'.format(page_element))
            if absence_is_ok:
                return True
            else:
                raise e

    def count_pcs_in_table(self):
        print('\n# Counting pcs in table')
        qty = 0
        for row in self.wait_n_get('total_table_pcs_qty'):
            qty += int(row.get_attribute('textContent'))
        print('# Qty in table: ' + str(qty))
        return qty

    def set_value(self, selector, value):
        print('\n# Sending value {} in {}'.format(value, selector))
        field = self.wait_n_get(selector)[0]
        field.send_keys(Keys.ESCAPE)
        field.send_keys(Keys.DELETE)
        field.send_keys(value)

    def compare(self, *args, raise_ex=False):
        print('\n# Comparing {}'.format(args))
        value = args[0]
        for arg in args:
            if arg != value and raise_ex:
                raise Exception('Compared items not equivalent!')
            elif arg != value and not raise_ex:
                print('!!!!!!!!!!!!!!!!! Compared items not equivalent!\n\n')

    def check_successful(self):
        try:
            final_phrase = self.wait_n_get('successful')[0].get_attribute('textContent')
            if final_phrase == 'There are no items in your cart.':
                print('\n\n\n\n Test completed')
            else:
                raise Exception
        except Exception as ex:
            print('\n\n\n\n Final check was not successful')
            raise ex

    def remember_new_window_as(self, name):
        self.current_window_dict[name] = list(set(self.driver.window_handles) - set(self.current_window_ids))[0]
        self.current_window_ids = self.driver.window_handles

    def move_to(self, name):
        self.driver.switch_to.window(self.current_window_dict[name])

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
    page.click('countries')
    page.click('add_new_country')
    page.click_all_links()
    page.driver.quit()

except Exception as e:
    page.close()
    raise e

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

import re

class Page:
    def __init__(self, close=True, write=False, timeout=3, product_limit=3):
        self.total_price = 0
        self.products_in_cart_qty = 0
        self.product_limit = product_limit
        self.write = write
        self.close_browser = close
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(driver=self.driver, timeout=timeout).until
        self.driver.get('http://localhost:8080/litecard/en/')
        self.driver.find = self.driver.find_elements_by_css_selector
        self.driver.xfind = self.driver.find_elements_by_xpath
        self.selectors = {
            'first_product': 'ul.listing-wrapper.products a.link',
            'add_to_cart_button': 'div.buy_now button[type=submit][name=add_cart_product]',
            'size': '//div[contains(@class, "buy_now")]//select[contains(@name, "Size")]',
            'qty': 'div#cart a.content span.quantity',
            'home': '//nav[@id="breadcrumbs"]//a[contains(text(), "Home")]',
            'checkout': '//header[@id="header"]//div[@id="cart"]//a[contains(text(),"Checkout")]',
            'products_in_cart_qty': 'ul.shortcuts li',
            'product_table_total_price': 'div#box-checkout-summary tr.footer td:not([colspan]) strong',
            'total_table_pcs_qty': '//div[@id="order_confirmation-wrapper"]//tr//td[contains(@class, "unit-cost")]'
                                   '/../td[not(@class)]',
            'del_from_cart_button': 'button[type=submit][name=remove_cart_item]',
            'qty_of_products_field_in_cart': 'input[type=number][name=quantity]',
            'successful':'div#checkout-cart-wrapper>p>em'
        }
        self.select_variants = [
            'Small',
            'Medium +$2.50',
            'Large +$5'
        ]


    def wait_n_get(self, selector):
        print('\n# Waiting for {}'.format(selector))
        selector = self.selectors[selector]
        if re.search('.*//.*', selector):
            if self.write:
                print('# Using xpath selector')
            return self.wait(lambda d: d.xfind('{}'.format(selector)))
        else:
            if self.write:
                print('# Using css selector')
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
        print('\n# Waiting fo refresh of {}'.format(page_element))
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

    def close(self):
        if self.close_browser:
            self.driver.close()



page = None
try:
    page = Page(close=False, write=True)
    for i in range(0, page.product_limit):
        page.remember('qty', save_text_to='remembered_qty')
        page.click('first_product')
        page.select('size', 'Medium')
        page.click('add_to_cart_button')
        page.wait_refreshing('qty', old_value='remembered_qty')
        page.click('home')
    page.click('checkout')
    page.compare(page.count_pcs_in_table(), page.product_limit, raise_ex=True)
    for i in range(0, page.product_limit):
        page.remember('product_table_total_price', save_text_to='total_price')
        page.set_value('qty_of_products_field_in_cart', '1')
        page.click('del_from_cart_button')
        if page.wait_refreshing('product_table_total_price', absence_is_ok=True):
            break
    page.check_successful()
    page.close()
except Exception as e:
    page.close()
    raise e

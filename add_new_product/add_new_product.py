from selenium import webdriver
from selenium.webdriver.support.select import Select
import time
import os

class Admin_page:
    def __init__(self, driver, browser):
        self.driver = driver
        self.find = self.driver.find_elements_by_css_selector
        self.xfind = self.driver.find_elements_by_xpath
        self.driver.get('http://localhost:8080/litecard/admin')
        self.user_field = self.find('div#box-login [name=username]')[0]
        self.password_field = self.find('div#box-login [name=password]')[0]
        self.login_button = self.find('div#box-login [name=login]')[0]
        self.product_name = '{} Brand New Coala'.format(browser)

        self.browser = browser
        self.cur_func = ''
        self.dates = {
            'FireFox':
                {
                    'date_valid_from': '2017-10-08',
                    'date_valid_to': '2017-10-08'
                },
            'Chrome':
                {
                    'date_valid_from': '08-10-2017',
                    'date_valid_to': '09-10-2017'
                },
            'Ie':
                {
                    'date_valid_from': '2017-10-08',
                    'date_valid_to': '2017-10-08'
                }
        }

    def authorization(self):
        self.cur_func = 'authorization'
        self.user_field.send_keys('admin')
        self.password_field.send_keys('admin')
        self.login_button.click()

    def go_to_section(self, section):
        self.cur_func = 'go_to_section {}'.format(section)
        self.xfind('//div[@id="box-apps-menu-wrapper"]//span[.="{}"]/../../a'.format(section))[0].click()

    def click_button_in_catalog(self, name):
        time.sleep(3)
        self.cur_func = 'click_button_in_catalog {}'.format(name)
        self.xfind('//td[@id="content"]//a[@class="button"][contains(text(),"{}")]'.format(name))[0].click()

    def fill_general(self):
        self.cur_func = 'fill_general'
        print('fill General')
        self.xfind('//div[@id="tab-general"]//label[contains(text(),"Enabled")]/input[@name="status"]')[0].click()
        self.find('div#tab-general input[name="name[en]"]')[0].send_keys(self.product_name)
        self.find('div#tab-general input[name="code"]')[0].send_keys('1986')
        ###Input qty###
        self.find('div#tab-general input[name=quantity]')[0].clear()
        self.find('div#tab-general input[name=quantity]')[0].send_keys('1.5')
        ###UploadImage###
        self.find('input[type=file]')[0].send_keys(os.path.join(os.getcwd(), 'my_lovely_coala.jpg'))
        ###Set_date###
        self.find('input[type=date]'
                  '[name=date_valid_from]')[0].send_keys('{}'.format(self.dates[self.browser]['date_valid_from']))
        self.find('input[type=date]'
                  '[name=date_valid_to]')[0].send_keys('{}'.format(self.dates[self.browser]['date_valid_to']))

        self.click_check_boxes(['Female', 'Male', 'Unisex'])


    def fill_Information(self):
        self.cur_func = 'fill_information'
        print('fill information')
        Select(self.find('select[name=manufacturer_id]')[0]).select_by_index(1)
        product_information = {
                                'keywords': 'Coala, love, deoxyribose',
                                'short_description': 'Coala',
                                'head_title': 'Coala',
                                'meta_description': 'I don\'t know what is it, but Coala'
        }
        for field in product_information:
            self.xfind('//input[contains(@name,"{}")]'.format(field))[0].send_keys(product_information[field])

        description_editor_xpath = '//textarea[contains(@name, "description")]/../div[contains(@class, "editor")]'
        self.xfind(description_editor_xpath)[0].send_keys('The best Coala in the World. Buy it.')

    def fill_Prices(self):
        self.cur_func = 'fill_Prices'
        print('fill prices')

        price = self.find('div#tab-prices input[name=purchase_price]')[0]
        price.clear()
        price.send_keys('100500')
        Select(self.find('div#tab-prices select[name=purchase_price_currency_code]')[0]).select_by_index(1)
        self.xfind('//div[@id="tab-prices"]//strong[contains(text(), "USD")]/../input')[0].send_keys('100500')
        self.xfind('//div[@id="tab-prices"]//strong[contains(text(), "EUR")]/../input')[0].send_keys('100500')

    def kick_checkbox(self, obj, action='check'):
        self.cur_func = 'kick_checkbox'
        cur_state = obj.get_attribute('checked')
        if (action == 'check' and cur_state != 'true') or (action == 'uncheck' and cur_state == 'true'):
            obj.click()

    def click_check_boxes(self, names):
        self.cur_func = 'click_check_boxes'
        if type(names) != list:
            names = [names]
        for name in names:
            self.kick_checkbox(self.xfind('//div[@class="content"]//td[.="{}"]/../td/input'.format(name))[0])

    def go_to_subsection(self, name):
        self.cur_func = 'go_to_subsection'
        self.xfind('//ul[@class="index"]/li/a[contains(text(),"{}")]'.format(name))[0].click()

    def fill_page(self, page):
        time.sleep(3)
        self.cur_func = 'fill_page'
        getattr(self, 'fill_{}'.format(page))()

    def save_product(self):
        self.cur_func = 'save_product'
        self.find('span.button-set button[name=save]')[0].click()

    def check_product(self):
        self.cur_func = 'check_product'
        if len(self.xfind('//table[@class="dataTable"]//a[contains(text(), "{}")]'.format(self.product_name))) > 0:
            print('\n\n\nProduct {} was successfully created'.format(self.product_name))
        else:
            raise Exception('\n\n!!! For some reason product {} wasn\'t created in {} \n\n\n'.format(self.product_name,
                                                                                                     self.browser))

#############################SCRIPT##################################

drivers = [
    [webdriver.Chrome(), 'Chrome'],
    [webdriver.Firefox(capabilities={'Marionette': True}), 'FireFox'],
    [webdriver.Ie(), 'Ie']
]


for driver in drivers:
    page = Admin_page(driver=driver[0], browser=driver[1])
    try:
        page.authorization()
        page.go_to_section('Catalog')
        page.click_button_in_catalog('Add New Product')
        page.fill_page('general')
        page.go_to_subsection('Information')
        page.fill_page('Information')
        page.go_to_subsection('Prices')
        page.fill_page('Prices')
        page.save_product()
        page.check_product()
        page.driver.quit()
    except Exception as e:
        print('\n\n!! Problem with {} in {}'.format(page.browser, page.cur_func))
        page.driver.quit()
        raise Exception(e)


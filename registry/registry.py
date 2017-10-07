from selenium import webdriver
from selenium.webdriver.support.select import Select

import random
import string

####################################API#########################################
class Page:
    def __init__(self):
        self.fields = {
            'Tax_ID': ['tax_id', '1234567890'],
            'Company': ['company', 'My Company'],
            'First_Name': ['firstname', 'Aleksey' ],
            'Last_Name': ['lastname', 'Glukhov'],
            'Address_1': ['address1', 'Moscow, Tulskaya str.'],
            'Address_2': ['address2', 'Moscow'],
            'Postcode': ['postcode', '12345'],
            'City': ['city', 'Moscow'],
            'Email': ['email', 'vach@mail.ru'],
            'Phone': ['phone', '89222662636'],
            'Desired Password': ['password','onotole'],
            'Confirm Password': ['confirmed_password', 'onotole']
        }
        self.email = ''
        self.password = 'onotole'
        self.driver = webdriver.Firefox(capabilities={'Marionette':True})
        self.find = self.driver.find_elements_by_css_selector
        self.driver.get('http://localhost:8080/litecard/en/')

    def collect_fields(self):
        for field in self.fields:

            try:
                css_selector = 'form[name=customer_form] input[name={}]'.format(self.fields[field][0])
                new_field = self.find(css_selector)[0]
            except Exception as e:
                print('Some problem was occured during formation of {}-field'.format(field))
                raise Exception(e)

            setattr(self, field, new_field)
            print('{} initialized.'.format(field))

    def fill_fields(self):
        for value in self.fields:
            try:
                getattr(self, value).send_keys(self.fields[value][1])
            except Exception as e:
                print('There\'s a problem with typing in {}-field'.format(value))
                raise Exception(e)
            print('Field {} is filled'.format(value))

        self.Email.clear()
        self.Email.send_keys(self.get_random_email())

    def get_random_email(self):
        email_user = ''
        email_user_lenght = random.randint(4,8)
        for letter in range(0, email_user_lenght):
            email_user += string.ascii_letters[random.randint(0, 25)]
        self.email = '{}@index.ru'.format(email_user)
        return self.email

    def choose_country(self, country='United States'):
        c_list = self.find('form[name=customer_form] select.select2-hidden-accessible')[0]
        Select(c_list).select_by_visible_text(country)

    def submit(self):
        # Если всплыло сообщение о том, что адрес уже зарегистрирован, заполняем новым рандомом
        if len(self.find('div.notice errors')) > 0:
            self.Email.send_keys(self.get_random_email())

        self.find('form[name=customer_form] button[type=submit]')[0].click()

    def relogin(self):
        self.driver.find_elements_by_xpath('//div[@id="box-account"]//a[.="Logout"]')[0].click()
        self.find('form[name=login_form] input[name=email]')[0].send_keys(self.email)
        self.find('form[name=login_form] input[name=password]')[0].send_keys(self.password)
        self.find('form[name=login_form] button[name=login]')[0].click()

    def start_registry(self):
        self.find('form[name=login_form] tr td a')[0].click()




####################################main####################################

def main():
    page = None
    try:
        page = Page()
        page.start_registry()
        page.collect_fields()
        page.fill_fields()
        page.choose_country()
        page.submit()
        page.relogin()
    except Exception as e:
        if hasattr(page, 'driver'):
            page.driver.quit()
        raise Exception(e)
    page.driver.quit()

##################################################################################
main()




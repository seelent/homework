from selenium import  webdriver
import time

def find_elements(selector, single=True, raise_on_fail=True):
    list_of_objects = driver.find_elements_by_css_selector(selector)
    qty = len(list_of_objects)

    if qty > 1 and single:
        raise Exception('Not accurate selector.')
    elif qty == 0 and raise_on_fail:
        raise Exception('Element wasn\'t found.')
    elif qty == 0 and not raise_on_fail:
        return []

    return_obj = list_of_objects
    if single:
        return_obj = list_of_objects[0]

    return return_obj

driver = webdriver.Firefox(capabilities={'Marionette':True})

try:
    driver.implicitly_wait(10)
    driver.get('http://localhost:8080/litecard/admin')
    user_field = find_elements(selector='div#box-login [name=username]')
    user_field.send_keys('admin')
    password_field = find_elements(selector='div#box-login [name=password]')
    password_field.send_keys('admin')
    login_button = find_elements(selector='div#box-login [name=login]')
    login_button.click()

    left_buttons = find_elements(selector='ul#box-apps-menu li#app- > a', single=False)
    outer_lenght = len(left_buttons)

    for button in range(0, outer_lenght):
        buttons = find_elements(selector='ul#box-apps-menu li#app- > a', single=False)
        print('\n\n\nCurrent link: {}'.format(buttons[button].get_attribute('href')))
        buttons[button].click()
        inner_lenght = len(find_elements(selector='li#app-.selected li', single=False, raise_on_fail=False))
        if inner_lenght != 0:
            for inner_button in range(0, inner_lenght):
                i_buttons = find_elements(selector='li#app-.selected li', single=False)
                print('Current sub_link name: {}'.format(i_buttons[inner_button].get_attribute('id')))
                i_buttons[inner_button].click()
                qty_of_h1 = find_elements(selector='td#content h1', single=False, raise_on_fail=False)
                print('There\'re {} headers'.format(len(qty_of_h1)))
        else:
            qty_of_h1 = find_elements(selector='td#content h1', single=False, raise_on_fail=False)
            print('There\'re no sublinks')
            print('There\'re {} headers'.format(len(qty_of_h1)))


except Exception as e:
    driver.quit()
    raise Exception(e)

driver.quit()
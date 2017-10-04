from selenium import webdriver
import time
import re

def check_page(reg_price_selector, cam_price_selector, name_selector, duck, page):
    reg_price_obj = find(reg_price_selector)[0]
    cam_price_obj = find(cam_price_selector)[0]
    duck['name'] = find(name_selector)[0].get_attribute('textContent')
    duck['regular_price'] = int(reg_price_obj.get_attribute('textContent').replace('$', ''))
    duck['campaign-price'] = int(cam_price_obj.get_attribute('textContent').replace('$', ''))

    check_price_properties(reg_price_obj, cam_price_obj, page)

    if duck['regular_price'] < duck['campaign-price']:
        raise Exception('Regular_price of duck on {} page is bigger than campaign price'.format(page))

def check_price_properties(regular_price, campaign_price, page):
    rp_color_raw = regular_price.value_of_css_property('color')
    rp_color = ((rp_color_raw.replace('rgba(', '')).replace(')','')).split(',')[0:3]
    if int(rp_color[0]) != int(rp_color[1]) or int(rp_color[1]) != int(rp_color[2]):
        raise Exception('Regular_price of duck on {} page isn\'t grey! Color: {}'.format(page, rp_color))
    if not re.search('.*line-through.*', regular_price.value_of_css_property('text-decoration')):
        raise Exception('Regular_price of duck on {} page isn\'t crossed'.format(page))

    cp_color_raw = campaign_price.value_of_css_property('color')
    cp_color = ((cp_color_raw.replace('rgba(', '')).replace(')', '')).split(',')[0:3]
    cp_weight = campaign_price.value_of_css_property('font-weight')
    if int(cp_color[1]) != 0 or int(cp_color[2]) != 0:
        raise Exception('Campaing_price of duck on {} page isn\'t red! Color: {}'.format(page, cp_color))
    if cp_weight == '700' or cp_weight == '900' or cp_weight == 'bold':
        pass
    else:
        raise Exception('Campaing_price of duck on {} page isn\'t bold! it\'s: {}'.format(page, cp_weight))

###############################SCRIPT#######################################################

drivers = [webdriver.Chrome(), webdriver.Ie(), webdriver.Firefox(capabilities={'Marionette': True})]

for driver in drivers:
    try:
        find = driver.find_elements_by_css_selector
        f_duck = {}
        p_duck = {}

        ###################GOING TO MAIN PAGE######################################
        driver.get('http://127.0.0.1:8080/litecard/en/')
        time.sleep(3)
        check_page('div#box-campaigns li.product.column.shadow.hover-light s.regular-price',
                   'div#box-campaigns li.product.column.shadow.hover-light strong.campaign-price',
                   'div#box-campaigns li.product.column.shadow.hover-light div.name',
                   f_duck,
                   'main')

        ####################GOING TO PRODUCT PAGE#############################################
        find('div#box-campaigns li.product.column.shadow.hover-light')[0].click()
        time.sleep(3)
        check_page('div.information div.price-wrapper s.regular-price',
                   'div.information div.price-wrapper strong.campaign-price',
                   'div#box-product h1.title',
                   p_duck,
                   'product')

        ####################COMPARING PROPERTIES######################################################
        for element in f_duck:
            if f_duck[element] != p_duck[element]:
                raise Exception('{} is not same on main and product pages'.format(element))

    except Exception as e:
        driver.quit()
        raise Exception(e)
    driver.quit()


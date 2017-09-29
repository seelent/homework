from selenium import webdriver

driver = webdriver.Firefox(capabilities={'Marionette':True})

try:
    driver.get('http://localhost:8080/litecard/')
    for duck in driver.find_elements_by_css_selector('div.content '
                                                     'li.product.column.shadow.hover-light '
                                                     'a.link'):
        if len(duck.find_elements_by_css_selector('[class^=sticker]')) != 1:
            driver.quit()
            raise Exception('There\'s no sticker at one duck, or there\'re more than 1 stickers')
except Exception as e:
    driver.quit()
    raise Exception(e)

print('All ducks have exactly one sticker')
driver.quit()
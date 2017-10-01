from selenium import webdriver
import time, re

driver = webdriver.Firefox(capabilities={'Marionette':True})
driver.implicitly_wait(10)



#########authorization########
driver.get('http://localhost:8080/litecard/admin')
user_field = driver.find_elements_by_css_selector('div#box-login [name=username]')
user_field[0].send_keys('admin')
password_field = driver.find_elements_by_css_selector('div#box-login [name=password]')
password_field[0].send_keys('admin')
login_button = driver.find_elements_by_css_selector('div#box-login [name=login]')
login_button[0].click()
############################

#####################main part#############################################
country_links = []
multiple_zone_countries = {}
try:
    driver.get('http://localhost:8080/litecard/admin/?app=countries&doc=countries')
    # Получаем список элементов-строк таблицы.
    country_rows = driver.find_elements_by_css_selector('form[name=countries_form] tr.row')
    # Перебором строк получаем список элементов-ссылок(для получения названий стран) и словарь Страна:кол.во геозон,
    # где кол.во геозон > 0.

    for row in country_rows:
        link = row.find_elements_by_css_selector('td > a:not([title=Edit]')[0]
        country_links.append(link)
        # TODO: Пока я предполагаю, что кол.во геозон всегда будет 6 элементом в строке. Необходимо попросить)
        # разработчиков дать этому элементу специфический класс, иначе придется творить шаткие костыли со сложными
        # селекторами и 'одноразовой' логикой.
        geo_zones = int(row.find_elements_by_css_selector('td')[5].get_attribute('textContent'))
        if geo_zones > 0:
            multiple_zone_countries[link.get_attribute('text')] = geo_zones

    # Получаем отсортированный в алфавитном порядке список названий стран. В будущем мы будем проходить по нему.
    country_names = [x.get_attribute('text') for x in country_links]
    country_names.sort()

    # Формируем на основании properties web-элементов  словарь, в котором в качестве ключей используются названия стран,
    #  а в качестве значений - координата y/
    country_coordinats = {country.text:country.location['y'] for country in country_links}

    # Проверяем, что 'y' координата каждого веб элемента, начиная со второго, имеет значение больше, чем у предыдущего.
    # Поскольку
    for country_index in range(1, len(country_names)):
        current = country_coordinats[country_names[country_index]]
        previous = country_coordinats[country_names[country_index - 1]]
        if current > previous:
            print('{} has y: {}'.format(country_names[country_index], current))
        else:
            raise Exception('{} has wrong y coordinat'.format(country_names[country_index]))

##############SECOND_TASK#######################################################
#Кликаем по ссылкам, в отображаемом тексе которых есть названия стран с множеством зон.
#Исходя примерно из той же логики парсим строки в таблице с зонами. По именам td элементов в tr регуляркой находим
#имена зон. Попутно формируем словарь: имя зоны: координата y
    for country in multiple_zone_countries:
        zone_list = []
        zone_ys = {}
        driver.find_elements_by_xpath('//form[@name="countries_form"]//td/a[.="{}"]'.format(country))[0].click()
        zone_rows = driver.find_elements_by_css_selector('table#table-zones tr:not(.header)')
        for row in zone_rows:
            #  Под селектор также попадает последняя строка из таблицы, которая мало отличается по аттрибутам, но имеет
            #  другую высоту. Отсеиваем только записи у которых стандартная высота.
            if row.size['height'] == 30:
                cells = row.find_elements_by_css_selector('td:not([style]) input')
                for cell in cells:
                    if re.search('.*name.*',cell.get_attribute('name')):
                        zone_list.append(cell.get_attribute('value'))
                        zone_ys[cell.get_attribute('value')] = row.location['y']
        # Отсортировываем по имени список зон
        zone_list.sort()
        # Аналогично ситуации со списком стран вынимаем по элементу из списка зон и сравниваем координаты.
        for zone_index in range(1, len(zone_list)):
            current = zone_ys[zone_list[zone_index]]
            previous = zone_ys[zone_list[zone_index-1]]
            if current > previous:
                print('{} has y: {}'.format(zone_list[zone_index], current))
            else:
                raise Exception('{} has wrong y coordinat'.format(zone_list[zone_index]))
        driver.get('http://localhost:8080/litecard/admin/?app=countries&doc=countries')
except Exception as e:
    driver.quit()
    raise Exception(e)

driver.quit()

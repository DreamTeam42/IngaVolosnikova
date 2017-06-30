from bs4 import BeautifulSoup
import requests
import json
import time

ADVERTS_TYPE_0 = {
    'Продажа квартиры': 'cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=\t&region=1',
    'Аренда квартиры': 'cat.php?deal_type=rent&engine_version=2&offer_type=flat&p=\t&region=1&type=4',
    'Посуточная аренда квартиры': 'cat.php?deal_type=rent&engine_version=2&offer_type=flat&p=\t&region=1&type=2',
    'Продажа комнаты': 'cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=\t&region=1&room0=1',
    'Аренда комнаты': 'cat.php?deal_type=rent&engine_version=2&offer_type=flat&p=\t&region=1&room0=1&type=4',
    'Посуточная аренда комнаты': 'cat.php?deal_type=rent&engine_version=2&offer_type=flat&p=\t&region=1&room0=1&type=2',
    'Аренда койко-места': 'cat.php?deal_type=rent&engine_version=2&offer_type=flat&p=\t&region=1&room10=1&type=4',
    'Посуточная аренда койко-места': 'cat.php?deal_type=rent&engine_version=2&offer_type=flat&p=\t&region=1&room10=1&type=2',
    'Продажа части квартиры': 'cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=\t&region=1&room8=1',
    'Продажа дома': 'cat.php?deal_type=sale&engine_version=2&object_type%5B0%5D=1&offer_type=suburban&p=\t&region=1',
    'Аренда дома': 'cat.php?deal_type=sale&engine_version=2&object_type%5B0%5D=1&offer_type=suburban&p=\t&region=1',
    'Посуточная аренда дома': 'cat.php?deal_type=rent&engine_version=2&object_type%5B0%5D=1&offer_type=suburban&p=\t&region=1&type=2',
    'Продажа таунхауса': 'cat.php?deal_type=sale&engine_version=2&object_type%5B0%5D=4&offer_type=suburban&p=\t&region=1',
    'Аренда таунхауса': 'cat.php?deal_type=rent&engine_version=2&object_type%5B0%5D=4&offer_type=suburban&p=\t&region=1&type=4',
    'Продажа части дома': 'cat.php?deal_type=sale&engine_version=2&object_type%5B0%5D=2&offer_type=suburban&p=\t&region=1',
    'Аренда части дома': 'cat.php?deal_type=rent&engine_version=2&object_type%5B0%5D=2&offer_type=suburban&p=\t&region=1',
    'Продажа участка': 'cat.php?deal_type=sale&engine_version=2&object_type%5B0%5D=3&offer_type=suburban&p=\t&region=1'
}

ADVERTS_TYPE_1 = {
    'Продажа офиса': 'cat.php?deal_type=sale&engine_version=2&offer_type=offices&office_type%5B0%5D=1&p=\t&region=1',
    'Аренда офиса': 'cat.php?deal_type=rent&engine_version=2&offer_type=offices&office_type%5B0%5D=1&p=\t&region=1',
    'Продажа торговой площади': 'cat.php?deal_type=sale&engine_version=2&offer_type=offices&office_type%5B0%5D=2&p=\t&region=1',
    'Аренда торговой площади': 'cat.php?deal_type=rent&engine_version=2&offer_type=offices&office_type%5B0%5D=2&p=\t&region=1',
    'Продажа склада': 'cat.php?deal_type=sale&engine_version=2&offer_type=offices&office_type%5B0%5D=3&p=\t&region=1',
    'Аренда склада': 'cat.php?deal_type=rent&engine_version=2&offer_type=offices&office_type%5B0%5D=3&p=\t&region=1',
    'Продажа ПСН': 'cat.php?deal_type=sale&engine_version=2&offer_type=offices&office_type%5B0%5D=5&p=\t&region=1',
    'Аренда ПСН': 'cat.php?deal_type=rent&engine_version=2&offer_type=offices&office_type%5B0%5D=5&p=\t&region=1',
    'Продажа гаража': 'cat.php?deal_type=sale&engine_version=2&offer_type=offices&office_type%5B0%5D=6&p=\t&region=1',
    'Аренда гаража': 'cat.php?deal_type=rent&engine_version=2&offer_type=offices&office_type%5B0%5D=6&p=\t&region=1',
    'Продажа здания': 'cat.php?deal_type=sale&engine_version=2&offer_type=offices&office_type%5B0%5D=11&p=\t&region=1',
    'Аренда здания': 'cat.php?deal_type=rent&engine_version=2&offer_type=offices&office_type%5B0%5D=11&p=\t&region=1'
}

def get_raiting(img_list):
    raiting = 0
    for i in range(5):
        star = img_list[i]['src'].split('/')[3]
        if(star == 'star_full.svg'):
            raiting += 1
        elif(star == 'star_half.svg'):
            raiting += 0.5
    return str(raiting)+'/5'


def get_residential(url, type):
    advert = {}
    advert['Тип объявления'] = type    # Тип задается при вызове исходя из раздела

    html = requests.get(url)
    soup = BeautifulSoup(html.text,'html.parser')

    date = soup.find_all('span', 'object_descr_dt_added')
    if(len(date)>1):
        advert['Дата подачи'] = date[1].text

    if(type.split().count('квартиры') == 1):
        rooms = soup.find_all('div', 'object_descr_title')
        if(len(rooms)>0):
            rooms = rooms[0].text.split('-')
            advert['Количество комнат'] = rooms[0].strip()

    address = soup.find_all('h1', 'object_descr_addr')
    if(len(address) > 0):
        address = address[0].find_all('a')
        advert['Адрес'] = ', '.join([address[elem].text for elem in range(len(address))])

    # Указание на метро может сочетаться с расстоянием до МКАД или отсутствовать
    metro = soup.find_all('p', 'objects_item_metro_prg')
    if(len(metro) > 0):
        for elem in range(len(metro)):
            if (metro[elem].find('span', 's-icon_subway') is not None):
                if(len(metro[elem].find_all('span', 'object_item_metro_comment')) > 0):
                    station = ' '.join([metro[elem].find_all('a')[0].text,
                                        ' '.join(metro[elem].find_all('span', 'object_item_metro_comment')[0].text.split())])
                else:
                    station = metro[elem].find_all('a')[0].text
               # station = ' '.join([metro[elem].find_all('a')[0].text, ' '.join(metro[elem].find_all('span', 'object_item_metro_comment')[0].text.split())])
                if(advert.get('Метро') == None):
                    advert['Метро'] = []
                advert['Метро'].append(station)
            else:
                if(len(metro[elem].find_all('span', 'objects_item_metro_comment')) > 1):
                    station = ' '.join([metro[elem].find('a').text,
                                       ' '.join(metro[elem].find_all('span', 'objects_item_metro_comment')[1].text.split())])
                else:
                    station = metro[elem].find('a').text
                if (advert.get('МКАД') == None):
                    advert['МКАД'] = []
                advert['МКАД'].append(station)

    price = soup.find('div', 'object_descr_price')
    advert['Цена'] = ' '.join(price.text.split())
    extra_price = soup.find(id='price_rur').nextSibling.nextSibling
    if(extra_price != None):
        advert['Подробнее о цене'] = ' '.join(extra_price.text.split())
    # advert['Цена'] = ' '.join(soup.find_all('div', 'object_descr_price')[0].text.split())

    # Универсальный блок парсинга свойств объекта
    properties = soup.find_all('table', 'object_descr_props')
    if(len(properties) > 0):
        properties = properties[0].find_all('tr')
        for row in range(1,len(properties)):
            prop = list(properties[row].find_all('th')[0].text.strip())
            prop.remove(':')
            prop = ''.join(prop)
            advert[prop] = ' '.join(properties[row].find('td').text.split())

    #advert['Описание'] = soup.find_all('div', 'object_descr_text')[0].contents[0].strip()
    text = str(soup.find_all('div', 'object_descr_text')[0])
    text = text.split('<div class="object_descr_text">')[1].split('<div style="clear: both">')[0]
    advert['Описание'] = (' '.join(text.split('<br/>'))).strip()

    details = soup.find_all('div', 'object_descr_details')
    if(len(details) > 0):
        details = details[0].find_all('ul')
        if(len(details) > 0):
            details = details[0].find_all('li')
            extra = []
            for unit in range(len(details)):
                extra.append(details[unit].contents[2].strip())
            if(len(extra)>0):
                advert['Дополнительно'] = ', '.join(extra)

    realtor = soup.find('h3', 'realtor-card__title')
    if(len(realtor.find_all('a')) == 0):
        advert['Продавец'] = realtor.contents[0].strip()
    else:
        advert['Продавец'] = realtor.find('a').text


    phone = soup.find_all('div', 'cf_offer_show_phone-number')
    if(len(phone) > 0):
        advert['Телефон продавца'] = phone[0].find('a').text

    # Информация о районе и доме, только в Мск
    bti_info = soup.find_all('table', 'bti__data')
    for t_count in range(len(bti_info)):
        tbody = bti_info[t_count].find('tbody').find_all('tr')
        if(t_count == 0):
            advert['О доме'] = {}
            for row in tbody:
                item = row.find('th').find('div', 'bti__data__name').text.strip()
                if (item == 'Конструктив и состояние' or item == 'Квартиры и планировки'):
                    advert['О доме'][item] = get_raiting(row.find('td').find_all('img'))
                else:
                    advert['О доме'][item] = row.find('td').text.strip()
        elif(t_count == 1):
            advert['Оценка стоимости и владения'] = {}
            for row in tbody:
                if(len(row.find('th').find('div', 'bti__data__name').contents) > 2):
                    item = row.find('th').find('div', 'bti__data__name').contents[0].strip()
                else:
                    item = row.find('th').find('div', 'bti__data__name').text.strip()
                advert['Оценка стоимости и владения'][item] = row.find('td').text.strip()
        elif(t_count == 2):
            advert['О районе'] = {}
            for row in tbody:
                item = row.find('th').find('div', 'bti__data__name').text.strip()
                advert['О районе'][item] = row.find('td').text.strip()
        else:
            advert['Рейтинг района'] = {}
            for row in tbody:
                item = row.find('th').find('div', 'bti__data__name').text.strip()
                advert['Рейтинг района'][item] = get_raiting(row.find('td').find_all('img'))

    return advert

def get_commercial(url, type):
    advert = {}
    advert['Тип объявления'] = type  # Тип задается при вызове исходя из раздела

    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')

    date = soup.find_all('span', 'object_descr_dt_added')
    if (len(date) > 1):
        advert['Дата подачи'] = date[1].text

    address = soup.find_all('h1', 'object_descr_addr')
    if(len(address) > 0):
        address = address[0].find_all('a')
        advert['Адрес'] = ', '.join([address[elem].text for elem in range(len(address))])

    # Указание на метро может сочетаться с расстоянием до МКАД или отсутствовать
    # P.S. или может быть записано не полностью... лентяи
    metro = soup.find_all('p', 'objects_item_metro_prg')
    if (len(metro) > 0):
        if (metro[0].find('span', 's-icon_subway') is not None):
            advert['Метро'] = []
        for elem in range(len(metro)):
            if (metro[elem].find('span', 's-icon_subway') is not None):
                if(len(metro[elem].find_all('span', 'object_item_metro_comment')) > 0):
                    station = ' '.join([metro[elem].find_all('a')[0].text,
                                        ' '.join(metro[elem].find_all('span', 'object_item_metro_comment')[0].text.split())])
                else:
                    station = metro[elem].find_all('a')[0].text
                advert['Метро'].append(station)
            else:
                advert['МКАД'] = ' '.join([metro[elem].find('a').text,
                                           ' '.join(metro[elem].find_all('span', 'objects_item_metro_comment')[
                                                        1].text.split())])

    price = soup.find('div', 'object_descr_price')
    advert['Цена'] = ' '.join(price.text.split())
    extra_price = soup.find(id='price_rur').nextSibling.nextSibling
    if (extra_price != None):
        advert['Подробнее о цене'] = ' '.join(extra_price.text.split())
    else:
        extra_price = soup.find('div', 'cf-object-descr-add')
        if(extra_price != None):
            advert['Подробнее о цене'] = ' '.join(extra_price.find('span').text.split())

    properties = soup.find_all('section', 'cf-comm-offer-detail__section')
    for section in properties:
        if(section.find('h2') is not None):
            title = section.find('h2').text.strip()
            if(title == 'Об объекте' or title == 'О здании'):
                advert[title] = {}
            elif(title != 'Инфраструктура' and title != 'Дополнительно'):
                advert['О здании'] = {}
                advert['О здании']['Название'] = title
                title = 'О здании'
            else:
                infra = section.find_all('li', 'cf-comm-offer-detail__infrastructure-item')
                if (len(infra) > 0):
                    extra = []
                    for item in infra:
                        extra.append(item.text)
                    if (len(extra) > 0 and title == 'Инфраструктура'):
                        advert['О здании'][title] = ', '.join(extra)
                    elif(len(extra) > 0 and title == 'Дополнительно'):
                        advert['Об объекте'][title] = ', '.join(extra)

            prop_list = section.find_all('dt')
            value_list = section.find_all('dd')
            for row in range(len(prop_list)):
                prop = list(prop_list[row].text.strip())
                prop.remove(':')
                prop = ''.join(prop)
                advert[title][prop] = ' '.join(value_list[row].text.split())

    # advert['Описание'] = soup.find_all('div', 'object_descr_text')[0].contents[0].text
    text = str(soup.find_all('div', 'object_descr_text')[0])
    text = text.split('<div class="object_descr_text">')[1].split('<div style="clear: both">')[0]
    advert['Описание'] = (' '.join(text.split('<br/>'))).strip()


    realtor = soup.find('h3', 'realtor-card__title')
    if (len(realtor.find_all('a')) == 0):
        advert['Продавец'] = realtor.contents[0].strip()
    else:
        advert['Продавец'] = realtor.find('a').text

    advert['Телефон продавца'] = soup.find_all('div', 'cf_offer_show_phone-number')[0].find('a').text

    return advert

def parse_one_page(page_url, prop_type, ad_type):
    # print('Начал парсить страницу')
    page = requests.get(page_url)
    soup = BeautifulSoup(page.text,'html.parser')
    ad_list = soup.find_all('div', 'serp-item')
    for ad in ad_list:
        if(prop_type == 0): # жилая недвижимость
            adverts_mas.append(get_residential(ad['href'], ad_type))
            # print('Я добавил жилое объявление')
        else: # коммерческая
            adverts_mas.append(get_commercial(ad['href'], ad_type))
            # print('Я добавил коммерческое объявление')

    # возвращаем номер последней доступной отсюда страницы или -1, если страниц еще очень много
    pages = soup.find_all('div', 'pager_pages')
    if(len(pages) > 0):
        pages = pages[0].contents
        last_page_number = pages[len(pages)-2].text
        try:
            last_page_number = int(last_page_number)
        except:
            last_page_number = -1
    else:
        last_page_number = 1 # Если нет списка страниц, то страница одна
    # print("Закончил")
    return last_page_number

def parse():
    # Жилая недвижимость
    prop_type = 0
    for key in ADVERTS_TYPE_0.keys():
        page_number = 1
        while True:
        #for i in range(1,3):
            page_url = base_url + str(page_number).join(ADVERTS_TYPE_0.get(key).split('\t'))
            last_page = parse_one_page(page_url, prop_type, key)
            time.sleep(5)
            if(last_page == page_number):
                break
            else:
                page_number += 1

    """print('Тестим продажу участка')
    ad_type = 'Продажа участка'
    page_number = 1
    # while True:
    for i in range(1, 2):
        page_url = base_url + str(page_number).join(ADVERTS_TYPE_0.get(ad_type).split('\t'))
        last_page = parse_one_page(page_url, prop_type, ad_type)
        if (last_page == page_number):
            break"""

    # Коммерческая недвижимость
    prop_type = 1
    for key in ADVERTS_TYPE_1.keys():
        page_number = 1
        while True:
        #for i in range(1,3):
            page_url = base_url + str(page_number).join(ADVERTS_TYPE_1.get(key).split('\t'))
            last_page = parse_one_page(page_url, prop_type, key)
            time.sleep(5)
            if (last_page == page_number):
                break
            else:
                page_number += 1

if __name__ == '__main__':
    base_url = 'https://www.cian.ru/'
    adverts_mas = []
    print('Начинаю работу')
    parse()
    print('Я все сделал, готовлю отчет')

    with open('realty_adverts.json', 'w', encoding='utf-8') as file:
        json.dump(adverts_mas, file, indent=2, ensure_ascii=False)

    print('Результаты в файле realty_adverts.json')


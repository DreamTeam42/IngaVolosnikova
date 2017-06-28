from bs4 import BeautifulSoup
import requests
import json
import re

ADVERT_TYPE = {
    'sale_flat': 'Продажа квартиры',
    'rent_flat': 'Аренда квартиры',
    'daily_rent_flat': 'Посуточная аренда квартиры',
    'sale_room': 'Продажа комнаты',
    'rent_room': 'Аренда комнаты',
    'daily_rent_room': 'Посуточная аренда комнаты',
    'rent_bed-place': 'Аренда койко-места',
    'daily_rent_bed-place': 'Посуточная аренда койко-места',
    'sale_part_of_flat': 'Продажа части квартиры',
    'sale_house': 'Продажа дома',
    'rent_house': 'Аренда дома',
    'daily_rent_house': 'Посуточная аренда дома',
    'sale_townhouse': 'Продажа таунхауса',
    'rent_townhouse': 'Аренда таунхауса',
    'sale_part_of_house': 'Продажа части дома',
    'rent_part_of_house': 'Аренда части дома',
    'sale_ground': 'Продажа участка',
    'sale_office': 'Продажа офиса',
    'rent_office': 'Аренда офиса',
    'sale_trade_area': 'Продажа торговой площади',
    'rent_trade_area': 'Аренда торговой площади',
    'sale_warehouse': 'Продажа склада',
    'rent_warehouse': 'Аренда склада',
    'sale_free_room': 'Продажа ПСН',
    'rent_free_room': 'Аренда ПСН',
    'sale_garage': 'Продажа гаража',
    'rent_garage': 'Аренда гаража',
    'sale_building': 'Продажа здания',
    'rent_building': 'Аренда здания'
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

    advert['Дата подачи'] = soup.find_all('span', 'object_descr_dt_added')[1].text

    if(type.split().count('квартиры') == 1):
        advert['Количество комнат'] = soup.find_all('div', 'object_descr_title')[0].text.strip()[0]

    address = soup.find_all('h1', 'object_descr_addr')[0].find_all('a')
    advert['Адрес'] = ', '.join([address[elem].text for elem in range(len(address))])

    # Указание на метро может сочетаться с расстоянием до МКАД или отсутствовать
    metro = soup.find_all('p', 'objects_item_metro_prg')
    if(len(metro) > 0):
        if(metro[0].find('span', 's-icon_subway') is not None):
            advert['Метро'] = []
        for elem in range(len(metro)):
            if (metro[elem].find('span', 's-icon_subway') is not None):
                station = ' '.join([metro[elem].find_all('a')[0].text,
                                    ' '.join(metro[elem].find_all('span', 'object_item_metro_comment')[0].text.split())])
                advert['Метро'].append(station)
            else:
                advert['МКАД'] = ' '.join([metro[elem].find('a').text,
                                       ' '.join(metro[elem].find_all('span', 'objects_item_metro_comment')[1].text.split())])

    price = soup.find('div', 'object_descr_price')
    advert['Цена'] = ' '.join(price.text.split())
    extra_price = soup.find(id='price_rur').nextSibling.nextSibling
    if(extra_price != None):
        advert['Подробнее о цене'] = ' '.join(extra_price.text.split())
    # advert['Цена'] = ' '.join(soup.find_all('div', 'object_descr_price')[0].text.split())

    # Универсальный блок парсинга свойств объекта
    properties = soup.find_all('table', 'object_descr_props')[0].find_all('tr')
    for row in range(1,len(properties)):
        prop = list(properties[row].find_all('th')[0].text.strip())
        prop.remove(':')
        prop = ''.join(prop)
        advert[prop] = ' '.join(properties[row].find('td').text.split())

    advert['Описание'] = soup.find_all('div', 'object_descr_text')[0].contents[0].strip()

    details = soup.find_all('div', 'object_descr_details')
    if(len(details) > 0):
        details = details[0].find_all('ul')[0].find_all('li')
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

    advert['Телефон продавца'] = soup.find_all('div', 'cf_offer_show_phone-number')[0].find('a').text

    # Информация о районе и доме, только в Мск и только в объявлениях аренды
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

    advert['Дата подачи'] = soup.find_all('span', 'object_descr_dt_added')[1].text

    address = soup.find_all('h1', 'object_descr_addr')[0].find_all('a')
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

if __name__ == '__main__':
    adverts_mas = []
    # example_url = 'https://www.cian.ru/rent/flat/156101470/'
    # adverts_mas.append(get_rent_flat_in_secondary(example_url))
    example_url = 'https://www.cian.ru/rent/flat/159118461/'
    type = 'Аренда офиса'
    adverts_mas.append(get_commercial(example_url,type))
    with open('realty_adverts.json', 'w', encoding='utf-8') as file:
        json.dump(adverts_mas, file, indent=2, ensure_ascii=False)



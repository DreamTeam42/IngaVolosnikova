from bs4 import BeautifulSoup
import requests
import json

def get_raiting(img_list):
    raiting = 0
    for i in range(5):
        star = img_list[i]['src'].split('/')[3]
        if(star == 'star_full.svg'):
            raiting += 1
        elif(star == 'star_half.svg'):
            raiting += 0.5
    return str(raiting)+'/5'


def get_rent_flat_in_secondary(url):
    advert = {}
    html = requests.get(url)
    soup = BeautifulSoup(html.text,'html.parser')
    advert['Дата подачи'] = soup.find_all('span', 'object_descr_dt_added')[1].text
    advert['Количество комнат'] = soup.find_all('div', 'object_descr_title')[0].text.strip()[0]
    address = soup.find_all('h1', 'object_descr_addr')[0].find_all('a')
    advert['Адрес'] = ', '.join([address[elem].text for elem in range(len(address))])
    metro = soup.find_all('p', 'objects_item_metro_prg')
    advert['Метро'] = []
    for elem in range(len(metro)):
        station = ' '.join([metro[elem].find_all('a')[0].text, ' '.join(metro[elem].find_all('span', 'object_item_metro_comment')[0].text.split())])
        advert['Метро'].append(station)
    advert['Цена'] = ' '.join(soup.find_all('div', 'object_descr_price')[0].text.split())
    properties = soup.find_all('table', 'object_descr_props')[0].find_all('tr')
    for row in range(len(properties)):
        prop = properties[row].find_all('th')[0].text.strip()
        if(prop == 'Этаж:'):
            advert['Этаж'] = ''.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Общая площадь:'):
            advert['Общая площадь'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Площадь комнат:'):
            advert['Площадь комнат'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Жилая площадь:'):
            advert['Жилая площадь'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Площадь кухни:'):
            advert['Площадь кухни'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Раздельных санузлов:'):
            advert['Количество санузлов'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Вид из окна:'):
            advert['Вид из окна'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Балкон:'):
            advert['Балкон'] = ' '.join(properties[row].find('td').text.split())
            continue
        if (prop == 'Ремонт:'):
            advert['Ремонт'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Тип дома:'):
            advert['Тип дома'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Высота потолков:'):
            advert['Высота потолков'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Год постройки:'):
            advert['Год постройки'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Лифт:'):
            advert['Лифт'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Парковка:'):
            advert['Парковка'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Телефон:'):
            advert['Телефон'] = ' '.join(properties[row].find('td').text.split())
            continue
    advert['Описание'] = soup.find_all('div', 'object_descr_text')[0].contents[0].strip()
    details = soup.find_all('div', 'object_descr_details')[0].find_all('ul')[0].find_all('li')
    extra = []
    for unit in range(len(details)):
        extra.append(details[unit].contents[2].strip())
    if(len(extra)>0):
        advert['Дополнительно'] = ', '.join(extra)
    advert['Продавец'] = soup.find_all('h3', 'realtor-card__title')[0].contents[0].strip()
    advert['Телефон продавца'] = soup.find_all('div', 'cf_offer_show_phone-number')[0].find('a').text

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

if __name__ == '__main__':
    adverts_mas = []
    example_url = 'https://www.cian.ru/rent/flat/156101470/'
    adverts_mas.append(get_rent_flat_in_secondary(example_url))
    example_url = 'https://www.cian.ru/rent/flat/159051043/'
    adverts_mas.append(get_rent_flat_in_secondary(example_url))
    with open('realty_adverts.json', 'w', encoding='utf-8') as file:
        json.dump(adverts_mas, file, indent=2, ensure_ascii=False)



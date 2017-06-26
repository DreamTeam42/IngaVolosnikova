from bs4 import BeautifulSoup
import requests
import json

exampleUrl = 'https://www.cian.ru/rent/flat/156101470/'
advert = {}

if __name__ == '__main__':
    html = requests.get(exampleUrl)
    soup = BeautifulSoup(html.text,'html.parser')
    # print(soup.prettify())
    advert['date'] = soup.find_all('span', 'object_descr_dt_added')[1].text
    # print(advert['date'])
    advert['rooms_number'] = soup.find_all('div', 'object_descr_title')[0].text.strip()[0]
    # print(advert['rooms_number'])
    address = soup.find_all('h1', 'object_descr_addr')[0].find_all('a')
    advert['address'] = ', '.join([address[elem].text for elem in range(len(address))])
    # print(advert['address'])
    metro = soup.find_all('p', 'objects_item_metro_prg')
    advert['metro'] = []
    for elem in range(len(metro)):
        station = ' '.join([metro[elem].find_all('a')[0].text, ' '.join(metro[elem].find_all('span', 'object_item_metro_comment')[0].text.split())])
        advert['metro'].append(station)
    advert['price'] = ' '.join(soup.find_all('div', 'object_descr_price')[0].text.split())
    properties = soup.find_all('table', 'object_descr_props')[0].find_all('tr')
    for row in range(len(properties)):
        prop = properties[row].find_all('th')[0].text.strip()
        if(prop == 'Этаж:'):
            advert['stage'] = ''.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Общая площадь:'):
            advert['general_area'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Площадь комнат:'):
            advert['rooms_area'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Жилая площадь:'):
            advert['living_area'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Площадь кухни:'):
            advert['kitchen_area'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Раздельных санузлов:'):
            advert['wc_count'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Вид из окна:'):
            advert['window_view'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Балкон:'):
            advert['balcony'] = ' '.join(properties[row].find('td').text.split())
            continue
        if (prop == 'Ремонт:'):
            advert['repairs'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Тип дома:'):
            advert['house_type'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Высота потолков:'):
            advert['ceil_height'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Год постройки:'):
            advert['year'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Лифт:'):
            advert['elevator'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Парковка:'):
            advert['parking'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Балкон:'):
            advert['balcony'] = ' '.join(properties[row].find('td').text.split())
            continue
        if(prop == 'Телефон:'):
            advert['phone'] = ' '.join(properties[row].find('td').text.split())
            continue
    advert['description'] = soup.find_all('div', 'object_descr_text')[0].text.strip()
    print(advert)


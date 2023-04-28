import os
import sys
import requests


def get_png(coord, zoom, map_file):
    l_str = 'sat,skl'
    size = '600,450'
    map_request = f"https://static-maps.yandex.ru/1.x/?ll={coord}&size={size}&z={zoom}&l={l_str}"
    response = requests.get(map_request)
    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
    with open(f'static/img/{map_file}', "wb") as file:
        file.write(response.content)
    return map_file


def delete_png(map_file):
    os.remove(f'static/img/{map_file}')
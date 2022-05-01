import requests
from bs4 import BeautifulSoup
import os
import datetime
from plyer import notification
from plyer.utils import platform
from pathlib import Path


cities = '297576'  # город (мой 297576)
hospital = '151'  # поликлиника (151)
specialization = '73'  # 73 специализация
weeks = ['14', '15', '16', '17', '18']  # недели для поиска (6 это 1-6 февраля)
year = '2022'


def write_to_file(msg):
    my_file = open(path_to_file, 'a') 
    now = datetime.datetime.now()   # 
    date = now.strftime('%d.%m.%Y %H:%M:%S')
    my_file.write('=============' + date + '===========\n' + msg + '\n')
    my_file.close()


# показ уведомления
def show_popup(msg):
    notification.notify(title='Электронная регистратура', message=msg, app_name='Application name',
    	app_icon=path_to_icon, timeout=30
    )
    

# URL электронной регистратуры
url = 'https://er.medkirov.ru/er/ereg3/cities/%s/hospitals/%s/specializations/%s/calendars/' \
      % (cities, hospital, specialization)
messages = []  # список для вывода сообщений
#path = str(os.path.dirname(os.path.abspath(__file__)))  # путь до папки, где будет лежать файл лога и иконки
path = str(Path(__file__).parent.absolute())

path_to_file = path + '/reg.log' 
path_to_icon = path + '/logo2.' + ('ico' if platform == 'win' else 'png')
# пробежимся по всем неделям
for week in weeks:
    param = {'week': week, 'year': year}    # добавляем GET параметры в запрос
    response = requests.get(url, params=param, verify=False)    # получаем ответ
    soup = BeautifulSoup(response.text, 'lxml')     # преобразовываем

    # получаем текущую неделю строкой
    current_week = soup.find('li', class_='current').find('span').text
    
    find = False    # призкак нашедшихся свободных записей
    doctors = []
    rows = soup.find('table', class_='timetable').find_all('tr', class_='tbody')  # получаем список строк таблицы
    for row in rows:
        doctor = row.find('td', class_='name').find('strong').text  # ФИО врача

        # список дней со свободными записями, в случае отсутствия будет пустым
        frees = row.find_all('span', class_='freeTickets')
        if len(frees) > 0:  # если же не пустой, то проставляем признак и добавляем сообщение
            find = True
            doctors.append(doctor)

    if find:  # если есть свободные записи, добавим в сообщение у каких врачей
        messages.append("%s: Найдены свободные записи у %s" % (current_week, ', '.join(doctors)))
    else:    # если же свободных записей нет, добавим в сообщение прочерк у данной недели
        messages.append("%s: - " % current_week)


message = "\n".join(messages)  # список сообщений преобразовываем в одну строку
write_to_file(message)  # в файл добавляем сообщение
# for msg in messages:
#     show_popup(msg)
show_popup(message)

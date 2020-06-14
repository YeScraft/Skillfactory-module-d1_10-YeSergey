import sys
import time
import requests

# Данные авторизации в API Trello
# Необходимо ввести свои данные
auth_params = {
    'key': "",
    'token': "",
}

# На сайте https://trello.com/ в правом верхнем углу кнопка "С", где настройки вашего профиля
# Необходимо ввести свои данные
user_id = ""

# Адрес, на котором расположен API Trello, # Именно туда мы будем отправлять HTTP запросы
base_url = "https://api.trello.com/1/{}"

board_id = None

def is_number(column_name):
    try:
        int(column_name)
        return True
    except ValueError:
        return False

def read(board_id):
    # Получим данные всех колонок на доске:
    column_data = requests.get(base_url.format('boards')+'/'+board_id+'/lists', params=auth_params).json()
    #print('column_data: ', column_data)
    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:
    for column in column_data:
        #print('column: ', column)
        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists')+'/'+column['id']+'/cards', params=auth_params).json()
        #print('task_data: ', task_data)
        print(column['name'] +'. Всего задач: '+ '{}'.format(len(task_data)))
        if not task_data:
            print('\t'+'Нет задач!')
            continue
        for i, task in enumerate(task_data, 1):
            print('\t{}. {}\tID: {}'.format(i, task['name'], task['id']))

def create(board_id):
    # Выводим данные всех колонок на доске
    column_base = {}
    column_data = requests.get(base_url.format('boards')+'/'+board_id+'/lists', params=auth_params).json()
    for i, column in enumerate(column_data, 1):
        # создаём словарь, где ключ это порядковый номер строки, а значение id строки
        column_base[i] = column['id']
        print('{}. {}'.format(i, column['name']))
    # Создаём список из словаря
    column_keys = list(column_base.keys())
    
    column_name = input("""Возможные действия:
        - введите номер нужной колонки;
        - введите наименование новой колонки
        - нажмите Enter для возврата в меню. \n""")

    # обработка введённого значения
    # если введена цифра и она есть в списке то добавим задачу в неё
    # иначе создаётся новая колонка с названием, как введённое значение
    if len(column_name)!=0 and is_number(column_name):
        if int(column_name) in column_keys:
            task_name = input("Введите наименование задачи: ")
            # отправляем пост запрос на создание задачи
            # column_base[int(column_name)] - id выбранной колонки из словаря column_base
            requests.post(base_url.format('cards'), data={'name': task_name, 'idList': column_base[int(column_name)], **auth_params})
            print('Задача {} добавлена.'.format(task_name))
            return main()
        else:
            # отправляем пост запрос на создание колонки и сразу с ответа берём id новой колонки
            column_id = (requests.post(base_url.format('lists'), data={'name': column_name, 'idBoard': board_id, **auth_params}).json())['id']
            task_name = input("Введите наименование задачи: ")
            requests.post(base_url.format('cards'), data={'name': task_name, 'idList': column_id, **auth_params})
            print('Задача {} добавлена.'.format(task_name))
            return main()
    elif len(column_name) == 0:
        return main()
    # если введена не цифра, то создаётся новая колонка после проверки на существование колонки с таким именем
    else:
        column_id = None
        for column in column_data:
            column_id = None
            if column['name'] == column_name:
                print('Колонка с таким именем уже существует, её ID: {}'.format(column['id']))
                column_id = column['id']
                break
        if column_id == None:
            # отправляем пост запрос на создание колонки и сразу с ответа берём id новой колонки
            column_id = (requests.post(base_url.format('lists'), data={'name': column_name, 'idBoard': board_id, **auth_params}).json())['id']
            task_name = input("Введите наименование задачи: ")
            requests.post(base_url.format('cards'), data={'name': task_name, 'idList': column_id, **auth_params})
            print('Задача {} добавлена.'.format(task_name))
        return main()

def move(board_id):
    # для выбора колонок или заданий использовались те же методы, что и в фунции create
    # Выводим данные всех колонок на доске
    column_base = {}
    column_data = requests.get(base_url.format('boards')+'/'+board_id+'/lists', params=auth_params).json()
    for i_c, column in enumerate(column_data, 1):
        column_base[i_c] = column['id']
        task_data = requests.get(base_url.format('lists')+'/'+column['id']+'/cards', params=auth_params).json()
        print('{}. {}. Всего задач: {}'.format(i_c, column['name'], len(task_data)))
        if not task_data:
            print('\t'+'Нет задач!')
            continue
        for task in task_data:
            print('\t{}\tID: {}'.format(task['name'], task['id']))
    # Создаём список, где ключ это порядковый номер строки, а значение id строки
    column_keys = list(column_base.keys())
    
    column_number = input("""Возможные действия:
        - введите номер колонки, из которой хотите переместить задачу;
        - нажмите Enter для возврата в меню. \n""")

    # логика проверки введённых параметров, как в функции create
    if len(column_number) == 0:
        return None
    else:
        if len(column_number)!=0 and is_number(column_number):
            if int(column_number) in column_keys:
                for column in column_data:
                    if column['id'] == column_base[int(column_number)]:
                        task_data = requests.get(base_url.format('lists')+'/'+column['id']+'/cards', params=auth_params).json()
                        task_base = {}
                        if not task_data:
                            print('\t'+'Нет задач!')
                            break
                        for i, task in enumerate(task_data, 1):
                            task_base[i] = task['id']
                            print('{}. \t{}\tLastActivity: {}\tID: {}'.format(i, task['name'], task['dateLastActivity'], task['id']))

                        task_keys = list(task_base.keys())

                        task_number = input("""Возможные действия:
                            - введите номер задания, которое вы хотите переместить;
                            - нажмите Enter для возврата в меню. \n""")
                        if len(task_number) == 0:
                            return None
                        else:
                            if len(task_number)!=0 and is_number(task_number):
                                if int(task_number) in task_keys:
                                    column_number = input ("Введите номер колонки, в которую хотите переместить задание: ")
                                    if len(column_number) == 0:
                                        return None
                                    else:
                                        if len(column_number)!=0 and is_number(column_number):
                                            if int(column_number) in column_keys:
                                                requests.put(base_url.format('cards')+'/'+task_base[int(task_number)]+'/idList', data = {'value': column_base[int(column_number)], **auth_params})
                                                break
                                            else:
                                                print("Не корректные данные.")
                                                return None
                                        else:
                                            print("Не корректные данные.")
                                            return None
                                else:
                                    print("Не корректные данные.")
                                    return None
                            else:
                                print("Не корректные данные.")
                                return None
            else:
                print("Не корректные данные.")
                return None
        else:
            print("Не корректные данные.")
            return None

def add_column(board_id):
    # Выводим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards')+'/'+board_id+'/lists', params=auth_params).json()
    for i, column in enumerate(column_data, 1):
        print('{}. {}'.format(i, column['name']))
    
    column_name = input("Введите наименование колонки или просто нажмите Enter для возврата в меню: ")
    # Проверка выбранного режима
    if len(column_name) == 0:
        return None
    else:
        # Проверка на существование колонки с вводимым именем
        column_id = None
        for column in column_data:
            column_id = None
            if column['name'] == column_name:
                print('Колонка с таким именем уже существует, её ID: {}'.format(column['id']))
                column_id = column['id']
                break
        if column_id == None:
            requests.post(base_url.format('lists'), data={'name': column_name, 'idBoard': board_id, **auth_params})
            

def main():
    board = requests.get(base_url.format('members/') + user_id + '/boards/', params=auth_params).json()
    # берём для работы первую доску из аккаунта
    if len(board) == 0:
        print("У вас не оказалось ни одной доски.")
        board_name = input("Введите имя новой доски: ")
        board = requests.post(base_url.format('boards/'), data={'name': board_name, **auth_params})
        # на всякий случай даём сайту раздуплиться
        time.sleep(5)
        main()
    board_id = board[0]['id']
    column_data = requests.get(base_url.format('boards')+'/'+board_id+'/lists', params=auth_params).json()
    if len(column_data) == 0:
        print("У вас не оказалось ни одной колонки.")
        column_name = input("Введите имя новой колонки: ")
        requests.post(base_url.format('lists'), data={'name': column_name, 'idBoard': board_id, **auth_params})
    mode = 0
    while mode != "3":
        mode = input("""Выбери режим:
        1 - Вывести данные;
        2 - Добавить колонку;
        3 - Добавить задачу;
        4 - Переместить задачу;
        5 - Выйти.\n""")
        if mode == "1":
            read(board_id)
        elif mode == "2":
            add_column(board_id)
        elif mode == "3":
            create(board_id)
        elif mode == "4":
            move(board_id)
        elif mode == "5":
            print("Благодарю за сотрудничество!")
            break
            # StopIteration
        else:
            print("Некорректный режим!")

if __name__ == "__main__":
    main()

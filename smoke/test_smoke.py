# -*- coding: utf-8 -*-
import pytest
import shutil
import os
import psutil
import time


# Здесь будут еще 3 теста. После теста 3 предполагается наличие запущенного секуроса в дефолтном режиме
# Как сам тест сделан будет, нужно будет изменить немного тест 4


def test_smoke_object(securos_auto):
    '''4. Добавление объекта (камера с вирт. видео)
    Описание: Тест для проверки возможности добавить рабочую камеру в конфигурацию. Проверяет возможность добавление
    объектов, работоспособность медиа клиента и отображение видео.
    Предусловия: Все предыдущие тесты в тест-комплекте завершены успешно. В папку с тестами помещено виртуальное видео
    из приложения 1.01.

    Шаги выполнения:
        1. Открыть дерево объектов в конфигурации из панели управления
        2. Выделить объект "Компьютер" в дереве
        3. Активировать контрол "Создать" на панели управления
        4. Выбрать элемент "Устройство видеозахвата" в выпадающем списке
        5. Ввести в поля следующую информацию и применить
            а. Тип: virtual
            b. Канал граббера: 01
        6. Создать под объектом граббера камеру со следующими настройками
            a. Канал: 1

    Ожидаемый результат:
        1. Дерево открылось
        2. Объект выделен
        3. Появилось контекстное меню с элементами для добавления
        4. Появилось окно настроек нового объекта
        5. Настройки запомнились, окно закрылось, в дереве объектов под объеком Компьютер появилась группа объектов
        Устройства видеозахвата, под которой появился объект Устройство видеозахвата 1
        6. Под объектом Устройство видеозахвата 1 появился объект Камера 1. На медиа клиенте появилась камера
        и видеопоток с нее.'''

    shutil.copy2(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "1._01"),
                 pytest.SECUROS_WIN)

    cli = securos_auto["client"].top_window()
    cli["CheckBox2"].click_input()

    tree = securos_auto["core"].top_window()
    assert tree.exists() # Шаг 1
    tree["Система"].click_input(double=True)
    tree["SecurOS Enterprise"].click_input(double=True)
    tree["Оборудование"].click_input(double=True)
    tree.window(title_re="Компьютер*").click_input()
    assert tree.window(title_re="Компьютер*").is_selected() # Шаг 2
    time.sleep(1)
    securos_auto["core"]["Pane22"]["Создать"].click_input()
    menu = securos_auto["core"].Menu
    assert menu.exists() # Шаг 3
    time.sleep(1)
    menu["Устройство видеозахвата"].click_input()
    sets = securos_auto["core"].window(title_re="Параметры")
    assert sets.exists() # Шаг 4
    time.sleep(1)
    sets["ComboBox"].click_input()
    sets["ListBox"].type_keys("{UP 1}{DOWN 40}{ENTER}") # TODO: костыль, сломается когда добавят больше производителей
    sets["Ok Enter"].click_input()
    time.sleep(1)
    pane = securos_auto["core"].Pane
    pane["ComboBox33"].click_input()
    pane["01"].click_input()
    pane["ОК"].click_input()
    assert tree["Устройство видеозахвата 1"].exists() # Шаг 5
    time.sleep(1)
    tree["Устройство видеозахвата 1"].click_input(button="right")
    menu["Создать"].click_input()
    menu["Камера"].click_input()
    sets["Ok Enter"].click_input()
    pane["ОК"].click_input()
    time.sleep(1)
    monitor = securos_auto["monitor"].top_window()
    monitor["Камера 1"].click_input()
    assert tree.window(title="Камера 1 [1]").exists() # Шаг 6
    '''Хитрая проверка - проверяем наличие кнопки "Поставить на рхрану" в окне камеры. Если камеры нет в МК или нет
    с нее видео - то кнопка будет недоступна и это баг. Так костыль пока конечно.'''
    assert monitor.window(title_re="Поставить на охрану*").exists() # TODO: Надо проверять видеопоток лучше возможно


def test_smoke_shutdown(securos_auto, securos_pids):
    '''5. Завершение работы
    Описание: Тест для проверки корректного завершения работы SecurOS по команде Завершить работу из панели управления.
    Предусловия: Все предыдущие тесты в тест-комплекте завершены успешно.

    Шаги выполнения:
        1. Активировать контрол-иконку слева в панели управления
        2. В выпадающем меню выбрать элемент "Завершение работы"

    Ожидаемый результат:
        1. Открылось выпадающее меню с вариантами "Справка (F1)", "Настройка Панели управления" и "Завершение работы"
        2. SecurOS закрыл все процессы и выгрузился из памяти без падений и сообщений об ошибках.'''

    cli = securos_auto["client"].top_window()
    cli["MenuItem"].click_input()
    menu = securos_auto["client"].Menu
    assert menu["Завершение работы"].exists() # Шаг 1
    menu["Завершение работы"].click_input()
    time.sleep(10)
    for pid in securos_pids.values(): # Шаг 2
        assert not psutil.pid_exists(pid)


def test_smoke_config(securos_start, securos_auto, securos_pids):
    '''6. Сохранение конфигурации (второй запуск)
    Описание: Тест, проверяющий повторный запуск уже настроенной системы и сохранение изменений, внесенных в конфигурацию
    за предыдущий сеанс работы.
    Предусловия: Все предыдущие тесты в тест-комплекте завершены успешно.

    Шаги выполнения:
        1. Запустить SecurOS
        2. Открыть дерево объектов в конфигурации из панели управления

    Ожидаемый результат:
        1. SecurOS запускается без ошибок, отображается медиа клиент и панель управления. В медиа клиенте есть камера,
        с которой идет отображение видео.
        2. В дереве объектов присутсвует группа объектов Устройства видеозахвата под объектом Компьютер, под группой
        присутствует объект Устройство видеозахвата 1, а под ней объект Камера 1.'''

    # Шаг 1 проверяется на этапе запуска теста в securos_auto
    cli = securos_auto["client"].top_window()
    cli["CheckBox2"].click_input()
    tree = securos_auto["core"].top_window()
    tree["Система"].click_input(double=True)
    tree["SecurOS Enterprise"].click_input(double=True)
    tree["Оборудование"].click_input(double=True)
    tree.window(title_re="Компьютер*").click_input(double=True)
    assert tree["Устройства видеозахвата"].exists()
    tree["Устройства видеозахвата"].click_input(double=True)
    assert tree["Устройство видеозахвата 1 [1]"].exists()
    tree["Устройство видеозахвата 1"].click_input(double=True)
    assert tree["Камера 1 [1]"].exists()
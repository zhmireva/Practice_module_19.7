import pytest
from api import PetFriends
from settings import valid_email, valid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """Проверяем что запрос api ключа возвращает статус 200 и в тезультате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо ''"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0

    def test_add_new_pet_simple(name='Murzik', animal_type='Cat', age='2'):
        _, auth_key = pf.get_api_key(valid_email, valid_password)
        status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
        assert status == 200
        assert result['name'] == name

def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер',
                                     age='4', pet_photo='images/cat1.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Mya', animal_type='Cat', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_add_new_pet_photo(pet_photo='images/Kotya.jpeg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) > 0:
        pet_id = my_pets['pets'][0]['id']
        status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo)

        assert status == 200
        assert 'pet_photo' in result


# Negative tests below
def test_get_api_key_for_invalid_user(email='invalid@mmm.ru', password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'Forbidden' in result


# Negative test below
def test_get_api_key_for_empty_user(email='', password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'Forbidden' in result


# Negative test below
def test_get_api_key_for_invalid_pswrd(email=valid_email, password='678'):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'Forbidden' in result


# Negative test below
def test_get_api_key_for_empty_pswrd(email=valid_email, password=''):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'Forbidden' in result


# Negative test below
def test_get_api_key_for_incorrect_userdata(email='23', password='password'):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert 'Forbidden' in result


# Negative test below
def test_get_all_pets_with_outdated_auth_key(filter=''):
    auth_key = {'key': 'd3c1355cc3c551acbebe5b58ead5d09897aa6ff03ce448554d40987d'}
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 403
    assert 'Forbidden' in result


# Negative test below
def test_get_all_pets_with_symbols_in_auth_key(filter=''):
    auth_key = {'key': '!@#$%^&*!@#$%^&*!@#$%^&*!@#$%^&!@#$%^&*!@#$%^&*!@#$%^&*@'}
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 403
    assert 'Forbidden' in result


# Negative test below
def test_get_all_pets_with_incorrect_filter(filter='pets'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 500
    assert 'Internal Server Error' in result


# Negative test below
def test_get_my_pets_with_cyrillic_in_filter(filter='ьн_зуеы'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 500
    assert 'Internal Server Error' in result


# Negative test below
def test_get_all_pets_with_255_characters_in_filter(
        filter='123456789123456789123456789123456789123456789123456789123456789123456789123123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 500
    assert 'Internal Server Error' in result


# Negative test below
def test_unsuccessful_delete_self_pet_with_empty_pet_id():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Кот", "Кошка", "2")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = ''
    status, _ = pf.delete_pet(auth_key, pet_id)

    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    assert status == 404
    assert pet_id not in my_pets.values()

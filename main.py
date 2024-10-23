import requests
import json
import argparse
import os
from tokene import token


def get_user_info(user_id, access_token):
    url = 'https://api.vk.com/method/users.get'
    params = {
        'user_ids': user_id,
        'access_token': access_token,
        'v': '5.131'
    }
    response = requests.get(url, params=params)
    return response.json()

def get_followers(user_id, access_token):
    url = 'https://api.vk.com/method/users.getFollowers'
    params = {
        'user_id': user_id,
        'access_token': access_token,
        'v': '5.131'
    }
    response = requests.get(url, params=params)
    return response.json()

def get_subscriptions(user_id, access_token):
    url = 'https://api.vk.com/method/users.getSubscriptions'
    params = {
        'user_id': user_id,
        'extended': 1,
        'access_token': access_token,
        'v': '5.131'
    }
    response = requests.get(url, params=params)
    return response.json()

def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main(user_id, output_file, access_token):
    user_info = get_user_info(user_id, access_token)
    followers = get_followers(user_id, access_token)
    subscriptions = get_subscriptions(user_id, access_token)

    if 'response' in user_info and 'response' in followers and 'response' in subscriptions:
        data = {
            'user_info': user_info['response'],
            'followers': followers['response']['items'],
            'subscriptions': subscriptions['response']['items']
        }

        save_to_json(data, output_file)
        print(f"Информация о пользователе '{user_id}' сохранена в '{output_file}'")
    else:
        print("Ошибка при получении данных. Проверьте идентификатор пользователя и токен доступа.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Получить информацию о пользователе ВК.')
    parser.add_argument('--user_id', type=str, default='1', help='Идентификатор пользователя ВК (по умолчанию 1)')
    parser.add_argument('--output_file', type=str, default='output.json', help='Путь к файлу результата (по умолчанию output.json)')
    args = parser.parse_args()

    ACCESS_TOKEN = token

    main(args.user_id, args.output_file, ACCESS_TOKEN)

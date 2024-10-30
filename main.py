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

# #Добавил функцю для обхода в глубину 
def get_user_data(user_id, access_token, depth=0, max_depth=2, visited=None):
    if visited is None:
        visited = set()

    if depth > max_depth or user_id in visited:
        return {}

    visited.add(user_id)

    user_info = get_user_info(user_id, access_token)
    followers = get_followers(user_id, access_token)
    subscriptions = get_subscriptions(user_id, access_token)

    data = {
        'user_info': user_info['response'][0] if 'response' in user_info and user_info['response'] else {},
        'followers': [],
        'subscriptions': []
    }

    # Отладочная информация
    print(f"Обрабатываем пользователя: {user_id}, глубина: {depth}, подписчики: {followers}")

    if depth < max_depth and 'response' in followers:
        for follower_id in followers['response']['items']:
            print(f"Обрабатываем подписчика: {follower_id} на глубине {depth + 1}")
            follower_data = get_user_data(follower_id, access_token, depth + 1, max_depth, visited)
            if follower_data:  # Добавляем только непустые данные
                data['followers'].append(follower_data)
            else:
                 print(f"Подписчик {follower_id} не имеет данных или не был найден.")

    if 'response' in subscriptions:
        for subscription in subscriptions['response']['items']:
            group_data = {
                'id': subscription['id'],
                'is_closed': subscription.get('is_closed', False),
                'type': subscription.get('type', ''),
                'screen_name': subscription.get('screen_name', 'Unknown')
            }
            if 'name' in subscription:
                group_data['name'] = subscription['name']
            else:
                group_data['name'] = 'Unknown'

            data['subscriptions'].append(group_data)

    return data

def main(user_id, output_file, access_token):
    data = get_user_data(user_id, access_token)

    save_to_json(data, output_file)
    print(f"Информация о пользователе '{user_id}' сохранена в '{output_file}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Получить информацию о пользователе ВК.')
    parser.add_argument('--user_id', type=str, default='1', help='Идентификатор пользователя ВК (по умолчанию 1)')
    parser.add_argument('--output_file', type=str, default='output7.json', help='Путь к файлу результата (по умолчанию output.json)')
    args = parser.parse_args()

    ACCESS_TOKEN = token

    main(args.user_id, args.output_file, ACCESS_TOKEN)
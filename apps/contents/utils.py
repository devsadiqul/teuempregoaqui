import requests

def get_user_info(user_id):
    try:
        response = requests.get(
            f"http://10.10.12.18:7000/api/v1/users/{user_id}/",
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None
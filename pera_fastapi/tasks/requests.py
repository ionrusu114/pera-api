import requests

def call_fastapi_endpoint_test_gwt_account(id_account):
    response = requests.get(f'https://www.api.ionrusu114.me/api/telegram/account/{id_account}')
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Request failed with status {response.status_code}")

def call_update_account_status(id_account, status):
    response = requests.patch(f'https://www.api.ionrusu114.me/api/telegram/account/{id_account}', params={'account': status})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Request update account failed with status {response.status_code}")

def call_fastapi_update_group_senders(id_group_senders, data):
    response = requests.put(f'https://www.api.ionrusu114.me/api/telegram/group_senders/{id_group_senders}', json=data)
    if response.status_code == 200:
        # print(response.json())
        return response.json()
    else:
        raise Exception(f"Request update group senders failed with status {response.status_code}")

def call_get_task_id(id_group_sender):
    response = requests.get(f'https://www.api.ionrusu114.me/tasks/task/{id_group_sender}/group_sender')
    if response.status_code == 200:
        # print(response.json())
        return response.json()
    else:
        raise Exception(f"Request get task id failed with status {response.status_code}")

def call_update_task_work(id_group_sender, data):
    task_id = call_get_task_id(id_group_sender)

    response = requests.put(f'https://www.api.ionrusu114.me/tasks/task/{task_id}/worker', json=data)
    if response.status_code == 200:
        # print(response.json())
        return response.json()
    else:
        raise Exception(f"Request update task work failed with status {response.status_code}")

def call_create_history(data):
    response = requests.post(f'https://www.api.ionrusu114.me/api/telegram/history', json=data)
    if response.status_code == 201:
        # print(response.json())
        return response.json()
    else:
        raise Exception(f"Request create hostory failed with status {response.status_code}")



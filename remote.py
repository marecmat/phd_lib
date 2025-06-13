import requests
import os     

def send_discord_notification(title, status, PATH='none'):

    if PATH == 'none': 
        PATH = os.path.dirname(__file__)+"/data/hook"

    HOOK = open(PATH, "r").read().strip()
    
    result = requests.post(
        HOOK, 
        json={
            "content": " ", 
            "username" : "Script status",
            "embeds": [{
                'description': status, 
                'title': title
            }]
        }
    )

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        return err
    else:
        return f"Payload delivered successfully, code {result.status_code}."


def send_data_somewhere(PATH, URL, AUTH_PATH='none', file_list=None):
    print(f"sending data from {PATH} to remote ...")
    if AUTH_PATH == 'none': 
        AUTH_PATH = os.path.dirname(__file__)+"/data/remote"

    with open(AUTH_PATH, 'r') as file:
        # Read the Auth logs
        content = file.read().split('\n')
        AUTH = tuple(content[:2])


    idx = -2 if PATH[-1] == '/' else -1
    split        = PATH.split('/')
    # Index to get the last current folder of the path
    folder_name  = split[idx]               # The current folder name
    rest_of_path = '/'.join(split[:idx])    # The pwd of the upper root of the files to send

    # Create the first folder
    response = requests.request('MKCOL', f'{URL}/{folder_name}', auth=AUTH)
    if file_list == None:
        for root, dirs, files in os.walk(PATH, topdown=True):
            # Walk recursively from the top down in the file tree to send
            current_dir = root.replace(rest_of_path, '')
            
            for dir in dirs:
                response = requests.request('MKCOL', f'{URL}/{current_dir}/{dir}', auth=AUTH)
                print(f"folder '{current_dir}/{dir}' creation {response}")

            for file in files:
                with open(f'{rest_of_path}/{current_dir}/{file}', 'rb') as data:
                    response = requests.put(
                        f'{URL}/{current_dir}/{file}',
                        data=data.read(),
                        auth=AUTH,
                    )
                print(f"file '{file }' creation {response}")

    else: 
        current_dir = PATH.replace(rest_of_path, '')
        for file in file_list:
            with open(f'{rest_of_path}/{current_dir}/{file}', 'rb') as data:
                response = requests.put(
                    f'{URL}/{current_dir}/{file}',
                    data=data.read(),
                    auth=AUTH,
                )
            print(f"file '{file }' creation {response}")
    return None
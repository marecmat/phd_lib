import requests
import os     

def send_discord_notification(filename, status, PATH='none'):
    if PATH == 'none': 
        PATH = os.path.dirname(__file__)+"/data/hook"
    HOOK = open(PATH, "r").read().strip()
    result = requests.post(
        HOOK, 
        json={
            "content": " ", 
            "username" : "Herald of (probably bad) news",
            "embeds": [{
                'description': status, 
                'title': filename
            }]
        }
    )

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        return err
    else:
        return f"Payload delivered successfully, code {result.status_code}."


def send_data_somewhere(PATH, AUTH_PATH='none'):
    print(f"sending data from {PATH} to remote ...")
    if AUTH_PATH == 'none': 
        AUTH_PATH = os.path.dirname(__file__)+"/data/remote"

    with open(AUTH_PATH, 'r') as file:
        content = file.read().split('\n')
        URL  = content[2]
        AUTH = tuple(content[:2])

    idx = -2 if PATH[-1] == '/' else -1
    split        = PATH.split('/')
    folder_name  = split[idx] 
    rest_of_path = '/'.join(split[:idx])

    response = requests.request('MKCOL', f'{URL}/{folder_name}', auth=AUTH)
    for root, dirs, files in os.walk(PATH, topdown=True):
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

if __name__ == '__main__':
    send_data_somewhere('/Users/mat/These/usefulStuff_toPythonPath/phd_lib/test_folder_2')
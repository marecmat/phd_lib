def send_discord_notification(filename, status, PATH='none'):
    import requests
    import os     
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

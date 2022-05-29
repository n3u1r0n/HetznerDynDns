import requests
import json
import fire

def get_records(zone_id):
    try:
        response = requests.get(
            url="https://dns.hetzner.com/api/v1/records",
            params={
                "zone_id": zone_id,
            },
            headers={
                "Auth-API-Token": token,
            },
        )
        print('Response HTTP Status Code: {status_code}'.format(status_code=response.status_code))
        return response.json()['records']
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def get_ids(array, name):
    return list(map(lambda element: element['id'], filter(lambda element: element['name'] == name, array)))

def delete_old(ids):
    for id in ids:
        try:
            response = requests.delete(
                url="https://dns.hetzner.com/api/v1/records/{}".format(id),
                headers={
                    "Auth-API-Token": token,
                },
            )
            print('Response HTTP Status Code: {status_code}'.format(status_code=response.status_code))
        except requests.exceptions.RequestException:
            print('HTTP Request failed')

def set_new(name, ip, zone_id, type='A', ttl=60):
    try:
        response = requests.post(
            url="https://dns.hetzner.com/api/v1/records",
            headers={
                "Content-Type": "application/json",
                "Auth-API-Token": token,
            },
            data=json.dumps({
                "value": ip,
                "ttl": ttl,
                "type": type,
                "name": name,
                "zone_id": zone_id
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(status_code=response.status_code))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def get_zones():
    try:
        response = requests.get(
            url="https://dns.hetzner.com/api/v1/zones",
            headers={
                "Auth-API-Token": token,
            },
        )
        print('Response HTTP Status Code: {status_code}'.format(status_code=response.status_code))
        return response.json()['zones']
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def update(zone_name, names, type='A', ttl=60, t=None):
    global token
    token = t or token
    if isinstance(names, str):
        names = [names]
    zone_id = get_ids(get_zones(), zone_name)[0]
    records = get_records(zone_id)
    ip = get_ip()
    for name in names:
        ids = get_ids(records, name)
        if len(ids) != 1:
            delete_old(get_ids(records, name))
            set_new(name, ip, zone_id, type, ttl)
        elif list(filter(lambda element: element['id'] == ids[0], records))[0]['value'] != ip:
            delete_old(get_ids(records, name))
            set_new(name, ip, zone_id, type, ttl)

def get_ip(endpoint='https://ipinfo.io/json'):
    try:
        response = requests.get(
            url=endpoint,
            verify=True
        )
        print('Response HTTP Status Code: {status_code}'.format(status_code=response.status_code))
        return response.json()['ip']
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

token = ''

if __name__ == '__main__':
    fire.Fire(update)
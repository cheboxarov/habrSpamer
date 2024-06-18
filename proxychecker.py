import requests
from typing import List

def proxy_check(proxies: List[str]):
    valid_proxies = []
    for proxy in proxies:
        proxies = {
            "https": f"http://{proxy}/"
        }
        url = 'https://api.ipify.org'
        try:
            response = requests.get(url, proxies=proxies)
            assert response.text == proxy.split("@")[1].split(":")[0]
            valid_proxies.append(proxy)
        except Exception as e:
            pass
    return valid_proxies

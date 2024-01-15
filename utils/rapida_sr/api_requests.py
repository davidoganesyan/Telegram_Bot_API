import requests
from typing import Optional, Dict


def api_request_sr(method: str, url: str, headers: Dict[str, str], **kwargs) -> Optional[str]:
    """
    Базовый запрос к API
    :param method: метод для запроса
    :param url: адрес для запроса
    :param headers: параметры доступа
    :param kwargs: прочие параметры
    :return: результат запроса или исключения
    """

    try:
        response = requests.request(method=method, url=url, headers=headers, timeout=100, **kwargs)
        if response.status_code == requests.codes.ok:
            return response.text
    except requests.exceptions as exc:
        return exc

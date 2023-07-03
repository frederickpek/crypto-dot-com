import time
from crypto_dot_com.consts import MAX_LEVEL


def get_nonce() -> int:
    return int(time.time() * 1000)


def get_id() -> int:
    return 69


def params_to_str(obj: dict, level=0) -> str:
    if level >= MAX_LEVEL:
        return str(obj)

    return_str = ""
    for key in sorted(obj):
        return_str += key
        if obj[key] is None:
            return_str += 'null'
        elif isinstance(obj[key], list):
            for subObj in obj[key]:
                return_str += params_to_str(subObj, ++level)
        else:
            return_str += str(obj[key])
    return return_str


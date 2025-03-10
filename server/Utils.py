
import time
import random

def to_base36_random() -> str:
    timestamp = int(time.time() * 10000000)
    random_number = random.randint(0, 999999)
    combined_value = timestamp * 1000000 + random_number
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyz"
    base36 = []
    while combined_value != 0:
        combined_value, i = divmod(combined_value, 36)
        base36.append(alphabet[i])
    result = "".join(reversed(base36))
    return result.zfill(9)
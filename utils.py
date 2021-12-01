import pathlib
import time
import requests

ROOT = pathlib.Path(__file__).parent
INPUTS_DIR = ROOT / 'inputs'
TOKEN = (ROOT / '.token').read_text().strip()
URL = f"https://adventofcode.com/2021/day/{{day}}"


def raw(day):
    day = str(day)
    file = INPUTS_DIR / f"day{day.rjust(2, '0')}.txt"

    if not file.exists():
        response = requests.get(url=URL.format(day=day) + "/input", cookies={"session": TOKEN})
        if not response.ok:
            raise ValueError("Requesting input failed.")
        file.write_text(response.text.strip())

    return file.read_text().splitlines()


def timed():
    def inner_decorator(func):
        def wrapper_method(*arg, **kw):
            start = time.time_ns()
            result = func(*arg, **kw)
            ms = (time.time_ns() - start) / (10 ** 6)
            print(f"{func.__name__}: {result} ({ms:.2f} ms)")
        return wrapper_method
    return inner_decorator

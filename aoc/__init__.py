import functools
import pathlib
import time
import re
import webbrowser
from typing import Callable

import bs4
import yaml

import requests

AOC_DIR = pathlib.Path(__file__).parent
ROOT_DIR = AOC_DIR / '..'
INPUTS_DIR = AOC_DIR / 'inputs'
SUBMISSIONS_FILE = AOC_DIR / 'submissions.yml'
TOKEN = (AOC_DIR / '.token').read_text().strip()
COOKIES = {"session": TOKEN}
URL = f"https://adventofcode.com/2021/day/{{day}}"


def raw(day):
    day = str(day)
    file = INPUTS_DIR / f"day{day.rjust(2, '0')}.txt"

    if not file.exists():
        response = requests.get(url=URL.format(day=day) + "/input", cookies=COOKIES)
        if not response.ok:
            raise ValueError("Requesting input failed.")
        file.write_text(response.text.strip())

    return file.read_text().strip()


def submit_core(day, func: Callable):
    day = str(day)
    part = "1" if func.__name__ == "part_one" else "2"
    submissions = yaml.full_load(SUBMISSIONS_FILE.read_text())
    current = submissions.setdefault(day, {"1": {}, "2": {}})[part]

    start = time.time_ns()
    solution = func()

    if solution is None:
        return

    ms = (time.time_ns() - start) / (10 ** 6)
    print(f"{func.__name__}: {solution} ({ms:.2f} ms)")

    solution = str(solution)

    if "solution" in current and current["solution"] == solution:
        print("✅ " + current[solution]['message'])
        current[solution]['time'] = ms
    elif solution in current:
        print('❗️ Solution already submitted: ' + current[solution]['message'])
    else:
        response = requests.post(
            url=URL.format(day=day) + "/answer",
            cookies=COOKIES,
            data={"level": part, "answer": solution}
        )

        if not response.ok:
            print('⚠️ ' + response.text)
            return

        response_text = bs4.BeautifulSoup(response.text, "html.parser").article.text
        message = re.split(r'[.!]', response_text)[0] + "!"

        if response_text.startswith('You gave an answer too recently'):
            print('⏳ ' + response_text)
            return
        elif response_text.startswith("That's the right answer"):
            print("✅ " + message)
            current["solution"] = solution
            if part == "1":
                webbrowser.open(response.url)
        else:
            print("❌ " + message)
        current[solution] = {"message": message, "time": ms}

    SUBMISSIONS_FILE.write_text(yaml.dump(submissions))


def submit(day: int):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper():
            submit_core(day, func)

        wrapper()

        return wrapper

    return decorator


def timed():
    def inner_decorator(func):
        def wrapper_method(*arg, **kw):
            start = time.time_ns()
            result = func(*arg, **kw)
            ms = (time.time_ns() - start) / (10 ** 6)
            print(f"{func.__name__}: {result} ({ms:.2f} ms)")

        return wrapper_method

    return inner_decorator

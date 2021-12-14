import functools
import time
import re
import webbrowser
from typing import Callable

import bs4
import yaml

import requests

from .constants import INPUTS_DIR, COOKIES, SUBMISSIONS_FILE, URL, EXAMPLES_FILE


def pad(x):
    return str(x).ljust(14)


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
    current = submissions.setdefault(day.rjust(2, '0'), {"1": {}, "2": {}})[part]

    start = time.time_ns()
    solution = func(raw(day=day))

    if solution is None:
        return

    ms = (time.time_ns() - start) / (10 ** 6)

    icon, message, solution = '', '', str(solution)
    if "solution" in current and current["solution"] == solution:
        icon, message = "✅", ""  # current[solution]['message']
        current[solution]['time'] = min(current[solution]['time'], ms)
    elif solution in current:
        icon, message = "❗️", current[solution]['message']
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
            icon, message = "⏳", response_text
        else:
            if response_text.startswith("That's the right answer"):
                icon, message = "✅", ""
                current["solution"] = solution
                if part == "1":
                    webbrowser.open(response.url)
            else:
                icon = "❗️"
            current[solution] = {"message": message, "time": ms}

    print(' '.join([f"{icon} input:  ", pad(solution), f"({ms:.2f} ms)"]))
    if len(message):
        print(message)

    SUBMISSIONS_FILE.write_text(yaml.dump(submissions))


def run_example(day: int, func: Callable):
    day = str(day)
    part = "1" if func.__name__ == "part_one" else "2"
    examples = yaml.full_load(EXAMPLES_FILE.read_text())
    example = examples.setdefault(day.rjust(2, '0'), {"1": {}, "2": {}, "input": ''})
    input = example['input']

    if input == '':
        print(f"⏩ example: {pad('no input')} (skipped)")
        return True

    start = time.time_ns()
    solution = func(input)
    expected = example[part]
    ms = (time.time_ns() - start) / (10 ** 6)

    success = solution == expected
    icon = "✅" if success else "❗"

    print(' '.join([f"{icon} example:", pad(solution), f"({ms:.2f} ms)"]))

    return success


def submit(day: int, skip_example=False):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper():
            print(f"{func.__name__}:")
            if skip_example or run_example(day, func):
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

# if __name__ == "__main__":

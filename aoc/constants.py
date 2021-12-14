import pathlib

AOC_DIR = pathlib.Path(__file__).parent
ROOT_DIR = AOC_DIR / '..'
INPUTS_DIR = AOC_DIR / 'inputs'
SUBMISSIONS_FILE = AOC_DIR / 'submissions.yml'
EXAMPLES_FILE = AOC_DIR / 'examples.yml'
TOKEN = (AOC_DIR / '.token').read_text().strip()
COOKIES = {"session": TOKEN}
URL = f"https://adventofcode.com/2021/day/{{day}}"


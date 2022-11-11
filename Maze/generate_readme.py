import itertools
import re
import subprocess


class Parser:
    ANY = object()

    def __init__(self, table):
        self.table = table

    def parse_first(self, state, data, drop_initial=False):
        i = 0
        start_res = 0
        initial_state = state
        while i < len(data) and state in self.table:
            nxt = self.table[state].get(data[i], self.table[state].get(Parser.ANY))
            if nxt is None:
                break
            if drop_initial and start_res == 0 and nxt != initial_state:
                start_res = i
            if callable(nxt):
                nxt = nxt(data[:i + 1])
            state = nxt
            i += 1
        return data[start_res:i], data[i:]

    def parse_all(self, state, data, drop_initial=False):
        left, right = self.parse_first(state, data, drop_initial=drop_initial)
        result = [left]
        while len(right) > 0:
            left, right = self.parse_first(state, right, drop_initial=drop_initial)
            result.append(left)
        return result


def files():
    with subprocess.Popen(["git", "ls-files"], shell=True, stdout=subprocess.PIPE) as ls_proc:
        ls_stdout, _ = ls_proc.communicate()
    for filename in ls_stdout.decode("utf-8").split("\n"):
        if filename.endswith(".py") and not filename.endswith("__init__.py") and not re.search(r"/test", filename):
            yield filename


def summarize(filename):
    class_splitter = Parser({
        -1: {},
        0: {"class": 1, '"""': 10, Parser.ANY: 0},
        1: {'"""': 2, Parser.ANY: 1},
        2: {'"""': -1, Parser.ANY: 2},
        10: {'"""': 0, Parser.ANY: 10},
    })
    def_splitter = Parser({
        -1: {},
        0: {"def": 1, '"""': 10, Parser.ANY: 0},
        1: {'"""': 2, Parser.ANY: 1},
        2: {'"""': -1, Parser.ANY: 2},
        10: {'"""': 0, Parser.ANY: 10},
    })
    with open(filename, "r", encoding="utf-8") as python_file:
        source_code = python_file.read()
    source_tokens = re.split(r"(\s+)", source_code)
    result = ""
    for class_preamble_tokens in class_splitter.parse_all(0, source_tokens, drop_initial=True):
        if class_preamble_tokens[0] == "class":
            if result:
                result += '\n'
            class_preamble = "".join(class_preamble_tokens) + "\n\n"
            result += class_preamble
    for func_preamble_tokens in def_splitter.parse_all(0, source_tokens, drop_initial=True):
        if (func_preamble_tokens[0] == "def"
                and len(func_preamble_tokens) > 2
                and not func_preamble_tokens[2].startswith("_")):
            func_preamble = "".join(itertools.takewhile(lambda it: it != '"""', func_preamble_tokens)).rstrip()
            result += (' ' * 4) + func_preamble + "\n"
    return result


def main():
    for filename in ["Common/state.py"]:  # files():
        print(f"### {filename}\n\n```python\n{summarize(filename).strip()}\n```\n")


if __name__ == "__main__":
    main()

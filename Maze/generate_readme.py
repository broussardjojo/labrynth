import itertools
import os
import re
import subprocess
import sys


def takewhile_plus1(predicate, iterable):
    for item in iterable:
        yield item
        if not predicate(item):
            break


def yield_if(should_yield, item):
    if should_yield:
        yield item


class Parser:
    ANY = object()

    def __init__(self, table):
        self.table = table

    def parse_first(self, state, data, drop_until_state=None):
        i = 0
        start_res = -1
        while i < len(data) and state in self.table:
            nxt = self.table[state].get(data[i], self.table[state].get(Parser.ANY))
            if nxt not in self.table:
                break
            if drop_until_state is not None and start_res == -1 and nxt == drop_until_state:
                start_res = i
            if callable(nxt):
                nxt = nxt(data[:i + 1])
            state = nxt
            i += 1
        start_res = max(0, start_res)
        return data[start_res:i], data[i:]

    def parse_all(self, state, data, drop_until_state=None):
        left, right = self.parse_first(state, data, drop_until_state=drop_until_state)
        result = [left]
        while len(right) > 0:
            left, right = self.parse_first(state, right, drop_until_state=drop_until_state)
            result.append(left)
        return result


def files():
    with subprocess.Popen(["/usr/bin/git", "ls-files"], cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE) as ls_proc:
        ls_stdout, ls_stderr = ls_proc.communicate()
    for filename in ls_stdout.decode("utf-8").split("\n"):
        if filename.endswith(".py") and not filename.endswith("__init__.py") and not re.search(r"/test", filename):
            yield filename


def code_folding_blocks(source_code):
    block_start = 0
    for match in re.finditer(r"\n *(?!\s)", source_code):
        leading_spaces = len(match.group(0)) - 1
        if leading_spaces == 0 and match.start() > block_start:
            yield source_code[block_start:match.start()]
            block_start = match.start()
    yield source_code[block_start:]


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
        1: {'"""': 2, "def": -2, Parser.ANY: 1},
        2: {'"""': -1, Parser.ANY: 2},
        10: {'"""': 0, Parser.ANY: 10},
    })
    with open(filename, "r", encoding="utf-8") as python_file:
        source_code = python_file.read()
    result = ""
    for code_block in code_folding_blocks(source_code):
        block_summary = []
        block_tokens = re.split(r"(\s+)", code_block)
        class_name = None
        for class_preamble_tokens in class_splitter.parse_all(0, block_tokens, drop_until_state=1):
            if class_preamble_tokens[0] == "class" and len(class_preamble_tokens) > 2:
                class_name = class_preamble_tokens[2].split("(")[0]
                block_summary.append("".join(class_preamble_tokens))
        for func_preamble_tokens in def_splitter.parse_all(0, block_tokens, drop_until_state=1):
            if func_preamble_tokens[0] == "def" and len(func_preamble_tokens) > 2:
                signature = list(itertools.takewhile(lambda it: it != '"""', func_preamble_tokens))
                func_name = func_preamble_tokens[2].split("(")[0]
                no_docstring = len(signature) == len(func_preamble_tokens)
                no_return_type = "->" not in signature
                if no_docstring:
                    if no_return_type:
                        signature = list(takewhile_plus1(lambda it: not it.endswith("):"), signature))
                    else:
                        arrow_idx = signature.index("->")
                        return_type_tokens = list(
                            takewhile_plus1(lambda it: not it.endswith(":"), signature[arrow_idx + 1:]))
                        signature = [*signature[:arrow_idx + 1], *return_type_tokens]
                signature_text = "".join(signature).rstrip()
                if no_docstring or (no_return_type and func_name != "__init__"):
                    whats_missing = [*yield_if(no_docstring, "docstring"),
                                     *yield_if(no_return_type and func_name != "__init__", "return type")]
                    class_txt = f" ({class_name})\n    " if class_name is not None else "\n"
                    print(f"Missing {' and '.join(whats_missing)} in {filename}{class_txt}{signature_text}", file=sys.stderr)
                if not func_name.startswith("_"):
                    block_summary.append(signature_text)
        if class_name:
            result += block_summary[0]
            if len(block_summary) > 1:
                result += "\n"
            for method_summary in block_summary[1:]:
                result += "\n" + (" " * 4) + method_summary
            result += "\n\n"
        elif len(block_summary) > 0:
            result += "\n".join(block_summary)
            result += "\n"
    return result


def main():
    ignore = {"generate_readme.py", "JSON/definitions.py"}
    for filename in files():
        if not (filename.endswith("Serializer.py") or filename in ignore):
            print(f"### {filename}\n\n```python\n{summarize(filename).strip()}\n```\n")


if __name__ == "__main__":
    main()

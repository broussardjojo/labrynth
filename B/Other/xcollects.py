import fileinput
import sys


def verify_input(input :str) -> bool:
    """
    Verifies the input string is an acceptable string
    :param input: a string that represents the user's input
    :return: true if the string is acceptable, otherwise false
    """
    acceptable_strings = ["\"┘\"\n", "\"┐\"\n", "\"└\"\n", "\"┌\"\n"]
    return input in acceptable_strings


if __name__ == "__main__":
    output_str = "\""
    # loops through stdin
    for line in fileinput.input():
        if verify_input(line):
            # removes extra quotes and new lines from input characters
            line = line.replace("\"", "")
            line = line.replace("\n", "")
            output_str += line
        else:
            sys.stdout.write("\"unacceptable input\"\n")
            exit()
    sys.stdout.write(output_str + "\"\n")



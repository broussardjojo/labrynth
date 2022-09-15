from json import JSONDecoder
import json
import sys

if __name__ == "__main__":
    output_list = []
    json_obj_list = []
    # remove leading spaces
    stdin = sys.stdin.read().lstrip()
    # initialize decoder object
    decoder = JSONDecoder()
    # loop through standard input reading JSON
    while len(stdin) > 0:
        json_obj, index = decoder.raw_decode(stdin)
        json_obj_list.append(json_obj)
        # remove previously read object from string
        stdin = stdin[index:]
        stdin = stdin.lstrip()
    # convert json objects to characters
    for i in json_obj_list:
        if i["vertical"] == "UP":
            if i["horizontal"] == "RIGHT":
                output_list.append("└")
            else:
                output_list.append("┘")
        else:
            if i["horizontal"] == "RIGHT":
                output_list.append("┌")
            else:
                output_list.append("┐")
    # ensure_ascii makes sure character isn't converted to unicode
    json_out = json.dumps(output_list, ensure_ascii=False)
    sys.stdout.write(json_out)

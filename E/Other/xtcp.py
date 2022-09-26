import json
import socket
import sys
from json import JSONDecoder


def parse_data(data_in):
    output_list = []
    json_obj_list = []
    # remove leading spaces
    stdin = data_in.lstrip()
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
    return output_list


if __name__ == "__main__":
    port = int(sys.argv[1])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    s.listen()
    conn, addr = s.accept()
    output = []
    with conn:
        while True:
            data = conn.recv(1024)
            output = output + parse_data(data.decode())
            if not data:
                json_out = json.dumps(output, ensure_ascii=False)
                conn.sendall((str(json_out) + '\n').encode())
                break
        conn.close()
    s.close()

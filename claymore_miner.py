#!/usr/local/bin/python3
# claymore miner api monitor
# 7/03/17
# updated 7/03/17

import json
import socket
import minor


def create_client():
    host = minor.claymore_host
    port = minor.claymore_port

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    return client


def create_request():
    request = {'method': 'miner_getstat1', 'jsonrpc': '2.0', 'id': 0}

    return json.dumps(request)


def get_stats(client, request):
    client.send(request.encode('ascii'))
    response = client.recv(1024)

    return json.loads(response.decode('ascii'))


stats = get_stats(create_client(), create_request())
print(stats)

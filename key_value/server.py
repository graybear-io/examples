import os
import json
import wifi
import mdns
import socketpool
import storage
from adafruit_httpserver import as_route, Route, Server, Request, Response, FileResponse, GET, POST


# .json file where the key/value data is pulled from
# default is keys.json
with open(os.getenv("key_file"), "r") as h:
    keys = json.load(h)
pool = socketpool.SocketPool(wifi.radio)


@as_route("/", GET)
def base_index(request: Request):
    return FileResponse(request, "index.html")


@as_route("/keys", GET)
def key_list(request: Request):
    return Response(request, json.dumps(keys), content_type="text/html")


def get_key_value(request: Request, key_name: str):
    val = keys.get(key_name, "")
    print(f"get_key_value: {key_name} = {val}")
    return Response(request, f"{val}", content_type="text/html")


def set_key_value(request: Request, key_name: str):
    print(f"set_key_value: {key_name}")
    print(request.json())
    return Response(request, "set_key_value", content_type="text/html")


get_key_route = Route("/key/<key_name>", GET, get_key_value)
set_key_route = Route("/key/<key_name>", POST, set_key_value)


def kv_server():
    # this causes our device to broadcast a hostname of "mdns-bear.local"
    # which you can then connect with using "mdns-bear.local"
    # default is mdns-bear
    mdns_hostname = os.getenv("mdns_host")
    # point the HTTPServer at the directory to use for files to serve
    # default is /static
    web_root = os.getenv("web_root")

    if storage.getmount('/').readonly:
        print('No SD Card detected or is read-only')
        file_storage = False
    else:
        print('SD Card detedted and is writeable')
        file_storage = True

    mdns_server = mdns.Server(wifi.radio)
    mdns_server.hostname = mdns_hostname
    mdns_server.advertise_service(service_type="_http", protocol="_tcp", port=5000)

    server = Server(pool, "/static", debug=True)
    server.add_routes(
        [
            base_index,
            key_list,
            get_key_route,
            set_key_route,
        ]
    )
    server.serve_forever(str(wifi.radio.ipv4_address))

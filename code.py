import os
import time
import server
import microcontroller


if os.getenv("mode") == "server":
    try:
        # setup the web server and listen for requests
        server.kv_server()
    except OSError:
        print("unable to start web server - restarting device in 30 seconds")
        time.sleep(30)
        microcontroller.reset()
else:
    # this is where you will start the client code
    # receive any config items from the server
    # set the clock
    # do stuff
    print("client mode")
    while True:
        time.sleep(5)

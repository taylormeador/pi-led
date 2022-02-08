# !usr/bin/env python
from samplebase import SampleBase
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
import time
import sys
import random
import threading
import queue
import subprocess
import requests

files_dict = {"text_scroller": "runtext.py", "colors": "pulsing_colors.py", "clock": "clock.py"}

"""
Sends a request to the server with your username
Server will look up your username and tell you which channel is currently selected
"""
def get_requested_channel():
    print("attempting to connect to server...")
    user = "bonesaw"
    payload = {"username": user}
    url = "http://pi-led.herokuapp.com/mypiledrequest"
    r = requests.get(url, params=payload)
    print("request received!")

    requested_channel = r.text
    if requested_channel not in files_dict:
        print("error parsing server response")
        print("quitting...")
        sys.exit()
    return requested_channel


"""
Sends a request to the server to determine which channel to run
Nested while loops poll the server to determine if the user has selected a new channel
If a new channel was selected, it terminates the old subprocess and starts a new one
I think web sockets would be more approriate here and I plan to implement that as I learn more about Flask sockets
"""


def main():
    current_channel = get_requested_channel()
    while True:
        file_name = files_dict[current_channel]
        run_channel = subprocess.Popen(['python', file_name])
        print(f"{file_name} started")

        stop_flag = False
        while not stop_flag:
            print(f"running {file_name}")
            time.sleep(5)

            new_channel = get_requested_channel()
            if new_channel != current_channel:
                print("user requested a new channel")
                print(f"changing channels... attempting to terminate {current_channel}")
                run_channel.terminate()
                stop_flag = True
                print(f"success... starting {new_channel}")

        stop_flag = False
        current_channel = new_channel


# Main function
if __name__ == "__main__":
    main()
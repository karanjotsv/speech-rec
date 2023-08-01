import os
import sys
import time
import threading

import socket_src.server as socket_server
from src.record import Recorder


is_running = False


def send_data(data):
    socket_server.send_data(data)

def fetch_data():
    return socket_server.receive_data()


def start_timer():
    global is_running

    t = 0
    while is_running:
        t += 1
        minutes, seconds = divmod(t, 60)
        try:
            send_data("TIMER|{:02d}:{:02d},".format(minutes, seconds))
        except Exception as e:
            print(e)

        time.sleep(1)

def start_timer_thread():
    threading.Thread(target=start_timer, daemon=True).start()


def monitor_recognizer(recognizer, halt):
    while is_running:
        text = recognizer.parser.get_last_utterance()

        if len(text) != 0:
            '''
            for line in transcription:
                send_socket_server(f'SPEECH|{line},')
            '''
            send_data(f'SPEECH|{text},')

        time.sleep(halt)


def start_recognizer(src):
    try:
        with Recorder(src) as recognizer:
            threading.Thread(target=monitor_recognizer, args=(recognizer, 1,),
                                daemon=True).start()
            recognizer.start()
    except KeyboardInterrupt:
        print("speech module stopped")


def run(stream=False):
    '''
    input stream False
    '''
    global is_running
    is_running = True
    
    # start socket server and timer
    socket_server.start_thread()
    start_timer_thread()

    if bool(stream):
        pass
    else:
        start_recognizer(0)
        pass

    socket_server.stop_thread()


is_stream = input("is a stream? (0/1) ")

run(is_stream == 1)

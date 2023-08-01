import sys
import threading
import traceback

import asyncio
import websockets

from queue import Queue

server_thread = None

IP = ""
PORT = 8090
CONNECTIONS = set()
rx_queue = Queue()


async def ws_echo(socket):
    global rx_queue, CONNECTIONS

    CONNECTIONS.add(socket)
    
    try:
        async for rx_data in socket:
            rx_queue.put_nowait(rx_data)
            print(f"received: {rx_data}")
    
    except Exception:
        traceback.print_exc(file=sys.stdout)
    finally:
        CONNECTIONS.remove(socket)


async def ws_main():
    async with websockets.serve(ws_echo, IP, PORT):
        await asyncio.Future()  # run forever


async def main():
    socket_task = asyncio.create_task(ws_main())
    await asyncio.gather(
        socket_task
    )


def start_server():
    asyncio.run(main())


def stop_server():
    pass


# broadcast to all clients
def cast(message):
    websockets.broadcast(CONNECTIONS, message)


async def send_to_sockets(data):
    global CONNECTIONS
    ex_list = set()

    for socket in CONNECTIONS:
        try:
            await socket.send(data)
        
        except Exception:
            traceback.print_exc(file=sys.stdout)
            ex_list.add(socket)
    
    print(f"sent data: {data}")
    CONNECTIONS -= ex_list


def send_data(data):
    asyncio.run(send_to_sockets(data))


def receive_data():
    global rx_queue

    if rx_queue.empty():
        return None

    print(f"rx_size: {rx_queue.qsize()}")
    return rx_queue.get_nowait()


def start_thread():
    '''
    start websocket server
    '''
    global server_thread

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()


def stop_thread():
    '''
    stop websocket server
    '''
    global server_thread
    stop_server()

    server_thread.join(timeout=2)

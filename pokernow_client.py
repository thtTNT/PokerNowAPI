import json

import websocket
import ssl
import time
import threading
import requests

WEB_SOCKET_URL_PATTERN = "wss://www.pokernow.club/socket.io/?gameID=${game_id}&=true&layout=d&EIO=3&transport=websocket"

TAKE_SEAT_URL = "https://www.pokernow.club/games/${game_id}/request_ingress"


class PokernowClient:

    def __init__(self, name="BOT_" + str(time.time())[-8:], initial_stack=2000, seat=9):
        self.game_id = None
        self.ping_interval = 20000
        self.self_player_id = None
        self.ws = None
        self.name = name
        self.initial_stack = initial_stack
        self.seat = seat

        response = requests.get("https://www.pokernow.club/")
        self.cookies = '; '.join([f'{name}={value}' for name, value in response.cookies.items()])

    def ping(self):
        self.ws.send("2")
        threading.Timer(self.ping_interval / 1000, self.ping).start()

    def listen_on_web_socket(self):
        while True:
            result = self.ws.recv()
            self.handle_message(result)

    def handle_message(self, raw_message):
        print(raw_message)
        if raw_message.startswith("0"):
            message = raw_message[1:]
            json_obj = json.loads(message)
            print(json_obj)
            self.self_player_id = json_obj["sid"]
            self.ping_interval = json_obj["pingInterval"]
            self.ping()
            print(f"Self player id: {self.self_player_id}")

    def connect_room(self, game_id):
        self.game_id = game_id
        url = WEB_SOCKET_URL_PATTERN.replace("${game_id}", game_id)
        ws = websocket.create_connection(url, header={"Cookie": self.cookies},
                                         sslopt={"cert_reqs": ssl.CERT_NONE})
        self.ws = ws
        threading.Thread(target=self.listen_on_web_socket).start()
        print("Connected to room successfully!")

    def take_seat(self):
        url = TAKE_SEAT_URL.replace("${game_id}", self.game_id)
        data = {
            "allowSpectator": False,
            "playerName": self.name,
            "stack": self.initial_stack,
            "seat": self.seat
        }
        response = requests.post(url, json=data, headers={"Cookie": self.cookies})
        print(response.text)
        print(f"Requested to take seat {self.seat} successfully!")

    def run(self):
        while True:
            time.sleep(1)
            pass


if __name__ == "__main__":
    client = PokernowClient()
    client.connect_room("pglEWKHK6FHRASEfbV4Pca47A")
    client.take_seat()
    client.run()

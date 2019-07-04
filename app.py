import time
import csv
import math
import json
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket

from solution.sorting_functions import (
    bubblesort,
    insertionsort,
    selectionsort,
    mergesort,
    quicksort,
    shellsort,
    heapsort,
)


ALGO_CHOICES = {
    "bubblesort": bubblesort,
    "insertionsort": insertionsort,
    "selectionsort": selectionsort,
    "mergesort": mergesort,
    "quicksort": quicksort,
    "shellsort": shellsort,
    "heapsort": heapsort,
}

FILE_CHOICES = {"f": "input/fr.csv", "i": "input/isere.csv", "p": "input/small.csv"}

SPEED_CHOICES = {"1": 0.01, "2": 0.1, "3": 0.6}


def get_distance_from_grenoble(city):
    """Retourne la distance entre la ville passée en paramètre et Grenoble

    Args:
        city (dict): Dictionnaire issu du csv. Contient les clés "latitude" et "longitude"

    Returns:
        int: la distance en km
    """
    grenoble_lat = 45.166667
    grenoble_long = 5.716667

    lat1, lon1 = (grenoble_lat, grenoble_long)
    lat2, lon2 = (float(city["latitude"]), float(city["longitude"]))
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)
    ) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


def get_dataset(dataset_type):
    file_path = FILE_CHOICES[dataset_type]
    dataset = []
    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for city in reader:
            try:
                dataset.append(get_distance_from_grenoble(city))
            except ValueError:
                pass
    return dataset


class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("new connection")

    async def on_message(self, message):
        message = json.loads(message)
        algo_function = ALGO_CHOICES[message["algo"]]
        speed = SPEED_CHOICES[message["speed"]]
        dataset_type = message["file"]
        distances = get_dataset(dataset_type)
        try:
            for j in algo_function(distances, 0, len(distances) - 1):
                self.write_message(json.dumps(j))
                time.sleep(speed)
        except (tornado.websocket.WebSocketClosedError, tornado.iostream.StreamClosedError):
            print("Websocket/Stream close error")

    def on_close(self):
        print("connection closed")

    def check_origin(self, origin):
        return True


application = tornado.web.Application([(r"/ws", WSHandler)], debug=True, autoreload=True)


if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print("*** Websocket Server Started at %s***" % myIP)
    tornado.ioloop.IOLoop.instance().start()

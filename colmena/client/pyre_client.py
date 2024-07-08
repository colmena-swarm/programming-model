#!/usr/bin/python
#
#  Copyright 2002-2023 Barcelona Supercomputing Center (www.bsc.es)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

# -*- coding: utf-8 -*-

import codecs
import pickle
import threading
import zmq
from colmena.utils.logger import Logger
from multiprocessing import Queue
from pyre.pyre import Pyre


class KeyValue:
    def __init__(self, key: str, value: object):
        self.key = key
        self.value = value


class PyreClient(threading.Thread):
    def __init__(self):
        super().__init__()
        self._logger = Logger(self).get_logger()
        self._publishers = {}
        self._subscribers = {}
        self.ctx = zmq.Context()
        self.publisher_socket = self.ctx.socket(zmq.PAIR)
        self.publisher_socket.connect("inproc://pyreclient")
        self.pyre = Pyre()

    def run(self):
        self.pyre.start()
        publisher_subscribe_socket = self.ctx.socket(zmq.PAIR)
        publisher_subscribe_socket.bind("inproc://pyreclient")
        poller = zmq.Poller()
        poller.register(publisher_subscribe_socket, zmq.POLLIN)
        poller.register(self.pyre.socket(), zmq.POLLIN)

        while True:
            try:
                sockets = dict(poller.poll())

                if publisher_subscribe_socket in sockets:
                    serialized_message = publisher_subscribe_socket.recv()
                    message = pickle.loads(serialized_message)
                    self.pyre.join(message.key)
                    current_group_peers = self.pyre.peers_by_group(message.key)
                    if len(current_group_peers) > 0:
                        string_rep = codecs.encode(
                            serialized_message, "base64"
                        ).decode()
                        self.pyre.whispers(current_group_peers[0], string_rep)

                if self.pyre.socket() in sockets:
                    parts = self.pyre.recv()
                    msg_type = parts.pop(0).decode("utf-8")
                    peer = parts.pop(0)
                    msg_name = parts.pop(0).decode("utf-8")
                    message = parts.pop(0).decode("utf-8")
                    print(f"message received: {msg_type} {peer} {msg_name} {message}")
                    if msg_type == "WHISPER":
                        deserialized_message = pickle.loads(
                            codecs.decode(message.encode(), "base64")
                        )
                        subscriber = self._subscribers[deserialized_message.key]
                        if subscriber is not None:
                            subscriber.publish(deserialized_message.value)

            except KeyboardInterrupt:
                print("Stopping pyre")
                self.pyre.stop()

    def publish(self, key: str, value: object):
        self.publisher_socket.send(pickle.dumps(KeyValue(key, value)))

    def subscribe(self, key: str):
        print(f"subscribing to {key}")
        subscriber = PyreSubscriber()
        self._subscribers[key] = subscriber
        self.pyre.join(key)
        return subscriber


class PyreSubscriber:
    def __init__(self):
        self.queue = Queue()

    def receive(self):
        elements = list()
        while self.queue.qsize():
            elements.append(self.queue.get())
        return elements

    def publish(self, value):
        self.queue.put(value)

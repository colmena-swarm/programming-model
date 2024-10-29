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

import pickle
import threading
import zmq
from zmq import ZMQError

from colmena.client.pyre import message_converter
from colmena.logger import Logger
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
        self.groups = []
        self._publishers = {}
        self._subscribers = {}
        self.ctx = zmq.Context()
        self.publisher_socket = self.ctx.socket(zmq.PAIR)
        self.publisher_socket.connect("inproc://pyreclient")
        self.pyre = Pyre()
        self.pyre.start()  #TODO: why is this required to be here for test_persistent?
        self.running = True

    def run(self):
        # socket for publishing messages to pyre
        publisher_subscription_socket = self.ctx.socket(zmq.PAIR)
        publisher_subscription_socket.bind("inproc://pyreclient")
        poller = zmq.Poller()
        poller.register(publisher_subscription_socket, zmq.POLLIN)
        poller.register(self.pyre.socket(), zmq.POLLIN)

        while self.running:
            try:
                #sockets with messages to process are returned by the poll
                sockets = dict(poller.poll())

                #messages to publish
                if publisher_subscription_socket in sockets:
                    serialized_message = publisher_subscription_socket.recv()
                    message = pickle.loads(serialized_message)
                    self.join_group_if_required(message.key)
                    current_group_peers = self.pyre.peers_by_group(message.key)
                    if len(current_group_peers) > 0:
                        self.pyre.whispers(current_group_peers[0], message_converter.encode(serialized_message))

                #messages from peers
                if self.pyre.socket() in sockets:
                    parts = self.pyre.recv()
                    msg_type = message_converter.pyre_message_type(parts)
                    if msg_type == "WHISPER":
                        pyre_message = message_converter.parse(parts)
                        self._logger.debug(f"message received: {pyre_message}")
                        payload = pickle.loads(message_converter.decode_payload(pyre_message))
                        subscriber = self._subscribers[payload.key]
                        if subscriber is not None:
                            subscriber.publish(payload.value)
                        #TODO: should probably try to leave the group if we're not interested in the message
            except KeyboardInterrupt:
                self._logger("interrupted")
            except ZMQError:
                self._logger.debug("caught zmq error")
        self._logger.debug("stopped pyre")

    def join_group_if_required(self, group_name):
        if group_name not in self.groups:
            self.pyre.join(group_name)
            self.groups.append(group_name)

    def stop(self):
        self._logger.debug("trying to stop pyre")
        self.running = False
        try:
            self.publisher_socket.close()
        except ZMQError:
            self._logger.debug("could not stop publisher socket gracefully")
        try:
            self.pyre.stop()
        except ZMQError:
            self._logger.debug("could not stop pyre gracefully")

    def publish(self, key: str, value: object):
        self.publisher_socket.send(pickle.dumps(KeyValue(key, value)))

    def subscribe(self, key: str):
        print(f"subscribing to {key}")
        subscriber = PyreSubscriber()
        self._subscribers[key] = subscriber
        self.join_group_if_required(key)
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

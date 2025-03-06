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

import os
from dataclasses import dataclass
from datetime import datetime
# -*- coding: utf-8 -*-

import pickle
import threading
import zmq
from zmq import ZMQError

from colmena.implementations.pyre import message_converter, receiver_selector
from colmena.logger import Logger
from multiprocessing import Queue
from pyre.pyre import Pyre


class ColmenaMessage:
    def __init__(self, key: str, value: object):
        self.send_time = datetime.now()
        self.key = key
        self.value = value

    def set_sender(self, sender):
        self.sender = sender

@dataclass
class Ack:
    send_time: datetime
    sender: str
    key: str

class PyreClient(threading.Thread):
    def __init__(self):
        super().__init__()
        self._logger = Logger(self).get_logger()
        self.groups = []
        self.message_receivers = {}
        self._publishers = {}
        self._subscribers = {}
        self.ctx = zmq.Context()
        self.publisher_socket = self.ctx.socket(zmq.PAIR)
        self.publisher_socket.connect("inproc://pyreclient")
        self.ack_socket = self.ctx.socket(zmq.PAIR)
        self.ack_socket.connect("inproc://ack")
        self.pyre = Pyre()
        self.set_peer_discovery_interface(self.pyre)
        self.pyre.start()
        self.running = True

    def set_peer_discovery_interface(self, pyre):
        try:
            self._logger.info(f"discovering peers on {os.environ['PEER_DISCOVERY_INTERFACE']}")
            pyre.set_interface(os.environ["PEER_DISCOVERY_INTERFACE"])
        except KeyError:
            self._logger.info("no interface set for peer discovery, using default...")
            return


    def run(self):
        self._logger.debug(f"pyre started. id: {self.pyre.uuid()}")
        # socket for publishing messages to pyre
        publisher_subscription_socket = self.ctx.socket(zmq.PAIR)
        publisher_subscription_socket.bind("inproc://pyreclient")
        ack_subscription_socket = self.ctx.socket(zmq.PAIR)
        ack_subscription_socket.bind("inproc://ack")
        poller = zmq.Poller()
        poller.register(publisher_subscription_socket, zmq.POLLIN)
        poller.register(self.pyre.socket(), zmq.POLLIN)
        poller.register(ack_subscription_socket, zmq.POLLIN)

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
                        receiver = self.message_receivers[message.key].select_recipient(current_group_peers)
                        self.pyre.whispers(receiver, message_converter.encode(serialized_message))

                #acks to process
                if ack_subscription_socket in sockets:
                    serialized_message = ack_subscription_socket.recv()
                    message = pickle.loads(serialized_message)
                    self.pyre.whispers(message.sender, message_converter.encode(serialized_message))

                #messages from peers
                if self.pyre.socket() in sockets:
                    parts = self.pyre.recv()
                    msg_type = message_converter.pyre_message_type(parts)
                    if msg_type == "WHISPER":
                        pyre_message = message_converter.parse(parts)
                        colmena_message = pickle.loads(message_converter.decode_payload(pyre_message))
                        topic = colmena_message.key
                        if isinstance(colmena_message, Ack):
                            sender = str(pyre_message.peer)
                            latency_estimate = datetime.now() - colmena_message.send_time
                            self.message_receivers[topic].update_estimate(sender, latency_estimate)
                        else:
                            colmena_message.set_sender(pyre_message.peer)
                            try:
                                subscriber = self._subscribers[topic]
                                subscriber.publish(colmena_message)
                            except KeyError:
                                pass # received a message which we are not subscribed

            except KeyboardInterrupt:
                self._logger.debug("interrupted")
            except ZMQError:
                self._logger.debug("caught zmq error")
        self._logger.debug("stopped pyre")

    def join_group_if_required(self, group_name):
        if group_name not in self.groups:
            self.groups.append(group_name)
            self.message_receivers[group_name] = receiver_selector.LeastLatencySelector()

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
        self.publisher_socket.send(pickle.dumps(ColmenaMessage(key, value)))

    def ack(self, message: ColmenaMessage):
        self.ack_socket.send(pickle.dumps(Ack(message.send_time, message.sender, message.key)))

    def subscribe(self, key: str):
        print(f"subscribing to {key}")
        subscriber = PyreSubscriber(self.ack)
        self._subscribers[key] = subscriber
        self.pyre.join(key)
        return subscriber


class PyreSubscriber:
    def __init__(self, ack):
        self.queue = Queue()
        self.ack = ack

    def receive(self) -> list[ColmenaMessage]:
        elements = list()
        while self.queue.qsize():
            elements.append(self.queue.get())
        return elements

    def publish(self, msg: ColmenaMessage):
        self.queue.put(msg)

    def ack(self, msg: ColmenaMessage):
        self.ack(msg)

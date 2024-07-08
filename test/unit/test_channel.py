#!/usr/bin/python
#
#  Copyright 2002-2024 Barcelona Supercomputing Center (www.bsc.es)
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

from unittest.mock import Mock

from colmena import Role, Service
from colmena.channel import Channel
from colmena.exceptions import ChannelNotExistException


class ServiceWithChannelDec(Service):
    @Channel(name='example_channel', scope='*')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class RoleWithChannelDec(Role):
        @Channel(name='example_channel')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


class ServiceWithoutChannelDec(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class RoleWithChannelDec(Role):
        @Channel(name='example_channel')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


class TestChannel:

    def test_decorator_config_service(self):
        channel = ServiceWithChannelDec.__init__.config['channels']
        assert channel == {'example_channel': '*'}

    def test_decorator_data_in_role(self):
        role = ServiceWithChannelDec.RoleWithChannelDec(ServiceWithChannelDec)
        assert role.channels[0] == 'example_channel'

        channel_interface = role.example_channel

        assert channel_interface._name == 'example_channel'
        assert channel_interface._scope == '*'

    def test_error_decorator_not_initialized(self):
        try:
            ServiceWithoutChannelDec.RoleWithChannelDec(ServiceWithoutChannelDec)
        except ChannelNotExistException:
            assert True
            return
        assert False

    def test_interface(self):
        assert ServiceWithChannelDec().config['RoleWithChannelDec']['channels'] == ['example_channel']

        role = ServiceWithChannelDec.RoleWithChannelDec(ServiceWithChannelDec)

        pyre_client = Mock()
        context_awareness = Mock()

        role.comms._Communications__context_awareness = context_awareness
        role.comms._Communications__pyre_client = pyre_client
        role.comms._Communications__initialize(role)

        channel_interface = role.example_channel
        channel_interface.publish(0)
        kwargs = context_awareness.publish.call_args.kwargs
        assert kwargs['key'] == 'example_channel'
        assert kwargs['value'] == 0

        channel_interface.receive()
        kwargs = pyre_client.subscribe.call_args.kwargs
        assert kwargs['key'] == 'example_channel'


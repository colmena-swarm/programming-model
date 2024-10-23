import time

from colmena import Service, Channel, Persistent, Role, Async
from busypie import wait, SECOND, MINUTE


class ServiceWithRoleBehaviors(Service):
    @Channel(name='example_channel', scope='*')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class PersistentRole(Role):
        @Channel(name='example_channel')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.iterations = 0

        @Persistent()
        def behavior(self):
            self.example_channel.publish(self.iterations)
            self.iterations += 1
            time.sleep(0.1)

    class AsyncRole(Role):
        @Channel(name='example_channel')
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.iterations = 0

        @Async(message='example_channel')
        def behavior(self, message):
            print(f"message: {message}")
            self.iterations = message


class TestBehavior:

    def test_persistent(self):
        persistent_role = ServiceWithRoleBehaviors.PersistentRole(ServiceWithRoleBehaviors)
        persistent_role.execute()
        wait().at_most(2, SECOND).until(lambda: persistent_role.iterations > 5)
        persistent_role.stop()

    def test_persistent_and_async(self):
        persistent_role = ServiceWithRoleBehaviors.PersistentRole(ServiceWithRoleBehaviors)
        async_role = ServiceWithRoleBehaviors.AsyncRole(ServiceWithRoleBehaviors)
        persistent_role.execute()
        async_role.execute()
        wait().at_most(2, SECOND).until_async(lambda: async_role.iterations > 0)
        persistent_role.stop()
        async_role.stop()

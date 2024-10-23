from colmena import Context, Service, Role


class ContextWithStructure(Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.structure = {"data_structure_key": "data_structure_value"}

    def locate(self, device):
        return True

class ServiceWithContext(Service):
    @Context(class_ref=ContextWithStructure, name="example_context")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class RoleWithContext(Role):
        @Context(name="example_context", scope="example_scope")
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

class TestContext:

    def test_context_config_in_service(self):
        service = ServiceWithContext()
        assert service.context['example_context'].structure == {'data_structure_key': 'data_structure_value'}
        assert service.context['example_context'].locate(None)

    def test_context_in_role(self):
        role = ServiceWithContext.RoleWithContext(ServiceWithContext)
        assert role._context == {'example_context': 'example_scope'}
class Context:
    def __init__(self):
        self._resources = {}
        self.variables = {}

    def store(self, name, resource):
        self._resources[name] = resource

    def get(self, name):
        if name not in self._resources:
            raise RuntimeError(f"Resource '{name}' not loaded")
        return self._resources[name]
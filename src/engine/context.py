class Context:
    def __init__(self):
        self._resources = {}
        self.variables = {}
        self.pipelines = {}

    def store(self, name, resource):
        self._resources[name] = resource

    def get(self, name):
        if name not in self._resources:
            raise RuntimeError(f"Resource '{name}' not loaded")
        return self._resources[name]
    
    def store_pipeline(self, name, pipeline):
        self.pipelines[name] = pipeline


    def get_pipeline(self, name):
        if name not in self.pipelines:
            raise RuntimeError(
                f"Pipeline '{name}' not found"
            )

        return self.pipelines[name]
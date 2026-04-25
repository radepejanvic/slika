from engine.context import Context

class Engine:
    def __init__(self, backend):
        self.backend = backend
        self.context = Context()

    def interpret(self, program):
        for stmt in program.statements:
            self.execute_stmt(stmt)

    def execute_stmt(self, stmt):
        class_name = stmt.__class__.__name__
        match class_name:
            case "Load":
                self.execute_load(stmt)
            case "Apply":
                self.execute_apply(stmt)
            case "Save":
                self.execute_save(stmt)

    def execute_load(self, stmt): 
        image = self.backend.load(stmt.path)
        if image is None:
          raise RuntimeError(f"Couldn't load resource: '{stmt.path}' ")
        self.context.store(stmt.name, image)

    def execute_save(self, stmt): 
        image = self.context.get(stmt.image.name)
        self.backend.save(image, stmt.path)

    def execute_apply(self, stmt):
        image = self.context.get(stmt.image.name)
        for step in stmt.pipeline.steps:
            image = self.execute_step(step, image)
        self.context.store(stmt.image.name, image)

    def execute_step(self, step, image):
        class_name = step.__class__.__name__
        match class_name:
            case "SimpleStep":
                return self.execute_simple_step(image, step)
            case "Resize":
                return self.backend.resize(image, step.width, step.height)
            case "ConvertColor":
                return self.backend.cvt_color(image, step.code)
            case "Threshold": 
                return self.backend.threshold(image, step.value, step.max_value, step.type)
            case _:
                raise RuntimeError(f"Unknown step: {class_name}")
            
    def execute_simple_step(self, image, step): 
        match (step.op):
            case "grayscale": 
                return self.backend.grayscale(image)
            case _:
                raise RuntimeError(f"Unknown simple step: {step.op}")

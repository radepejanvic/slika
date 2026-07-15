class StepError(RuntimeError):

    def __init__(self, step_name, original_exception, traceback_str):
        super().__init__(str(original_exception))
        self.step_name = step_name
        self.original_exception = original_exception
        self.traceback_str = traceback_str


class BatchError:

    def __init__(self, filename, step_name, original_exception, traceback_str):
        self.filename = filename
        self.step_name = step_name
        self.original_exception = original_exception
        self.traceback_str = traceback_str
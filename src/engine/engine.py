import os
import traceback
from src.engine.context import Context
from src.engine.media import *
from src.engine.expr import evaluate_expr
from src.engine.errors import *
from src.engine.report import *

STEP_DISPLAY_NAMES = {
    "Resize": "resize",
    "Crop": "crop",
    "ConvertColor": "cvt_color",
    "Threshold": "threshold",
    "Erode": "erode",
    "Dilate": "dilate",
    "Opening": "opening",
    "Closing": "closing",
    "Canny": "canny",
}

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
            case "Capture":
                self.execute_capture(stmt)
            case "Let":
                self.execute_let(stmt)
            case "Apply":
                self.execute_apply(stmt)
            case "Show":
                self.execute_show(stmt)
            case "Save":
                self.execute_save(stmt)

    def execute_load(self, stmt):
        media = self.load_media(stmt.path)
        self.context.store(stmt.name, media)

    def load_media(self, path):
        if os.path.isdir(path):
            collection = self.load_folder(path)
            if not collection.items:
                raise RuntimeError(f"No supported media files in folder: '{path}'")
            return collection
        return self.load_file(path)
    
    def load_folder(self, path):
        items = []
        for entry in sorted(os.listdir(path)):
            full = os.path.join(path, entry)
            if os.path.isdir(full):
                sub = self.load_folder(full)
                if sub.items:
                    items.append((entry, sub))
                continue
            ext = os.path.splitext(entry)[1].lower()
            if ext in IMAGE_EXTENSIONS or ext in VIDEO_EXTENSIONS:
                items.append((entry, self.load_file(full)))
        return MediaCollection(items)

    def load_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext in IMAGE_EXTENSIONS:
            image = self.backend.load(path)
            if image is None:
                raise RuntimeError(f"Couldn't load image: '{path}'")
            return ImageMedia(image)
        if ext in VIDEO_EXTENSIONS:
            frames, fps = self.backend.load_video(path)
            return VideoMedia(frames, fps)
        raise RuntimeError(f"Unsupported file type: '{path}'")

    def execute_save(self, stmt): 
        media = self.context.get(stmt.image.name)
        media.save(self.backend, stmt.path)
        errors = getattr(media, "batch_errors", None)
        if errors:
            report_path = stmt.report_path if stmt.report_path else os.path.join(stmt.path, "report.txt")
            report_path = write_report(errors, report_path)
            print(f"{len(errors)} item(s) failed during processing (skipped). Report written to: {report_path}")

    def execute_let(self, stmt):
        self.context.variables[stmt.name] = evaluate_expr(stmt.value, self.context.variables)

    def eval(self, expr):
        value = evaluate_expr(expr, self.context.variables)
        return None if value is None else int(value)

    def execute_apply(self, stmt):
        media = self.context.get(stmt.image.name)
        if isinstance(media, MediaCollection):
            media.batch_errors = self.apply_to_collection(media, stmt.pipeline)
            if media.batch_errors:
                print(f"Warning: {len(media.batch_errors)} item(s) failed during pipeline processing; "
                      f"they will be skipped on save. A report will be written next to the output.")
        else:
            media.map(lambda frame: self.apply_pipeline(stmt.pipeline, frame))

    def apply_to_collection(self, collection, pipeline, prefix=""):
        errors = []
        for filename, media in collection.items:
            rel_path = filename if not prefix else f"{prefix}/{filename}"
            if isinstance(media, MediaCollection):
                errors.extend(self.apply_to_collection(media, pipeline, rel_path))
                continue
            try:
                media.map(lambda frame: self.apply_pipeline(pipeline, frame))
            except StepError as e:
                media.failed = True
                errors.append(BatchError(rel_path, e.step_name, e.original_exception, e.traceback_str))
        return errors

    def execute_step(self, step, image):
        class_name = step.__class__.__name__
        match class_name:
            case "SimpleStep":
                return self.execute_simple_step(image, step)
            case "Resize":
                return self.backend.resize(image, self.eval(step.width), self.eval(step.height))
            case "Crop":
                return self.backend.crop(image, self.eval(step.x), self.eval(step.y), self.eval(step.width), self.eval(step.height))
            case "ConvertColor":
                return self.backend.cvt_color(image, step.code)
            case "Threshold":
                return self.backend.threshold(image, self.eval(step.value), self.eval(step.max_value), step.type or 'binary')
            case "Erode":
                return self.backend.erode(image, self.eval(step.kernel_size), self.eval(step.iterations))
            case "Dilate":
                return self.backend.dilate(image, self.eval(step.kernel_size), self.eval(step.iterations))
            case "Opening":
                return self.backend.opening(image, self.eval(step.kernel_size), self.eval(step.iterations))
            case "Closing":
                return self.backend.closing(image, self.eval(step.kernel_size), self.eval(step.iterations))
            case "Canny":
                return self.backend.canny(image, self.eval(step.threshold1), self.eval(step.threshold2))
            case _:
                raise RuntimeError(f"Unknown step: {class_name}")
            
    def execute_simple_step(self, image, step): 
        match (step.op):
            case "grayscale": 
                return self.backend.grayscale(image)
            case _:
                raise RuntimeError(f"Unknown simple step: {step.op}")
            
    def execute_capture(self, stmt):
        cap = self.backend.open_capture(stmt.device)
        self.context.store(stmt.name, StreamMedia(cap))

    def execute_show(self, stmt):
        media = self.context.get(stmt.image.name)
        if isinstance(media, StreamMedia):
            media.run(self.backend)
        else:
            self.backend.display(media.frame, "slika")
            self.backend.wait_key(0)
            self.backend.release(None)
            
    def apply_pipeline(self, pipeline, frame):
        for step in pipeline.steps:
            try:
                frame = self.execute_step(step, frame)
            except Exception as e:
                raise StepError(self.step_display_name(step), e, traceback.format_exc()) from e
        return frame

    def step_display_name(self, step):
        class_name = step.__class__.__name__
        if class_name == "SimpleStep":
            return step.op
        return STEP_DISPLAY_NAMES.get(class_name, class_name)

import os
from engine.context import Context
from engine.media import (
    ImageMedia, VideoMedia, MediaCollection,
    IMAGE_EXTENSIONS, VIDEO_EXTENSIONS,
)

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
        media = self.load_media(stmt.path)
        self.context.store(stmt.name, media)

    def load_media(self, path):
        if os.path.isdir(path):
            return self.load_folder(path)
        return self.load_file(path)

    def load_folder(self, path):
        items = []
        for entry in sorted(os.listdir(path)):
            full = os.path.join(path, entry)
            if not os.path.isfile(full):
                continue
            ext = os.path.splitext(entry)[1].lower()
            if ext in IMAGE_EXTENSIONS or ext in VIDEO_EXTENSIONS:
                items.append((entry, self.load_file(full)))
        if not items:
            raise RuntimeError(f"No supported media files in folder: '{path}'")
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

    def execute_apply(self, stmt):
        media = self.context.get(stmt.image.name)
        media.map(lambda frame: self.apply_pipeline(stmt.pipeline, frame))

    def execute_step(self, step, image):
        class_name = step.__class__.__name__
        match class_name:
            case "SimpleStep":
                return self.execute_simple_step(image, step)
            case "Resize":
                return self.backend.resize(image, step.width, step.height)
            case "Crop":
                return self.backend.crop(image, step.x, step.y, step.width, step.height)
            case "ConvertColor":
                return self.backend.cvt_color(image, step.code)
            case "Threshold":
                return self.backend.threshold(image, step.value, step.max_value, step.type)
            case "Erode":
                return self.backend.erode(image, step.kernel_size, step.iterations)
            case "Dilate":
                return self.backend.dilate(image, step.kernel_size, step.iterations)
            case "Opening":
                return self.backend.opening(image, step.kernel_size, step.iterations)
            case "Closing":
                return self.backend.closing(image, step.kernel_size, step.iterations)
            case "Canny":
                return self.backend.canny(image, step.threshold1, step.threshold2)
            case _:
                raise RuntimeError(f"Unknown step: {class_name}")
            
    def execute_simple_step(self, image, step): 
        match (step.op):
            case "grayscale": 
                return self.backend.grayscale(image)
            case _:
                raise RuntimeError(f"Unknown simple step: {step.op}")
            
    def apply_pipeline(self, pipeline, frame):
        for step in pipeline.steps:
            frame = self.execute_step(step, frame)
        return frame

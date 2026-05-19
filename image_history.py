import time
import torch
import folder_paths
import os
from PIL import Image
import numpy as np

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False
any = AnyType("*")

class ImageHistoryBuffer:
    def __init__(self):
        self.history = []
        self.name_history = []
        self.path_history = []
        self.last_preset = None
        self.last_reset = 0
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {
                    "tooltip": "Input image batch to store in history."
                }),
                "preset": (["2 Images", "4 Images", "6 Images", "8 Images", "10 Images"], {
                    "default": "2 Images",
                    "tooltip": "Maximum number of images to keep in history. Older images are automatically removed."
                }),
            },
            "optional": {
                "image_name_opt": (any, {
                    "default": "", 
                    "forceInput": True, 
                    "display_name": "image_name (opt)",
                    "tooltip": "Optional: Custom name for the image.\nShown in history list and under the grid.\nExample: 'my_cat'"
                }),
                "image_path_opt": (any, {
                    "default": "", 
                    "forceInput": True, 
                    "display_name": "image_path (opt)",
                    "tooltip": "Optional: File path for the image.\nIf full path (ending with .png/.jpg) is provided, it will be used directly.\nOtherwise, the name will be added to the path."
                }),
                "reset_trigger": ("RESET_TRIGGER", {
                    "tooltip": "Button: Click to clear ALL history (images, names, and paths)."
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("passthrough", "history_names", "history_paths")
    FUNCTION = "process"
    CATEGORY = "Useful-Meti"

    @classmethod
    def IS_CHANGED(cls, image, preset, image_name_opt=None, image_path_opt=None, reset_trigger=None):
        return float("NaN")

    def get_max_history_from_preset(self, preset):
        presets = {
            "2 Images": 2,
            "4 Images": 4,
            "6 Images": 6,
            "8 Images": 8,
            "10 Images": 10,
        }
        return presets.get(preset, 2)

    def extract_name_from_path(self, path):
        if not path:
            return ""
        path_str = str(path)
        if "/" in path_str:
            path_str = path_str.split("/")[-1]
        if "\\" in path_str:
            path_str = path_str.split("\\")[-1]
        if "." in path_str:
            path_str = path_str.split(".")[0]
        return path_str

    def clean_path(self, path):
        if not path:
            return ""
        path_str = str(path).strip()
        if path_str.startswith('"') and path_str.endswith('"'):
            path_str = path_str[1:-1]
        if path_str.startswith("'") and path_str.endswith("'"):
            path_str = path_str[1:-1]
        return path_str

    def clean_name(self, name):
        if not name:
            return ""
        name_str = str(name).strip()
        if name_str.startswith('"') and name_str.endswith('"'):
            name_str = name_str[1:-1]
        if name_str.startswith("'") and path_str.endswith("'"):
            name_str = name_str[1:-1]
        return name_str

    def tensor_to_image_file(self, tensor, index):
        img = tensor.cpu().numpy()
        img = (img * 255).astype(np.uint8)
        if img.shape[0] == 1:
            img = img[0]
        pil_img = Image.fromarray(img)
        
        temp_dir = folder_paths.get_temp_directory()
        file = f"history_img_{index}_{hash(img.tobytes())}.png"
        path = os.path.join(temp_dir, file)
        pil_img.save(path)
        
        return file

    def process(self, image, preset, image_name_opt=None, image_path_opt=None, reset_trigger=None):
        max_history = self.get_max_history_from_preset(preset)
        
        if reset_trigger == 1 and self.last_reset == 0:
            self.history = []
            self.name_history = []
            self.path_history = []
            self.last_preset = preset
            self.last_reset = reset_trigger
            return (image, "✅ Reset triggered!", "✅ Reset triggered!")
        self.last_reset = reset_trigger
        
        if self.last_preset != preset:
            self.history = []
            self.name_history = []
            self.path_history = []
            self.last_preset = preset
        
        raw_name = self.clean_name(image_name_opt) if image_name_opt else ""
        raw_path = self.clean_path(image_path_opt) if image_path_opt else ""
        
        # تعیین نام نمایشی
        if raw_name:
            display_name = raw_name
        elif raw_path:
            display_name = self.extract_name_from_path(raw_path)
        else:
            display_name = f"Image_{len(self.history) + 1}"
        
        # تشخیص نوع مسیر (کامل یا فقط پوشه)
        is_full_path = False
        if raw_path:
            if raw_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                is_full_path = True
        
        # تعیین مسیر کامل
        if raw_path and is_full_path:
            full_path = raw_path
        elif raw_path and display_name:
            full_path = f"{raw_path}\\{display_name}"
        elif raw_path:
            full_path = raw_path
        else:
            full_path = f"Unknown path_{len(self.history) + 1}"
        
        self.history.append(image.clone())
        self.name_history.append(display_name)
        self.path_history.append(full_path)
        
        while len(self.history) > max_history:
            self.history.pop(0)
            self.name_history.pop(0)
            self.path_history.pop(0)
        
        history_images_info = []
        for i, img in enumerate(self.history):
            file_name = self.tensor_to_image_file(img[0], i+1)
            history_images_info.append({
                "index": i + 1,
                "image_file": file_name,
                "image_name": self.name_history[i]
            })
        
        history_lines_names = []
        for i, name in enumerate(self.name_history, 1):
            history_lines_names.append(f"[{i}] {name}")
        history_info_names = "\n".join(history_lines_names)
        
        history_lines_paths = []
        for i, path in enumerate(self.path_history, 1):
            history_lines_paths.append(f"[{i}] {path}")
        history_info_paths = "\n".join(history_lines_paths)
        
        return {
            "result": (image, history_info_names, history_info_paths),
            "ui": {"images_info": history_images_info}
        }


NODE_CLASS_MAPPINGS = {
    "ImageHistoryBuffer": ImageHistoryBuffer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageHistoryBuffer": "📸 Past Images [meti]",
}
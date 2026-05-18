import torch
import folder_paths
from PIL import Image
import numpy as np
import os
import time
import shutil

class SaveImageAdvanced:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                "custom_path": ("STRING", {"default": "", "placeholder": "Leave empty for default ComfyUI output"}),
                "mode": (["Save", "Preview"], {"default": "Save"}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "filename", "full_path")
    FUNCTION = "save"
    OUTPUT_NODE = True
    CATEGORY = "Useful-Meti"

    def save(self, images, filename_prefix, custom_path, mode):
        save = (mode == "Save")
        
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        full_filename = f"{filename_prefix}_{timestamp}.png"
        
        # ذخیره در temp (همیشه)
        temp_dir = folder_paths.get_temp_directory()
        temp_path = os.path.join(temp_dir, full_filename)
        
        img = images[0].cpu().numpy()
        img = (img * 255).astype(np.uint8)
        pil_img = Image.fromarray(img)
        pil_img.save(temp_path)
        
        if save:
            # کپی به مقصد نهایی
            if custom_path and custom_path.strip():
                save_dir = custom_path.strip()
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir, exist_ok=True)
            else:
                save_dir = self.output_dir
            
            full_path = os.path.join(save_dir, full_filename)
            shutil.copy2(temp_path, full_path)
            
            filename_result = full_filename
            path_result = full_path
            
            # برای مسیر سفارشی، preview را از temp نمایش بده
            if custom_path and custom_path.strip():
                preview_source = temp_path
                preview_type = "temp"
            else:
                preview_source = full_path
                preview_type = "output"
        else:
            filename_result = full_filename
            path_result = temp_path
            preview_source = temp_path
            preview_type = "temp"
        
        # نمایش preview در پنجره Image Viewer
        preview_results = [{
            "filename": os.path.basename(preview_source),
            "subfolder": "",
            "type": preview_type
        }]
        
        return {
            "result": (images, filename_result, path_result),
            "ui": {"images": preview_results}
        }


NODE_CLASS_MAPPINGS = {
    "SaveImageAdvanced": SaveImageAdvanced,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageAdvanced": "💾 Save Image Advanced [meti]",
}
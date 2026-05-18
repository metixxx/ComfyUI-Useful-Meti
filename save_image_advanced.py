import torch
import folder_paths
from PIL import Image
import numpy as np
import os
import time
import shutil
import re
import json
from PIL import PngImagePlugin

class SaveImageAdvanced:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.counter_cache = {}
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {
                    "tooltip": "Input image(s) to save. Accepts any image batch."
                }),
                "filename_prefix": ("STRING", {
                    "default": "ComfyUI", 
                    "tooltip": "Available variables:\n• %date% - Full date (2026-05-19)\n• %time% - Full time (14-30-45)\n• %datetime% - Date+Time (20260519_143045)\n• %year%, %month%, %day% - Date parts\n\nExample: 'image_%date%_%time%' → 'image_2026-05-19_14-30-45.png'\nLeave empty to use default 'ComfyUI'"
                }),
                "custom_path": ("STRING", {
                    "default": "", 
                    "placeholder": "Leave empty for default ComfyUI output",
                    "tooltip": "Custom save directory. Leave empty to use ComfyUI/output/\nExample: C:/my_images/"
                }),
                "mode": (["Save", "Preview"], {
                    "default": "Save",
                    "tooltip": "Save: Writes to disk and shows preview.\nPreview: Shows preview only (nothing saved to disk)."
                }),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "filename", "full_path")
    FUNCTION = "save"
    OUTPUT_NODE = True
    CATEGORY = "Useful-Meti"

    def parse_dynamic_filename(self, filename_prefix):
        """تبدیل متغیرهای پویا در نام فایل"""
        now = time.localtime()
        
        variables = {
            '%date%': f"{now.tm_year:04d}-{now.tm_mon:02d}-{now.tm_mday:02d}",
            '%time%': f"{now.tm_hour:02d}-{now.tm_min:02d}-{now.tm_sec:02d}",
            '%datetime%': f"{now.tm_year:04d}{now.tm_mon:02d}{now.tm_mday:02d}_{now.tm_hour:02d}{now.tm_min:02d}{now.tm_sec:02d}",
            '%year%': f"{now.tm_year:04d}",
            '%month%': f"{now.tm_mon:02d}",
            '%day%': f"{now.tm_mday:02d}",
        }
        
        result = filename_prefix
        for key, value in variables.items():
            if key in result:
                result = result.replace(key, value)
        
        # حذف کاراکترهای غیرمجاز
        result = re.sub(r'[<>:"/\\|?*]', '_', result)
        
        return result

    def get_next_filename(self, base_name, save_dir, ext):
        """شماره‌گذاری خودکار فایل"""
        cache_key = f"{save_dir}_{base_name}"
        
        if cache_key not in self.counter_cache:
            counter = 1
            pattern = re.compile(rf'^{re.escape(base_name)}_?(\d*)\.{re.escape(ext)}$')
            
            if os.path.exists(save_dir):
                for filename in os.listdir(save_dir):
                    match = pattern.match(filename)
                    if match:
                        num_str = match.group(1)
                        if num_str:
                            try:
                                num = int(num_str)
                                if num >= counter:
                                    counter = num + 1
                            except:
                                pass
                        else:
                            counter = 2
            self.counter_cache[cache_key] = counter
        else:
            counter = self.counter_cache[cache_key]
            self.counter_cache[cache_key] = counter + 1
        
        if counter == 1:
            filename = f"{base_name}.{ext}"
        else:
            filename = f"{base_name}_{counter:03d}.{ext}"
        
        full_path = os.path.join(save_dir, filename)
        return filename, full_path

    def save(self, images, filename_prefix, custom_path, mode, prompt=None, extra_pnginfo=None):
        # اگر filename_prefix خالی بود، مقدار پیش‌فرض بگذار
        if not filename_prefix or not filename_prefix.strip():
            filename_prefix = "ComfyUI"
        
        save = (mode == "Save")
        
        parsed_prefix = self.parse_dynamic_filename(filename_prefix)
        
        temp_dir = folder_paths.get_temp_directory()
        temp_filename = f"{parsed_prefix}_temp.png"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        img = images[0].cpu().numpy()
        img = (img * 255).astype(np.uint8)
        pil_img = Image.fromarray(img)
        
        # ایجاد metadata
        metadata = PngImagePlugin.PngInfo()
        if prompt is not None:
            metadata.add_text("prompt", json.dumps(prompt))
        if extra_pnginfo is not None:
            for key, value in extra_pnginfo.items():
                metadata.add_text(key, json.dumps(value))
        
        # ذخیره در temp با metadata
        pil_img.save(temp_path, pnginfo=metadata)
        
        if save:
            if custom_path and custom_path.strip():
                save_dir = custom_path.strip()
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir, exist_ok=True)
            else:
                save_dir = self.output_dir
            
            full_filename, full_path = self.get_next_filename(parsed_prefix, save_dir, "png")
            # کپی با حفظ metadata (shutil.copy2 حفظ می‌کند)
            shutil.copy2(temp_path, full_path)
            
            filename_result = full_filename
            path_result = full_path
            
            if custom_path and custom_path.strip():
                preview_source = temp_path
                preview_type = "temp"
            else:
                preview_source = full_path
                preview_type = "output"
        else:
            filename_result = temp_filename
            path_result = temp_path
            preview_source = temp_path
            preview_type = "temp"
        
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
import time
import execution


class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")


def human_readable_duration(seconds):
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes, sec = divmod(int(seconds), 60)
    if minutes < 60:
        return f"{minutes}m {sec}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m {sec}s"


class GlobalTimer:
    workflow_start_time = None

    @classmethod
    def start_workflow_timer(cls):
        if cls.workflow_start_time is None:
            cls.workflow_start_time = time.perf_counter()

    @classmethod
    def get_workflow_elapsed_time(cls):
        if cls.workflow_start_time is not None:
            return time.perf_counter() - cls.workflow_start_time
        else:
            return 0

    @classmethod
    def reset_workflow_timer(cls):
        cls.workflow_start_time = None


class MetiGenerationTime:
    timer = GlobalTimer()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_any": (any, {'forceInput': True}),
                "input_string": ("STRING", {"default": "Generation Time", "multiline": False}),
            }
        }
    
    RETURN_TYPES = (any, "STRING", "STRING")
    RETURN_NAMES = ("passthrough", "time_with_label", "time_only")
    FUNCTION = "get_time"
    CATEGORY = "Generation Time - Meti"

    def get_time(self, input_any, input_string):
        elapsed = self.timer.get_workflow_elapsed_time()
        readable = human_readable_duration(elapsed)
        
        time_with_label = f"{input_string}: {readable}"
        time_only = f"(Runtime: {readable})"
        
        return (input_any, time_with_label, time_only)


original_execute = execution.PromptExecutor.execute

def new_execute(self, prompt, prompt_id, extra_data={}, execute_outputs=[]):
    GlobalTimer.start_workflow_timer()
    result = original_execute(self, prompt, prompt_id, extra_data, execute_outputs)
    GlobalTimer.reset_workflow_timer()
    return result

execution.PromptExecutor.execute = new_execute


NODE_CLASS_MAPPINGS = {
    "MetiGenerationTime": MetiGenerationTime,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MetiGenerationTime": "⏱️ Generation Time",
}
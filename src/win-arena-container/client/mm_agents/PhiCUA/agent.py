import json
import logging
import re
from typing import Dict, List
import requests
import copy
from io import BytesIO
import io
from PIL import Image

logger = logging.getLogger("desktopenv.agent")

def remove_min_leading_spaces(text):  
    lines = text.split('\n')  
    min_spaces = min(len(line) - len(line.lstrip(' ')) for line in lines if line)  
    return '\n'.join([line[min_spaces:] for line in lines])  

class PhiCUA:
    def __init__(self, 
        agent_url: str = None,  # true agent implementation on remote server
    ):
        self.is_initialized = False  # the first calling of predict will initialize the agent
        self.task_instruction = None
        self.action_space = "pyautogui"
        self.url = agent_url
        self.response_id = None
        self.step_counter = 0

    def predict(self, instruction: str, obs: Dict) -> List:
        """
        obs = {
                "screenshot": screenshot,
                "accessibility_tree": accessibility_tree,
                "terminal": terminal,
                "instruction": self.instruction,
                "window_title": window_title,
                "window_rect": window_rect,
                "window_image": window_image,
                "window_names_str": window_names_str,
                "computer_clipboard": computer_clipboard,
                "human_input": human_input
                }
        """
        logs={}

        # processing observation
        image_file = BytesIO(obs['screenshot'])
        view_image = Image.open(image_file).convert("RGB")
        window_title, window_names_str, window_rect, computer_clipboard = obs['window_title'], obs['window_names_str'], obs['window_rect'], obs['computer_clipboard']
        

        # caling api
        buf = BytesIO()  
        view_image.save(buf, format="JPEG", quality=90)
        buf.seek(0)

        files = {  
            # key 名称要和 FastAPI 接口的 parameter 一致  
            "screenshot": ("processed.jpg", buf, "image/jpeg")  
        }
        data = {
            "instruction": instruction,
            "response_id": self.response_id,
            "accessibility_tree": obs['accessibility_tree'],
            "clipboard_content": computer_clipboard
        }


        resp = requests.post(self.url, files=files, data=data)
        res_json = resp.json()
        # for debug
#         import random
#         x = random.randint(100, 500)
#         y = random.randint(100, 500)
#         res_json = {
#             "plan_result": f"""
# ```python
# pyautogui.click(x={x}, y={y})
# ```
# ```decision
# COMMAND
# ```
# """,
#             "response_id": "aaa"}

        # --------------------------------------------------

        plan_result = res_json["plan_result"]
        response_id = res_json["response_id"]


        if not self.is_initialized:
            self.task_instruction = instruction
            self.is_initialized = True
            self.response_id = response_id

            
        logs['plan_result'] = plan_result

        code_block = re.search(r'```python\n(.*?)```', plan_result, re.DOTALL)
        if code_block:
            code_block_text = code_block.group(1)
            code_block_text = remove_min_leading_spaces(code_block_text)
            actions = [code_block_text]
        else:
            logger.error("Plan not found")
            code_block_text = "# plan not found"
            actions = ["# plan not found"]

        decision_block = re.search(r'```decision\n(.*?)```', plan_result, re.DOTALL)
        if decision_block:
            self.decision_block_text = decision_block.group(1)
            if "DONE" in self.decision_block_text:
                actions = ["DONE"]
            elif "FAIL" in self.decision_block_text:
                actions = ["FAIL"]
            elif "WAIT" in self.decision_block_text:
                actions = ["WAIT"]

        self.step_counter += 1
        return "", actions, logs, None
        

    def reset(self):
        self.is_initialized = False
        self.task_instruction = None
        self.step_counter = 0
        self.response_id = None
import json
import os
import sys
from bot_config.steps.bedrock_llm import BedrockLLM


class Llama(BedrockLLM):

    def payload(self, prompt):

        result = { 
            "prompt": prompt, 
            "max_gen_len": self.max_gen_len,
            "temperature": self.temperature or 0.5,
            "top_p": self.top_p or 0.9
            }
    
        return result
    

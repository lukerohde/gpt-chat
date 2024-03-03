from bot_manager.bot_step import Step

import json
import os
import sys


class Llama(Step):

    async def process(self, payload):

        payload['bedrock'] = { 
            "prompt": payload['prompt'], 
            "max_gen_len": self.config.maxAnswerTokens or 512,
            "temperature": self.config.temperature or 0.5,
            "top_p": self.config.topp or 0.9
            }
    
        print(payload['bedrock'])
        return payload
    
if __name__ == "__main__":
    Llama.main()
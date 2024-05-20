import json
import os
import sys
import bot_config.steps.bedrock


class BedrockLLM():

    def __init__(self, model, config):
        self.model = model
        self.config = config

        self.max_gen_len = config.get('maxAnswerTokens') or 512
        self.temperature = config.get('temperature') or 0.5
        self.top_p = config.get('topp') or 0.9
        self.debug = config.get('debug') or False
        


    def payload(self, prompt):
        result = { 
            "inputText": prompt, 
            "textGenerationConfig": {
                "maxTokenCount":self.max_gen_len or 512,
                "stopSequences":[],
                "temperature": self.temperature or 0,
                "topP": self.top_p or 0.9               
            }}
    
        return result

    async def ask(self, chatml):
        prompt = self.prompt(chatml)
        if self.debug:
            print(f"Prompt: {prompt}")

        answer = await bot_config.steps.bedrock.ask(self.model, self.payload(prompt))
        return answer
    
    def prompt(self, chatml):
        messages = [f"\n\
            {message['name']}: {message['content']}\n" 
            for message in chatml
        ]

        #TODO implement the upstream logic to ensure fit in the context window
        prompt = ','.join(messages)
        return prompt
    
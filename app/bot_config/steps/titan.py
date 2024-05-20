import json
import os
import sys
from bot_config.steps.bedrock_llm import BedrockLLM


class Titan(BedrockLLM):
    pass
    

    
# from bot_manager.bot_step import Step

# import json
# import os
# import sys


# class Titan(Step):

#     async def process(self, payload):
        
#         parameters = {
#                 "maxTokenCount":self.config.maxAnswerTokens or 512,
#                 "stopSequences":[],
#                 "temperature":self.config.temperature or 0,
#                 "topP":self.config.topp or 0.9
#                 }

#         payload['bedrock'] = {"inputText": payload['prompt'], "textGenerationConfig": parameters}
    
#         return payload
    
# if __name__ == "__main__":
#     Titan.main()
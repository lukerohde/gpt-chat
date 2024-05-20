from bot_manager.bot_step import Step
from bot_config.steps.chatgpt import ChatGPT
from bot_config.steps.llm import LLM
import json

class ChatGPTAsk(Step):

    async def process(self, payload):
        
        if payload['type'] != 'direct_message': 
            return payload

        if payload['draft']['body'] != '¯\_(ツ)_/¯':
            return payload
        
        config = self.config.get('llm_config', {})
        config = config.update(payload['user_profile_bot_data'])
            
        llm = LLM(self.config.model, config)
        #payload['openai'] = await ChatGPT.ask(payload['chatml'], self.config.model)
        payload['openai'] = await llm.ask(payload['chatml'])
        
        if not 'draft' in payload: 
            payload['draft'] = {}

        payload['draft']['body'] = payload['openai']['reply']
        
        return payload
    
       
    @property
    def activity(self):
        return f"thinking with {self.config.model}..."


if __name__ == "__main__":
    ChatGPTAsk.main()
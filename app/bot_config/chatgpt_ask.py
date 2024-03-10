from bot_manager.bot_step import Step
from chatgpt import ChatGPT
import json

class ChatGPTAsk(Step):

    async def process(self, payload):
        
        if payload['type'] != 'direct_message': 
            return payload

        if payload['draft']['body'] != '¯\_(ツ)_/¯':
            return payload

        #print(json.dumps(payload, indent=4))

        print(payload['chatml'])
        
        payload['openai'] = await ChatGPT.ask(payload['chatml'], self.config.model)
        
        if not 'draft' in payload: 
            payload['draft'] = {}

        payload['draft']['body'] = payload['openai']['reply']
        
        return payload
    
       
    @property
    def activity(self):
        return f"thinking with {self.config.model}..."


if __name__ == "__main__":
    ChatGPTAsk.main()
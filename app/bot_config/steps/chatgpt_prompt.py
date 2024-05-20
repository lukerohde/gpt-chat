from bot_manager.bot_step import Step

import pytz 
import datetime
import dateutil.parser
from bot_config.steps.llm import LLM

class ChatGPTPrompt(Step):

    async def process(self, payload):
        messages=payload['messages']

        payload['chatml'] = [ LLM.chatml(message, self.bot_name, self._dress_content) for message in messages ]

        return payload
    
    def _dress_content(self, message):
        content = message['body']

        if message["user"] != self.bot_name:
            if 'each_user_message' in self.config:
                content = self.config.each_user_message.replace('{content}', content)
            
            input_time = dateutil.parser.parse(message['timestamp'])
            target_tz = pytz.timezone("Australia/Melbourne")
            melbourne_time = input_time.astimezone(target_tz)

            content = content.replace('{timestamp}', str(melbourne_time))            
        
        return content 

if __name__ == "__main__":
    ChatGPTPrompt.main()
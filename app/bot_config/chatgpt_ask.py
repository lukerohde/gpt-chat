from bot_manager.bot_step import Step
import backoff
import openai
import json 
import os
from aiohttp import ClientSession

class ChatGPTAsk(Step):


    async def process(self, payload):
        if payload['type'] != 'direct_message': 
            return payload

        payload['openai'] = await self._ask_openai(payload['chatml'])
        if not 'draft' in payload: 
            payload['draft'] = {}

        if 'choices' in payload['openai']:
            payload['draft']['body'] = payload['openai']['choices'][0]['message']['content']
        elif 'error' in payload['openai']:
            payload['draft']['body'] = f"OpenAI Error: {payload['openai']['error']['message']}"
        else:
            payload['draft']['body'] = f"An unknown error occurred"   
        
        return payload
    
    @backoff.on_exception(backoff.expo, openai.error.RateLimitError)
    async def _ask_openai(self, messages):
       async with ClientSession() as session:
            url = 'https://api.openai.com/v1/chat/completions'
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            }

            payload = {
                "model": self.config.model or "gpt-4",
                "messages": messages
            }

            async with session.post(url, json=payload, headers=headers) as response:
                result =  await response.text()
                    
            return json.loads(result)
       
    @property
    def activity(self):
        return f"thinking with {self.config.model}..."


if __name__ == "__main__":
    ChatGPTAsk.main()
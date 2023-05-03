from bot_step import Step
import backoff
import openai
import json 
import os
from aiohttp import ClientSession

class Gpt(Step):

    async def process(self, payload):
        payload['openai'] = await self._ask_openai(payload['chatml'])

        payload['draft']['body'] = payload['openai']['choices'][0]['message']['content']
        
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


if __name__ == "__main__":
    Step2.main()
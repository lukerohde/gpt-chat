from bot_step import Step
     
class Format(Step):

    async def process(self, payload):
        messages=payload['messages']

        payload['chatml'] = self._chatml(messages)

        payload['draft']={
            'user': payload['messages'][-1]['recipient'],
            'recipient': payload['messages'][-1]['user'],
            'body': '¯\_(ツ)_/¯'
        }

        payload['reply'] = payload['draft']
        
        return payload
    
    def _chatml(self, messages):
        results = [{ 
            "content": message["body"],
            "name": message["user"],
            "role": "assistant" if message["user"] == self.bot_name else "user"
         } for message in messages]
        
        return results

if __name__ == "__main__":
    Step1.main()
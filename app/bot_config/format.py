from bot_manager.bot_step import Step
     
class Format(Step):

    async def process(self, payload):
        messages=payload['messages']

        payload['chatml'] = self._chatml(messages)

        return payload
    
    def dress_content(self, message):
        content = message['body']

        if message["user"] != self.bot_name:
            if 'each_user_message' in self.config:
                content = self.config.each_user_message.replace('{content}', content)
            
            content = content.replace('{timestamp}', message['timestamp'])            
        
        return content 
    
    def _chatml(self, messages):
        results = [{ 
            "content": self.dress_content(message),
            "name": message["user"],
            "role": "assistant" if message["user"] == self.bot_name else "user"
         } for message in messages]
        
        return results

if __name__ == "__main__":
    Format.main()
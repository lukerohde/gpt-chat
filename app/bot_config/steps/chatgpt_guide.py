from bot_manager.bot_step import Step
from datetime import datetime
import pytz
     
class ChatGPTGuide(Step):

    async def process(self, payload):

        if not 'chatml' in payload:
            payload['chatml'] = {}
        
        if 'before' in self.config:
            before_message = self._chatml_message("system", f'{self.bot_name}_supervisor', self.config['before'])
            payload['chatml'].insert(0, before_message)
        
        if 'after' in self.config:
            after_message = self._chatml_message("system", f'{self.bot_name}_supervisor', self.config['after'])
            payload['chatml'].append(after_message)
        
        return payload
    
    def _chatml_message(self, role = str, name = str, content = str):
        input_time = datetime.utcnow().replace(tzinfo=pytz.utc)
        target_tz = pytz.timezone("Australia/Melbourne")
        melbourne_time = input_time.astimezone(target_tz)

        content = content.replace("{current_time}", melbourne_time.isoformat())

        return {
            "role": role, 
            "name": name, 
            "content": content
        }
    

if __name__ == "__main__":
    ChatGPTGuide.main()
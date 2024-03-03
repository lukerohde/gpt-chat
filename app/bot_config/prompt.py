from bot_manager.bot_step import Step
from datetime import datetime
import pytz
     
class Prompt(Step):

    async def process(self, payload):
        messages=payload['messages']

        payload['prompt'] = self._format_messages(messages)

        return payload

    def _format_messages(self, messages):
        prompt = "" 
        input_time = datetime.utcnow().replace(tzinfo=pytz.utc)
        target_tz = pytz.timezone("Australia/Melbourne")
        melbourne_time = input_time.astimezone(target_tz)

        if 'before' in self.config:
            before_message = f"\nInstruction:  {self.config['before']}"
            before_message = before_message.replace("{current_time}", melbourne_time.isoformat())

        if 'after' in self.config:
            after_message = f"\nInstruction:  {self.config['after']}"
            after_message = after_message.replace("{current_time}", melbourne_time.isoformat())

        strings = [f"\n\
            {'Answer: ' if message['user'] == self.bot_name else 'Question: '} \
            {message['body']}\
            "
            for message in messages]
            
        qanda = ""
        # Add as much message history as we can
        for message in reversed(strings):
            if (self.config.maxPromptLength or 7000 * 4) > len(before_message + after_message + qanda + message): 
                qanda = f"{message}{qanda}"
            else:
                break

        return f"{before_message}{qanda}{after_message}"
    

if __name__ == "__main__":
    Prompt.main()
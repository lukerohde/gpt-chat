from bot_manager.bot_step import Step
from bot_config.steps.chatgpt import ChatGPT
import json
from bot_config.steps.llm import LLM 

class ChatGPTUserData(Step):

    async def process(self, payload):

        #print(json.dumps(payload['user_profile_bot_data'], indent=2))

        if not 'user_profile_bot_data' in payload:
            return payload

        model = self.config.get('model',  "gpt-3.5-turbo")
            
        blanks = {k: v for k, v in payload['user_profile_bot_data'].items() if not v}
        
        if blanks: 
            print(f"Asking {model} to check user reply for {blanks} in {json.dumps(payload['user_profile_bot_data'], indent = 2)}")

            request = self.config.get("prompt") or """
                Please inspect the user's reply and if possible, fill in any blank values in the following JSON.  
                
                {user_profile_bot_data}
                
                If the user hasn't explicitly given you a value, leave it blank.  Don't make up anything. 
                If nothing is to be updated, return the json unchanged.  
                Your entire response will be parsed by json.loads into a python dict.  
                Do not add or remove keys.  
            """
            request = request.replace("{user_profile_bot_data}", json.dumps(blanks))
            
            last_user_message = payload['messages'][-1]
            chatml = [
                {
                    "content": last_user_message['body'],
                    "name": last_user_message['user'],
                    "role": "user"
                }, 
                {
                    "content": request, 
                    "name": f'{self.bot_name}_supervisor',
                    "role": "user"
                }
            ]

            if self.config.get('debug', False):    
                print(json.dumps(chatml, indent=2))

            config = self.config.get('llm_config', {})
            llm = LLM(self.config.model, config)
            response = await llm.ask(chatml)
            
            try: 
                parsed_json = json.loads(response['reply'])
                print(parsed_json)
                
                if parsed_json == blanks:
                    payload['draft']['body'] = f"Please provide the following information: {', '.join(blanks.keys())}"
                else:
                    payload['user_profile_bot_data'].update(parsed_json)
                    payload['draft']['body'] = f"Your profile data has been updated.  \n {json.dumps(payload['user_profile_bot_data'])}"
            
            except json.JSONDecodeError:
                payload['draft']['body'] = f"Failed to parse JSON returned by {self.config.model} in {self.step_name}\n\n{response['reply']}"
                
        return payload 

if __name__ == "__main__":
    ChatGPTUserData.main()
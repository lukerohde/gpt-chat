from bot_manager.bot_step import Step
from bot_config.steps.chatgpt import ChatGPT
import json
import re
from bot_config.steps.llm import LLM 

class ChatGPTDirector(Step):

    async def process(self, payload):

        payload['capability'] = {}

        if not self.can_process(payload):
            return payload 

        instruction = self.get_instruction()
        chatml = self.get_chatml(payload, instruction)

        config = self.config.get('llm_config', {})
        config.update(payload['user_profile_bot_data'])
        llm = LLM(self.config.model, config)
        response = await llm.ask(chatml)
        
        try: 
            reply = re.sub(r'`([^`]*)`', r'\1', response['reply']) # Remove backticks
            reply = re.sub(r'^json\n|\n$', '', reply, flags=re.MULTILINE) #remove json
                    
            parsed_json = json.loads(reply)
            
            if parsed_json:
                payload['draft']['body'] = f"I've classified this as {json.dumps(parsed_json, indent=2)}"
                print(payload['draft']['body'])
                payload['capability'] = parsed_json
            else:
                payload['notices'].append("ChatGPTDirector could not match this request to a capability")
                
        except json.JSONDecodeError:
            payload['draft']['body'] = f"Failed to parse JSON returned by {self.config.model} in {self.__class__.__name__}\n\n{response['reply']}"
            
        return payload 

    def can_process(self, payload):
            # TODO better validation
            capabilities = self.config.get('capabilities', {})
            chatml = payload.get('chatml', [])

            return bool(capabilities and chatml)

    def get_instruction(self):

        instruction = self.config.get('prompt') or """
            For each user request, classify the action and object
            then respond with a JSON object. For example:
            
            {request_response_examples}
            
            These are the only actions and objects that are shown in the examples.  
            If the user's request doesn't relate to these answer with an 
            empty json response like {}

            Your entire reponse will be directly parsed by `json.loads` into a python dict 
            so only answer with a json dict.
        """

        # format examples
        capabilities = self.config.get('capabilities', {})  # Access capabilities here
        request_response_examples = ""

        for noun, actions in capabilities.items():
            for verb, examples in actions.items():
                for request in examples:
                    # Append each example to the prompt
                    example_response = f'{{"action": "{verb}", "object": "{noun}"}}'
                    request_response_examples += f'When a user says "{request}" please respond with:\n{example_response}\n\n'


        instruction = instruction.replace("{request_response_examples}", request_response_examples)
        
        return instruction

    def get_chatml(self, payload, instruction):
        # TODO figure out the right about to put in the context window with out overflow 
        # I suspect all chatgpt helpers need to be in our chatgpt class, and probably shouldn't 
        # be steps in their own right
        result = [ item for item in payload['chatml'][-3:] ]
        result.append( 
            {
                "content": instruction, 
                "name": f'{self.bot_name}_supervisor',
                "role": "system"
            }
        )

        return result

if __name__ == "__main__":
    ChatGPTDirector.main()
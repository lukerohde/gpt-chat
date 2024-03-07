from bot_manager.bot_step import Step
import json
     
class ChatGPTFitContext(Step):

    async def process(self, payload):

        if not 'chatml' in payload:
            payload['chatml'] = []

        payload['overflow'] = []
 
        if len(json.dumps(payload['chatml'])) > self.config.maxPromptLength:
            # Select recent messages that fit into the context window
            # We specially handle the first message if its a system instruction to make sure it is kept
            if 'before' in self.config:
                selection = [payload['chatml'][0]]
                payload['chatml'] = payload['chatml'][1:] # Keep everything but the first item
            else:
                selection = [] 

            current_length = len(json.dumps(selection))

            for message in reversed(payload['chatml']): 
                message_length = len(json.dumps(message))
                if current_length + message_length + 1 < self.config.maxPromptLength: # +1 for comma in JSON array
                    selection.insert(0, message)
                    current_length += message_length + 1 
                else: 
                    payload['overflow'].insert(0, message)

            if payload['overflow']:
                print(f"Dropped {len(payload['overflow'])} older messages from the context window")   

            payload['chatml'] = selection
            
        return payload

if __name__ == "__main__":
    ChatGPTFitContext.main()
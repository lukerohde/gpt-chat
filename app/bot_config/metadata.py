from bot_manager.bot_step import Step
import datetime
import json
import regex
import re
     
class Metadata(Step):

    async def process(self, payload):

        if not ('draft' in payload and 'body' in payload['draft']):
            return payload 
        
        before_metadata = payload['draft']['body']
        after_metadata = ""

        # Define a regular expression pattern to match the metadata markdown heading
        metadata_pattern = r'# metadata'

        # Search for the metadata markdown heading
        metadata_match = re.search(metadata_pattern, payload['draft']['body'])

        if metadata_match:
            # Split the string at the position of the metadata markdown heading
            before_metadata, _, after_metadata = payload['draft']['body'].partition(metadata_match.group())
        
        json_pattern = r'\{(?:[^{}]|(?R))*\}'
        json_match = regex.search(json_pattern, after_metadata,  regex.DOTALL)

        if json_match:
            json_str = json_match.group()
            try:
                json_obj = json.loads(json_str)
                payload['draft']['metadata'] = json.dumps(json_obj, indent=2)
                payload['draft']['body'] = before_metadata

            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
 
        return payload
    

if __name__ == "__main__":
    Metadata.main()
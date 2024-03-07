from bot_manager.bot_step import Step
      
class Reply(Step):
    
    async def process(self, payload):
        
        if 'draft' in payload:
            payload['reply'] = payload['draft']

            payload['reply']['metadata'] = payload['reply'].get('metadata', {})

            if payload['notices']:
                payload['reply']['metadata']['notices'] = payload['notices']

            if payload['user_profile_bot_data']:
                payload['reply']['metadata']['user_profile_bot_data'] = payload['user_profile_bot_data']
        
        return payload

if __name__ == "__main__":
    Reply.main()
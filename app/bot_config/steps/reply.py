from bot_manager.bot_step import Step
      
class Reply(Step):
    
    async def process(self, payload):

        if 'draft' in payload:
            payload['reply'] = payload['draft']

            payload['reply']['metadata'] = payload['reply'].get('metadata', {})

            if 'notices' in payload:
                payload['reply']['metadata']['notices'] = payload['notices']

            if 'user_profile_bot_data' in payload:
                payload['reply']['metadata']['user_profile_bot_data'] = payload['user_profile_bot_data']
        
            if 'reminder' in payload:
                payload['reply']['metadata']['reminder'] = payload['reminder']

        return payload

if __name__ == "__main__":
    Reply.main()
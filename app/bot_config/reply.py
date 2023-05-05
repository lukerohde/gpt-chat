from bot_manager.bot_step import Step
      
class Reply(Step):
    
    async def process(self, payload):
        
        if 'draft' in payload:
            payload['reply'] = payload['draft']
        
        return payload

if __name__ == "__main__":
    Reply.main()
from bot_step import Step
      
class Step3(Step):
    
    async def process(self, payload):
        
        payload['reply']['body'] = payload['draft']['body']
        
        return payload

if __name__ == "__main__":
    Step3.main()
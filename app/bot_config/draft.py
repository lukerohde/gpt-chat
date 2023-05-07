from bot_manager.bot_step import Step
     
class Draft(Step):

    async def process(self, payload):
        messages=payload['messages']

        payload['draft']={
            'user': payload['messages'][-1]['recipient'],
            'recipient': payload['messages'][-1]['user'],
            'body': '¯\_(ツ)_/¯'
        }

        return payload

if __name__ == "__main__":
    Draft.main()
from bot_manager.bot_step import Step
     
class Draft(Step):

    async def process(self, payload):
        messages=payload['messages']

        payload['draft']={
            'user': payload['messages'][-1]['recipient'],
            'recipient': payload['messages'][-1]['user'],
            'body': '¯\_(ツ)_/¯'
        }

        if 'user_profile_bot_data' not in payload:
            payload['user_profile_bot_data'] = {}

        payload['notices'] = []

        return payload

if __name__ == "__main__":
    Draft.main()
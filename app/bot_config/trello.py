from bot_manager.bot_step import Step

class Trello(Step):

    async def process(self, payload):

        if 'trello_api_key' not in payload['user_profile_bot_data']:
            payload['user_profile_bot_data']['trello_api_key'] = "xxx"
        
        if payload['user_profile_bot_data']['trello_api_key']:
            # TODO Trello Stuff
            payload['reminder'] = {
                'target': 'Trello',
                'countdown_seconds': 10
            }
            pass 
        else:
            payload['notices'].append("For this bot to connect to your trello task list, please provide your trello API token.")
        
        return payload 

if __name__ == "__main__":
    Trello.main()
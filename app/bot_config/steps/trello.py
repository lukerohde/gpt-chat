from bot_manager.bot_step import Step
import requests
from requests.exceptions import RequestException

class Trello(Step):

    async def process(self, payload):

        if self.trello_ready(payload):
            # TODO Trello Stuff
            # payload['reminder'] = {
            #     'target': 'Trello',
            #     'countdown_seconds': 10
            # }

            # Get the board
            board_id = payload['user_profile_bot_data']['trello_board_id']
            api_key = payload['user_profile_bot_data']['trello_api_key']
            token = payload['user_profile_bot_data']['trello_token']

            # Construct the API endpoint URL
            url = f'https://api.trello.com/1/boards/{board_id}/lists'

            # Make a GET request to the API endpoint
            try: 
                response = requests.get(url, params={'key': api_key, 'token': token, 'cards': 'open'}, verify=False)
                response.raise_for_status()

                if response.status_code == 200:
                    payload['trello_lists'] = self.get_board(response.json(), payload['user_profile_bot_data']['trello_lists'])
                    payload['chatml'].append({ 
                        "role": "system", 
                        "name": f"{self.bot_name}_supervisor", 
                        "content": payload['trello_lists']
                    })

                    print(payload['trello_lists']) 

            except RequestException as e:
                if e.response is not None: 
                    if e.response.status_code == 403 or e.response.status_code == 401: 
                        payload['draft']['body'] = f"Trello access denied.  Erasing your credentials so you can supply them again."
                        payload['user_profile_bot_data']['trello_api_key'] = ""
                        payload['user_profile_bot_data']['trello_token'] = ""
                        payload['user_profile_bot_data']['trello_board_id'] = ""
                        payload['user_profile_lists']['trello_lists'] = ""
                    elif e.response.status_code == 404:
                        payload['draft']['body'] = f"Trello not found.  Erasing your board_id so you can supply it again."
                        payload['user_profile_bot_data']['trello_lists'] = ""
                    else: 
                        payload['draft']['body'] = f"We encounted a problem accessing Trello.  Status {e.response.status_code} e.response"
                else:
                    payload['draft']['body'] = f"We encounted a problem accessing Trello.  {str(e)}"
                        
        return payload 

    def trello_ready(self, payload):

        if 'trello_api_key' not in payload['user_profile_bot_data']:
            payload['user_profile_bot_data']['trello_api_key'] = ""
            payload['notices'].append("Visit https://trello.com/app-key and get your API key")
        
        if 'trello_token' not in payload['user_profile_bot_data']:
            payload['user_profile_bot_data']['trello_token'] = ""
            payload['notices'].append("Visit https://trello.com/app-key and find the link to obtain your token")
        
        if 'trello_board_id' not in payload['user_profile_bot_data']:
            payload['user_profile_bot_data']['trello_board_id'] = ""
            payload['notices'].append("For this bot to connect to your trello task list, please provide your trello board id.  Its in the board's url.")

        if 'trello_lists' not in payload['user_profile_bot_data']:
            payload['user_profile_bot_data']['trello_lists'] = ""
            payload['notices'].append("For this bot to connect to your trello task list, please list the boards you are interested in.")
        

        result = \
            payload['user_profile_bot_data']['trello_api_key'] and \
            payload['user_profile_bot_data']['trello_token'] and \
            payload['user_profile_bot_data']['trello_board_id'] and \
            payload['user_profile_bot_data']['trello_lists']

        return result 

    def get_board(self, board, lists):

        #import ipdb; ipdb.set_trace()
       
        tasks = f"# FYI here is the user's trello board: \n"

        for list_data in board:
            list_name = list_data['name']

            lists = [item.lower() for item in lists]
            if list_name and list_name.lower() not in lists:
                continue  # Skip this list
            
            tasks += f"\n## List {list_data['pos'] + 1}: {list_name} \n"
            
            cards = list_data['cards']
            
            for card in cards:
                card_name = card['name']
                tasks += f"- {card_name}\n"

        return tasks


if __name__ == "__main__":
    Trello.main()
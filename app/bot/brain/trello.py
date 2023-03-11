import requests

class Trello:

    def __init__(self, endpoint, api_key, token):
# Define the API endpoint
        self.endpoint = endpoint
        self.api_key = api_key
        self.token = token
        self.current_board = None

    def get_board(self, target_board):
        # Get all boards
        url = f"{self.endpoint}/members/me/boards?key={self.api_key}&token={self.token}"
        r = requests.get(url)
        jobs = ""
        if r.status_code == 200: 
            boards = r.json()
            for board in boards:
                if board['name'] == target_board:
                    url = f"{self.endpoint}/boards/{board['id']}/lists?key={self.api_key}&token={self.token}"
                    r = requests.get(url)
                    if r.status_code == 200: 
                        lists = r.json()
                        for list in lists: 
                            if "Brook" in list['name'] and not "Done" in list['name']:
                                url=f"{self.endpoint}/lists/{list['id']}/cards?key={self.api_key}&token={self.token}"
                                r = requests.get(url)
                                if r.status_code == 200:
                                    cards = r.json()
                                    for card in cards: 
                                        jobs += f"{list['name']} - {card['name']}\n"
        return jobs
    
                    

from bot_step import Step

class Step1(Step):
    def process(self, payload):
        message=payload['message']
        payload['reply']={
            'user': message['recipient'],
            'recipient': message['user'],
            'body': 'hello'
        }
        return payload

if __name__ == "__main__":
    Step1.main()
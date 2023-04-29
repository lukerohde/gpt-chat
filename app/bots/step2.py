from bot_step import Step

class Step2(Step):
    def process(self, payload):
        print(payload)
        return payload

if __name__ == "__main__":
    Step1.main()
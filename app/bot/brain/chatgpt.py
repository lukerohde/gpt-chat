import openai
import backoff

class ChatGPT():
    def __init__(self, key, model, temp, tokens):
        openai.api_key = key
        self.model = model
        self.tokens = 0
        self.temperature = float(temp)
        self.max_tokens = int(tokens)
        self.frequency_penalty = 1
    
    @backoff.on_exception(backoff.expo, openai.error.RateLimitError)
    def answer(self, history):
        result = ""
        response = None
        #try:
        response = openai.Completion.create(model=self.model, prompt=history, temperature=self.temperature, max_tokens=self.max_tokens, frequency_penalty = self.frequency_penalty)
        self.tokens = response['usage']['total_tokens']
        result = response["choices"][0]["text"]
        # except openai.error.RateLimitError as e: 
        #     import ipdb; ipdb.set_trace()
        #     result = e
        
        return result
    

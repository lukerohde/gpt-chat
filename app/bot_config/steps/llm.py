from bot_config.steps.langchain_llm import LangChainLLM
from bot_config.steps.llama import Llama
from bot_config.steps.chatgpt import ChatGPT
from bot_config.steps.titan import Titan
from bot_config.steps.anthropic import Anthropic

class LLM():

    def __init__(self, model, llm_config):
        # instantiate model - chatgpt, llamba, titan or claud, each model is prefixed by brand
        self.model = model
            
        if model.startswith('gpt'):
            self.llm = LangChainLLM(model, llm_config)
        elif model.startswith('claude'):
            self.llm = LangChainLLM(model, llm_config)
        elif model.startswith('gpt'):
            self.llm = ChatGPT(model, llm_config)
        elif model.startswith('anthropic'):
            self.llm = Anthropic(model, llm_config)
        elif model.startswith('meta.llama'):
            self.llm = Llama(model, llm_config)
        elif model.startswith('amazon.titan'):
            self.llm = Titan(model, llm_config) 
        else: 
            raise ValueError(f"Unknown model {model}")
        
        
    async def ask(self, chatml):
        return await self.llm.ask(chatml)
    
    @staticmethod
    def chatml(message, bot_name, dress_function = None):
        if dress_function:
            content = dress_function(message)
        else:
            content = message['body']
    
        result = {
            "content": content,
            "name": message["user"],
            "role": "assistant" if message["user"] == bot_name else "user"
        }

        return result
    

from bot_manager.bot_step import Step
import json
import os
import sys

from bot_config.steps.llm import LLM 

sys.path.append('./bot_config/')


class LangchainAsk(Step):

    async def process(self, payload):

        if payload['type'] != 'direct_message': 
            return payload

        if payload['draft']['body'] != '¯\_(ツ)_/¯':
            return payload

        config = self.config.get('llm_config', {})
        config.update(payload['user_profile_bot_data'])
        
        llm = LLM(self.config.model, config)
        payload['llm'] = await llm.ask(payload['chatml'])

        if not 'draft' in payload: 
            payload['draft'] = {}

        payload['draft']['body'] = payload['llm']
        
        return payload
       
    @property
    def activity(self):
        return f"{self.config.model} is thinking..."

if __name__ == "__main__":
    LLMAsk.main()
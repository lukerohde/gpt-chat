from bot_manager.bot_step import Step
import backoff
from datetime import datetime
import pytz

import json
import os
import sys

import boto3
import botocore
from bot_config.steps.llm import LLM 
from aiohttp import ClientSession

sys.path.append('./bot_config/')
import bot_config.steps.bedrock


class LLMAsk(Step):

    async def process(self, payload):

        if payload['type'] != 'direct_message': 
            return payload

        if payload['draft']['body'] != '¯\_(ツ)_/¯':
            return payload

        config = self.config.get('llm_config', {})
        config.update(payload['user_profile_bot_data'])
        
        llm = LLM(self.config.model, config)
        #payload['openai'] = await ChatGPT.ask(payload['chatml'], self.config.model)
        # payload['answer'] = await self._ask_bedrock(payload['bedrock'])
        payload['llm'] = await llm.ask(payload['chatml'])
        

        if not 'draft' in payload: 
            payload['draft'] = {}

        payload['draft']['body'] = payload['llm']['reply']
        
        return payload

 
       
    @property
    def activity(self):
        return f"{self.config.model} is thinking..."

if __name__ == "__main__":
    BedrockAsk.main()
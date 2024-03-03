from bot_manager.bot_step import Step
import backoff
from datetime import datetime
import pytz

import json
import os
import sys

import boto3
import botocore
from aiohttp import ClientSession

sys.path.append('./bot_config/')
import bedrock


class Ask_bedrock(Step):

    async def process(self, payload):
        
        payload['answer'] = await self._ask_bedrock(payload['bedrock'])

        if not 'draft' in payload: 
            payload['draft'] = {}

        payload['draft']['body'] = payload['answer']
        
        return payload

 
    async def _ask_bedrock(self, payload):
       async with ClientSession() as session:
            
            body = json.dumps(payload)
            modelId = self.config.model #"amazon.titan-tg1-large"  # change this to use a different version from the model provider

            accept = "application/json"
            contentType = "application/json"

            boto3_bedrock = bedrock.get_bedrock_client(
                assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None),
                region=os.environ.get("AWS_DEFAULT_REGION", None)
            )

            answer = ""
            try:
                response = boto3_bedrock.invoke_model(
                    body=body, modelId=modelId, accept=accept, contentType=contentType
                )
                response_body = json.loads(response.get("body").read())
                
                # This handles different bedrock formats.  Consider splitting this out into seperate steps.
                if "results" in response_body:
                    answer = response_body.get("results")[0].get("outputText")
                elif "generation" in response_body:
                    answer = response_body.get("generation")
                else:
                    answer = json.dumps(response_body)
                
            except botocore.exceptions.ClientError as error:
                answer = f"Error Code: error.response['Error']['Code']\n{error.response['Error']['Message']}"
                if  error.response['Error']['Code'] == 'AccessDeniedException':
                    answer += f"\
                    \nTo troubeshoot this issue please refer to the following resources.\
                    \nhttps://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html\
                    \nhttps://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html\
                    "  

            return answer
       
    @property
    def activity(self):
        return f"querying aws bedrock's {self.config.model}..."

if __name__ == "__main__":
    Ask_bedrock.main()
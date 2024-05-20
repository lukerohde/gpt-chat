from bot_manager.bot_step import Step
import sys
import os
import boto3
from botocore.exceptions import ClientError

sys.path.append('./bot_config/')

class BedrockAgentAsk(Step):


    async def process(self, payload):

        config = self.config.get('llm_config', {})

        prompt = payload['messages'][-1]['body']
        session_id = f"{payload['messages'][-1]['user']}_{payload['messages'][-1]['recipient']}"
        
        response = self.invoke_agent(
            config.agent_id, 
            config.agent_alias_id,
            session_id,
            prompt
        )
        
        if not 'draft' in payload: 
            payload['draft'] = {}

        payload['draft']['body'] = response
        
        return payload
    
    def invoke_agent(self, agent_id, agent_alias_id, session_id, prompt):
        
        runtime_client = boto3.client(
            service_name="bedrock-agent-runtime", region_name=os.environ.get("AWS_DEFAULT_REGION", None)
        )

        try:
            response = runtime_client.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                inputText=prompt,
            )

            completion = ""

            for event in response.get("completion"):
                chunk = event["chunk"]
                completion = completion + chunk["bytes"].decode()

        except ClientError as e:
            print(f"Couldn't invoke agent. {e}")
            raise

        return completion

 
       
    @property
    def activity(self):
        return f"Onesie is thinking hard..."

if __name__ == "__main__":
    BedrockAsk.main()
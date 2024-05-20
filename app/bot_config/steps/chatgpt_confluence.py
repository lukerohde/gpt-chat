from bot_manager.bot_step import Step
from bot_config.steps.chatgpt import ChatGPT
import requests
from requests.exceptions import RequestException
import json 
import re
import textwrap
import html2text
from bot_config.steps.llm import LLM

class ChatGPTConfluence(Step):

    async def process(self, payload):
        
        if self.actionable(payload):
            
            profile = payload['user_profile_bot_data']
            action = payload['capability']['action']
                
            if action == 'read':
                # Construct prompt for OpenAI to generate a JQL search
                instruction = self.config.get('jql_prompt', "" ) or textwrap.dedent(""" 
                    Given the chat history and the following JIRA configuration, 
                    please reply with a list of enquiries to be answered from one or more confluence page ids.
                                                                                    
                    For example, for the following request 
                    ```from https://<your-confluence-site>.atlassian.net/wiki/spaces/DOCS/pages/123456789/My+Page please list these repos in epic order and tell me which repos we should start with```
                                                                                    
                    Please format your response in raw json (no markdown) like this:

                    {
                        "enquiries": ["list the repos in epic order", "tell me which repos we should start with"],
                        "page_ids": ["123456789"]
                    } 
                                                                                
                    We will download these pages from the confluence id and pass them to an LLM along with your enquiries.                                                       

                    Your response needs to be machine readable with no markdown.
                                                                                                                                       
                    If there are no confluence pages being queried, discard the enquires and answer with empty json dict {} (w/no markdown)
                    """)
                
                chatml = self.get_chatml(payload, instruction)
                
                if self.config.get('debug', False):
                    print(json.dumps(chatml, indent=2))

                llm = LLM(self.config.model, self.config.get('llm_config', {}))
                response = await llm.ask(chatml)
                try: 
                    reply = re.sub(r'`([^`]*)`', r'\1', response['reply']) # Remove backticks
                    reply = re.sub(r'^json\n|\n$', '', reply, flags=re.MULTILINE) #remove json
                    reply = json.loads(reply)

                    payload['notices'].append(reply)
                    
                    # Call Jira API
                    payload['draft']['body'] = "I couldn't figure out what confluence page to read"
                    if reply:
                        read_results = self.read(reply['page_ids'], profile)
                        if read_results:
                            instruction = self.config.get('jql_prompt', "" ) or textwrap.dedent(f""" 
                                Given the the following page data ```{json.dumps(read_results)}```
                                                                                                                                                                   
                                Please answer these enquiries ```{json.dumps(reply['enquiries'])}```
                                """)
                            
                            chatml = [{
                                "content": instruction, 
                                "role": "user",
                                "name": self.bot_name
                            }]

                            if self.config.get('debug', False):
                                print(json.dumps(chatml, indent=2))

                            response = await llm.ask(chatml)
                            body = response['reply']
                        else:
                            body = read_results.get('error')
                        
                        payload['draft']['body'] = body
                        
                except json.JSONDecodeError:
                    payload['draft']['body'] = f"Failed to parse JSON returned by {self.config.model} in {self.__class__.__name__}\n\n{response['reply']}"
                   
        return payload 

    def actionable(self, payload):
        actionable = bool(payload['capability'] and \
            payload['capability'].get('object') == 'confluence' and \
            payload['capability']['action'] in ('read') )


        # Define a list of required JIRA configuration fields and their corresponding messages
        required_jira_fields = {
            'JIRA_USER': "Please configure your JIRA user email (e.g., yyy@xxx.com.au).",
            'JIRA_API_TOKEN': "Please provide your JIRA API token. You can find or generate one in your JIRA account settings.",
            'JIRA_API_URL': "Please set your JIRA API URL (e.g., https://xxx.atlassian.net/rest/api/2/issue).",
        }

        user_profile_bot_data = payload.get('user_profile_bot_data', {}) 

        # Iterate over each required field to check its presence and append a notice if it's missing
        for field, message in required_jira_fields.items():
            if field not in user_profile_bot_data:
                user_profile_bot_data[field] = ""  # Set a blank value to indicate it needs to be completed
                payload['notices'].append(message)

        # Ensure the updated user_profile_bot_data is back in the payload, in case it wasn't there initially
        payload['user_profile_bot_data'] = user_profile_bot_data

        # Now, to check if all JIRA configuration fields are present
        ready = all(user_profile_bot_data.get(field) for field in required_jira_fields)

        return ready and actionable 

    
    def read(self, page_ids, profile):
        # Your Confluence details
        base_url = "https://wesdigital.atlassian.net/wiki/rest/api/content/"
        
        # The endpoint URL to get page content
        content = ""
        for page_id in page_ids:
            url = f"{base_url}{page_id}?expand=body.storage"
            
            # Making the GET request with basic authentication
            try: 
                response = requests.get(
                    url, 
                    auth=(profile['JIRA_USER'], profile['JIRA_API_TOKEN']),
                    headers={'Content-Type': 'application/json'},
                    verify=False #TODO bot session that sets verify to either true or the CA_CERT if in ENV
                )
                response.raise_for_status()

                if response.status_code == 200:
                    page_content = response.json()
                    # Extracting the page content in storage format
                    content += self.convert_html_to_markdown(page_content['body']['storage']['value'])
            except requests.exceptions.RequestException as e:
                content += f"could not load {url}: {e}"
            
            return content
    
    
    def convert_html_to_markdown(self, html_content):
        text_maker = html2text.HTML2Text()
        text_maker.ignore_links = False
        markdown_content = text_maker.handle(html_content)
        return markdown_content


            


    def get_chatml(self, payload, instruction, message_count = 4):
        # TODO figure out the right about to put in the context window with out overflow 
        # I suspect all chatgpt helpers need to be in our chatgpt class, and probably shouldn't 
        # be steps in their own right
        result = [ item for item in payload['chatml'][-message_count:] ]
        result.append( 
            {
                "content": instruction, 
                "name": f'{self.bot_name}_supervisor',
                "role": "system"
            }
        )

        return result


if __name__ == "__main__":
    ChatGPTConfluence.main()


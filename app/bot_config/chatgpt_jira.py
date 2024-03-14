from bot_manager.bot_step import Step
from bot_config.chatgpt import ChatGPT
import requests
from requests.exceptions import RequestException
import json 

class ChatGPTJira(Step):

    async def process(self, payload):
        
        if self.actionable(payload):
            
            profile = payload['user_profile_bot_data']
            action = payload['capability']['action']
            if action == 'search':
                # Construct prompt for OpenAI to generate a JQL search
                jira_config = {k: v for k, v in profile.items() if k.startswith('JIRA_')}
                instruction = self.config.get('jql_prompt', "" ) or """ 
                    Given the chat history and the following JIRA configuration, 
                    please reply with valid JQL to be used with JIRA's search API.
                    The user's request contains keyworks that maybe found the epic name, 
                    summary, description or some combination there of.  More search results 
                    are better.  Reply only in JQL as your response will be directly used in an API call.
                    Order by most to least recently updated. Leave the jql bare without quotes.
                    {jira_config}

                    JQL: 
                    """
                instruction = instruction.replace('{jira_config}', json.dumps(jira_config))
                
                chatml = self.get_chatml(payload, instruction)
                print(json.dumps(chatml, indent=2))

                # Call OpenAI for JQL
                model = self.config.get('model',  "gpt-3.5-turbo")

                response = await ChatGPT.ask(chatml, model)
                try: 
                    jql = response['reply']
                    payload['notices'].append(jql)
                    
                    # Call Jira API
                    reply = "No tickets found"
                    if jql:
                        search_results = self.search(jql, profile)
                        if not search_results.get('error'):
                            # Render the results in markdown format
                            table_result = self.extract_info_markdown_table(search_results, profile)
                            reply = f"`{jql}` \n\n {table_result}"
                        else:
                            reply = search_results.get('error')
                        
                    payload['draft']['body'] = reply
                except json.JSONDecodeError:
                    payload['draft']['body'] = f"Failed to parse JSON returned by {model} in {self.__class__.__name__}\n\n{response['reply']}"
                    
                return payload 

                # Add the system instruction to payload['chatml']
            elif action == 'create': 
                pass
                # Construct the prompt with user data and template API json, and user request
                # Call OpenAI to generate JSON for each ticket
                # Call Jira API for each ticket (later we'll move this to after approval)
                # Render the ticket links in markdown
                # Create a payload['draft']['body'] with the ticket results
            
                # TEMPLATE_FILE=template-story-v2.json
                # {
                #     "update": {},
                #     "fields": {
                #         "summary": "[INSERT TICKET TITLE HERE]",
                #         "issuetype": {
                #         "id": "JIRA_STORY_TYPE_ID"
                #         },
                #         "project": {
                #         "key": "JIRA_PROJECT_ID"
                #         },
                #         "description": "As a [INSERT ROLE], I <want/need/can/etc> [INSERT STORY GOAL] so that [INSERT STORY BENEFIT].\n",
                #         "priority": {
                #         "id": "4"
                #         },
                #         "JIRA_TEAM_FIELD": "TEAM_ID",
                #         "JIRA_EPIC_FIELD": "EPIC_ID",
                #         "JIRA_SIZE_FIELD": "SIZE",
                #         "labels": [],
                #         "JIRA_AC_FIELD": "* Criteria 1\n \n* Criteria 2\n \n* Criteria 3"
                #     }
                # }
            
            
            elif action == "update":
                pass
                # Construct the prompt with user data and template API json, and user request
                #   Make sure Jira Ticket IDs are known for all tickets to be update
                # Call OpenAI to generate the update JSON
                # Call Jira API
                # Render the ticket links in markdown
                # Create a payload['draft']['body'] with the ticket markdown
             

            
                      
        return payload 

    def actionable(self, payload):
        actionable = bool(payload['capability'] and \
            payload['capability']['object'] and \
            payload['capability']['action'] in ('create', 'update', 'search') )


        # Define a list of required JIRA configuration fields and their corresponding messages
        required_jira_fields = {
            'JIRA_USER': "Please configure your JIRA user email (e.g., yyy@xxx.com.au).",
            'JIRA_API_TOKEN': "Please provide your JIRA API token. You can find or generate one in your JIRA account settings.",
            'JIRA_API_URL': "Please set your JIRA API URL (e.g., https://xxx.atlassian.net/rest/api/2/issue).",
            'JIRA_DEFAULT_TEAM_ID': "Please provide your JIRA default team ID.",
            'JIRA_DEFAULT_SIZE': "Please set a default size for your JIRA tasks.",
            'JIRA_STORY_TYPE_ID': "Please provide the Jira id for your story types e.g. 10010",
            'JIRA_PROJECT_ID': "Please provide your jira project id e.g. OP", 
            'JIRA_TEAM_FIELD': "Please provide your jira custom team field e.g. customfield_10001",
            'JIRA_EPIC_FIELD': "Please provide your jira custom epic field e.g. customfield_10014",
            'JIRA_SIZE_FIELD': "Please provide your jira custom size field e.g. customfield_10033",
            'JIRA_AC_FIELD': "Please provide your jira custom AC field e.g. customfield_10255",
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

    def update_ticket():
        pass


    def get_ticket():
        pass

        # RUBY CODE TO BE CONVERTED TO PYTHON AND UPDATED TO WORK
        # jira_result = {}
		# RestClient::Request.new(
		# 	:method => :get,
		# 	:url => ENV['JIRA_API_URL'] + "/#{id}",
		# 	:user => ENV['JIRA_USER'],
		# 	:password => ENV['JIRA_API_TOKEN'],
		# 	:headers => { :accept => :json, :content_type => :json }
		# ).execute do |response, request, result|
		# 	jira_result = JSON.parse(response.body) rescue {}
		# end

		# jira_result
        
    # RUBY CODE TO BE CONVERTED TO PYTHON
	# def create_ticket(payload)
	# 	jira_result = {}
	# 	RestClient::Request.new(
	# 		:method => :post,
	# 		:url => ENV['JIRA_API_URL'],
	# 		:user => ENV['JIRA_USER'],
	# 		:password => ENV['JIRA_API_TOKEN'],
	# 		:payload => payload.to_json,
	# 		:headers => { :accept => :json, :content_type => :json }
	# 	).execute do |response, request, result|
	# 		jira_result = JSON.parse(response.body) rescue {}
	# 		jira_result["summary"] = payload['fields']['summary']
	# 	end

	# 	jira_result
	# end

    
    def search(self, jql, profile):

        try:
            response = requests.get(
                url=profile['JIRA_API_URL'].replace("issue", "search"),
                auth=(profile['JIRA_USER'], profile['JIRA_API_TOKEN']),
                headers={'Content-Type': 'application/json'},
                params={'jql': jql},
                verify=False #TODO bot session that sets verify to either true or the CA_CERT if in ENV
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return { 'error': str(e) }

    def extract_info_html_table(self, jira_payload):
        base_url = "https://wesdigital.atlassian.net/browse/"
        # Start the HTML table with the header
        html_lines = ['<table>', '<tr><th>Status</th><th>Assignee</th><th>Ticket</th></tr>']

        for issue in jira_payload.get('issues', []):
            key = issue.get('key')
            summary = issue.get('fields', {}).get('summary', 'No Summary Available')
            status = issue.get('fields', {}).get('status', {}).get('name', 'No Status')
            
            # Safely get assignee name or use 'Unassigned'
            assignee_dict = issue.get('fields', {}).get('assignee', {})
            assignee = assignee_dict.get('displayName', 'Unassigned') if assignee_dict else 'Unassigned'
            
            issue_link = f"{base_url}{key}"

            # Each row in the table: Status - Assignee - Ticket Link
            html_line = f"<tr><td>{status}</td><td>{assignee}</td><td><a href='{issue_link}'>{key} {summary}</a></td></tr>"
            html_lines.append(html_line)

        html_lines.append('</table>')
        return "\n".join(html_lines)


    def extract_info_markdown_table(self, jira_payload, profile):
        base_url = "https://wesdigital.atlassian.net/browse/"
        markdown_lines = ["| Status | Assignee | Points | Ticket |", "| --- | --- | --- | --- |"]  # Table header

        for issue in jira_payload.get('issues', []):
            key = issue.get('key')
            summary = issue.get('fields', {}).get('summary', 'No Summary Available')
            status = issue.get('fields', {}).get('status', {}).get('name', 'No Status')
            
            # Safely get assignee name or use 'Unassigned'
            assignee_dict = issue.get('fields', {}).get('assignee', {})
            assignee = assignee_dict.get('displayName', 'Unassigned') if assignee_dict else 'Unassigned'
            
            story_points = issue.get('fields', {}).get(profile['JIRA_SIZE_FIELD'], 'N/A')
            
            # Extract reporter name
            reporter_dict = issue.get('fields', {}).get('reporter', {})
            reporter = reporter_dict.get('displayName', 'Unknown')

            issue_link = f"{base_url}{key}"

            # Each row in the table: Status - Assignee - [OP-12345 Ticket Name](Link to JIRA)
            markdown_line = f"| {status} | {assignee} | {story_points} | [{key} {summary}]({issue_link}) |"
            markdown_lines.append(markdown_line)

        return "\n".join(markdown_lines)

        ## TRELLO API CALL TO BE CONVERTED INTO JIRA THAT CAN TAKE JQL
            # Make a GET request to the API endpoint
            # try: 
            #     response = requests.get(url, params={'key': api_key, 'token': token, 'cards': 'open'}, verify=False)
            #     response.raise_for_status()

            #     if response.status_code == 200:
            #         payload['trello_lists'] = self.get_board(response.json(), payload['user_profile_bot_data']['trello_lists'])
            #         payload['chatml'].append({ 
            #             "role": "system", 
            #             "name": f"{self.bot_name}_supervisor", 
            #             "content": payload['trello_lists']
            #         })

            #         print(payload['trello_lists']) 

            # except RequestException as e:
            #     if e.response is not None: 
            #         if e.response.status_code == 403 or e.response.status_code == 401: 
            #             payload['draft']['body'] = f"Trello access denied.  Erasing your credentials so you can supply them again."
            #             payload['user_profile_bot_data']['trello_api_key'] = ""
            #             payload['user_profile_bot_data']['trello_token'] = ""
            #             payload['user_profile_bot_data']['trello_board_id'] = ""
            #             payload['user_profile_lists']['trello_lists'] = ""
            #         elif e.response.status_code == 404:
            #             payload['draft']['body'] = f"Trello not found.  Erasing your board_id so you can supply it again."
            #             payload['user_profile_bot_data']['trello_lists'] = ""
            #         else: 
            #             payload['draft']['body'] = f"We encounted a problem accessing Trello.  Status {e.response.status_code} e.response"
            #     else:
            #         payload['draft']['body'] = f"We encounted a problem accessing Trello.  {str(e)}"
              
        

    def get_chatml(self, payload, instruction):
        # TODO figure out the right about to put in the context window with out overflow 
        # I suspect all chatgpt helpers need to be in our chatgpt class, and probably shouldn't 
        # be steps in their own right
        result = [ item for item in payload['chatml'][-3:] ]
        result.append( 
            {
                "content": instruction, 
                "name": f'{self.bot_name}_supervisor',
                "role": "system"
            }
        )

        return result


if __name__ == "__main__":
    ChatGPTJira.main()
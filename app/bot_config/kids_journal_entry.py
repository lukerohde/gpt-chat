from bot_manager.bot_step import Step
from datetime import date
import json
import textwrap

class KidsJournalEntry(Step):
    
    async def process(self, payload):

        if not ('metadata' in payload):
            return payload 
        
        metadata = json.loads(payload['metadata'])
        
        journal_entry = f'''
        ```
        # {metadata['client']}'s Journal for {date.today().isoformat()}

        ## Grateful for
        {metadata['summary_for_child']['thankful_for'] or 'Not captured'}

        ## Looking forward to 
        {metadata['summary_for_child']['looking_forward_to'] or 'Not captured'}

        ## Concerns
        {metadata['summary_for_parent']['notes_of_concern'] or 'Not captured'}

        ## Advice for parents
        {metadata['summary_for_parent']['parenting_advice'] or 'None'}
        ```

        Let me know if I haven't got this right and I'll update it.  
        '''
        journal_entry = textwrap.dedent(journal_entry)

        payload['reply'] = {}
        payload['reply']['user'] = payload['messages'][-1]['recipient']
        payload['reply']['recipient'] = payload['messages'][-1]['user']
        payload['reply']['body'] = journal_entry
        payload['reply']['metadata'] = metadata
        
        return payload

if __name__ == "__main__":
    KidsJournalEntry.main()
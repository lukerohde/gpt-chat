import json
import os
import sys
from bot_config.steps.bedrock_llm import BedrockLLM
from itertools import groupby


class Anthropic(BedrockLLM):

    def payload(self, prompt):

        result = { 
            "messages": prompt['messages'], 
            "max_tokens": self.max_gen_len,
            "anthropic_version": self.config.get('anthropic_version', 'bedrock-2023-05-31'), 
            "temperature": self.temperature or 0.5,
            "top_p": self.top_p or 0.9,
            "system": prompt['system'],
            }
    
        return result
    
    def prompt(self, chatml):
        system_message = self.extract_system_prompt(chatml)
        conversation_messages = self.extract_conversation_messages(chatml) 
        combined = self.combine_consecutive_messages(conversation_messages)
        messages = [
            {
                "role": message['role'],
                "content": [
                    {
                        "type": "text",
                        "text": f"{message['content']}"
                    }
                ]
            }
            for message in combined
        ]

        result = {
            "messages": messages,
            "system": system_message,
        }

        return result
    
    def extract_system_prompt(self, chatml):
        # from the array of chat messages, pull out the system messages
        system_messages = [message['content'] for message in chatml if message['role'] == 'system']

        return "/n/n".join(system_messages)
    
    def extract_conversation_messages(self, chatml):
        # from the array of chat messages, pull out the user messages
        user_messages = [message for message in chatml if message['role'] in ('user', 'bot')]
        if user_messages[0]['role'] == 'bot':
            user_messages = user_messages[1:]

        return user_messages

    def combine_consecutive_messages(self, messages):
        combined_messages = []

        for sender, message_group in groupby(messages, key=lambda x: x['role']):
            combined_content = "\n\n".join(message['content'] for message in message_group)
            combined_messages.append({
                'role': sender,
                'content': combined_content,
            })

        return combined_messages
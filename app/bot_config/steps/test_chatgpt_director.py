import unittest
from unittest.mock import patch, AsyncMock
from bot_config.steps.chatgpt_director import ChatGPTDirector

class TestChatGPTDirector(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.config = {
            'capabilities': {
                'jira': {
                    'create': ['Can you create a jira ticket for...']
                }
            },
            'model': 'gpt-3.5-turbo',
            'prompt': "For each user request... {request_response_examples}"
        }

        self.name = "ChatGPTDirector"
        
        self.bot_name = "TestBot"

        self.director = ChatGPTDirector(self.bot_name, self.name, self.config)

        self.payload = {
            'chatml': [{'content': 'test message', 'name': 'user1', 'role': 'user'}],
            'notices': [],
            'draft': {'body': ''}
        }

    def test_can_process(self):
        self.assertTrue(self.director.can_process(self.payload))

        empty_payload = {'chatml': [], 'notices': [], 'draft': {'body': ''}}
        self.assertFalse(self.director.can_process(empty_payload))

    def test_get_instruction(self):
        instruction = self.director.get_instruction()
        self.assertIn('For each user request', instruction)
        self.assertIn('{"action": "create", "object": "jira"}', instruction)

    def test_get_chatml(self):
        instruction = "Sample instruction"
        updated_chatml = self.director.get_chatml(self.payload, instruction)
        self.assertEqual(len(updated_chatml), 2)  # Checks if only the last 3 chatml items + instruction are included
        self.assertIn('Sample instruction', updated_chatml[-1]['content'])

    @patch('bot_config.chatgpt.ChatGPT.ask', new_callable=AsyncMock)
    async def test_process_with_valid_response(self, mock_ask):
        mock_ask.return_value = {'reply': '{"action": "create", "object": "jira"}'}
        updated_payload = await self.director.process(self.payload)
        self.assertIn('I\'ve classified this as', updated_payload['draft']['body'])
        mock_ask.assert_awaited()

    @patch('bot_config.chatgpt.ChatGPT.ask', new_callable=AsyncMock)
    async def test_process_with_empty_response(self, mock_ask):
        mock_ask.return_value = {'reply': '{}'}
        updated_payload = await self.director.process(self.payload)
        self.assertIn('ChatGPTDirector could not match this request to a capability', updated_payload['notices'])

    @patch('bot_config.chatgpt.ChatGPT.ask', new_callable=AsyncMock)
    async def test_process_with_json_decode_error(self, mock_ask):
        mock_ask.return_value = {'reply': 'not a json'}
        updated_payload = await self.director.process(self.payload)
        self.assertIn('Failed to parse JSON', updated_payload['draft']['body'])

if __name__ == '__main__':
    unittest.main()

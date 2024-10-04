# tests/test_integration.py

import unittest
import asyncio
from main import process_file
from config import load_config, load_function_schema

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.config = load_config("config/test_config.json")
        self.function_schema = load_function_schema("config/test_function_schema.json")
        self.sample_file = "tests/sample.py"
        self.sample_code = """
def example_function(param1, param2):
    \"\"\"This function does something.\"\"\"
    return param1 + param2

class ExampleClass:
    \"\"\"An example class.\"\"\"
    
    def method_one(self):
        \"\"\"Method one.\"\"\"
        pass
    
    async def method_two(self):
        \"\"\"Async method two.\"\"\"
        pass
        """
        with open(self.sample_file, 'w', encoding='utf-8') as f:
            f.write(self.sample_code)
    
    def tearDown(self):
        import os
        if os.path.exists(self.sample_file):
            os.remove(self.sample_file)
    
    def test_process_file(self):
        loop = asyncio.get_event_loop()
        doc = loop.run_until_complete(process_file(self.sample_file, self.config, self.function_schema))
        self.assertIsNotNone(doc)
        self.assertIn("elements", doc)
        self.assertGreater(len(doc["elements"]), 0)

if __name__ == '__main__':
    unittest.main()

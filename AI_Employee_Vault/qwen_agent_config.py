"""
Qwen-Agent Configuration for Personal AI Employee
Connects qwen-agent framework with local Ollama models (FREE)
"""

from qwen_agent.llm import get_chat_model

# ===========================================
# OLLAMA LOCAL MODEL CONFIGURATION
# ===========================================
# This connects qwen-agent to your local Ollama server
# No API costs - runs completely free on your machine

llm_cfg = {
    'model': 'qwen2.5',  # Your local Ollama model name
    'model_server': 'http://localhost:11434/v1',  # Ollama OpenAI-compatible API
    'api_key': 'EMPTY',  # Ollama doesn't require authentication
}

# Initialize the LLM
llm = get_chat_model(llm_cfg)


# ===========================================
# TEST FUNCTION
# ===========================================
def test_llm(prompt: str = "Hello! I'm your AI employee assistant."):
    """Test the local LLM connection"""
    messages = [
        {'role': 'system', 'content': 'You are a helpful AI employee assistant.'},
        {'role': 'user', 'content': prompt}
    ]
    
    try:
        response = llm.chat(messages=messages)
        print(f"Response: {response}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Ollama is running: ollama serve")
        return None


if __name__ == '__main__':
    print("Testing Qwen-Agent with Ollama...")
    test_llm("What can you help me with?")

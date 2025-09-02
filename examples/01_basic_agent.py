#!/usr/bin/env python3
"""
Example 1: Basic Agent Loop with Ollama

This example demonstrates the fundamental concept of an AI agent:
1. Perceive: Receive input from the user
2. Think: Process the input using the LLM (Ollama)
3. Act: Generate a response
4. Learn: Update internal state

What you'll learn:
- Basic agent interaction loop
- Simple reasoning and response generation
- How agents perceive and process input
- Basic error handling and fallbacks

Prerequisites:
- Ollama installed and running
- Mistral model pulled: ollama pull mistral
"""

import sys
import os
import time

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from config.settings import get_config


class BasicAgent(BaseAgent):
    """
    A simple AI agent that demonstrates the basic perceive-think-act-learn loop.
    
    This agent:
    - Receives user input
    - Processes it through the LLM
    - Generates responses
    - Maintains conversation history
    """
    
    def __init__(self, model: str = None):
        """Initialize the basic agent."""
        super().__init__(model=model)
        print(f"🤖 Basic Agent initialized with model: {self.model}")
        print("💡 This agent demonstrates the core agent loop: Perceive → Think → Act → Learn")
        print()
    
    def run_interactive(self):
        """Run the agent in interactive mode."""
        print("🎯 Basic Agent is ready! Type 'quit' to exit.")
        print("=" * 50)
        
        while True:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye! Thanks for trying the Basic Agent.")
                    break
                
                if not user_input:
                    continue
                
                print(f"🤔 Agent is thinking...")
                
                # Run the agent loop
                start_time = time.time()
                result = self.run(user_input)
                end_time = time.time()
                
                # Display results
                print(f"\n🤖 Agent: ", end="")
                
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                elif "response" in result:
                    print(result["response"])
                else:
                    print("🤷 No response generated")
                
                # Show timing and stats
                response_time = end_time - start_time
                print(f"\n⏱️  Response time: {response_time:.2f} seconds")
                
                # Show agent stats
                stats = self.get_stats()
                print(f"📊 Tool calls: {stats['tool_calls']}, Conversations: {stats['conversation_length']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("🔄 Continuing...")
    
    def run_single_query(self, query: str):
        """Run the agent on a single query and return results."""
        print(f"🤔 Processing query: {query}")
        
        start_time = time.time()
        result = self.run(query)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"⏱️  Response time: {response_time:.2f} seconds")
        print(f"📊 Tool calls: {self.get_stats()['tool_calls']}")
        
        return result


def demonstrate_agent_capabilities():
    """Demonstrate various agent capabilities."""
    print("🚀 Demonstrating Basic Agent Capabilities")
    print("=" * 50)
    
    # Initialize agent
    agent = BasicAgent()
    
    # Test queries
    test_queries = [
        "Hello! How are you today?",
        "What is the capital of France?",
        "Can you explain what machine learning is?",
        "What's 15 + 27?",
        "Tell me a joke"
    ]
    
    print("\n🧪 Running test queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i} ---")
        result = agent.run_single_query(query)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        elif "response" in result:
            print(f"✅ Response: {result['response']}")
        else:
            print("🤷 No response generated")
        
        # Small delay between queries
        time.sleep(1)
    
    print(f"\n🎯 Final Stats:")
    stats = agent.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


def main():
    """Main function to run the example."""
    print("🧠 AI Agent Demonstration - Example 1: Basic Agent Loop")
    print("=" * 60)
    print()
    
    # Check configuration
    config = get_config()
    print(f"🔧 Configuration:")
    print(f"  Ollama URL: {config['ollama_base_url']}")
    print(f"  Default Model: {config['default_model']}")
    print(f"  Agent Timeout: {config['agent_timeout']} seconds")
    print()
    
    # Check if user wants to run tests or interactive mode
    print("Choose an option:")
    print("1. Run capability demonstration (test queries)")
    print("2. Interactive mode (chat with the agent)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                demonstrate_agent_capabilities()
                break
            elif choice == "2":
                agent = BasicAgent()
                agent.run_interactive()
                break
            elif choice == "3":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Please try again.")


if __name__ == "__main__":
    main()

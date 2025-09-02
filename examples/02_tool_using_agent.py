#!/usr/bin/env python3
"""
Example 2: Tool-Using Agent

This example demonstrates how AI agents can use tools/functions to accomplish tasks:
1. Perceive: Receive user request
2. Think: Decide which tools to use
3. Act: Execute tools and process results
4. Learn: Update state based on tool usage

What you'll learn:
- How agents integrate with external tools
- Tool selection and execution
- Processing tool results
- Multi-tool workflows

Prerequisites:
- Ollama installed and running
- Mistral model pulled: ollama pull mistral
"""

import sys
import os
import time
import json

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from tools.code_tools import analyze_code, format_code, lint_code
from tools.data_tools import query_data, analyze_data, transform_data
from tools.search_tools import search_knowledge, create_search_index
from config.settings import get_config


class ToolUsingAgent(BaseAgent):
    """
    An AI agent that can use various tools to accomplish tasks.
    
    This agent demonstrates:
    - Tool integration and selection
    - Multi-step task execution
    - Result processing and synthesis
    - Error handling for tool failures
    """
    
    def __init__(self, model: str = None):
        """Initialize the tool-using agent with available tools."""
        # Define available tools
        tools = [
            analyze_code,
            format_code,
            lint_code,
            query_data,
            analyze_data,
            transform_data,
            search_knowledge
        ]
        
        super().__init__(model=model, tools=tools)
        
        print(f"🛠️  Tool-Using Agent initialized with model: {self.model}")
        print(f"🔧 Available tools: {len(self.tools)}")
        for tool in self.tools:
            print(f"  - {tool.__name__}: {tool.__doc__.split('.')[0] if tool.__doc__ else 'No description'}")
        print()
        print("💡 This agent can use tools to analyze code, process data, and search knowledge bases.")
        print()
    
    def demonstrate_code_tools(self):
        """Demonstrate code analysis tools."""
        print("🔍 Demonstrating Code Analysis Tools")
        print("=" * 50)
        
        # Sample code for analysis
        sample_code = '''
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def process_data(data_list):
    result = []
    for item in data_list:
        if item > 0:
            result.append(item * 2)
    return result

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def add_item(self, item):
        self.data.append(item)
    
    def get_sum(self):
        return sum(self.data)
'''
        
        print("📝 Sample code to analyze:")
        print(sample_code)
        print()
        
        # Analyze the code
        print("🔍 Analyzing code...")
        analysis_result = analyze_code(sample_code, "python")
        
        if "error" not in analysis_result:
            print("✅ Code Analysis Results:")
            metrics = analysis_result.get("metrics", {})
            print(f"  📊 Lines of code: {metrics.get('code_lines', 'N/A')}")
            print(f"  🏗️  Classes: {metrics.get('classes', 'N/A')}")
            print(f"  ⚙️  Functions: {metrics.get('functions', 'N/A')}")
            print(f"  📦 Imports: {metrics.get('imports', 'N/A')}")
            print(f"  🔀 Complexity: {metrics.get('complexity', 'N/A')}")
            
            if analysis_result.get("issues"):
                print("  ⚠️  Issues found:")
                for issue in analysis_result["issues"][:3]:  # Show first 3 issues
                    print(f"    - {issue}")
            
            if analysis_result.get("suggestions"):
                print("  💡 Suggestions:")
                for suggestion in analysis_result["suggestions"][:3]:  # Show first 3 suggestions
                    print(f"    - {suggestion}")
        else:
            print(f"❌ Analysis failed: {analysis_result['error']}")
        
        print()
        
        # Lint the code
        print("🧹 Linting code...")
        lint_result = lint_code(sample_code, "python")
        
        if "error" not in lint_result:
            print("✅ Linting Results:")
            print(f"  📊 Total issues: {lint_result.get('total_issues', 0)}")
            print(f"  ⚠️  Warnings: {lint_result.get('total_warnings', 0)}")
            print(f"  🎯 Severity: {lint_result.get('severity', 'unknown')}")
        else:
            print(f"❌ Linting failed: {lint_result['error']}")
        
        print()
    
    def demonstrate_data_tools(self):
        """Demonstrate data manipulation tools."""
        print("📊 Demonstrating Data Tools")
        print("=" * 50)
        
        # Sample data
        sample_data = [1, 2, 3, 4, 5, "hello", "world", 6, 7, 8, 9, 10]
        sample_dict = {
            "users": ["Alice", "Bob", "Charlie"],
            "ages": [25, 30, 35],
            "scores": [85, 92, 78],
            "active": [True, True, False]
        }
        
        print("📝 Sample data:")
        print(f"  List: {sample_data}")
        print(f"  Dict: {sample_dict}")
        print()
        
        # Query the data
        print("🔍 Querying data...")
        queries = [
            "count items",
            "find numeric values",
            "first 5 items"
        ]
        
        for query in queries:
            print(f"  Query: '{query}'")
            result = query_data(sample_data, query)
            if "error" not in result:
                print(f"    Result: {result.get('result', 'N/A')}")
            else:
                print(f"    Error: {result['error']}")
        
        print()
        
        # Analyze the data
        print("📊 Analyzing data...")
        analysis_result = analyze_data(sample_data)
        
        if "error" not in analysis_result:
            print("✅ Data Analysis Results:")
            print(f"  📊 Total items: {analysis_result.get('length', 'N/A')}")
            print(f"  🏷️  Data types: {analysis_result.get('data_types', {})}")
            
            if analysis_result.get("patterns"):
                print("  🔍 Patterns found:")
                for pattern in analysis_result["patterns"][:3]:
                    print(f"    - {pattern}")
            
            if analysis_result.get("insights"):
                print("  💡 Insights:")
                for insight in analysis_result["insights"][:3]:
                    print(f"    - {insight}")
        else:
            print(f"❌ Analysis failed: {analysis_result['error']}")
        
        print()
        
        # Transform the data
        print("🔄 Transforming data...")
        transformations = [
            "filter numeric values",
            "sort ascending",
            "remove duplicates"
        ]
        
        for transformation in transformations:
            print(f"  Transformation: '{transformation}'")
            result = transform_data(sample_data, transformation)
            if "error" not in result:
                print(f"    Result: {result.get('transformed_data', 'N/A')}")
                print(f"    Changes: {result.get('changes_made', 'N/A')}")
            else:
                print(f"    Error: {result['error']}")
        
        print()
    
    def demonstrate_search_tools(self):
        """Demonstrate search and knowledge tools."""
        print("🔍 Demonstrating Search Tools")
        print("=" * 50)
        
        # Sample knowledge base
        knowledge_base = [
            {
                "title": "Python Basics",
                "content": "Python is a high-level programming language known for its simplicity and readability.",
                "tags": ["python", "programming", "basics"]
            },
            {
                "title": "Machine Learning",
                "content": "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed.",
                "tags": ["machine learning", "AI", "algorithms"]
            },
            {
                "title": "Data Science",
                "content": "Data science combines statistics, programming, and domain expertise to extract insights from data.",
                "tags": ["data science", "statistics", "analytics"]
            },
            {
                "title": "Web Development",
                "content": "Web development involves creating websites and web applications using various technologies.",
                "tags": ["web development", "frontend", "backend"]
            }
        ]
        
        print("📚 Sample knowledge base created with 4 items")
        print()
        
        # Search queries
        print("🔍 Testing search functionality...")
        search_queries = [
            "python",
            "machine learning",
            "web development",
            "statistics"
        ]
        
        for query in search_queries:
            print(f"  Search: '{query}'")
            result = search_knowledge(query, knowledge_base)
            
            if "error" not in result:
                print(f"    Results: {result.get('total_results', 0)}")
                if result.get("top_results"):
                    top_result = result["top_results"][0]
                    print(f"    Top result: {top_result['item']['title']}")
                    print(f"    Score: {top_result['score']:.2f}")
            else:
                print(f"    Error: {result['error']}")
        
        print()
        
        # Create search index
        print("🔧 Creating search index...")
        index_result = create_search_index(knowledge_base)
        
        if "error" not in index_result:
            print("✅ Search index created:")
            print(f"  📊 Total items: {index_result.get('total_items', 'N/A')}")
            print(f"  🔍 Indexed fields: {index_result.get('indexed_fields', [])}")
            print(f"  📝 Unique terms: {index_result.get('unique_terms', 'N/A')}")
        else:
            print(f"❌ Index creation failed: {index_result['error']}")
        
        print()
    
    def run_interactive(self):
        """Run the agent in interactive mode."""
        print("🎯 Tool-Using Agent is ready! Type 'quit' to exit.")
        print("Available commands:")
        print("  - 'demo code': Demonstrate code analysis tools")
        print("  - 'demo data': Demonstrate data manipulation tools")
        print("  - 'demo search': Demonstrate search tools")
        print("  - 'analyze <code>': Analyze some code")
        print("  - 'query <data> <query>': Query data")
        print("  - 'search <query>': Search knowledge base")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye! Thanks for trying the Tool-Using Agent.")
                    break
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == 'demo code':
                    self.demonstrate_code_tools()
                    continue
                elif user_input.lower() == 'demo data':
                    self.demonstrate_data_tools()
                    continue
                elif user_input.lower() == 'demo search':
                    self.demonstrate_search_tools()
                    continue
                
                # Handle tool-specific commands
                if user_input.lower().startswith('analyze '):
                    code = user_input[8:]  # Remove 'analyze ' prefix
                    print(f"🔍 Analyzing code: {code[:50]}...")
                    result = analyze_code(code, "python")
                    if "error" not in result:
                        print("✅ Analysis complete!")
                        print(f"  Functions: {result.get('metrics', {}).get('functions', 'N/A')}")
                        print(f"  Lines: {result.get('metrics', {}).get('code_lines', 'N/A')}")
                    else:
                        print(f"❌ Analysis failed: {result['error']}")
                    continue
                
                if user_input.lower().startswith('query '):
                    parts = user_input[6:].split(' ', 1)  # Remove 'query ' prefix
                    if len(parts) == 2:
                        data_str, query = parts
                        try:
                            # Try to parse as list or dict
                            data = eval(data_str)
                            print(f"🔍 Querying data with: '{query}'")
                            result = query_data(data, query)
                            if "error" not in result:
                                print(f"✅ Result: {result.get('result', 'N/A')}")
                            else:
                                print(f"❌ Query failed: {result['error']}")
                        except:
                            print("❌ Invalid data format. Use Python list or dict syntax.")
                    else:
                        print("❌ Usage: query <data> <query>")
                    continue
                
                if user_input.lower().startswith('search '):
                    query = user_input[7:]  # Remove 'search ' prefix
                    print(f"🔍 Searching for: '{query}'")
                    
                    # Create a simple knowledge base for demonstration
                    kb = [
                        {"title": "AI Agents", "content": "AI agents are autonomous systems that can perceive, think, and act.", "tags": ["AI", "agents"]},
                        {"title": "Machine Learning", "content": "Machine learning enables computers to learn from data.", "tags": ["ML", "AI"]}
                    ]
                    
                    result = search_knowledge(query, kb)
                    if "error" not in result:
                        print(f"✅ Found {result.get('total_results', 0)} results")
                        if result.get("top_results"):
                            top = result["top_results"][0]
                            print(f"  Top result: {top['item']['title']}")
                    else:
                        print(f"❌ Search failed: {result['error']}")
                    continue
                
                # Default: use the agent's reasoning
                print(f"🤔 Agent is thinking...")
                
                start_time = time.time()
                result = self.run(user_input)
                end_time = time.time()
                
                print(f"\n🤖 Agent: ", end="")
                
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                elif "response" in result:
                    print(result["response"])
                else:
                    print("🤷 No response generated")
                
                response_time = end_time - start_time
                print(f"\n⏱️  Response time: {response_time:.2f} seconds")
                
                stats = self.get_stats()
                print(f"📊 Tool calls: {stats['tool_calls']}, Conversations: {stats['conversation_length']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("🔄 Continuing...")


def main():
    """Main function to run the example."""
    print("🧠 AI Agent Demonstration - Example 2: Tool-Using Agent")
    print("=" * 60)
    print()
    
    # Check configuration
    config = get_config()
    print(f"🔧 Configuration:")
    print(f"  Ollama URL: {config['ollama_base_url']}")
    print(f"  Default Model: {config['default_model']}")
    print(f"  Agent Timeout: {config['agent_timeout']} seconds")
    print()
    
    # Check if user wants to run demos or interactive mode
    print("Choose an option:")
    print("1. Run all tool demonstrations")
    print("2. Interactive mode (use tools manually)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                agent = ToolUsingAgent()
                print("\n" + "="*60)
                agent.demonstrate_code_tools()
                print("\n" + "="*60)
                agent.demonstrate_data_tools()
                print("\n" + "="*60)
                agent.demonstrate_search_tools()
                print("\n🎯 All demonstrations completed!")
                break
            elif choice == "2":
                agent = ToolUsingAgent()
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

#!/usr/bin/env python3
"""
Example 6: Knowledge Search Agent (Simplified)

This example demonstrates an AI agent specialized for knowledge search:
1. Perceive: Receive search queries and knowledge base
2. Think: Understand query intent and select search strategy
3. Act: Execute searches and synthesize results
4. Learn: Remember search patterns and improve results

What you'll learn:
- Knowledge base management and search
- Query understanding and optimization
- Result ranking and relevance scoring
- Search index creation and optimization
- Semantic search and similarity matching

Prerequisites:
- Ollama installed and running
- Mistral model pulled: ollama pull mistral
"""

import sys
import os
import time
import json
import random

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from agents.memory import Memory
from tools.search_tools import search_knowledge, create_search_index, search_with_index, semantic_search
from config.settings import get_config


class KnowledgeSearchAgent(BaseAgent):
    """
    An AI agent specialized for knowledge base search and information retrieval.
    
    This agent demonstrates:
    - Knowledge base management
    - Advanced search strategies
    - Result ranking and relevance
    - Search optimization and learning
    - Semantic understanding
    """
    
    def __init__(self, model: str = None):
        """Initialize the knowledge search agent."""
        # Define search tools
        tools = [
            search_knowledge,
            create_search_index,
            search_with_index,
            semantic_search
        ]
        
        super().__init__(model=model, tools=tools)
        
        # Initialize memory for search history and knowledge
        self.memory = Memory()
        
        # Sample knowledge base
        self.knowledge_base = self._create_sample_knowledge_base()
        
        # Search index
        self.search_index = None
        
        print(f"🔍 Knowledge Search Agent initialized with model: {self.model}")
        print(f"🔧 Available tools: {len(self.tools)}")
        print(f"💾 Memory system: {self.memory.get_stats()['total_items']} items")
        print(f"📚 Knowledge base: {len(self.knowledge_base)} items")
        print()
        print("💡 This agent specializes in knowledge search, retrieval, and information synthesis.")
        print()
        
        # Create search index
        self._create_search_index()
    
    def _create_sample_knowledge_base(self):
        """Create a sample knowledge base for demonstration."""
        return [
            {
                "title": "AI Agents Fundamentals",
                "content": "AI agents are autonomous systems that can perceive their environment, reason about what actions to take, and act to achieve goals. They follow the perceive-think-act-learn cycle and can use tools, maintain memory, and plan complex tasks.",
                "tags": ["AI", "agents", "fundamentals", "autonomy"],
                "category": "AI Theory",
                "difficulty": "beginner",
                "created_at": "2024-01-15"
            },
            {
                "title": "Machine Learning Basics",
                "content": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. It includes supervised learning, unsupervised learning, and reinforcement learning approaches.",
                "tags": ["machine learning", "AI", "data", "algorithms"],
                "category": "Machine Learning",
                "difficulty": "beginner",
                "created_at": "2024-01-10"
            },
            {
                "title": "Python Programming",
                "content": "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used in data science, web development, AI, and automation. Key features include dynamic typing, garbage collection, and extensive libraries.",
                "tags": ["python", "programming", "language", "development"],
                "category": "Programming",
                "difficulty": "beginner",
                "created_at": "2024-01-05"
            },
            {
                "title": "Web Development",
                "content": "Web development involves creating websites and web applications. It includes frontend development (HTML, CSS, JavaScript), backend development (server-side languages, databases), and full-stack development combining both.",
                "tags": ["web development", "frontend", "backend", "full-stack"],
                "category": "Web Development",
                "difficulty": "intermediate",
                "created_at": "2024-01-01"
            }
        ]
    
    def _create_search_index(self):
        """Create a search index for the knowledge base."""
        try:
            self.search_index = create_search_index(self.knowledge_base)
            print("✅ Search index created successfully")
        except Exception as e:
            print(f"⚠️  Failed to create search index: {e}")
            self.search_index = None
    
    def search_knowledge(self, query: str, search_type: str = "standard"):
        """Search the knowledge base using the specified search strategy."""
        start_time = time.time()
        
        try:
            if search_type == "indexed" and self.search_index:
                results = search_with_index(query, self.search_index, self.knowledge_base)
            elif search_type == "semantic":
                results = semantic_search(query, self.knowledge_base)
            else:
                results = search_knowledge(query, self.knowledge_base)
            
            # Store search results in memory
            search_result = {
                "query": query,
                "search_type": search_type,
                "results_count": len(results.get("results", [])) if isinstance(results, dict) else 0,
                "search_time": time.time() - start_time,
                "timestamp": time.time()
            }
            
            self.memory.store(
                content=search_result,
                item_type="search_results",
                importance=0.7
            )
            
            return results
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return {"error": str(e)}
    
    def get_search_suggestions(self, query: str):
        """Get search suggestions based on query history and patterns."""
        # Retrieve recent searches
        recent_searches = self.memory.retrieve(
            item_type="search_results",
            limit=5
        )
        
        suggestions = []
        if recent_searches:
            # Simple suggestion logic based on recent searches
            for item in recent_searches:
                recent_query = item.content.get("query", "")
                if query.lower() in recent_query.lower():
                    suggestions.append(f"Related: {recent_query}")
        
        # Add some default suggestions
        if not suggestions:
            suggestions = [
                f"Try searching for: {query} basics",
                f"Related topic: {query} examples",
                f"Advanced: {query} advanced concepts"
            ]
        
        return suggestions[:5]
    
    def demonstrate_search_capabilities(self):
        """Demonstrate basic search capabilities."""
        print("🔍 Demonstrating Search Capabilities")
        print("=" * 60)
        
        # Test different search types
        test_queries = ["AI", "python", "machine learning"]
        
        for query in test_queries:
            print(f"\n🔍 Searching for: '{query}'")
            
            # Standard search
            results = self.search_knowledge(query, "standard")
            if isinstance(results, dict) and "error" not in results:
                result_count = results.get("total_results", 0)
                print(f"  📊 Standard search: {result_count} results")
                top_results = results.get("top_results", [])
                if top_results:
                    top_item = top_results[0].get("item", {})
                    print(f"    Top result: {top_item.get('title', 'Unknown')}")
            else:
                print(f"  ❌ Standard search failed: {results.get('error', 'Unknown error')}")
            
            # Indexed search
            if self.search_index:
                results = self.search_knowledge(query, "indexed")
                if isinstance(results, dict) and "error" not in results:
                    result_count = results.get("total_results", 0)
                    print(f"  🔍 Indexed search: {result_count} results")
                else:
                    print(f"  ❌ Indexed search failed: {results.get('error', 'Unknown error')}")
            
            # Semantic search
            results = self.search_knowledge(query, "semantic")
            if isinstance(results, dict) and "error" not in results:
                result_count = results.get("total_results", 0)
                print(f"  🧠 Semantic search: {result_count} results")
            else:
                print(f"  ❌ Semantic search failed: {results.get('error', 'Unknown error')}")
        
        print()
    
    def demonstrate_advanced_search(self):
        """Demonstrate advanced search with filters and optimization."""
        print("🚀 Demonstrating Advanced Search")
        print("=" * 60)
        
        # Create a more complex query
        complex_query = "AI programming fundamentals"
        print(f"🔍 Complex query: '{complex_query}'")
        
        # Search with different strategies
        strategies = ["standard", "indexed", "semantic"]
        
        for strategy in strategies:
            print(f"\n📊 Testing {strategy} strategy:")
            start_time = time.time()
            
            results = self.search_knowledge(complex_query, strategy)
            
            if isinstance(results, dict) and "error" not in results:
                search_time = time.time() - start_time
                result_count = results.get("total_results", 0)
                print(f"  ✅ Results: {result_count} items found")
                print(f"  ⏱️  Search time: {search_time:.3f}s")
                
                # Show top results
                top_results = results.get("top_results", [])
                for i, result in enumerate(top_results[:3]):
                    item = result.get("item", {})
                    print(f"    {i+1}. {item.get('title', 'Unknown')}")
                    print(f"       Category: {item.get('category', 'Unknown')}")
                    print(f"       Difficulty: {item.get('difficulty', 'Unknown')}")
            else:
                print(f"  ❌ Search failed: {results.get('error', 'Unknown error')}")
        
        print()
    
    def demonstrate_knowledge_management(self):
        """Demonstrate knowledge base management capabilities."""
        print("📚 Demonstrating Knowledge Base Management")
        print("=" * 60)
        
        # Show knowledge base statistics
        print("📊 Knowledge Base Statistics:")
        print(f"  📝 Total items: {len(self.knowledge_base)}")
        
        # Category distribution
        categories = {}
        difficulties = {}
        tags = []
        
        for item in self.knowledge_base:
            category = item.get("category", "Unknown")
            difficulty = item.get("difficulty", "Unknown")
            
            categories[category] = categories.get(category, 0) + 1
            difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
            tags.extend(item.get("tags", []))
        
        print(f"  🏷️  Categories: {len(categories)}")
        for category, count in categories.items():
            print(f"    - {category}: {count} items")
        
        print(f"  📈 Difficulties: {len(difficulties)}")
        for difficulty, count in difficulties.items():
            print(f"    - {difficulty}: {count} items")
        
        print(f"  🏷️  Unique tags: {len(set(tags))}")
        if tags:
            sample_tags = random.sample(list(set(tags)), min(10, len(set(tags))))
            print(f"    Sample tags: {', '.join(sample_tags)}")
        else:
            print("    Sample tags: None")
        
        print()
        
        # Show search index information
        if self.search_index and "error" not in self.search_index:
            print("🔧 Search Index Information:")
            print(f"  📝 Indexed fields: {self.search_index.get('indexed_fields', [])}")
            print(f"  🔍 Unique terms: {self.search_index.get('unique_terms', 0)}")
            print(f"  📊 Field weights: {self.search_index.get('field_weights', {})}")
        else:
            print("⚠️  Search index not available")
        
        print()
    
    def demonstrate_search_learning(self):
        """Demonstrate how the agent learns from search patterns."""
        print("🧠 Demonstrating Search Learning")
        print("=" * 60)
        
        # Perform several searches to build history
        test_searches = [
            "python programming",
            "machine learning algorithms",
            "web development frameworks",
            "database design principles",
            "cloud computing services"
        ]
        
        print("📝 Building search history...")
        for query in test_searches:
            self.search_knowledge(query, "standard")
            time.sleep(0.1)  # Small delay
        
        print("✅ Search history built")
        print()
        
        # Show search suggestions
        print("💡 Search Suggestions for 'AI':")
        suggestions = self.get_search_suggestions("AI")
        for suggestion in suggestions:
            print(f"  {suggestion}")
        
        print()
        
        # Show search patterns
        print("📊 Search Pattern Analysis:")
        search_history = self.memory.retrieve(
            item_type="search_results",
            limit=10
        )
        
        if search_history:
            print(f"  📝 Recent searches: {len(search_history)}")
            
            # Analyze search types
            search_types = {}
            for item in search_history:
                search_type = item.content.get("search_type", "unknown")
                search_types[search_type] = search_types.get(search_type, 0) + 1
            
            print("  🔍 Search type distribution:")
            for search_type, count in search_types.items():
                print(f"    - {search_type}: {search_type}")
            
            # Show average search time
            search_times = [
                item.content.get("search_time", 0) 
                for item in search_history 
                if item.content.get("search_time")
            ]
            
            if search_times:
                avg_time = sum(search_times) / len(search_times)
                print(f"  ⏱️  Average search time: {avg_time:.3f}s")
        else:
            print("  📝 No search history available")
        
        print()
    
    def run_interactive(self):
        """Run the agent in interactive mode."""
        print("🎯 Knowledge Search Agent is ready! Type 'quit' to exit.")
        print("Available commands:")
        print("  - 'demo search': Demonstrate search capabilities")
        print("  - 'demo advanced': Demonstrate advanced search")
        print("  - 'demo knowledge': Demonstrate knowledge management")
        print("  - 'demo learning': Demonstrate search learning")
        print("  - 'search <query>': Search knowledge base")
        print("  - 'advanced <query> [filters]': Advanced search with filters")
        print("  - 'suggest <query>': Get search suggestions")
        print("  - 'info': Show knowledge base information")
        print("=" * 80)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'demo search':
                    self.demonstrate_search_capabilities()
                elif user_input.lower() == 'demo advanced':
                    self.demonstrate_advanced_search()
                elif user_input.lower() == 'demo knowledge':
                    self.demonstrate_knowledge_management()
                elif user_input.lower() == 'demo learning':
                    self.demonstrate_search_learning()
                elif user_input.lower().startswith('search '):
                    query = user_input[7:].strip()
                    print(f"🔍 Searching for: {query}")
                    results = self.search_knowledge(query)
                    if isinstance(results, dict) and "error" not in results:
                        result_count = results.get("total_results", 0)
                        print(f"📊 Found {result_count} results:")
                        top_results = results.get("top_results", [])
                        for i, result in enumerate(top_results[:5]):
                            item = result.get("item", {})
                            print(f"  {i+1}. {item.get('title', 'Unknown')}")
                    else:
                        print(f"❌ Search failed: {results.get('error', 'Unknown error')}")
                elif user_input.lower().startswith('advanced '):
                    parts = user_input[9:].split()
                    if len(parts) >= 1:
                        query = parts[0]
                        filters = parts[1:] if len(parts) > 1 else []
                        print(f"🚀 Advanced search for: {query} with filters: {filters}")
                        # This would implement advanced filtering logic
                        results = self.search_knowledge(query, "semantic")
                        if isinstance(results, list):
                            print(f"📊 Found {len(results)} results")
                        else:
                            print(f"❌ Search failed: {results.get('error', 'Unknown error')}")
                    else:
                        print("❌ Please provide a search query")
                elif user_input.lower().startswith('suggest '):
                    query = user_input[8:].strip()
                    print(f"💡 Search suggestions for: {query}")
                    suggestions = self.get_search_suggestions(query)
                    for suggestion in suggestions:
                        print(f"  - {suggestion}")
                elif user_input.lower() == 'info':
                    print("📚 Knowledge Base Information:")
                    print(f"  📝 Total items: {len(self.knowledge_base)}")
                    print(f"  💾 Memory items: {self.memory.get_stats()['total_items']}")
                    if self.search_index:
                        print(f"  🔍 Search index: Available")
                    else:
                        print(f"  🔍 Search index: Not available")
                else:
                    print("❓ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("🔄 Please try again.")
    
    def run_demo(self):
        """Run all demonstrations."""
        print("🚀 Running Knowledge Search Agent Demonstrations")
        print("=" * 80)
        
        # Run all demonstrations
        self.demonstrate_search_capabilities()
        self.demonstrate_advanced_search()
        self.demonstrate_knowledge_management()
        self.demonstrate_search_learning()
        
        print("🎯 All demonstrations completed!")
        print("\n💡 How the agent used search and knowledge management:")
        print(f"  📝 Performed searches across {len(self.knowledge_base)} knowledge items")
        print(f"  💾 Stored {self.memory.get_stats()['total_items']} memory items")
        print(f"  🔍 Created and used search index: {'Yes' if self.search_index else 'No'}")
        print(f"  🧠 Generated search suggestions and analyzed patterns")


def main():
    """Main function to run the knowledge search agent."""
    print("🧠 AI Agent Demonstration - Example 6: Knowledge Search Agent")
    print("=" * 80)
    
    # Show configuration
    config = get_config()
    print("🔧 Configuration:")
    print(f"  Ollama URL: {config['ollama_base_url']}")
    print(f"  Default Model: {config['default_model']}")
    print(f"  Agent Timeout: {config['agent_timeout']} seconds")
    print(f"  Memory Max Size: {config['memory_max_size']}")
    print()
    
    while True:
        try:
            print("Choose an option:")
            print("1. Run capability demonstration (test all features)")
            print("2. Interactive mode (use the agent manually)")
            print("3. Exit")
            print()
            
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == "1":
                agent = KnowledgeSearchAgent()
                agent.run_demo()
                break
            elif choice == "2":
                agent = KnowledgeSearchAgent()
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

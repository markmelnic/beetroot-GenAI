#!/usr/bin/env python3
"""
Example 6: Knowledge Search Agent

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
                "content": "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used in data science, web development, AI, and automation. Python emphasizes code readability and supports multiple programming paradigms.",
                "tags": ["python", "programming", "language", "development"],
                "category": "Programming",
                "difficulty": "beginner",
                "created_at": "2024-01-05"
            },
            {
                "title": "Data Analysis Techniques",
                "content": "Data analysis involves examining, cleaning, transforming, and modeling data to discover useful information and support decision-making. Techniques include statistical analysis, data mining, and visualization.",
                "tags": ["data analysis", "statistics", "visualization", "insights"],
                "category": "Data Science",
                "difficulty": "intermediate",
                "created_at": "2024-01-12"
            },
            {
                "title": "Web Development",
                "content": "Web development encompasses creating websites and web applications. It includes frontend development (HTML, CSS, JavaScript) and backend development (server-side programming, databases, APIs).",
                "tags": ["web development", "frontend", "backend", "programming"],
                "category": "Web Development",
                "difficulty": "intermediate",
                "created_at": "2024-01-08"
            },
            {
                "title": "Database Design",
                "content": "Database design involves creating efficient database schemas that support data integrity, performance, and scalability. It includes normalization, indexing, and relationship modeling.",
                "tags": ["database", "design", "SQL", "normalization"],
                "category": "Database",
                "difficulty": "intermediate",
                "created_at": "2024-01-14"
            },
            {
                "title": "Cybersecurity Fundamentals",
                "content": "Cybersecurity focuses on protecting computer systems, networks, and data from digital attacks. It includes threat modeling, vulnerability assessment, and security controls implementation.",
                "tags": ["cybersecurity", "security", "threats", "protection"],
                "category": "Security",
                "difficulty": "intermediate",
                "created_at": "2024-01-16"
            },
            {
                "title": "Cloud Computing",
                "content": "Cloud computing provides on-demand access to computing resources over the internet. It includes Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS).",
                "tags": ["cloud computing", "AWS", "Azure", "infrastructure"],
                "category": "Cloud",
                "difficulty": "intermediate",
                "created_at": "2024-01-11"
            },
            {
                "title": "DevOps Practices",
                "content": "DevOps combines software development and IT operations to shorten development cycles and improve software quality. It includes continuous integration, continuous deployment, and infrastructure as code.",
                "tags": ["devops", "CI/CD", "automation", "deployment"],
                "category": "DevOps",
                "difficulty": "advanced",
                "created_at": "2024-01-13"
            },
            {
                "title": "Artificial Intelligence Ethics",
                "content": "AI ethics addresses the moral implications of artificial intelligence systems. It includes fairness, transparency, accountability, and the impact of AI on society and human rights.",
                "tags": ["AI ethics", "fairness", "transparency", "society"],
                "category": "AI Theory",
                "difficulty": "advanced",
                "created_at": "2024-01-17"
            }
        ]
    
    def _create_search_index(self):
        """Create a search index for the knowledge base."""
        print("🔧 Creating search index...")
        
        try:
            self.search_index = create_search_index(
                self.knowledge_base,
                ["title", "content", "tags", "category"]
            )
            
            if "error" not in self.search_index:
                print(f"✅ Search index created with {self.search_index.get('unique_terms', 0)} unique terms")
            else:
                print(f"⚠️  Search index creation failed: {self.search_index['error']}")
                self.search_index = None
                
        except Exception as e:
            print(f"❌ Search index creation failed: {e}")
            self.search_index = None
    
    def search_knowledge(self, query: str, search_type: str = "standard") -> dict:
        """
        Search the knowledge base using different strategies.
        
        Args:
            query: Search query
            search_type: Type of search to perform
            
        Returns:
            Search results and metadata
        """
        print(f"🔍 Searching knowledge base for: '{query}' (type: {search_type})")
        
        # Store the search query in memory
        memory_id = self.memory.store(
            content={"query": query, "search_type": search_type, "timestamp": time.time()},
            item_type="search_query",
            importance=0.7
        )
        
        start_time = time.time()
        
        try:
            if search_type == "standard":
                # Use standard search
                results = search_knowledge(query, self.knowledge_base)
            elif search_type == "indexed" and self.search_index:
                # Use indexed search
                results = search_with_index(query, self.search_index, self.knowledge_base)
            elif search_type == "semantic":
                # Use semantic search
                results = semantic_search(query, self.knowledge_base, similarity_threshold=0.3)
            else:
                # Fallback to standard search
                results = search_knowledge(query, self.knowledge_base)
            
            end_time = time.time()
            
            # Enhance results with metadata
            enhanced_results = {
                "query": query,
                "search_type": search_type,
                "results": results,
                "search_time": end_time - start_time,
                "query_id": memory_id
            }
            
            # Store search results in memory
            self.memory.store(
                content=enhanced_results,
                item_type="search_results",
                importance=0.8,
                metadata={
                    "query_id": memory_id,
                    "search_type": search_type,
                    "result_count": results.get("total_results", 0),
                    "search_time": enhanced_results["search_time"]
                }
            )
            
            return enhanced_results
            
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}
    
    def advanced_search(self, query: str, filters: dict = None) -> dict:
        """
        Perform advanced search with filters and options.
        
        Args:
            query: Search query
            filters: Dictionary of filters to apply
            
        Returns:
            Filtered search results
        """
        print(f"🔍 Advanced search for: '{query}' with filters: {filters}")
        
        # Start with standard search
        base_results = self.search_knowledge(query, "standard")
        
        if "error" in base_results:
            return base_results
        
        # Apply filters
        filtered_results = self._apply_filters(base_results["results"], filters)
        
        # Store advanced search in memory
        self.memory.store(
            content={"query": query, "filters": filters, "results": filtered_results},
            item_type="advanced_search",
            importance=0.8,
            metadata={"timestamp": time.time()}
        )
        
        return {
            "query": query,
            "filters": filters,
            "results": filtered_results,
            "original_count": base_results["results"].get("total_results", 0),
            "filtered_count": len(filtered_results.get("results", []))
        }
    
    def _apply_filters(self, search_results: dict, filters: dict) -> dict:
        """Apply filters to search results."""
        if not filters:
            return search_results
        
        results = search_results.get("results", [])
        filtered_results = []
        
        for result in results:
            item = result.get("item", {})
            
            # Apply category filter
            if "category" in filters and item.get("category") != filters["category"]:
                continue
            
            # Apply difficulty filter
            if "difficulty" in filters and item.get("difficulty") != filters["difficulty"]:
                continue
            
            # Apply tag filter
            if "tags" in filters:
                required_tags = filters["tags"]
                item_tags = item.get("tags", [])
                if not all(tag in item_tags for tag in required_tags):
                    continue
            
            # Apply date filter
            if "date_after" in filters:
                try:
                    item_date = item.get("created_at", "")
                    if item_date < filters["date_after"]:
                        continue
                except:
                    pass
            
            filtered_results.append(result)
        
        return {
            "query": search_results.get("query", ""),
            "results": filtered_results,
            "total_results": len(filtered_results),
            "filters_applied": filters
        }
    
    def get_search_suggestions(self, query: str) -> list:
        """Get search suggestions based on the query."""
        suggestions = []
        
        # Get search history
        history = self.memory.retrieve(
            query=query,
            item_type="search_results",
            limit=5
        )
        
        if history:
            suggestions.append("Recent searches:")
            for item in history[:3]:
                suggestions.append(f"  - {item.content.get('query', 'Unknown')}")
        
        # Get related knowledge items
        related_items = self.memory.retrieve(
            query=query,
            item_type="search_results",
            limit=3
        )
        
        if related_items:
            suggestions.append("Related topics:")
            for item in related_items:
                results = item.content.get("results", {})
                if results.get("top_results"):
                    top_result = results["top_results"][0]
                    suggestions.append(f"  - {top_result['item']['title']}")
        
        # Get category suggestions
        categories = set(item.get("category") for item in self.knowledge_base)
        suggestions.append("Available categories:")
        for category in list(categories)[:5]:
            suggestions.append(f"  - {category}")
        
        return suggestions
    
    def demonstrate_search_capabilities(self):
        """Demonstrate search capabilities."""
        print("🔍 Demonstrating Search Capabilities")
        print("=" * 60)
        
        # Test different search types
        test_queries = [
            "AI agents",
            "machine learning",
            "python programming",
            "web development",
            "cybersecurity"
        ]
        
        search_types = ["standard", "indexed", "semantic"]
        
        for query in test_queries:
            print(f"\n📝 Testing query: '{query}'")
            
            for search_type in search_types:
                print(f"  🔍 {search_type.title()} search:")
                result = self.search_knowledge(query, search_type)
                
                if "error" not in result:
                    results = result["results"]
                    print(f"    ✅ Found {results.get('total_results', 0)} results")
                    print(f"    ⏱️  Time: {result['search_time']:.3f}s")
                    
                    if results.get("top_results"):
                        top_result = results["top_results"][0]
                        print(f"    🏆 Top result: {top_result['item']['title']}")
                        print(f"    📊 Score: {top_result.get('score', 'N/A')}")
                else:
                    print(f"    ❌ Search failed: {result['error']}")
        
        print()
    
    def demonstrate_advanced_search(self):
        """Demonstrate advanced search with filters."""
        print("🔍 Demonstrating Advanced Search with Filters")
        print("=" * 60)
        
        # Test advanced searches
        advanced_searches = [
            {
                "query": "programming",
                "filters": {"category": "Programming", "difficulty": "beginner"}
            },
            {
                "query": "AI",
                "filters": {"difficulty": "advanced"}
            },
            {
                "query": "development",
                "filters": {"tags": ["programming"]}
            }
        ]
        
        for search_config in advanced_searches:
            query = search_config["query"]
            filters = search_config["filters"]
            
            print(f"\n🔍 Advanced search: '{query}' with filters: {filters}")
            result = self.advanced_search(query, filters)
            
            if "error" not in result:
                print(f"  ✅ Found {result['filtered_count']} results (from {result['original_count']} total)")
                
                results = result["results"]
                if results.get("results"):
                    top_result = results["results"][0]
                    print(f"  🏆 Top result: {top_result['item']['title']}")
                    print(f"  📊 Score: {top_result.get('score', 'N/A')}")
            else:
                print(f"  ❌ Search failed: {result['error']}")
        
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
                print(f"    - {search_type}: {count}")
            
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
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye! Thanks for trying the Knowledge Search Agent.")
                    break
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == 'demo search':
                    self.demonstrate_search_capabilities()
                    continue
                elif user_input.lower() == 'demo advanced':
                    self.demonstrate_advanced_search()
                    continue
                elif user_input.lower() == 'demo knowledge':
                    self.demonstrate_knowledge_management()
                    continue
                elif user_input.lower() == 'demo learning':
                    self.demonstrate_search_learning()
                    continue
                elif user_input.lower() == 'info':
                    self.demonstrate_knowledge_management()
                    continue
                
                # Handle search commands
                if user_input.lower().startswith('search '):
                    query = user_input[7:]  # Remove 'search ' prefix
                    result = self.search_knowledge(query, "standard")
                    
                    if "error" not in result:
                        results = result["results"]
                        print(f"✅ Found {results.get('total_results', 0)} results")
                        
                        if results.get("top_results"):
                            for i, item in enumerate(results["top_results"][:3], 1):
                                print(f"  {i}. {item['item']['title']}")
                                print(f"     Score: {item.get('score', 'N/A'):.2f}")
                                print(f"     Category: {item['item'].get('category', 'N/A')}")
                    else:
                        print(f"❌ Search failed: {result['error']}")
                    continue
                
                # Handle advanced search commands
                if user_input.lower().startswith('advanced '):
                    parts = user_input[9:].split(' ', 1)  # Remove 'advanced ' prefix
                    if len(parts) == 2:
                        query, filters_str = parts
                        try:
                            filters = json.loads(filters_str)
                            result = self.advanced_search(query, filters)
                            
                            if "error" not in result:
                                print(f"✅ Advanced search completed")
                                print(f"📊 Found {result['filtered_count']} results (from {result['original_count']} total)")
                                
                                results = result["results"]
                                if results.get("results"):
                                    top_result = results["results"][0]
                                    print(f"🏆 Top result: {top_result['item']['title']}")
                            else:
                                print(f"❌ Advanced search failed: {result['error']}")
                        except json.JSONDecodeError:
                            print("❌ Invalid filter format. Use JSON syntax: {'category': 'Programming'}")
                    else:
                        print("❌ Usage: advanced <query> <filters>")
                    continue
                
                # Handle suggestion commands
                if user_input.lower().startswith('suggest '):
                    query = user_input[8:]  # Remove 'suggest ' prefix
                    suggestions = self.get_search_suggestions(query)
                    
                    print(f"💡 Search suggestions for '{query}':")
                    for suggestion in suggestions:
                        print(f"  {suggestion}")
                    continue
                
                # Default: treat as a search query
                print(f"🔍 Searching for: '{user_input}'")
                result = self.search_knowledge(user_input, "standard")
                
                if "error" not in result:
                    results = result["results"]
                    print(f"✅ Found {results.get('total_results', 0)} results")
                    
                    if results.get("top_results"):
                        for i, item in enumerate(results["top_results"][:3], 1):
                            print(f"  {i}. {item['item']['title']}")
                            print(f"     Score: {item.get('score', 'N/A'):.2f}")
                            print(f"     Category: {item['item'].get('category', 'N/A')}")
                else:
                    print(f"❌ Search failed: {result['error']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("🔄 Continuing...")


def main():
    """Main function to run the example."""
    print("🧠 AI Agent Demonstration - Example 6: Knowledge Search Agent")
    print("=" * 70)
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
    print("1. Run all demonstrations")
    print("2. Interactive mode (search knowledge base manually)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                agent = KnowledgeSearchAgent()
                print("\n" + "="*70)
                agent.demonstrate_search_capabilities()
                print("\n" + "="*70)
                agent.demonstrate_advanced_search()
                print("\n" + "="*70)
                agent.demonstrate_knowledge_management()
                print("\n" + "="*70)
                agent.demonstrate_search_learning()
                print("\n🎯 All demonstrations completed!")
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

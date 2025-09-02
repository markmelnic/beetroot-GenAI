#!/usr/bin/env python3
"""
Example 5: Data Query Agent

This example demonstrates an AI agent specialized for data analysis:
1. Perceive: Receive data and query requests
2. Think: Understand data structure and query intent
3. Act: Execute data operations and generate insights
4. Learn: Remember data patterns and improve queries

What you'll learn:
- Data analysis and manipulation
- Natural language query processing
- Statistical analysis and visualization
- Data transformation workflows
- Query optimization and learning

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
from tools.data_tools import query_data, analyze_data, transform_data, generate_chart, calculate_statistics
from config.settings import get_config


class DataQueryAgent(BaseAgent):
    """
    An AI agent specialized for data analysis and querying.
    
    This agent demonstrates:
    - Natural language data queries
    - Data analysis and insights
    - Data transformation and manipulation
    - Chart generation and visualization
    - Query learning and optimization
    """
    
    def __init__(self, model: str = None):
        """Initialize the data query agent."""
        # Define data analysis tools
        tools = [
            query_data,
            analyze_data,
            transform_data,
            generate_chart,
            calculate_statistics
        ]
        
        super().__init__(model=model, tools=tools)
        
        # Initialize memory for data and query history
        self.memory = Memory()
        
        # Sample datasets for demonstration
        self.sample_datasets = self._create_sample_datasets()
        
        print(f"📊 Data Query Agent initialized with model: {self.model}")
        print(f"🔧 Available tools: {len(self.tools)}")
        print(f"💾 Memory system: {self.memory.get_stats()['total_items']} items")
        print(f"📈 Sample datasets: {len(self.sample_datasets)} available")
        print()
        print("💡 This agent specializes in data analysis, querying, and insights generation.")
        print()
    
    def _create_sample_datasets(self):
        """Create sample datasets for demonstration."""
        return {
            "sales_data": {
                "name": "Sales Data",
                "description": "Monthly sales data for different products",
                "data": [
                    {"month": "Jan", "product": "Laptop", "sales": 120, "revenue": 144000},
                    {"month": "Jan", "product": "Phone", "sales": 200, "revenue": 120000},
                    {"month": "Feb", "product": "Laptop", "sales": 150, "revenue": 180000},
                    {"month": "Feb", "product": "Phone", "sales": 180, "revenue": 108000},
                    {"month": "Mar", "product": "Laptop", "sales": 130, "revenue": 156000},
                    {"month": "Mar", "product": "Phone", "sales": 220, "revenue": 132000},
                    {"month": "Apr", "product": "Laptop", "sales": 160, "revenue": 192000},
                    {"month": "Apr", "product": "Phone", "sales": 190, "revenue": 114000}
                ],
                "type": "list_of_dicts"
            },
            "user_scores": {
                "name": "User Scores",
                "description": "User performance scores across different tests",
                "data": [85, 92, 78, 96, 88, 91, 79, 94, 87, 90, 82, 89, 93, 86, 91],
                "type": "list"
            },
            "inventory": {
                "name": "Inventory",
                "description": "Current inventory levels for various items",
                "data": {
                    "laptops": 45,
                    "phones": 120,
                    "tablets": 30,
                    "accessories": 200,
                    "cables": 500,
                    "chargers": 150
                },
                "type": "dict"
            },
            "temperature_readings": {
                "name": "Temperature Readings",
                "description": "Daily temperature readings over a month",
                "data": [22.5, 24.1, 21.8, 25.3, 23.7, 26.2, 24.8, 22.9, 25.6, 23.4, 
                        26.8, 24.2, 22.1, 25.9, 23.8, 26.5, 24.7, 22.3, 25.1, 23.9,
                        26.3, 24.5, 22.7, 25.4, 23.6, 26.1, 24.9, 22.4, 25.7, 23.2],
                "type": "list"
            }
        }
    
    def query_dataset(self, dataset_name: str, query: str) -> dict:
        """
        Query a specific dataset using natural language.
        
        Args:
            dataset_name: Name of the dataset to query
            query: Natural language query
            
        Returns:
            Query results and analysis
        """
        if dataset_name not in self.sample_datasets:
            return {"error": f"Dataset '{dataset_name}' not found"}
        
        dataset = self.sample_datasets[dataset_name]
        data = dataset["data"]
        
        print(f"🔍 Querying {dataset['name']} with: '{query}'")
        
        # Store the query in memory
        memory_id = self.memory.store(
            content={"dataset": dataset_name, "query": query, "timestamp": time.time()},
            item_type="data_query",
            importance=0.7
        )
        
        # Execute the query
        start_time = time.time()
        query_result = query_data(data, query)
        end_time = time.time()
        
        # Enhance with additional analysis
        enhanced_result = {
            "query": query,
            "dataset": dataset_name,
            "query_result": query_result,
            "query_time": end_time - start_time,
            "data_summary": self._summarize_data(data),
            "suggestions": self._generate_query_suggestions(query, data)
        }
        
        # Store the result in memory
        self.memory.store(
            content=enhanced_result,
            item_type="query_result",
            importance=0.8,
            metadata={
                "query_id": memory_id,
                "dataset": dataset_name,
                "query_time": enhanced_result["query_time"]
            }
        )
        
        return enhanced_result
    
    def analyze_dataset(self, dataset_name: str) -> dict:
        """
        Perform comprehensive analysis of a dataset.
        
        Args:
            dataset_name: Name of the dataset to analyze
            
        Returns:
            Comprehensive analysis results
        """
        if dataset_name not in self.sample_datasets:
            return {"error": f"Dataset '{dataset_name}' not found"}
        
        dataset = self.sample_datasets[dataset_name]
        data = dataset["data"]
        
        print(f"📊 Analyzing {dataset['name']}...")
        
        # Perform various analyses
        analysis_results = {
            "dataset_info": {
                "name": dataset["name"],
                "description": dataset["description"],
                "type": dataset["type"],
                "size": len(data) if isinstance(data, (list, dict)) else "N/A"
            },
            "basic_analysis": analyze_data(data),
            "statistics": calculate_statistics(data),
            "insights": self._generate_data_insights(data),
            "visualization_suggestions": self._suggest_visualizations(data)
        }
        
        # Store analysis in memory
        self.memory.store(
            content=analysis_results,
            item_type="data_analysis",
            importance=0.9,
            metadata={
                "dataset": dataset_name,
                "timestamp": time.time()
            }
        )
        
        return analysis_results
    
    def transform_dataset(self, dataset_name: str, transformation: str) -> dict:
        """
        Transform a dataset according to specified rules.
        
        Args:
            dataset_name: Name of the dataset to transform
            transformation: Description of transformation to apply
            
        Returns:
            Transformation results
        """
        if dataset_name not in self.sample_datasets:
            return {"error": f"Dataset '{dataset_name}' not found"}
        
        dataset = self.sample_datasets[dataset_name]
        data = dataset["data"]
        
        print(f"🔄 Transforming {dataset['name']} with: '{transformation}'")
        
        # Perform transformation
        start_time = time.time()
        transform_result = transform_data(data, transformation)
        end_time = time.time()
        
        # Store transformation in memory
        self.memory.store(
            content=transform_result,
            item_type="data_transformation",
            importance=0.8,
            metadata={
                "dataset": dataset_name,
                "transformation": transformation,
                "transform_time": end_time - start_time
            }
        )
        
        return {
            "dataset": dataset_name,
            "transformation": transformation,
            "result": transform_result,
            "transform_time": end_time - start_time
        }
    
    def generate_chart(self, dataset_name: str, chart_type: str = "auto") -> dict:
        """
        Generate chart data for a dataset.
        
        Args:
            dataset_name: Name of the dataset
            chart_type: Type of chart to generate
            
        Returns:
            Chart configuration and data
        """
        if dataset_name not in self.sample_datasets:
            return {"error": f"Dataset '{dataset_name}' not found"}
        
        dataset = self.sample_datasets[dataset_name]
        data = dataset["data"]
        
        print(f"📈 Generating {chart_type} chart for {dataset['name']}...")
        
        # Auto-detect chart type if not specified
        if chart_type == "auto":
            chart_type = self._suggest_chart_type(data)
        
        # Generate chart data
        chart_result = generate_chart(data, chart_type)
        
        # Store chart in memory
        self.memory.store(
            content=chart_result,
            item_type="chart_data",
            importance=0.7,
            metadata={
                "dataset": dataset_name,
                "chart_type": chart_type,
                "timestamp": time.time()
            }
        )
        
        return {
            "dataset": dataset_name,
            "chart_type": chart_type,
            "chart_data": chart_result
        }
    
    def _summarize_data(self, data) -> dict:
        """Generate a summary of the data structure and content."""
        if isinstance(data, list):
            if not data:
                return {"type": "empty_list", "count": 0}
            
            # Check if it's a list of dictionaries
            if all(isinstance(item, dict) for item in data):
                keys = set()
                for item in data:
                    keys.update(item.keys())
                
                return {
                    "type": "list_of_dicts",
                    "count": len(data),
                    "keys": list(keys),
                    "sample_items": data[:3] if len(data) > 3 else data
                }
            else:
                # Simple list
                return {
                    "type": "simple_list",
                    "count": len(data),
                    "data_types": list(set(type(item).__name__ for item in data)),
                    "sample_items": data[:5] if len(data) > 5 else data
                }
        
        elif isinstance(data, dict):
            return {
                "type": "dictionary",
                "count": len(data),
                "keys": list(data.keys()),
                "value_types": {k: type(v).__name__ for k, v in data.items()}
            }
        
        else:
            return {"type": type(data).__name__, "value": str(data)}
    
    def _generate_query_suggestions(self, query: str, data) -> list:
        """Generate suggestions for related queries."""
        suggestions = []
        
        if isinstance(data, list) and data:
            if all(isinstance(item, dict) for item in data):
                # List of dictionaries
                suggestions.extend([
                    "Show the first 5 items",
                    "Count total items",
                    "Find items with specific values",
                    "Sort by any field",
                    "Filter by conditions"
                ])
            else:
                # Simple list
                suggestions.extend([
                    "Count items",
                    "Find minimum and maximum values",
                    "Calculate average",
                    "Show unique values",
                    "Sort in ascending/descending order"
                ])
        
        elif isinstance(data, dict):
            suggestions.extend([
                "Show all keys",
                "Show all values",
                "Find specific keys",
                "Sort by values",
                "Filter by value conditions"
            ])
        
        return suggestions
    
    def _generate_data_insights(self, data) -> list:
        """Generate insights about the data."""
        insights = []
        
        if isinstance(data, list) and data:
            if all(isinstance(item, dict) for item in data):
                # List of dictionaries
                keys = set()
                for item in data:
                    keys.update(item.keys())
                
                insights.append(f"Data contains {len(data)} records with {len(keys)} fields")
                
                # Check for numeric fields
                numeric_fields = []
                for key in keys:
                    if all(isinstance(item.get(key), (int, float)) for item in data if item.get(key) is not None):
                        numeric_fields.append(key)
                
                if numeric_fields:
                    insights.append(f"Numeric fields available for analysis: {', '.join(numeric_fields)}")
                
                # Check for categorical fields
                categorical_fields = []
                for key in keys:
                    unique_values = set(item.get(key) for item in data if item.get(key) is not None)
                    if len(unique_values) < len(data) * 0.5:  # Less than 50% unique values
                        categorical_fields.append(key)
                
                if categorical_fields:
                    insights.append(f"Categorical fields for grouping: {', '.join(categorical_fields)}")
            
            else:
                # Simple list
                insights.append(f"List contains {len(data)} items")
                
                if all(isinstance(item, (int, float)) for item in data):
                    insights.append("All items are numeric - suitable for statistical analysis")
                elif all(isinstance(item, str) for item in data):
                    insights.append("All items are strings - suitable for text analysis")
                else:
                    insights.append("Mixed data types - may need data cleaning")
        
        elif isinstance(data, dict):
            insights.append(f"Dictionary contains {len(data)} key-value pairs")
            
            numeric_values = sum(1 for v in data.values() if isinstance(v, (int, float)))
            if numeric_values > 0:
                insights.append(f"{numeric_values} numeric values available for analysis")
        
        return insights
    
    def _suggest_visualizations(self, data) -> list:
        """Suggest appropriate visualizations for the data."""
        suggestions = []
        
        if isinstance(data, list) and data:
            if all(isinstance(item, dict) for item in data):
                # List of dictionaries
                suggestions.extend([
                    "Bar chart for categorical data",
                    "Line chart for time series data",
                    "Scatter plot for numeric relationships",
                    "Pie chart for proportions",
                    "Heatmap for correlation analysis"
                ])
            else:
                # Simple list
                if all(isinstance(item, (int, float)) for item in data):
                    suggestions.extend([
                        "Histogram for distribution",
                        "Box plot for outliers",
                        "Line chart for trends",
                        "Bar chart for frequency"
                    ])
                else:
                    suggestions.append("Bar chart for frequency analysis")
        
        elif isinstance(data, dict):
            suggestions.extend([
                "Bar chart for key-value pairs",
                "Pie chart for proportions",
                "Horizontal bar chart for long labels"
            ])
        
        return suggestions
    
    def _suggest_chart_type(self, data) -> str:
        """Auto-suggest the best chart type for the data."""
        if isinstance(data, list) and data:
            if all(isinstance(item, dict) for item in data):
                # Check if there's a time-related field
                if any('time' in str(k).lower() or 'date' in str(k).lower() or 'month' in str(k).lower() 
                       for item in data for k in item.keys()):
                    return "line"
                else:
                    return "bar"
            else:
                if all(isinstance(item, (int, float)) for item in data):
                    return "histogram"
                else:
                    return "bar"
        
        elif isinstance(data, dict):
            return "bar"
        
        return "bar"  # Default fallback
    
    def demonstrate_data_analysis(self):
        """Demonstrate data analysis capabilities."""
        print("📊 Demonstrating Data Analysis Capabilities")
        print("=" * 60)
        
        # Analyze each dataset
        for dataset_name in self.sample_datasets:
            print(f"\n🔍 Analyzing {dataset_name}...")
            analysis = self.analyze_dataset(dataset_name)
            
            if "error" not in analysis:
                dataset_info = analysis["dataset_info"]
                print(f"  📝 {dataset_info['name']}: {dataset_info['description']}")
                print(f"  📊 Type: {dataset_info['type']}, Size: {dataset_info['size']}")
                
                # Show insights
                insights = analysis.get("insights", [])
                if insights:
                    print(f"  💡 Insights:")
                    for insight in insights[:3]:  # Show first 3 insights
                        print(f"    - {insight}")
                
                # Show visualization suggestions
                viz_suggestions = analysis.get("visualization_suggestions", [])
                if viz_suggestions:
                    print(f"  📈 Visualization suggestions:")
                    for suggestion in viz_suggestions[:3]:  # Show first 3 suggestions
                        print(f"    - {suggestion}")
            else:
                print(f"  ❌ Analysis failed: {analysis['error']}")
        
        print()
    
    def demonstrate_query_capabilities(self):
        """Demonstrate query capabilities."""
        print("🔍 Demonstrating Query Capabilities")
        print("=" * 60)
        
        # Test queries on sales data
        dataset_name = "sales_data"
        test_queries = [
            "count total items",
            "find highest revenue",
            "show data for laptops only",
            "calculate total revenue",
            "show first 3 items"
        ]
        
        print(f"📊 Testing queries on {dataset_name}...")
        
        for query in test_queries:
            print(f"\n  Query: '{query}'")
            result = self.query_dataset(dataset_name, query)
            
            if "error" not in result:
                query_result = result["query_result"]
                print(f"    Result: {query_result.get('result', 'N/A')}")
                print(f"    Type: {query_result.get('type', 'N/A')}")
                print(f"    Time: {result['query_time']:.3f}s")
            else:
                print(f"    Error: {result['error']}")
        
        print()
    
    def demonstrate_transformations(self):
        """Demonstrate data transformation capabilities."""
        print("🔄 Demonstrating Data Transformations")
        print("=" * 60)
        
        # Test transformations on user scores
        dataset_name = "user_scores"
        transformations = [
            "sort ascending",
            "filter values above 90",
            "remove duplicates",
            "calculate statistics"
        ]
        
        print(f"📊 Testing transformations on {dataset_name}...")
        
        for transformation in transformations:
            print(f"\n  Transformation: '{transformation}'")
            result = self.transform_dataset(dataset_name, transformation)
            
            if "error" not in result:
                transform_result = result["result"]
                print(f"    Success: {transform_result.get('transformation_type', 'N/A')}")
                print(f"    Changes: {transform_result.get('changes_made', 'N/A')}")
                print(f"    Time: {result['transform_time']:.3f}s")
            else:
                print(f"    Error: {result['error']}")
        
        print()
    
    def demonstrate_chart_generation(self):
        """Demonstrate chart generation capabilities."""
        print("📈 Demonstrating Chart Generation")
        print("=" * 60)
        
        # Generate charts for different datasets
        chart_examples = [
            ("sales_data", "bar"),
            ("user_scores", "histogram"),
            ("inventory", "pie"),
            ("temperature_readings", "line")
        ]
        
        for dataset_name, chart_type in chart_examples:
            print(f"\n📊 Generating {chart_type} chart for {dataset_name}...")
            result = self.generate_chart(dataset_name, chart_type)
            
            if "error" not in result:
                chart_data = result["chart_data"]
                print(f"  ✅ Chart generated successfully")
                print(f"  📊 Labels: {len(chart_data.get('labels', []))}")
                print(f"  📈 Values: {len(chart_data.get('values', []))}")
            else:
                print(f"  ❌ Chart generation failed: {result['error']}")
        
        print()
    
    def run_interactive(self):
        """Run the agent in interactive mode."""
        print("🎯 Data Query Agent is ready! Type 'quit' to exit.")
        print("Available commands:")
        print("  - 'demo analysis': Demonstrate data analysis")
        print("  - 'demo queries': Demonstrate query capabilities")
        print("  - 'demo transforms': Demonstrate transformations")
        print("  - 'demo charts': Demonstrate chart generation")
        print("  - 'datasets': List available datasets")
        print("  - 'query <dataset> <query>': Query a dataset")
        print("  - 'analyze <dataset>': Analyze a dataset")
        print("  - 'transform <dataset> <transformation>': Transform a dataset")
        print("  - 'chart <dataset> [type]': Generate a chart")
        print("=" * 80)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye! Thanks for trying the Data Query Agent.")
                    break
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == 'demo analysis':
                    self.demonstrate_data_analysis()
                    continue
                elif user_input.lower() == 'demo queries':
                    self.demonstrate_query_capabilities()
                    continue
                elif user_input.lower() == 'demo transforms':
                    self.demonstrate_transformations()
                    continue
                elif user_input.lower() == 'demo charts':
                    self.demonstrate_chart_generation()
                    continue
                elif user_input.lower() == 'datasets':
                    print("📊 Available datasets:")
                    for name, dataset in self.sample_datasets.items():
                        print(f"  - {name}: {dataset['description']}")
                    continue
                
                # Handle query commands
                if user_input.lower().startswith('query '):
                    parts = user_input[6:].split(' ', 1)  # Remove 'query ' prefix
                    if len(parts) == 2:
                        dataset_name, query = parts
                        result = self.query_dataset(dataset_name, query)
                        
                        if "error" not in result:
                            query_result = result["query_result"]
                            print(f"✅ Query result: {query_result.get('result', 'N/A')}")
                            print(f"📊 Query type: {query_result.get('type', 'N/A')}")
                            print(f"⏱️  Query time: {result['query_time']:.3f}s")
                        else:
                            print(f"❌ Query failed: {result['error']}")
                    else:
                        print("❌ Usage: query <dataset> <query>")
                    continue
                
                # Handle analysis commands
                if user_input.lower().startswith('analyze '):
                    dataset_name = user_input[8:]  # Remove 'analyze ' prefix
                    result = self.analyze_dataset(dataset_name)
                    
                    if "error" not in result:
                        dataset_info = result["dataset_info"]
                        print(f"✅ Analysis completed for {dataset_info['name']}")
                        print(f"📊 Dataset size: {dataset_info['size']}")
                        
                        insights = result.get("insights", [])
                        if insights:
                            print(f"💡 Key insights:")
                            for insight in insights[:3]:
                                print(f"  - {insight}")
                    else:
                        print(f"❌ Analysis failed: {result['error']}")
                    continue
                
                # Handle transformation commands
                if user_input.lower().startswith('transform '):
                    parts = user_input[10:].split(' ', 1)  # Remove 'transform ' prefix
                    if len(parts) == 2:
                        dataset_name, transformation = parts
                        result = self.transform_dataset(dataset_name, transformation)
                        
                        if "error" not in result:
                            print(f"✅ Transformation completed")
                            print(f"🔄 Type: {result['result'].get('transformation_type', 'N/A')}")
                            print(f"⏱️  Time: {result['transform_time']:.3f}s")
                        else:
                            print(f"❌ Transformation failed: {result['error']}")
                    else:
                        print("❌ Usage: transform <dataset> <transformation>")
                    continue
                
                # Handle chart commands
                if user_input.lower().startswith('chart '):
                    parts = user_input[6:].split(' ')  # Remove 'chart ' prefix
                    if len(parts) >= 1:
                        dataset_name = parts[0]
                        chart_type = parts[1] if len(parts) > 1 else "auto"
                        
                        result = self.generate_chart(dataset_name, chart_type)
                        
                        if "error" not in result:
                            chart_data = result["chart_data"]
                            print(f"✅ Chart generated")
                            print(f"📊 Type: {result['chart_type']}")
                            print(f"📈 Data points: {len(chart_data.get('labels', []))}")
                        else:
                            print(f"❌ Chart generation failed: {result['error']}")
                    else:
                        print("❌ Usage: chart <dataset> [type]")
                    continue
                
                # Default: treat as a general query
                print(f"🤔 Processing as general query...")
                
                # Try to find the best dataset for the query
                best_dataset = self._find_best_dataset_for_query(user_input)
                
                if best_dataset:
                    print(f"🔍 Using dataset: {best_dataset}")
                    result = self.query_dataset(best_dataset, user_input)
                    
                    if "error" not in result:
                        query_result = result["query_result"]
                        print(f"✅ Result: {query_result.get('result', 'N/A')}")
                    else:
                        print(f"❌ Query failed: {result['error']}")
                else:
                    print("❌ Could not determine appropriate dataset for query")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("🔄 Continuing...")
    
    def _find_best_dataset_for_query(self, query: str) -> str:
        """Find the best dataset for a given query."""
        query_lower = query.lower()
        
        # Simple keyword matching
        if any(word in query_lower for word in ["sales", "revenue", "product", "month"]):
            return "sales_data"
        elif any(word in query_lower for word in ["score", "performance", "test", "grade"]):
            return "user_scores"
        elif any(word in query_lower for word in ["inventory", "stock", "item", "count"]):
            return "inventory"
        elif any(word in query_lower for word in ["temperature", "reading", "daily", "weather"]):
            return "temperature_readings"
        
        # Default to user_scores for numeric queries
        if any(word in query_lower for word in ["calculate", "average", "mean", "statistics"]):
            return "user_scores"
        
        return None


def main():
    """Main function to run the example."""
    print("🧠 AI Agent Demonstration - Example 5: Data Query Agent")
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
    print("1. Run all demonstrations")
    print("2. Interactive mode (analyze data manually)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                agent = DataQueryAgent()
                print("\n" + "="*60)
                agent.demonstrate_data_analysis()
                print("\n" + "="*60)
                agent.demonstrate_query_capabilities()
                print("\n" + "="*60)
                agent.demonstrate_transformations()
                print("\n" + "="*60)
                agent.demonstrate_chart_generation()
                print("\n🎯 All demonstrations completed!")
                break
            elif choice == "2":
                agent = DataQueryAgent()
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

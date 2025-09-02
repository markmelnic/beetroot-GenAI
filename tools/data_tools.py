"""
Data manipulation and analysis tools for AI agents.
Provides functions for querying, analyzing, and transforming data.
"""

import json
import logging
import math
import statistics
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def query_data(data: Union[List, Dict], query: str) -> Dict[str, Any]:
    """
    Query data using natural language-like queries.
    
    Args:
        data: Data to query (list or dictionary)
        query: Natural language query
        
    Returns:
        Dictionary containing query results
    """
    try:
        query_lower = query.lower()
        
        if isinstance(data, list):
            return _query_list_data(data, query_lower)
        elif isinstance(data, dict):
            return _query_dict_data(data, query_lower)
        else:
            return {"error": f"Unsupported data type: {type(data)}"}
            
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


def analyze_data(data: Union[List, Dict]) -> Dict[str, Any]:
    """
    Analyze data for patterns, statistics, and insights.
    
    Args:
        data: Data to analyze
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        if isinstance(data, list):
            return _analyze_list_data(data)
        elif isinstance(data, dict):
            return _analyze_dict_data(data)
        else:
            return {"error": f"Unsupported data type: {type(data)}"}
            
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}


def transform_data(data: Union[List, Dict], transformation: str) -> Dict[str, Any]:
    """
    Transform data according to specified transformation rules.
    
    Args:
        data: Data to transform
        transformation: Description of transformation to apply
        
    Returns:
        Dictionary containing transformed data and metadata
    """
    try:
        transformation_lower = transformation.lower()
        
        if isinstance(data, list):
            return _transform_list_data(data, transformation_lower)
        elif isinstance(data, dict):
            return _transform_dict_data(data, transformation_lower)
        else:
            return {"error": f"Unsupported data type: {type(data)}"}
            
    except Exception as e:
        return {"error": f"Transformation failed: {str(e)}"}


def generate_chart(data: Union[List, Dict], chart_type: str = "bar") -> Dict[str, Any]:
    """
    Generate chart data for visualization.
    
    Args:
        data: Data to visualize
        chart_type: Type of chart to generate
        
    Returns:
        Dictionary containing chart configuration and data
    """
    try:
        if isinstance(data, list):
            return _generate_list_chart(data, chart_type)
        elif isinstance(data, dict):
            return _generate_dict_chart(data, chart_type)
        else:
            return {"error": f"Unsupported data type: {type(data)}"}
            
    except Exception as e:
        return {"error": f"Chart generation failed: {str(e)}"}


def calculate_statistics(data: Union[List, Dict]) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics for the data.
    
    Args:
        data: Data to analyze
        
    Returns:
        Dictionary containing statistical measures
    """
    try:
        if isinstance(data, list):
            return _calculate_list_statistics(data)
        elif isinstance(data, dict):
            return _calculate_dict_statistics(data)
        else:
            return {"error": f"Unsupported data type: {type(data)}"}
            
    except Exception as e:
        return {"error": f"Statistics calculation failed: {str(e)}"}


def _query_list_data(data: List, query: str) -> Dict[str, Any]:
    """Query list data using natural language."""
    results = []
    
    if "count" in query or "how many" in query:
        if "unique" in query or "distinct" in query:
            unique_count = len(set(data))
            return {"result": unique_count, "query": query, "type": "unique_count"}
        else:
            return {"result": len(data), "query": query, "type": "total_count"}
    
    elif "find" in query or "search" in query:
        # Extract search term from query
        search_terms = []
        for word in query.split():
            if word not in ["find", "search", "for", "in", "the", "a", "an"]:
                search_terms.append(word)
        
        if search_terms:
            for item in data:
                if any(term.lower() in str(item).lower() for term in search_terms):
                    results.append(item)
        
        return {"result": results, "query": query, "type": "search", "count": len(results)}
    
    elif "filter" in query or "where" in query:
        # Basic filtering based on query keywords
        if "number" in query or "numeric" in query:
            results = [item for item in data if isinstance(item, (int, float))]
        elif "text" in query or "string" in query:
            results = [item for item in data if isinstance(item, str)]
        elif "empty" in query or "null" in query:
            results = [item for item in data if item is None or item == ""]
        
        return {"result": results, "query": query, "type": "filter", "count": len(results)}
    
    elif "first" in query:
        if "n" in query or "few" in query:
            # Extract number from query
            n = 5  # default
            for word in query.split():
                if word.isdigit():
                    n = int(word)
                    break
            results = data[:n]
        else:
            results = data[0] if data else None
        
        return {"result": results, "query": query, "type": "first_n"}
    
    elif "last" in query:
        if "n" in query or "few" in query:
            n = 5  # default
            for word in query.split():
                if word.isdigit():
                    n = int(word)
                    break
            results = data[-n:]
        else:
            results = data[-1] if data else None
        
        return {"result": results, "query": query, "type": "last_n"}
    
    else:
        # Default: return all data
        return {"result": data, "query": query, "type": "all", "count": len(data)}


def _query_dict_data(data: Dict, query: str) -> Dict[str, Any]:
    """Query dictionary data using natural language."""
    results = {}
    
    if "keys" in query or "what keys" in query:
        return {"result": list(data.keys()), "query": query, "type": "keys"}
    
    elif "values" in query or "what values" in query:
        return {"result": list(data.values()), "query": query, "type": "values"}
    
    elif "find" in query or "search" in query:
        # Extract search term from query
        search_terms = []
        for word in query.split():
            if word not in ["find", "search", "for", "in", "the", "a", "an"]:
                search_terms.append(word)
        
        if search_terms:
            for key, value in data.items():
                if any(term.lower() in str(key).lower() or term.lower() in str(value).lower() 
                       for term in search_terms):
                    results[key] = value
        
        return {"result": results, "query": query, "type": "search", "count": len(results)}
    
    elif "filter" in query or "where" in query:
        # Basic filtering
        if "string" in query or "text" in query:
            results = {k: v for k, v in data.items() if isinstance(v, str)}
        elif "number" in query or "numeric" in query:
            results = {k: v for k, v in data.items() if isinstance(v, (int, float))}
        elif "empty" in query or "null" in query:
            results = {k: v for k, v in data.items() if v is None or v == ""}
        
        return {"result": results, "query": query, "type": "filter", "count": len(results)}
    
    else:
        # Default: return all data
        return {"result": data, "query": query, "type": "all", "count": len(data)}


def _analyze_list_data(data: List) -> Dict[str, Any]:
    """Analyze list data for patterns and insights."""
    if not data:
        return {"error": "Empty data"}
    
    analysis = {
        "data_type": "list",
        "length": len(data),
        "data_types": {},
        "patterns": [],
        "insights": []
    }
    
    # Analyze data types
    type_counts = {}
    for item in data:
        item_type = type(item).__name__
        type_counts[item_type] = type_counts.get(item_type, 0) + 1
    
    analysis["data_types"] = type_counts
    
    # Find patterns
    if len(data) > 1:
        # Check for duplicates
        unique_items = set(data)
        if len(unique_items) < len(data):
            analysis["patterns"].append(f"Contains {len(data) - len(unique_items)} duplicate items")
        
        # Check for sequences
        if all(isinstance(item, (int, float)) for item in data):
            sorted_data = sorted(data)
            if data == sorted_data:
                analysis["patterns"].append("Data is in ascending order")
            elif data == sorted_data[::-1]:
                analysis["patterns"].append("Data is in descending order")
        
        # Check for common values
        value_counts = {}
        for item in data:
            value_counts[item] = value_counts.get(item, 0) + 1
        
        most_common = max(value_counts.items(), key=lambda x: x[1])
        if most_common[1] > len(data) * 0.5:
            analysis["patterns"].append(f"Value '{most_common[0]}' appears {most_common[1]} times ({most_common[1]/len(data)*100:.1f}%)")
    
    # Generate insights
    if len(data) > 100:
        analysis["insights"].append("Large dataset - consider sampling for analysis")
    
    if len(analysis["data_types"]) > 3:
        analysis["insights"].append("Mixed data types - may need data cleaning")
    
    return analysis


def _analyze_dict_data(data: Dict) -> Dict[str, Any]:
    """Analyze dictionary data for patterns and insights."""
    if not data:
        return {"error": "Empty data"}
    
    analysis = {
        "data_type": "dict",
        "length": len(data),
        "key_types": {},
        "value_types": {},
        "patterns": [],
        "insights": []
    }
    
    # Analyze key and value types
    key_types = {}
    value_types = {}
    
    for key, value in data.items():
        key_type = type(key).__name__
        value_type = type(value).__name__
        
        key_types[key_type] = key_types.get(key_type, 0) + 1
        value_types[value_type] = value_types.get(value_type, 0) + 1
    
    analysis["key_types"] = key_types
    analysis["value_types"] = value_types
    
    # Find patterns
    if len(data) > 1:
        # Check for nested structures
        nested_count = sum(1 for v in data.values() if isinstance(v, (dict, list)))
        if nested_count > 0:
            analysis["patterns"].append(f"Contains {nested_count} nested structures")
        
        # Check for consistent value types
        if len(value_types) == 1:
            analysis["patterns"].append("All values have the same type")
        elif len(value_types) > 5:
            analysis["patterns"].append("Highly diverse value types")
        
        # Check for key patterns
        key_lengths = [len(str(k)) for k in data.keys()]
        if len(set(key_lengths)) == 1:
            analysis["patterns"].append("All keys have the same length")
    
    # Generate insights
    if len(data) > 50:
        analysis["insights"].append("Large dictionary - consider using specialized data structures")
    
    if any(isinstance(v, (dict, list)) for v in data.values()):
        analysis["insights"].append("Contains nested structures - may need recursive analysis")
    
    return analysis


def _transform_list_data(data: List, transformation: str) -> Dict[str, Any]:
    """Transform list data according to transformation rules."""
    original_data = data.copy()
    
    if "sort" in transformation:
        if "reverse" in transformation or "descending" in transformation:
            data = sorted(data, reverse=True)
        else:
            data = sorted(data)
        transformation_type = "sort_descending" if "reverse" in transformation else "sort_ascending"
    
    elif "reverse" in transformation:
        data = data[::-1]
        transformation_type = "reverse"
    
    elif "unique" in transformation or "remove duplicates" in transformation:
        data = list(dict.fromkeys(data))  # Preserves order
        transformation_type = "remove_duplicates"
    
    elif "filter" in transformation:
        if "empty" in transformation or "null" in transformation:
            data = [item for item in data if item is not None and item != ""]
            transformation_type = "filter_empty"
        elif "numeric" in transformation or "number" in transformation:
            data = [item for item in data if isinstance(item, (int, float))]
            transformation_type = "filter_numeric"
        elif "string" in transformation or "text" in transformation:
            data = [item for item in data if isinstance(item, str)]
            transformation_type = "filter_string"
    
    elif "map" in transformation or "apply" in transformation:
        if "uppercase" in transformation:
            data = [str(item).upper() for item in data]
            transformation_type = "map_uppercase"
        elif "lowercase" in transformation:
            data = [str(item).lower() for item in data]
            transformation_type = "map_lowercase"
        elif "string" in transformation:
            data = [str(item) for item in data]
            transformation_type = "map_string"
    
    else:
        return {"error": f"Unknown transformation: {transformation}"}
    
    return {
        "original_data": original_data,
        "transformed_data": data,
        "transformation": transformation,
        "transformation_type": transformation_type,
        "changes_made": len(original_data) - len(data) if "filter" in transformation else 0
    }


def _transform_dict_data(data: Dict, transformation: str) -> Dict[str, Any]:
    """Transform dictionary data according to transformation rules."""
    original_data = data.copy()
    
    if "sort" in transformation:
        if "keys" in transformation:
            if "reverse" in transformation:
                data = dict(sorted(data.items(), key=lambda x: x[0], reverse=True))
            else:
                data = dict(sorted(data.items(), key=lambda x: x[0]))
            transformation_type = "sort_by_keys"
        elif "values" in transformation:
            if "reverse" in transformation:
                data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
            else:
                data = dict(sorted(data.items(), key=lambda x: x[1]))
            transformation_type = "sort_by_values"
    
    elif "filter" in transformation:
        if "empty" in transformation or "null" in transformation:
            data = {k: v for k, v in data.items() if v is not None and v != ""}
            transformation_type = "filter_empty_values"
        elif "numeric" in transformation or "number" in transformation:
            data = {k: v for k, v in data.items() if isinstance(v, (int, float))}
            transformation_type = "filter_numeric_values"
        elif "string" in transformation or "text" in transformation:
            data = {k: v for k, v in data.items() if isinstance(v, str)}
            transformation_type = "filter_string_values"
    
    elif "invert" in transformation or "swap" in transformation:
        data = {v: k for k, v in data.items()}
        transformation_type = "invert_keys_values"
    
    elif "flatten" in transformation:
        # Basic flattening for nested dictionaries
        flattened = {}
        for k, v in data.items():
            if isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    flattened[f"{k}.{sub_k}"] = sub_v
            else:
                flattened[k] = v
        data = flattened
        transformation_type = "flatten_nested"
    
    else:
        return {"error": f"Unknown transformation: {transformation}"}
    
    return {
        "original_data": original_data,
        "transformed_data": data,
        "transformation": transformation,
        "transformation_type": transformation_type,
        "changes_made": len(original_data) - len(data) if "filter" in transformation else 0
    }


def _generate_list_chart(data: List, chart_type: str) -> Dict[str, Any]:
    """Generate chart data for list data."""
    if not data:
        return {"error": "Empty data"}
    
    chart_data = {
        "chart_type": chart_type,
        "data": data,
        "labels": [],
        "values": []
    }
    
    if chart_type == "bar" or chart_type == "line":
        # Count occurrences of each value
        value_counts = {}
        for item in data:
            value_counts[item] = value_counts.get(item, 0) + 1
        
        chart_data["labels"] = list(value_counts.keys())
        chart_data["values"] = list(value_counts.values())
        
    elif chart_type == "pie":
        # Similar to bar chart
        value_counts = {}
        for item in data:
            value_counts[item] = value_counts.get(item, 0) + 1
        
        chart_data["labels"] = list(value_counts.keys())
        chart_data["values"] = list(value_counts.values())
    
    elif chart_type == "histogram":
        # For numeric data
        if all(isinstance(item, (int, float)) for item in data):
            # Simple histogram with 10 bins
            min_val, max_val = min(data), max(data)
            bin_size = (max_val - min_val) / 10
            
            bins = [0] * 10
            labels = []
            
            for i in range(10):
                bin_start = min_val + i * bin_size
                bin_end = min_val + (i + 1) * bin_size
                labels.append(f"{bin_start:.1f}-{bin_end:.1f}")
                
                for item in data:
                    if bin_start <= item < bin_end:
                        bins[i] += 1
            
            chart_data["labels"] = labels
            chart_data["values"] = bins
    
    return chart_data


def _generate_dict_chart(data: Dict, chart_type: str) -> Dict[str, Any]:
    """Generate chart data for dictionary data."""
    if not data:
        return {"error": "Empty data"}
    
    chart_data = {
        "chart_type": chart_type,
        "data": data,
        "labels": list(data.keys()),
        "values": list(data.values())
    }
    
    return chart_data


def _calculate_list_statistics(data: List) -> Dict[str, Any]:
    """Calculate comprehensive statistics for list data."""
    if not data:
        return {"error": "Empty data"}
    
    stats = {
        "count": len(data),
        "data_types": {}
    }
    
    # Analyze data types
    type_counts = {}
    for item in data:
        item_type = type(item).__name__
        type_counts[item_type] = type_counts.get(item_type, 0) + 1
    
    stats["data_types"] = type_counts
    
    # Numeric statistics
    numeric_data = [item for item in data if isinstance(item, (int, float))]
    if numeric_data:
        stats["numeric"] = {
            "count": len(numeric_data),
            "min": min(numeric_data),
            "max": max(numeric_data),
            "sum": sum(numeric_data),
            "mean": statistics.mean(numeric_data),
            "median": statistics.median(numeric_data),
            "mode": statistics.mode(numeric_data) if len(numeric_data) > 0 else None,
            "std_dev": statistics.stdev(numeric_data) if len(numeric_data) > 1 else None,
            "variance": statistics.variance(numeric_data) if len(numeric_data) > 1 else None
        }
    
    # String statistics
    string_data = [item for item in data if isinstance(item, str)]
    if string_data:
        string_lengths = [len(item) for item in string_data]
        stats["string"] = {
            "count": len(string_data),
            "min_length": min(string_lengths),
            "max_length": max(string_lengths),
            "avg_length": statistics.mean(string_lengths),
            "total_chars": sum(string_lengths)
        }
    
    # List statistics
    list_data = [item for item in data if isinstance(item, list)]
    if list_data:
        list_lengths = [len(item) for item in list_data]
        stats["list"] = {
            "count": len(list_data),
            "min_length": min(list_lengths),
            "max_length": max(list_lengths),
            "avg_length": statistics.mean(list_lengths)
        }
    
    # Dictionary statistics
    dict_data = [item for item in data if isinstance(item, dict)]
    if dict_data:
        dict_lengths = [len(item) for item in dict_data]
        stats["dict"] = {
            "count": len(dict_data),
            "min_length": min(dict_lengths),
            "max_length": max(dict_lengths),
            "avg_length": statistics.mean(dict_lengths)
        }
    
    return stats


def _calculate_dict_statistics(data: Dict) -> Dict[str, Any]:
    """Calculate comprehensive statistics for dictionary data."""
    if not data:
        return {"error": "Empty data"}
    
    stats = {
        "count": len(data),
        "key_types": {},
        "value_types": {}
    }
    
    # Analyze types
    key_types = {}
    value_types = {}
    
    for key, value in data.items():
        key_type = type(key).__name__
        value_type = type(value).__name__
        
        key_types[key_type] = key_types.get(key_type, 0) + 1
        value_types[value_type] = value_types.get(value_type, 0) + 1
    
    stats["key_types"] = key_types
    stats["value_types"] = value_types
    
    # Key statistics
    key_lengths = [len(str(k)) for k in data.keys()]
    stats["keys"] = {
        "min_length": min(key_lengths),
        "max_length": max(key_lengths),
        "avg_length": statistics.mean(key_lengths),
        "total_chars": sum(key_lengths)
    }
    
    # Value statistics
    numeric_values = [v for v in data.values() if isinstance(v, (int, float))]
    if numeric_values:
        stats["numeric_values"] = {
            "count": len(numeric_values),
            "min": min(numeric_values),
            "max": max(numeric_values),
            "sum": sum(numeric_values),
            "mean": statistics.mean(numeric_values),
            "median": statistics.median(numeric_values)
        }
    
    string_values = [v for v in data.values() if isinstance(v, str)]
    if string_values:
        string_lengths = [len(v) for v in string_values]
        stats["string_values"] = {
            "count": len(string_values),
            "min_length": min(string_lengths),
            "max_length": max(string_lengths),
            "avg_length": statistics.mean(string_lengths),
            "total_chars": sum(string_lengths)
        }
    
    return stats

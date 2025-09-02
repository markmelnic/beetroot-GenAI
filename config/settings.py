"""
Configuration settings for the AI Agent project.
Customize these settings based on your environment and needs.
"""

import os
from typing import Dict, Any

# Ollama Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

# Agent Configuration
MAX_MEMORY_ITEMS = int(os.getenv("MAX_MEMORY_ITEMS", "100"))
MAX_PLANNING_STEPS = int(os.getenv("MAX_PLANNING_STEPS", "10"))
AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", "30"))

# Memory Configuration
MEMORY_TTL = int(os.getenv("MEMORY_TTL", "3600"))  # 1 hour in seconds
MEMORY_MAX_SIZE = int(os.getenv("MEMORY_MAX_SIZE", "1000"))

# Planning Configuration
PLANNING_MAX_DEPTH = int(os.getenv("PLANNING_MAX_DEPTH", "5"))
PLANNING_TIMEOUT = int(os.getenv("PLANNING_TIMEOUT", "60"))

# Tool Configuration
TOOL_TIMEOUT = int(os.getenv("TOOL_TIMEOUT", "10"))
MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", "5"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Development Configuration
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
VERBOSE = os.getenv("VERBOSE", "False").lower() == "true"

# Model-specific prompts
SYSTEM_PROMPTS = {
    "mistral": """You are a helpful AI assistant. You can:
1. Answer questions clearly and concisely
2. Help with problem-solving
3. Provide explanations and examples
4. Use tools when available to accomplish tasks

Always be helpful, accurate, and follow instructions carefully.""",
    
    "llama2": """You are a helpful AI assistant. You can:
1. Answer questions clearly and concisely
2. Help with problem-solving
3. Provide explanations and examples
4. Use tools when available to accomplish tasks

Always be helpful, accurate, and follow instructions carefully.""",
    
    "codellama": """You are a helpful AI coding assistant. You can:
1. Write, review, and debug code
2. Explain programming concepts
3. Suggest improvements and optimizations
4. Help with software architecture
5. Use tools when available to accomplish tasks

Always provide clear, well-commented code and helpful explanations."""
}

# Default tool descriptions
DEFAULT_TOOL_DESCRIPTIONS = {
    "search": "Search for information in a knowledge base",
    "calculate": "Perform mathematical calculations",
    "analyze_code": "Analyze and review code for issues",
    "query_data": "Query and analyze data",
    "plan_task": "Break down a complex task into steps"
}

def get_config() -> Dict[str, Any]:
    """Get the current configuration as a dictionary."""
    return {
        "ollama_base_url": OLLAMA_BASE_URL,
        "default_model": DEFAULT_MODEL,
        "max_memory_items": MAX_MEMORY_ITEMS,
        "max_planning_steps": MAX_PLANNING_STEPS,
        "agent_timeout": AGENT_TIMEOUT,
        "memory_ttl": MEMORY_TTL,
        "memory_max_size": MEMORY_MAX_SIZE,
        "planning_max_depth": PLANNING_MAX_DEPTH,
        "planning_timeout": PLANNING_TIMEOUT,
        "tool_timeout": TOOL_TIMEOUT,
        "max_tool_calls": MAX_TOOL_CALLS,
        "log_level": LOG_LEVEL,
        "debug": DEBUG,
        "verbose": VERBOSE
    }

def get_system_prompt(model: str = None) -> str:
    """Get the system prompt for a specific model."""
    if model is None:
        model = DEFAULT_MODEL
    
    return SYSTEM_PROMPTS.get(model, SYSTEM_PROMPTS["mistral"])

"""
Base Agent class that provides the foundation for all AI agents.
This class implements the core agent loop: Perceive → Think → Act → Learn
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
import requests

from config.settings import get_config, get_system_prompt

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for AI agents implementing the core agent loop.
    
    The agent follows this pattern:
    1. Perceive: Receive input from environment
    2. Think: Process information and decide on action
    3. Act: Execute chosen action
    4. Learn: Update internal state based on results
    """
    
    def __init__(self, model: str = None, tools: List[Callable] = None):
        """
        Initialize the base agent.
        
        Args:
            model: The LLM model to use (defaults to config setting)
            tools: List of callable tools the agent can use
        """
        self.config = get_config()
        self.model = model or self.config["default_model"]
        self.tools = tools or []
        self.system_prompt = get_system_prompt(self.model)
        
        # Agent state
        self.conversation_history = []
        self.tool_calls = 0
        self.start_time = time.time()
        
        # Validate Ollama connection
        self._validate_ollama_connection()
        
        logger.info(f"Initialized {self.__class__.__name__} with model: {self.model}")
    
    def _validate_ollama_connection(self):
        """Validate that Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.config['ollama_base_url']}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Ollama connection successful")
            else:
                logger.warning("⚠️ Ollama responded but with unexpected status")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to connect to Ollama: {e}")
            logger.error("Make sure Ollama is running: ollama serve")
            raise ConnectionError("Ollama is not accessible. Please start Ollama first.")
    
    def perceive(self, input_data: Any) -> Dict[str, Any]:
        """
        Perceive the environment and input data.
        
        Args:
            input_data: Raw input from the environment
            
        Returns:
            Processed perception data
        """
        logger.debug(f"Perceiving input: {input_data}")
        
        # Store in conversation history
        self.conversation_history.append({
            "role": "user",
            "content": str(input_data),
            "timestamp": time.time()
        })
        
        return {
            "input": input_data,
            "context": self._get_context(),
            "timestamp": time.time()
        }
    
    def think(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process perception and decide on the next action.
        
        Args:
            perception: Output from perceive() method
            
        Returns:
            Decision about what action to take
        """
        logger.debug("Thinking about next action...")
        
        # Prepare the prompt for the LLM
        prompt = self._build_prompt(perception)
        
        # Get response from LLM
        try:
            response = self._call_llm(prompt)
            decision = self._parse_llm_response(response)
            
            logger.debug(f"Decision made: {decision}")
            return decision
            
        except Exception as e:
            logger.error(f"Error during thinking phase: {e}")
            return {
                "action": "error",
                "reason": f"Failed to process input: {str(e)}",
                "fallback": True
            }
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the decided action.
        
        Args:
            decision: Output from think() method
            
        Returns:
            Result of the action execution
        """
        logger.debug(f"Executing action: {decision}")
        
        action = decision.get("action", "unknown")
        
        try:
            if action == "use_tool":
                result = self._execute_tool(decision)
            elif action == "respond":
                result = {"response": decision.get("content", "No response generated")}
            elif action == "error":
                result = {"error": decision.get("reason", "Unknown error")}
            else:
                result = {"unknown_action": action}
            
            # Store the action and result
            self.conversation_history.append({
                "role": "assistant",
                "action": action,
                "result": result,
                "timestamp": time.time()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error during action execution: {e}")
            return {"error": f"Action execution failed: {str(e)}"}
    
    def learn(self, action_result: Dict[str, Any]) -> None:
        """
        Learn from the action result and update internal state.
        
        Args:
            action_result: Output from act() method
        """
        logger.debug("Learning from action result...")
        
        # Update tool call count if a tool was used
        if "tool_used" in action_result:
            self.tool_calls += 1
        
        # Store learning insights
        learning_data = {
            "action_result": action_result,
            "timestamp": time.time(),
            "total_tool_calls": self.tool_calls,
            "session_duration": time.time() - self.start_time
        }
        
        # Store in conversation history for context
        self.conversation_history.append({
            "role": "system",
            "type": "learning",
            "data": learning_data
        })
        
        logger.debug("Learning phase completed")
    
    def run(self, input_data: Any) -> Dict[str, Any]:
        """
        Run the complete agent loop: Perceive → Think → Act → Learn
        
        Args:
            input_data: Input to process
            
        Returns:
            Final result of the agent's processing
        """
        logger.info(f"Starting agent loop with input: {input_data}")
        
        try:
            # 1. Perceive
            perception = self.perceive(input_data)
            
            # 2. Think
            decision = self.think(perception)
            
            # 3. Act
            action_result = self.act(decision)
            
            # 4. Learn
            self.learn(action_result)
            
            logger.info("Agent loop completed successfully")
            return action_result
            
        except Exception as e:
            logger.error(f"Agent loop failed: {e}")
            return {"error": f"Agent execution failed: {str(e)}"}
    
    def _build_prompt(self, perception: Dict[str, Any]) -> str:
        """
        Build the prompt for the LLM based on perception and context.
        
        Args:
            perception: Current perception data
            
        Returns:
            Formatted prompt string
        """
        # Get recent conversation context
        recent_context = self.conversation_history[-5:] if self.conversation_history else []
        
        prompt = f"{self.system_prompt}\n\n"
        prompt += "Available tools:\n"
        
        for i, tool in enumerate(self.tools):
            tool_name = tool.__name__ if hasattr(tool, '__name__') else f"tool_{i}"
            tool_doc = tool.__doc__ or "No description available"
            prompt += f"- {tool_name}: {tool_doc}\n"
        
        prompt += "\nRecent conversation:\n"
        for entry in recent_context:
            if entry["role"] == "user":
                prompt += f"User: {entry['content']}\n"
            elif entry["role"] == "assistant":
                prompt += f"Assistant: {entry.get('result', {}).get('response', 'Action executed')}\n"
        
        prompt += f"\nCurrent input: {perception['input']}\n"
        prompt += "\nPlease respond with a JSON object containing:\n"
        prompt += '{"action": "use_tool|respond|error", "tool_name": "tool_name_if_using_tool", "content": "response_content", "reason": "explanation"}'
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call the Ollama LLM API.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            LLM response as string
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            response = requests.post(
                f"{self.config['ollama_base_url']}/api/generate",
                json=payload,
                timeout=self.config["agent_timeout"]
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                raise Exception(f"LLM API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            raise Exception("LLM request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"LLM request failed: {e}")
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response to extract action and parameters.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed decision dictionary
        """
        try:
            # Try to extract JSON from the response
            if "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
                
                decision = json.loads(json_str)
                
                # Validate required fields
                if "action" not in decision:
                    decision["action"] = "respond"
                
                return decision
            else:
                # Fallback: treat as simple response
                return {
                    "action": "respond",
                    "content": response.strip(),
                    "reason": "LLM provided direct response"
                }
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON, treating as direct response")
            return {
                "action": "respond",
                "content": response.strip(),
                "reason": "LLM provided direct response"
            }
    
    def _execute_tool(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool based on the decision.
        
        Args:
            decision: Decision containing tool information
            
        Returns:
            Tool execution result
        """
        tool_name = decision.get("tool_name")
        
        if not tool_name:
            return {"error": "No tool name specified"}
        
        # Find the tool
        tool = None
        for t in self.tools:
            if hasattr(t, '__name__') and t.__name__ == tool_name:
                tool = t
                break
        
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}
        
        try:
            # Execute the tool
            tool_args = decision.get("tool_args", {})
            result = tool(**tool_args)
            
            return {
                "tool_used": tool_name,
                "result": result,
                "success": True
            }
            
        except Exception as e:
            return {
                "tool_used": tool_name,
                "error": str(e),
                "success": False
            }
    
    def _get_context(self) -> Dict[str, Any]:
        """Get current context for the agent."""
        return {
            "conversation_length": len(self.conversation_history),
            "tool_calls": self.tool_calls,
            "session_duration": time.time() - self.start_time,
            "available_tools": [t.__name__ if hasattr(t, '__name__') else str(t) for t in self.tools]
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "model": self.model,
            "tool_calls": self.tool_calls,
            "conversation_length": len(self.conversation_history),
            "session_duration": time.time() - self.start_time,
            "available_tools": len(self.tools)
        }

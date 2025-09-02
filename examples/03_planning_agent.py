#!/usr/bin/env python3
"""
Example 3: Planning Agent with Memory

This example demonstrates an AI agent with advanced capabilities:
1. Memory: Stores and retrieves context and information
2. Planning: Breaks complex tasks into smaller steps
3. Multi-step reasoning: Maintains state across interactions
4. Adaptive behavior: Learns from previous interactions

What you'll learn:
- Memory management and context retention
- Task decomposition and planning
- Multi-step problem solving
- State persistence and learning

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
from agents.memory import Memory
from agents.planner import Planner, TaskStatus, TaskPriority
from tools.code_tools import analyze_code, lint_code
from tools.data_tools import analyze_data, transform_data
from config.settings import get_config


class PlanningAgent(BaseAgent):
    """
    An AI agent with memory and planning capabilities.
    
    This agent demonstrates:
    - Memory management for context retention
    - Task planning and decomposition
    - Multi-step problem solving
    - Learning from interactions
    """
    
    def __init__(self, model: str = None):
        """Initialize the planning agent with memory and planning systems."""
        # Define available tools
        tools = [
            analyze_code,
            lint_code,
            analyze_data,
            transform_data
        ]
        
        super().__init__(model=model, tools=tools)
        
        # Initialize memory and planning systems
        self.memory = Memory()
        self.planner = Planner()
        
        print(f"🧠 Planning Agent initialized with model: {self.model}")
        print(f"🔧 Available tools: {len(self.tools)}")
        print(f"💾 Memory system: {self.memory.get_stats()['total_items']} items")
        print(f"📋 Planning system: Ready for task decomposition")
        print()
        print("💡 This agent can remember, plan, and solve complex multi-step problems.")
        print()
    
    def run_with_memory(self, input_data: str) -> dict:
        """
        Run the agent with memory context.
        
        Args:
            input_data: User input to process
            
        Returns:
            Agent response with memory context
        """
        # Store the input in memory
        memory_id = self.memory.store(
            content=input_data,
            item_type="user_input",
            importance=0.7,
            metadata={"timestamp": time.time()}
        )
        
        # Get relevant context from memory
        context = self.memory.get_context(recent_count=3, important_count=2)
        
        # Enhance the input with context
        enhanced_input = f"""
Current input: {input_data}

Recent context:
{json.dumps(context['recent_memories'], indent=2)}

Important memories:
{json.dumps(context['important_memories'], indent=2)}
"""
        
        # Run the agent
        result = self.run(enhanced_input)
        
        # Store the result in memory
        self.memory.store(
            content=result,
            item_type="agent_response",
            importance=0.6,
            metadata={"input_id": memory_id, "timestamp": time.time()}
        )
        
        return result
    
    def create_and_execute_plan(self, goal: str) -> dict:
        """
        Create and execute a plan for achieving a goal.
        
        Args:
            goal: The goal to achieve
            
        Returns:
            Plan execution results
        """
        print(f"🎯 Creating plan for goal: {goal}")
        
        # Create a new plan
        plan_id = self.planner.create_plan(goal)
        
        # Store the plan in memory
        self.memory.store(
            content={"goal": goal, "plan_id": plan_id},
            item_type="plan",
            importance=0.9,
            metadata={"created_at": time.time()}
        )
        
        # Decompose the goal into subtasks
        subtasks = self._decompose_goal(goal)
        
        if subtasks:
            self.planner.decompose_task(plan_id, subtasks)
            print(f"📋 Plan created with {len(subtasks)} subtasks")
            
            # Execute the plan
            return self._execute_plan(plan_id)
        else:
            print("❌ Could not decompose goal into subtasks")
            return {"error": "Goal decomposition failed"}
    
    def _decompose_goal(self, goal: str) -> list:
        """
        Decompose a goal into subtasks using the LLM.
        
        Args:
            goal: The goal to decompose
            
        Returns:
            List of subtask definitions
        """
        prompt = f"""
Break down the following goal into 3-5 specific subtasks:

Goal: {goal}

For each subtask, provide:
- title: Brief description
- description: Detailed explanation
- priority: 1 (low), 2 (medium), 3 (high), 4 (critical)
- estimated_time: Time in minutes
- dependencies: List of subtask indices this depends on (empty if none)

Respond with a JSON array of subtasks.
"""
        
        try:
            response = self._call_llm(prompt)
            
            # Try to extract JSON from response
            if "[" in response and "]" in response:
                start = response.find("[")
                end = response.rfind("]") + 1
                json_str = response[start:end]
                
                subtasks = json.loads(json_str)
                
                # Validate and clean subtasks
                cleaned_subtasks = []
                for i, subtask in enumerate(subtasks):
                    if isinstance(subtask, dict):
                        cleaned_subtask = {
                            "title": subtask.get("title", f"Subtask {i+1}"),
                            "description": subtask.get("description", ""),
                            "priority": min(max(subtask.get("priority", 2), 1), 4),
                            "estimated_time": max(subtask.get("estimated_time", 5), 1),
                            "dependencies": subtask.get("dependencies", [])
                        }
                        cleaned_subtasks.append(cleaned_subtask)
                
                return cleaned_subtasks
            
        except Exception as e:
            print(f"⚠️  Goal decomposition failed: {e}")
        
        # Fallback: create basic subtasks
        return [
            {
                "title": "Analyze the goal",
                "description": "Understand and break down the goal into components",
                "priority": 3,
                "estimated_time": 5,
                "dependencies": []
            },
            {
                "title": "Execute the goal",
                "description": "Perform the main work to achieve the goal",
                "priority": 4,
                "estimated_time": 10,
                "dependencies": [0]
            },
            {
                "title": "Verify completion",
                "description": "Check that the goal has been achieved",
                "priority": 2,
                "estimated_time": 3,
                "dependencies": [1]
            }
        ]
    
    def _execute_plan(self, plan_id: str) -> dict:
        """
        Execute a plan step by step.
        
        Args:
            plan_id: ID of the plan to execute
            
        Returns:
            Plan execution results
        """
        print(f"🚀 Executing plan: {plan_id}")
        
        execution_results = []
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Get the next task to execute
            next_task = self.planner.get_next_task(plan_id)
            
            if not next_task:
                print("✅ All tasks completed!")
                break
            
            print(f"\n📋 Executing task: {next_task.title}")
            print(f"   Description: {next_task.description}")
            print(f"   Priority: {next_task.priority.name}")
            
            # Start the task
            if self.planner.start_task(next_task.id):
                print(f"   🚀 Task started")
                
                # Execute the task
                task_result = self._execute_task(next_task)
                
                # Mark task as completed
                self.planner.complete_task(next_task.id, task_result)
                
                print(f"   ✅ Task completed")
                
                # Store task result in memory
                self.memory.store(
                    content=task_result,
                    item_type="task_result",
                    importance=0.8,
                    metadata={
                        "task_id": next_task.id,
                        "task_title": next_task.title,
                        "plan_id": plan_id,
                        "timestamp": time.time()
                    }
                )
                
                execution_results.append({
                    "task_id": next_task.id,
                    "title": next_task.title,
                    "result": task_result,
                    "status": "completed"
                })
                
            else:
                print(f"   ❌ Failed to start task")
                execution_results.append({
                    "task_id": next_task.id,
                    "title": next_task.title,
                    "result": None,
                    "status": "failed_to_start"
                })
            
            # Small delay between tasks
            time.sleep(1)
        
        # Get final plan status
        plan_summary = self.planner.get_plan_summary(plan_id)
        
        return {
            "plan_id": plan_id,
            "execution_results": execution_results,
            "plan_summary": plan_summary,
            "iterations": iteration
        }
    
    def _execute_task(self, task) -> dict:
        """
        Execute a specific task.
        
        Args:
            task: The task to execute
            
        Returns:
            Task execution result
        """
        task_title = task.title.lower()
        
        try:
            if "analyze" in task_title:
                # Analyze some sample data or code
                sample_data = [1, 2, 3, 4, 5, "hello", "world"]
                result = analyze_data(sample_data)
                return {"action": "analyze", "data": sample_data, "result": result}
            
            elif "execute" in task_title or "perform" in task_title:
                # Perform some transformation
                sample_data = [1, 2, 3, 4, 5]
                result = transform_data(sample_data, "sort ascending")
                return {"action": "transform", "data": sample_data, "result": result}
            
            elif "verify" in task_title or "check" in task_title:
                # Verify something
                return {"action": "verify", "status": "success", "message": "Verification completed"}
            
            elif "code" in task_title:
                # Analyze some code
                sample_code = "def hello(): print('Hello, World!')"
                result = analyze_code(sample_code, "python")
                return {"action": "code_analysis", "code": sample_code, "result": result}
            
            else:
                # Generic task execution
                return {"action": "generic", "message": f"Executed: {task.title}"}
                
        except Exception as e:
            return {"action": "error", "error": str(e)}
    
    def demonstrate_memory(self):
        """Demonstrate memory capabilities."""
        print("💾 Demonstrating Memory System")
        print("=" * 50)
        
        # Store various types of information
        print("📝 Storing information in memory...")
        
        # Store user preferences
        self.memory.store(
            content="User prefers detailed explanations",
            item_type="user_preference",
            importance=0.8,
            metadata={"category": "communication_style"}
        )
        
        # Store technical knowledge
        self.memory.store(
            content="Python is the primary programming language",
            item_type="technical_knowledge",
            importance=0.9,
            metadata={"category": "programming", "language": "python"}
        )
        
        # Store recent conversation
        self.memory.store(
            content="User asked about AI agents",
            item_type="conversation",
            importance=0.6,
            metadata={"topic": "AI agents", "timestamp": time.time()}
        )
        
        print("✅ Information stored")
        print()
        
        # Demonstrate memory retrieval
        print("🔍 Retrieving information from memory...")
        
        # Search for specific information
        results = self.memory.retrieve(query="python", limit=5)
        print(f"  Found {len(results)} items related to 'python'")
        
        # Get context
        context = self.memory.get_context(recent_count=3, important_count=2)
        print(f"  Recent memories: {len(context['recent_memories'])}")
        print(f"  Important memories: {len(context['important_memories'])}")
        
        # Show memory statistics
        stats = self.memory.get_stats()
        print(f"  Total items: {stats['total_items']}")
        print(f"  Type distribution: {stats['type_distribution']}")
        
        print()
    
    def demonstrate_planning(self):
        """Demonstrate planning capabilities."""
        print("📋 Demonstrating Planning System")
        print("=" * 50)
        
        # Create and execute a simple plan
        goal = "Analyze and improve a Python function"
        print(f"🎯 Creating plan for: {goal}")
        
        result = self.create_and_execute_plan(goal)
        
        if "error" not in result:
            print("✅ Plan execution completed!")
            print(f"📊 Results: {len(result['execution_results'])} tasks executed")
            
            for task_result in result['execution_results']:
                status_emoji = "✅" if task_result['status'] == 'completed' else "❌"
                print(f"  {status_emoji} {task_result['title']}: {task_result['status']}")
            
            # Show plan summary
            plan_summary = result['plan_summary']
            progress = plan_summary.get('progress', {})
            print(f"\n📈 Plan Progress:")
            print(f"  Completion: {progress.get('completion_percentage', 0):.1f}%")
            print(f"  Total tasks: {progress.get('total_tasks', 0)}")
            print(f"  Completed: {progress.get('completed_tasks', 0)}")
            print(f"  Duration: {progress.get('plan_duration', 0):.1f} minutes")
        else:
            print(f"❌ Plan execution failed: {result['error']}")
        
        print()
    
    def demonstrate_multi_step_reasoning(self):
        """Demonstrate multi-step reasoning capabilities."""
        print("🧠 Demonstrating Multi-Step Reasoning")
        print("=" * 50)
        
        # Create a complex goal that requires multiple steps
        complex_goal = "Create a data analysis report with code review and recommendations"
        print(f"🎯 Complex goal: {complex_goal}")
        
        # This will demonstrate how the agent can break down complex tasks
        result = self.create_and_execute_plan(complex_goal)
        
        if "error" not in result:
            print("✅ Complex plan executed successfully!")
            
            # Show how the agent used memory and planning together
            print("\n🔍 How the agent used memory and planning:")
            
            # Get recent memories
            recent_memories = self.memory.retrieve(item_type="task_result", limit=5)
            print(f"  📝 Stored {len(recent_memories)} task results in memory")
            
            # Get plan information
            all_plans = self.planner.get_all_plans()
            print(f"  📋 Created {len(all_plans)} plans")
            
            for plan in all_plans:
                progress = plan.get('progress', {})
                print(f"    Plan '{plan['goal'][:30]}...': {progress.get('completion_percentage', 0):.1f}% complete")
        else:
            print(f"❌ Complex plan failed: {result['error']}")
        
        print()
    
    def run_interactive(self):
        """Run the agent in interactive mode."""
        print("🎯 Planning Agent is ready! Type 'quit' to exit.")
        print("Available commands:")
        print("  - 'demo memory': Demonstrate memory system")
        print("  - 'demo planning': Demonstrate planning system")
        print("  - 'demo reasoning': Demonstrate multi-step reasoning")
        print("  - 'plan <goal>': Create and execute a plan for a goal")
        print("  - 'remember <info>': Store information in memory")
        print("  - 'recall <query>': Search memory for information")
        print("=" * 70)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye! Thanks for trying the Planning Agent.")
                    break
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == 'demo memory':
                    self.demonstrate_memory()
                    continue
                elif user_input.lower() == 'demo planning':
                    self.demonstrate_planning()
                    continue
                elif user_input.lower() == 'demo reasoning':
                    self.demonstrate_multi_step_reasoning()
                    continue
                
                # Handle planning commands
                if user_input.lower().startswith('plan '):
                    goal = user_input[5:]  # Remove 'plan ' prefix
                    print(f"🎯 Creating plan for: {goal}")
                    result = self.create_and_execute_plan(goal)
                    
                    if "error" not in result:
                        print("✅ Plan completed!")
                        print(f"📊 Executed {len(result['execution_results'])} tasks")
                    else:
                        print(f"❌ Plan failed: {result['error']}")
                    continue
                
                # Handle memory commands
                if user_input.lower().startswith('remember '):
                    info = user_input[9:]  # Remove 'remember ' prefix
                    memory_id = self.memory.store(
                        content=info,
                        item_type="user_input",
                        importance=0.7,
                        metadata={"timestamp": time.time()}
                    )
                    print(f"💾 Stored in memory with ID: {memory_id}")
                    continue
                
                if user_input.lower().startswith('recall '):
                    query = user_input[7:]  # Remove 'recall ' prefix
                    print(f"🔍 Searching memory for: '{query}'")
                    results = self.memory.retrieve(query=query, limit=5)
                    
                    if results:
                        print(f"✅ Found {len(results)} items:")
                        for i, item in enumerate(results[:3], 1):
                            print(f"  {i}. {item.content[:100]}...")
                    else:
                        print("❌ No matching items found")
                    continue
                
                # Default: use the agent with memory
                print(f"🤔 Agent is thinking (with memory context)...")
                
                start_time = time.time()
                result = self.run_with_memory(user_input)
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
                
                # Show memory and planning stats
                memory_stats = self.memory.get_stats()
                print(f"📊 Memory: {memory_stats['total_items']} items, Tool calls: {self.get_stats()['tool_calls']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("🔄 Continuing...")


def main():
    """Main function to run the example."""
    print("🧠 AI Agent Demonstration - Example 3: Planning Agent with Memory")
    print("=" * 70)
    print()
    
    # Check configuration
    config = get_config()
    print(f"🔧 Configuration:")
    print(f"  Ollama URL: {config['ollama_base_url']}")
    print(f"  Default Model: {config['default_model']}")
    print(f"  Agent Timeout: {config['agent_timeout']} seconds")
    print(f"  Memory Max Items: {config['memory_max_size']}")
    print(f"  Planning Max Depth: {config['planning_max_depth']}")
    print()
    
    # Check if user wants to run demos or interactive mode
    print("Choose an option:")
    print("1. Run all demonstrations")
    print("2. Interactive mode (use memory and planning manually)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                agent = PlanningAgent()
                print("\n" + "="*70)
                agent.demonstrate_memory()
                print("\n" + "="*70)
                agent.demonstrate_planning()
                print("\n" + "="*70)
                agent.demonstrate_multi_step_reasoning()
                print("\n🎯 All demonstrations completed!")
                break
            elif choice == "2":
                agent = PlanningAgent()
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

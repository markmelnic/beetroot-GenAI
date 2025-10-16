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

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

# Add the current and parent directories to the path so we can import our modules
sys.path.extend([path for path in {CURRENT_DIR, PARENT_DIR} if path not in sys.path])

from agents.base_agent import BaseAgent
from agents.memory import Memory
from agents.planner import Planner, TaskStatus, TaskPriority
from tools.code_tools import analyze_code, lint_code
from tools.data_tools import analyze_data, transform_data
from config.settings import get_config
from console_layout import ConsoleLayout


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

        # Initialize helpers, memory, and planning systems
        self.console = ConsoleLayout(width=70)
        self.memory = Memory()
        self.planner = Planner()

        intro = self.console.compose(
            self.console.banner("Planning Agent Ready"),
            self.console.section(
                "Initialization Summary",
                self.console.key_values(
                    [
                        ("Model", self.model),
                        ("Registered tools", len(self.tools)),
                        ("Memory items", self.memory.get_stats()["total_items"]),
                        ("Planning status", "Ready for task decomposition"),
                    ]
                )
                + [
                    self.console.spacer(),
                    self.console.highlight(
                        "💡",
                        "This agent can remember, plan, and solve complex multi-step problems.",
                    ),
                ],
            ),
        )
        print(intro)
    
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
        log_lines = [self.console.highlight("🎯", f"Goal: {goal}")]

        # Create a new plan
        plan_id = self.planner.create_plan(goal)
        log_lines.extend(self.console.key_values([("Plan ID", plan_id)]))

        # Store the plan in memory
        self.memory.store(
            content={"goal": goal, "plan_id": plan_id},
            item_type="plan",
            importance=0.9,
            metadata={"created_at": time.time()}
        )

        # Decompose the goal into subtasks
        subtasks, decomposition_messages = self._decompose_goal(goal)
        log_lines.extend(decomposition_messages)

        if subtasks:
            self.planner.decompose_task(plan_id, subtasks)
            log_lines.append(
                self.console.highlight("📋", f"Plan created with {len(subtasks)} subtasks")
            )

            # Execute the plan
            execution = self._execute_plan(plan_id)
            log_lines.extend(execution.get("log_lines", []))
            execution["log_lines"] = log_lines
            return execution

        log_lines.append(self.console.highlight("❌", "Could not decompose goal into subtasks"))
        return {"error": "Goal decomposition failed", "plan_id": plan_id, "log_lines": log_lines}
    
    def _decompose_goal(self, goal: str) -> tuple[list, list[str]]:
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
        
        messages: list[str] = []

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
                
                return cleaned_subtasks, messages

        except Exception as e:
            messages.append(self.console.highlight("⚠️", f"Goal decomposition failed: {e}"))

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
        ], messages
    
    def _execute_plan(self, plan_id: str) -> dict:
        """
        Execute a plan step by step.
        
        Args:
            plan_id: ID of the plan to execute
            
        Returns:
            Plan execution results
        """
        log_lines = [self.console.highlight("🚀", f"Executing plan: {plan_id}")]
        execution_results = []
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            
            # Get the next task to execute
            next_task = self.planner.get_next_task(plan_id)
            
            if not next_task:
                log_lines.append(self.console.highlight("✅", "All tasks completed!"))
                break

            log_lines.append(self.console.spacer())
            log_lines.append(self.console.highlight("📋", f"Executing task: {next_task.title}"))
            log_lines.extend(
                self.console.key_values(
                    [
                        ("Description", next_task.description),
                        ("Priority", next_task.priority.name),
                    ]
                )
            )

            # Start the task
            if self.planner.start_task(next_task.id):
                log_lines.append(self.console.highlight("🚀", "Task started"))

                # Execute the task
                task_result = self._execute_task(next_task)

                # Mark task as completed
                self.planner.complete_task(next_task.id, task_result)
                log_lines.append(self.console.highlight("✅", "Task completed"))

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
                log_lines.append(self.console.highlight("❌", "Failed to start task"))
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
            "iterations": iteration,
            "log_lines": log_lines,
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
        lines = [self.console.highlight("📝", "Storing information in memory...")]
        
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
        
        lines.append(self.console.highlight("✅", "Information stored"))
        lines.append(self.console.spacer())
        lines.append(self.console.highlight("🔍", "Retrieving information from memory..."))

        results = self.memory.retrieve(query="python", limit=5)
        context = self.memory.get_context(recent_count=3, important_count=2)
        stats = self.memory.get_stats()

        lines.extend(
            self.console.key_values(
                [
                    ("Matches for 'python'", len(results)),
                    ("Recent memories", len(context["recent_memories"])),
                    ("Important memories", len(context["important_memories"])),
                    ("Total stored items", stats["total_items"]),
                    ("Type distribution", stats["type_distribution"]),
                ]
            )
        )

        print(
            self.console.compose(
                self.console.section("Memory System Demonstration", lines)
            )
        )
    
    def demonstrate_planning(self):
        """Demonstrate planning capabilities."""
        goal = "Analyze and improve a Python function"
        result = self.create_and_execute_plan(goal)

        lines = result.get("log_lines", [])

        if "error" not in result:
            lines.append(self.console.spacer())
            lines.append(self.console.highlight("✅", "Plan execution completed"))
            lines.extend(
                self.console.key_values(
                    [("Executed tasks", len(result["execution_results"]))]
                )
            )

            task_lines: list[str] = []
            for task_result in result["execution_results"]:
                status_emoji = "✅" if task_result["status"] == "completed" else "❌"
                task_lines.extend(
                    self.console.bullet_list(
                        [f"{status_emoji} {task_result['title']} ({task_result['status']})"],
                        bullet="-",
                    )
                )

            if task_lines:
                lines.append(self.console.spacer())
                lines.append(self.console.highlight("🗂️", "Task results"))
                lines.extend(task_lines)

            plan_summary = result["plan_summary"]
            progress = plan_summary.get("progress", {})
            lines.append(self.console.spacer())
            lines.append(self.console.highlight("📈", "Plan progress"))
            lines.extend(
                self.console.key_values(
                    [
                        ("Completion", f"{progress.get('completion_percentage', 0):.1f}%"),
                        ("Total tasks", progress.get("total_tasks", 0)),
                        ("Completed", progress.get("completed_tasks", 0)),
                        ("Duration", f"{progress.get('plan_duration', 0):.1f} minutes"),
                    ]
                )
            )
        else:
            lines.append(self.console.spacer())
            lines.append(self.console.highlight("❌", f"Plan execution failed: {result['error']}"))

        print(
            self.console.compose(
                self.console.section("Planning System Demonstration", lines)
            )
        )
    
    def demonstrate_multi_step_reasoning(self):
        """Demonstrate multi-step reasoning capabilities."""
        complex_goal = "Create a data analysis report with code review and recommendations"
        result = self.create_and_execute_plan(complex_goal)

        lines = result.get("log_lines", [])

        if "error" not in result:
            lines.append(self.console.spacer())
            lines.append(self.console.highlight("✅", "Complex plan executed successfully"))

            recent_memories = self.memory.retrieve(item_type="task_result", limit=5)
            all_plans = self.planner.get_all_plans()

            lines.append(self.console.spacer())
            lines.append(self.console.highlight("🔍", "How memory and planning were used"))
            lines.extend(
                self.console.bullet_list(
                    [
                        f"📝 Stored {len(recent_memories)} recent task results",
                        f"📋 Created {len(all_plans)} plans",
                    ],
                    bullet="-",
                )
            )

            plan_progress_lines: list[str] = []
            for plan in all_plans:
                progress = plan.get('progress', {})
                plan_progress_lines.extend(
                    self.console.bullet_list(
                        [
                            f"Plan '{plan['goal'][:30]}...' - {progress.get('completion_percentage', 0):.1f}% complete",
                        ],
                        bullet="•",
                    )
                )
            if plan_progress_lines:
                lines.append(self.console.spacer())
                lines.append(self.console.highlight("📊", "Plan progress overview"))
                lines.extend(plan_progress_lines)
        else:
            lines.append(self.console.spacer())
            lines.append(self.console.highlight("❌", f"Complex plan failed: {result['error']}"))

        print(
            self.console.compose(
                self.console.section("Multi-Step Reasoning Demonstration", lines)
            )
        )
    
    def run_interactive(self):
        """Run the agent in interactive mode."""
        intro = self.console.compose(
            self.console.banner("Planning Agent Interactive Mode"),
            self.console.section(
                "Available Commands",
                self.console.bullet_list(
                    [
                        "Type 'quit' to exit",
                        "'demo memory' to demonstrate memory system",
                        "'demo planning' to demonstrate planning system",
                        "'demo reasoning' to demonstrate multi-step reasoning",
                        "'plan <goal>' to create and execute a plan",
                        "'remember <info>' to store information",
                        "'recall <query>' to search memory",
                    ],
                    bullet="-",
                ),
            ),
        )
        print(intro)

        while True:
            try:
                user_input = input("\n👤 You: ").strip()

                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print(
                        self.console.section(
                            "Session Closed",
                            [self.console.highlight("👋", "Goodbye! Thanks for trying the Planning Agent.")],
                        )
                    )
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
                    result = self.create_and_execute_plan(goal)
                    lines = result.get("log_lines", [])

                    if "error" in result:
                        lines.append(self.console.spacer())
                        lines.append(self.console.highlight("❌", f"Plan failed: {result['error']}"))
                    else:
                        lines.append(self.console.spacer())
                        lines.append(self.console.highlight("✅", "Plan completed"))
                        lines.extend(
                            self.console.key_values(
                                [("Executed tasks", len(result["execution_results"]))]
                            )
                        )

                    print(
                        self.console.section(
                            "Custom Plan",
                            lines,
                        )
                    )
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
                    print(
                        self.console.section(
                            "Memory Update",
                            [self.console.highlight("💾", f"Stored information with ID: {memory_id}")],
                        )
                    )
                    continue

                if user_input.lower().startswith('recall '):
                    query = user_input[7:]  # Remove 'recall ' prefix
                    results = self.memory.retrieve(query=query, limit=5)
                    lines = [self.console.highlight("🔍", f"Results for '{query}'")]

                    if results:
                        lines.append(self.console.highlight("✅", f"Found {len(results)} items"))
                        preview = [f"{i}. {item.content[:100]}..." for i, item in enumerate(results[:3], 1)]
                        lines.extend(self.console.bullet_list(preview, bullet="•"))
                    else:
                        lines.append(self.console.highlight("❌", "No matching items found"))

                    print(self.console.section("Memory Search", lines))
                    continue

                # Default: use the agent with memory
                start_time = time.time()
                result = self.run_with_memory(user_input)
                end_time = time.time()

                response_time = end_time - start_time
                memory_stats = self.memory.get_stats()
                stats = self.get_stats()

                response_lines: list[str] = []
                if "error" in result:
                    response_lines.append(self.console.highlight("❌", f"Error: {result['error']}"))
                elif "response" in result:
                    response_lines.extend(
                        self.console.key_values([("Response", result["response"])]))
                else:
                    response_lines.append(self.console.highlight("🤷", "No response generated"))

                response_lines.append(self.console.spacer())
                response_lines.extend(
                    self.console.key_values(
                        [
                            ("Response time", f"{response_time:.2f} seconds"),
                            ("Memory items", memory_stats["total_items"]),
                            ("Tool calls", stats.get("tool_calls", 0)),
                        ]
                    )
                )

                print(self.console.section("Agent Response", response_lines))

            except KeyboardInterrupt:
                print(
                    self.console.section(
                        "Session Closed",
                        [self.console.highlight("👋", "Interrupted by user. Goodbye!")],
                    )
                )
                break
            except Exception as e:
                print(
                    self.console.section(
                        "Warning",
                        [
                            self.console.highlight("❌", f"Unexpected error: {e}"),
                            self.console.highlight("🔄", "Continuing..."),
                        ],
                    )
                )


def main():
    """Main function to run the example."""
    console = ConsoleLayout(width=70)

    config = get_config()
    header = console.compose(
        console.banner("AI Agent Demonstration", "Example 3: Planning Agent with Memory"),
        console.section(
            "Configuration",
            console.key_values(
                [
                    ("Ollama URL", config['ollama_base_url']),
                    ("Default Model", config['default_model']),
                    ("Agent Timeout", f"{config['agent_timeout']} seconds"),
                    ("Memory Max Items", config['memory_max_size']),
                    ("Planning Max Depth", config['planning_max_depth']),
                ]
            ),
        ),
        console.section(
            "Choose an Option",
            console.bullet_list(
                [
                    "1. Run all demonstrations",
                    "2. Interactive mode (use memory and planning manually)",
                    "3. Exit",
                ],
                bullet="•",
            ),
        ),
    )
    print(header)

    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()

            if choice == "1":
                agent = PlanningAgent()
                print(
                    console.section(
                        "Demonstrations",
                        [console.highlight("🚀", "Running memory, planning, and reasoning demos...")],
                    )
                )
                agent.demonstrate_memory()
                agent.demonstrate_planning()
                agent.demonstrate_multi_step_reasoning()
                print(
                    console.section(
                        "Demonstrations",
                        [console.highlight("🎯", "All demonstrations completed!")],
                    )
                )
                break
            elif choice == "2":
                agent = PlanningAgent()
                agent.run_interactive()
                break
            elif choice == "3":
                print(console.section("Goodbye", [console.highlight("👋", "See you next time!")]))
                break
            else:
                print(
                    console.section(
                        "Invalid Choice",
                        [console.highlight("❌", "Please enter 1, 2, or 3.")],
                    )
                )

        except KeyboardInterrupt:
            print(console.section("Goodbye", [console.highlight("👋", "Interrupted by user. Goodbye!")]))
            break
        except Exception as e:
            print(
                console.section(
                    "Warning",
                    [
                        console.highlight("❌", f"Error: {e}"),
                        console.highlight("🔄", "Please try again."),
                    ],
                )
            )


if __name__ == "__main__":
    main()

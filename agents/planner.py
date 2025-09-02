"""
Planning system for AI agents.
Breaks down complex tasks into smaller, manageable steps and tracks progress.
"""

import time
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from config.settings import get_config

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of a planning task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class PlanningTask:
    """Represents a single planning task."""
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    estimated_time: float = 0.0  # in minutes
    actual_time: float = 0.0     # in minutes
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_ready(self, completed_tasks: List[str]) -> bool:
        """Check if all dependencies are completed."""
        return all(dep in completed_tasks for dep in self.dependencies)
    
    def can_start(self, completed_tasks: List[str]) -> bool:
        """Check if task can start (dependencies met and not already started)."""
        return (self.status == TaskStatus.PENDING and 
                self.is_ready(completed_tasks))
    
    def start(self):
        """Mark task as started."""
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.IN_PROGRESS
            self.started_at = time.time()
            logger.info(f"Started task: {self.title}")
    
    def complete(self, result: Any = None):
        """Mark task as completed."""
        if self.status == TaskStatus.IN_PROGRESS:
            self.status = TaskStatus.COMPLETED
            self.completed_at = time.time()
            self.actual_time = (self.completed_at - self.started_at) / 60.0  # Convert to minutes
            self.result = result
            logger.info(f"Completed task: {self.title}")
    
    def fail(self, error: str):
        """Mark task as failed."""
        if self.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
            self.status = TaskStatus.FAILED
            self.error = error
            if self.started_at:
                self.actual_time = (time.time() - self.started_at) / 60.0
            logger.error(f"Failed task: {self.title} - {error}")
    
    def skip(self, reason: str = "Not needed"):
        """Mark task as skipped."""
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.SKIPPED
            self.metadata["skip_reason"] = reason
            logger.info(f"Skipped task: {self.title} - {reason}")


class Planner:
    """
    Planning system for AI agents.
    
    Features:
    - Task decomposition and dependency management
    - Priority-based scheduling
    - Progress tracking and estimation
    - Adaptive planning based on results
    """
    
    def __init__(self, max_depth: int = None, timeout: int = None):
        """
        Initialize the planner.
        
        Args:
            max_depth: Maximum depth for task decomposition
            timeout: Planning timeout in seconds
        """
        config = get_config()
        self.max_depth = max_depth or config["planning_max_depth"]
        self.timeout = timeout or config["planning_timeout"]
        
        # Planning state
        self.tasks: Dict[str, PlanningTask] = {}
        self.task_counter = 0
        self.plan_start_time = None
        self.plan_status = TaskStatus.PENDING
        
        logger.info(f"Planner initialized with max_depth={self.max_depth}, timeout={self.timeout}")
    
    def create_plan(self, goal: str, context: Dict[str, Any] = None) -> str:
        """
        Create a new plan for achieving a goal.
        
        Args:
            goal: The goal to achieve
            context: Additional context information
            
        Returns:
            Plan ID
        """
        plan_id = f"plan_{int(time.time())}_{self.task_counter}"
        self.task_counter += 1
        
        # Create root task
        root_task = PlanningTask(
            id=plan_id,
            title="Achieve Goal",
            description=goal,
            priority=TaskPriority.HIGH,
            metadata={"goal": goal, "context": context or {}}
        )
        
        self.tasks[plan_id] = root_task
        self.plan_start_time = time.time()
        self.plan_status = TaskStatus.PENDING
        
        logger.info(f"Created plan: {plan_id} for goal: {goal}")
        return plan_id
    
    def decompose_task(self, task_id: str, subtasks: List[Dict[str, Any]]) -> List[str]:
        """
        Break down a task into subtasks.
        
        Args:
            task_id: ID of the task to decompose
            subtasks: List of subtask definitions
            
        Returns:
            List of created subtask IDs
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        parent_task = self.tasks[task_id]
        if len(parent_task.subtasks) > 0:
            logger.warning(f"Task {task_id} already has subtasks")
            return parent_task.subtasks
        
        created_subtasks = []
        
        for i, subtask_def in enumerate(subtasks):
            subtask_id = f"{task_id}_sub_{i}"
            
            subtask = PlanningTask(
                id=subtask_id,
                title=subtask_def.get("title", f"Subtask {i}"),
                description=subtask_def.get("description", ""),
                priority=TaskPriority(subtask_def.get("priority", TaskPriority.MEDIUM.value)),
                dependencies=subtask_def.get("dependencies", []),
                estimated_time=subtask_def.get("estimated_time", 0.0),
                metadata=subtask_def.get("metadata", {})
            )
            
            self.tasks[subtask_id] = subtask
            created_subtasks.append(subtask_id)
        
        # Update parent task
        parent_task.subtasks = created_subtasks
        
        logger.info(f"Decomposed task {task_id} into {len(created_subtasks)} subtasks")
        return created_subtasks
    
    def get_next_task(self, plan_id: str) -> Optional[PlanningTask]:
        """
        Get the next task that can be executed.
        
        Args:
            plan_id: ID of the plan
            
        Returns:
            Next available task or None
        """
        if plan_id not in self.tasks:
            return None
        
        # Get all tasks in the plan
        plan_tasks = self._get_plan_tasks(plan_id)
        
        # Find tasks that are ready to start
        ready_tasks = []
        completed_tasks = [t.id for t in plan_tasks if t.status == TaskStatus.COMPLETED]
        
        for task in plan_tasks:
            if task.can_start(completed_tasks):
                ready_tasks.append(task)
        
        if not ready_tasks:
            return None
        
        # Sort by priority and creation time
        ready_tasks.sort(key=lambda t: (t.priority.value, t.created_at))
        
        return ready_tasks[0]
    
    def start_task(self, task_id: str) -> bool:
        """
        Start executing a task.
        
        Args:
            task_id: ID of the task to start
            
        Returns:
            True if task was started successfully
        """
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        task = self.tasks[task_id]
        
        if not task.can_start(self._get_completed_task_ids()):
            logger.warning(f"Task {task_id} is not ready to start")
            return False
        
        task.start()
        return True
    
    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """
        Mark a task as completed.
        
        Args:
            task_id: ID of the task to complete
            result: Result of the task execution
            
        Returns:
            True if task was completed successfully
        """
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        task = self.tasks[task_id]
        
        if task.status != TaskStatus.IN_PROGRESS:
            logger.warning(f"Task {task_id} is not in progress")
            return False
        
        task.complete(result)
        
        # Check if plan is complete
        self._check_plan_completion()
        
        return True
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """
        Mark a task as failed.
        
        Args:
            task_id: ID of the task to mark as failed
            error: Error description
            
        Returns:
            True if task was marked as failed successfully
        """
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        task = self.tasks[task_id]
        task.fail(error)
        
        # Check if plan should be abandoned
        if task.priority == TaskPriority.CRITICAL:
            self.plan_status = TaskStatus.FAILED
            logger.error(f"Critical task failed, abandoning plan")
        
        return True
    
    def skip_task(self, task_id: str, reason: str = "Not needed") -> bool:
        """
        Mark a task as skipped.
        
        Args:
            task_id: ID of the task to skip
            reason: Reason for skipping
            
        Returns:
            True if task was skipped successfully
        """
        if task_id not in self.tasks:
            logger.error(f"Task {task_id} not found")
            return False
        
        task = self.tasks[task_id]
        task.skip(reason)
        
        # Check if plan is complete
        self._check_plan_completion()
        
        return True
    
    def get_plan_progress(self, plan_id: str) -> Dict[str, Any]:
        """
        Get progress information for a plan.
        
        Args:
            plan_id: ID of the plan
            
        Returns:
            Progress information dictionary
        """
        if plan_id not in self.tasks:
            return {}
        
        plan_tasks = self._get_plan_tasks(plan_id)
        
        total_tasks = len(plan_tasks)
        completed_tasks = len([t for t in plan_tasks if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in plan_tasks if t.status == TaskStatus.FAILED])
        skipped_tasks = len([t for t in plan_tasks if t.status == TaskStatus.SKIPPED])
        in_progress_tasks = len([t for t in plan_tasks if t.status == TaskStatus.IN_PROGRESS])
        
        # Calculate time estimates
        total_estimated = sum(t.estimated_time for t in plan_tasks)
        total_actual = sum(t.actual_time for t in plan_tasks if t.actual_time > 0)
        
        progress = {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "skipped_tasks": skipped_tasks,
            "in_progress_tasks": in_progress_tasks,
            "pending_tasks": total_tasks - completed_tasks - failed_tasks - skipped_tasks - in_progress_tasks,
            "completion_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "total_estimated_time": total_estimated,
            "total_actual_time": total_actual,
            "plan_status": self.plan_status.value,
            "plan_duration": (time.time() - self.plan_start_time) / 60.0 if self.plan_start_time else 0
        }
        
        return progress
    
    def get_plan_summary(self, plan_id: str) -> Dict[str, Any]:
        """
        Get a summary of the plan execution.
        
        Args:
            plan_id: ID of the plan
            
        Returns:
            Plan summary dictionary
        """
        if plan_id not in self.tasks:
            return {}
        
        plan_tasks = self._get_plan_tasks(plan_id)
        progress = self.get_plan_progress(plan_id)
        
        # Group tasks by status
        tasks_by_status = {}
        for status in TaskStatus:
            tasks_by_status[status.value] = [t.id for t in plan_tasks if t.status == status]
        
        # Get task details
        task_details = {}
        for task in plan_tasks:
            task_details[task.id] = {
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "dependencies": task.dependencies,
                "estimated_time": task.estimated_time,
                "actual_time": task.actual_time,
                "result": task.result,
                "error": task.error,
                "metadata": task.metadata
            }
        
        summary = {
            "plan_id": plan_id,
            "goal": self.tasks[plan_id].description,
            "progress": progress,
            "tasks_by_status": tasks_by_status,
            "task_details": task_details,
            "created_at": self.tasks[plan_id].created_at,
            "plan_duration": progress["plan_duration"]
        }
        
        return summary
    
    def _get_plan_tasks(self, plan_id: str) -> List[PlanningTask]:
        """Get all tasks that belong to a plan."""
        if plan_id not in self.tasks:
            return []
        
        # Find all tasks that are part of this plan
        plan_tasks = []
        root_task = self.tasks[plan_id]
        plan_tasks.append(root_task)
        
        # Add all subtasks recursively
        self._add_subtasks_recursive(plan_id, plan_tasks)
        
        return plan_tasks
    
    def _add_subtasks_recursive(self, parent_id: str, task_list: List[PlanningTask]):
        """Recursively add subtasks to the task list."""
        parent_task = self.tasks[parent_id]
        
        for subtask_id in parent_task.subtasks:
            if subtask_id in self.tasks:
                subtask = self.tasks[subtask_id]
                task_list.append(subtask)
                # Recursively add subtasks of this subtask
                self._add_subtasks_recursive(subtask_id, task_list)
    
    def _get_completed_task_ids(self) -> List[str]:
        """Get IDs of all completed tasks."""
        return [t.id for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
    
    def _check_plan_completion(self):
        """Check if the current plan is complete."""
        # Get all tasks
        all_tasks = list(self.tasks.values())
        
        if not all_tasks:
            return
        
        # Check if all non-skipped tasks are completed
        non_skipped_tasks = [t for t in all_tasks if t.status != TaskStatus.SKIPPED]
        
        if all(t.status == TaskStatus.COMPLETED for t in non_skipped_tasks):
            self.plan_status = TaskStatus.COMPLETED
            logger.info("Plan completed successfully")
        elif any(t.status == TaskStatus.FAILED for t in all_tasks):
            self.plan_status = TaskStatus.FAILED
            logger.error("Plan failed due to task failures")
    
    def cleanup_old_plans(self, older_than_hours: int = 24):
        """Remove old completed or failed plans."""
        cutoff_time = time.time() - (older_than_hours * 3600)
        
        plans_to_remove = []
        for task_id, task in self.tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and 
                task.completed_at and task.completed_at < cutoff_time):
                plans_to_remove.append(task_id)
        
        for plan_id in plans_to_remove:
            del self.tasks[plan_id]
        
        if plans_to_remove:
            logger.info(f"Cleaned up {len(plans_to_remove)} old plans")
    
    def get_all_plans(self) -> List[Dict[str, Any]]:
        """Get summary of all plans."""
        plans = []
        
        for task_id, task in self.tasks.items():
            if not task.subtasks:  # This is a root task (plan)
                plan_summary = self.get_plan_summary(task_id)
                plans.append(plan_summary)
        
        return plans

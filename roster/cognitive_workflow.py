"""Execute provider-produced cognitive workflows through Roster's existing safety pipeline."""
from __future__ import annotations

import inspect
import re

from roster.cancel import CancellationToken
from roster.cognitive_planner import CognitivePlanner
from roster.execution_verifier import ExecutionVerifier
from roster.goal_state import GoalStateEngine
from roster.models import Action, Intent
from roster.security import PermissionGate
from roster.workflow_trust import (
    WorkflowResultReference,
    validate_result_reference,
)


_RESULT_RE = re.compile(r"\$RESULT:([^\s]+)")


class WorkflowVerificationError(RuntimeError):
    def __init__(self, task_name, status, evidence, execution):
        super().__init__(f"workflow step '{task_name}' verification {status}: {evidence}")
        self.task_name = task_name
        self.status = status
        self.evidence = evidence
        self.execution = list(execution)


class WorkflowGoalStateError(RuntimeError):
    def __init__(self, task_name, status, evidence, execution):
        super().__init__(f"workflow step '{task_name}' goal-state {status}: {evidence}")
        self.task_name = task_name
        self.status = status
        self.evidence = evidence
        self.execution = list(execution)


class WorkflowPermissionDenied(RuntimeError):
    pass


class CognitiveWorkflowExecutor:
    def __init__(self, tools, permissions=None, verifier=None, max_tasks=8):
        if max_tasks < 1:
            raise ValueError("max_tasks must be positive")
        self.tools = tools
        self.permissions = permissions or PermissionGate()
        self.verifier = verifier or ExecutionVerifier()
        self.max_tasks = max_tasks
        self.planner = CognitivePlanner()
        self.goal_state = GoalStateEngine()

    def execute(self, raw_steps, goal, provider, *, cancellation=None):
        if not isinstance(raw_steps, list) or len(raw_steps) > self.max_tasks:
            raise ValueError(f"workflow must contain 1-{self.max_tasks} steps")

        graph = self.planner.from_specs(raw_steps)
        completed = set()
        outputs = {}
        execution = []

        while len(completed) < len(graph.plan.steps):
            token = cancellation or CancellationToken()
            token.raise_if_cancelled()
            ready = graph.ready(completed)
            if not ready:
                raise RuntimeError("cognitive workflow cannot make progress")

            step = ready[0]
            task = step.task
            metadata = dict(task.metadata)
            action_name = str(metadata.get("action", "")).strip().lower()
            if not action_name:
                raise ValueError(f"task '{task.name}' has no action")

            try:
                action = Action(action_name)
            except ValueError as exc:
                raise ValueError(f"task '{task.name}' has invalid action: {action_name}") from exc

            argument = str(metadata.get("argument", task.input))
            argument = self._resolve_results(argument, outputs, graph, action)
            intent = Intent(action=action, argument=argument, metadata=metadata)

            confirmed = False
            if self.permissions.requires_confirmation(action, self.tools.registry):
                if not self.permissions.request(intent):
                    execution.append({
                        "task": task.name,
                        "action": action.value,
                        "argument": argument,
                        "result": "permission denied",
                        "verification": "denied",
                    })
                    raise WorkflowPermissionDenied(
                        f"permission denied for workflow step '{task.name}'"
                    )
                confirmed = True

            token.raise_if_cancelled()
            execute_parameters = inspect.signature(self.tools.execute).parameters
            kwargs = {}
            if "cancellation" in execute_parameters:
                kwargs["cancellation"] = token
            if "confirmed" in execute_parameters:
                kwargs["confirmed"] = confirmed

            running, result = self.tools.execute(intent, goal, provider, **kwargs)
            token.raise_if_cancelled()
            result_text = str(result)
            verification = self.verifier.verify(
                intent, result, goal=goal, provider=provider
            )

            execution.append({
                "task": task.name,
                "action": action.value,
                "argument": argument,
                "result": result_text[:2000],
                "verification": verification.status,
            })

            verified = getattr(
                verification,
                "verified",
                str(getattr(verification, "status", "")).lower() == "verified",
            )
            if not verified:
                raise WorkflowVerificationError(
                    task.name, verification.status, verification.evidence, execution
                )

            expected_state = self.goal_state.parse(metadata.get("expected_state"))
            if expected_state is not None:
                evaluation = self.goal_state.evaluate(
                    expected_state,
                    result=result_text,
                )
                execution[-1]["goal_state"] = evaluation.status
                execution[-1]["goal_state_evidence"] = evaluation.evidence
                if not evaluation.satisfied:
                    raise WorkflowGoalStateError(
                        task.name,
                        evaluation.status,
                        evaluation.evidence,
                        execution,
                    )

            outputs[task.id] = result_text
            outputs[task.name] = result_text
            completed.add(task.id)
            if not running and action is Action.EXIT:
                break

        final = execution[-1]["result"] if execution else "Workflow completed."
        return False, final, execution

    @staticmethod
    def _resolve_results(argument, outputs, graph, action):
        def replace(match):
            key = match.group(1)
            reference = WorkflowResultReference(key)
            validate_result_reference(action, reference)
            if key.isdigit() and 1 <= int(key) <= len(graph.specs):
                task = graph.plan.steps[int(key) - 1].task
                if task.id not in outputs:
                    raise ValueError(f"workflow result '{key}' is not available")
                return outputs[task.id]
            if key not in outputs:
                raise ValueError(f"workflow result '{key}' is not available")
            return outputs[key]

        return _RESULT_RE.sub(replace, argument)

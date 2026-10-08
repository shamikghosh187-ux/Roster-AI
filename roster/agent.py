from roster.memory import ConversationMemory
from roster.models import Action
from roster.security import PermissionGate
from roster.trace import ExecutionTrace
from roster.state import AgentState, StateMachine
from roster.cancel import CancellationToken, CancelledError
from roster.execution_verifier import ExecutionVerifier
from roster.intelligent_memory import IntelligentMemory
import inspect

from roster.cognitive_workflow import CognitiveWorkflowExecutor
from roster.cognitive_planner import CognitivePlanner
from roster.adaptive_recovery import AdaptiveRecovery


class Agent:
    def __init__(self, provider, tools, memory=None, permissions=None, max_steps=5, trace=None, verifier=None, intelligent_memory=None):
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        self.provider = provider
        self.tools = tools
        self.memory = memory or ConversationMemory()
        self.permissions = permissions or PermissionGate()
        self.max_steps = max_steps
        self.trace = trace or ExecutionTrace()
        self.verifier = verifier or ExecutionVerifier()
        self.intelligent_memory = intelligent_memory
        self.state = StateMachine()
        self.cognitive_recovery = AdaptiveRecovery(
            self.provider,
            CognitivePlanner(),
            max_replans=2,
            memory=self.intelligent_memory,
        )
        self.cognitive_workflow = CognitiveWorkflowExecutor(
            self.tools,
            self.permissions,
            self.verifier,
            max_tasks=max(1, max_steps * 2),
        )

    def _try_cognitive_workflow(self, goal, cancellation):
        """Run a bounded cognitive workflow with adaptive recovery on verification failures."""
        token = cancellation or CancellationToken()
        raw_steps = None
        history = []
        max_attempts = self.cognitive_recovery.max_replans + 1

        for attempt in range(max_attempts):
            token.raise_if_cancelled()
            if raw_steps is None:
                try:
                    raw_steps = self.provider.workflow_plan(
                        goal,
                        self.memory.as_messages(),
                        tool_descriptions=self.tools.registry.descriptions(),
                    )
                except Exception as planning_error:
                    self.trace.record(
                        "cognitive_replan_requested",
                        reason=type(planning_error).__name__,
                    )
                    graph = self.cognitive_recovery.replan(
                        goal, history, planning_error, attempt=min(attempt, self.cognitive_recovery.max_replans - 1)
                    )
                    raw_steps = [
                        {
                            "name": spec.name,
                            "input": spec.input,
                            "depends_on": list(spec.depends_on),
                            "priority": spec.priority,
                            "metadata": dict(spec.metadata or {}),
                        }
                        for spec in graph.specs
                    ]

            if not isinstance(raw_steps, list) or len(raw_steps) <= 1:
                return None

            self.trace.record(
                "cognitive_workflow_planned",
                steps=len(raw_steps),
                attempt=attempt + 1,
            )
            try:
                running, result, execution = self.cognitive_workflow.execute(
                    raw_steps,
                    goal,
                    self.provider,
                    cancellation=token,
                )
                history.extend(execution[-8:])
                for item in execution:
                    self.trace.record(
                        "cognitive_task_finished",
                        task=item["task"],
                        action=item["action"],
                        verification=item["verification"],
                        result=item["result"][:500],
                    )
                    self.memory.add(
                        "assistant",
                        f"[cognitive:{item['action']}] {item['result'][:1000]}",
                    )
                self.trace.record(
                    "cognitive_workflow_finished",
                    status="completed",
                    steps=len(execution),
                    attempts=attempt + 1,
                )
                if self.intelligent_memory:
                    self.intelligent_memory.record_experience(
                        goal,
                        str(result),
                        [item["action"] for item in execution],
                    )
                self.memory.add("assistant", result)
                self.state.move(AgentState.COMPLETED)
                return running, result
            except CancelledError:
                raise
            except Exception as failure:
                partial = getattr(failure, "execution", [])
                history.extend(partial[-8:])
                if self.intelligent_memory:
                    strategy = self.cognitive_recovery.strategy_selector.choose(
                        goal, str(failure)[:500]
                    ).strategy.value
                    self.intelligent_memory.record_failure(
                        goal,
                        str(failure)[:500],
                        [item.get("action", "") for item in partial[-6:]],
                    )
                    self.intelligent_memory.record_recovery_outcome(
                        goal,
                        str(failure)[:500],
                        strategy,
                        False,
                        getattr(failure, "evidence", str(failure)),
                    )
                if attempt >= self.cognitive_recovery.max_replans:
                    raise
                self.trace.record(
                    "cognitive_recovery",
                    attempt=attempt + 1,
                    failure=type(failure).__name__,
                )
                graph = self.cognitive_recovery.replan(
                    goal,
                    history,
                    failure,
                    attempt=attempt,
                )
                raw_steps = [
                    {
                        "name": spec.name,
                        "input": spec.input,
                        "depends_on": list(spec.depends_on),
                        "priority": spec.priority,
                        "metadata": dict(spec.metadata or {}),
                    }
                    for spec in graph.specs
                ]

        return None

    def handle(self, user_text, cancellation=None):
        token = cancellation or CancellationToken()
        self.state.reset()
        self.trace.clear()
        self.trace.record("request_started", user_text=user_text)
        self.state.move(AgentState.PLANNING)
        self.memory.add("user", user_text)
        if self.intelligent_memory:
            self.intelligent_memory.learn_from_user(user_text)
        goal = user_text.strip()

        # Prefer the cognitive graph for genuinely multi-step requests. If a
        # provider cannot produce a valid structured workflow, retain the
        # proven single-action loop as a safe compatibility fallback.
        try:
            workflow_result = self._try_cognitive_workflow(goal, token)
            if workflow_result is not None:
                return workflow_result
        except CancelledError:
            raise
        except Exception as exc:
            self.trace.record(
                "cognitive_workflow_fallback",
                error=type(exc).__name__,
            )
            self.memory.add(
                "assistant",
                f"[cognitive_workflow_fallback:{type(exc).__name__}]",
            )
            if self.intelligent_memory:
                self.intelligent_memory.record_failure(
                    goal,
                    f"{type(exc).__name__}: {str(exc)[:500]}",
                )

        goal = user_text.strip()
        current_request = goal
        execution_history = []
        seen_actions = set()
        try:
            for step in range(self.max_steps):
                token.raise_if_cancelled()
                if step > 0:
                    self.state.move(AgentState.PLANNING)

                self.trace.record(
                    "planning",
                    step=step + 1,
                    goal=goal,
                    history_size=len(execution_history),
                )
                planning_request = current_request
                if self.intelligent_memory:
                    recalled = self.intelligent_memory.context(goal + " " + current_request)
                    if recalled:
                        planning_request = f"{current_request}\n\n{recalled}"
                intent = self.provider.plan(
                    planning_request,
                    self.memory.as_messages(),
                    tool_descriptions=self.tools.registry.descriptions(),
                )
                token.raise_if_cancelled()

                action_key = (intent.action.value, intent.argument.strip())
                self.trace.record(
                    "plan_created",
                    action=intent.action.value,
                    argument=intent.argument,
                    step=step + 1,
                )

                # Prevent an agent model from blindly repeating the same
                # action after an ambiguous or unsuccessful tool result.
                if action_key in seen_actions and intent.action not in {Action.CHAT, Action.EXIT}:
                    self.trace.record(
                        "repeated_action_blocked",
                        action=intent.action.value,
                        argument=intent.argument,
                    )
                    self.memory.add(
                        "assistant",
                        f"[blocked-repeat:{intent.action.value}] {intent.argument}",
                    )
                    current_request = (
                        "The proposed action was already attempted. Do not repeat it. "
                        "Use the previous execution result to choose a different recovery "
                        "action, verify the state, or finish the user's goal. "
                        f"Goal: {goal}. Execution history: {execution_history[-5:]}"
                    )
                    continue

                confirmed = False
                if self.permissions.requires_confirmation(intent.action, self.tools.registry):
                    self.state.move(AgentState.WAITING_PERMISSION)
                    self.trace.record("permission_requested", action=intent.action.value)
                    if not self.permissions.request(intent):
                        self.trace.record("permission_denied", action=intent.action.value)
                        reply = "I didn't perform that action."
                        self.memory.add("assistant", reply)
                        self.state.move(AgentState.COMPLETED)
                        return True, reply
                    confirmed = True
                    token.raise_if_cancelled()

                self.state.move(AgentState.EXECUTING)
                self.trace.record("tool_started", action=intent.action.value, step=step + 1)
                execute_parameters = inspect.signature(self.tools.execute).parameters
                execute_kwargs = {}
                if "cancellation" in execute_parameters:
                    execute_kwargs["cancellation"] = token
                if "confirmed" in execute_parameters:
                    execute_kwargs["confirmed"] = confirmed

                if execute_kwargs:
                    running, result = self.tools.execute(
                        intent,
                        goal,
                        self.provider,
                        **execute_kwargs,
                    )
                else:
                    token.raise_if_cancelled()
                    running, result = self.tools.execute(intent, goal, self.provider)

                token.raise_if_cancelled()
                result_text = str(result)
                seen_actions.add(action_key)
                execution_history.append(
                    {
                        "step": step + 1,
                        "action": intent.action.value,
                        "argument": intent.argument,
                        "result": result_text[:1000],
                    }
                )
                self.trace.record(
                    "tool_finished",
                    action=intent.action.value,
                    result=result_text[:500],
                    step=step + 1,
                )

                verification = self.verifier.verify(intent, result, goal=goal, provider=self.provider)
                self.trace.record(
                    "verification",
                    action=intent.action.value,
                    status=verification.status,
                    evidence=verification.evidence[:500],
                    step=step + 1,
                )
                if verification.failed or verification.unknown:
                    status_label = verification.status
                    self.memory.add(
                        "assistant",
                        f"[verification_{status_label}:{intent.action.value}] "
                        f"{verification.evidence}",
                    )
                    if self.intelligent_memory:
                        self.intelligent_memory.record_failure(
                            goal,
                            f"{intent.action.value}: {status_label}: "
                            f"{verification.evidence[:500]}",
                            [intent.action.value],
                        )
                    self.state.move(AgentState.OBSERVING)
                    if not running:
                        self.state.move(AgentState.FAILED)
                        self.trace.record(
                            "request_finished",
                            status="unverified",
                            steps=len(execution_history),
                        )
                        return True, (
                            "I performed the action, but I couldn't verify that it "
                            "achieved the requested state."
                        )
                    current_request = (
                        "The last action did not produce a verified success. "
                        "Do not repeat it blindly. Diagnose the failure or unknown "
                        "state, inspect the current state, choose a safe recovery "
                        "action, or explain that the goal cannot be completed. "
                        f"Goal: {goal}. Latest evidence: {verification.evidence}"
                    )
                    continue

                if intent.action in {Action.CHAT, Action.EXIT}:
                    if self.intelligent_memory and intent.action is Action.CHAT:
                        self.intelligent_memory.record_experience(
                            goal,
                            result_text,
                            [item["action"] for item in execution_history],
                        )
                    self.memory.add("assistant", result)
                    self.state.move(AgentState.COMPLETED)
                    self.trace.record(
                        "request_finished",
                        status="completed",
                        steps=len(execution_history),
                    )
                    return running, result

                self.memory.add(
                    "assistant",
                    f"[tool:{intent.action.value}] {result_text[:1000]}",
                )

                if not running:
                    if self.intelligent_memory:
                        self.intelligent_memory.record_experience(
                            goal,
                            result_text,
                            [item["action"] for item in execution_history],
                        )
                    self.state.move(AgentState.COMPLETED)
                    self.trace.record(
                        "request_finished",
                        status="completed",
                        steps=len(execution_history),
                    )
                    return running, result

                self.state.move(AgentState.OBSERVING)
                current_request = (
                    "Continue executing the user's goal. You are in an autonomous "
                    "multi-step loop. Do not repeat completed actions. Inspect the "
                    "latest result, recover from failure when possible, and choose "
                    "the single best next action. If the goal is complete, use chat "
                    "and answer concisely. "
                    f"Goal: {goal}. Execution history: {execution_history[-5:]}"
                )

            self.state.move(AgentState.FAILED)
            self.trace.record(
                "request_finished",
                status="step_limit",
                steps=len(execution_history),
            )
            return True, "I reached the execution limit before finishing the task."
        except CancelledError:
            self.state.move(AgentState.CANCELLED)
            self.trace.record(
                "request_finished",
                status="cancelled",
                steps=len(execution_history),
            )
            return True, "Task cancelled."
        except Exception as exc:
            self.state.move(AgentState.FAILED)
            self.trace.record("request_failed", error=type(exc).__name__)
            raise

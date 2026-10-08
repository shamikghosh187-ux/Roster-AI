from roster.memory import ConversationMemory
from roster.models import Action
from roster.security import PermissionGate
from roster.trace import ExecutionTrace
from roster.state import AgentState, StateMachine
from roster.cancel import CancellationToken, CancelledError
import inspect


class Agent:
    def __init__(self, provider, tools, memory=None, permissions=None, max_steps=5, trace=None):
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        self.provider = provider
        self.tools = tools
        self.memory = memory or ConversationMemory()
        self.permissions = permissions or PermissionGate()
        self.max_steps = max_steps
        self.trace = trace or ExecutionTrace()
        self.state = StateMachine()

    def handle(self, user_text, cancellation=None):
        token = cancellation or CancellationToken()
        self.state.reset()
        self.trace.clear()
        self.trace.record("request_started", user_text=user_text)
        self.state.move(AgentState.PLANNING)
        self.memory.add("user", user_text)
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
                intent = self.provider.plan(
                    current_request,
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

                if intent.action in {Action.CHAT, Action.EXIT}:
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

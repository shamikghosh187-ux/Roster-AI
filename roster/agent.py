from roster.memory import ConversationMemory
from roster.models import Action
from roster.security import PermissionGate
from roster.trace import ExecutionTrace
from roster.state import AgentState, StateMachine
from roster.cancel import CancellationToken, CancelledError

class Agent:
    def __init__(self, provider, tools, memory=None, permissions=None, max_steps=5, trace=None):
        self.provider=provider
        self.tools=tools
        self.memory=memory or ConversationMemory()
        self.permissions=permissions or PermissionGate()
        self.max_steps=max_steps
        self.trace=trace or ExecutionTrace()
        self.state=StateMachine()

    def handle(self, user_text, cancellation=None):
        token=cancellation or CancellationToken()
        self.trace.clear()
        self.trace.record("request_started", user_text=user_text)
        self.state.move(AgentState.PLANNING)
        self.memory.add("user", user_text)
        current_request=user_text
        try:
            for step in range(self.max_steps):
                token.raise_if_cancelled()
                self.trace.record("planning", step=step+1)
                intent=self.provider.plan(current_request,self.memory.as_messages(),tool_descriptions=self.tools.registry.descriptions())
                self.trace.record("plan_created",action=intent.action.value,argument=intent.argument)
                token.raise_if_cancelled()
                if self.permissions.requires_confirmation(intent.action,self.tools.registry):
                    self.state.move(AgentState.WAITING_PERMISSION)
                    self.trace.record("permission_requested",action=intent.action.value)
                    if not self.permissions.request(intent):
                        self.trace.record("permission_denied",action=intent.action.value)
                        reply="I didn't perform that action."
                        self.memory.add("assistant",reply)
                        self.state.move(AgentState.COMPLETED)
                        return True,reply
                token.raise_if_cancelled()
                self.state.move(AgentState.EXECUTING)
                self.trace.record("tool_started",action=intent.action.value)
                running,result=self.tools.execute(intent,user_text,self.provider)
                token.raise_if_cancelled()
                self.trace.record("tool_finished",action=intent.action.value,result=str(result)[:500])
                if intent.action in {Action.CHAT,Action.EXIT}:
                    self.memory.add("assistant",result); self.state.move(AgentState.COMPLETED)
                    self.trace.record("request_finished",status="completed")
                    return running,result
                self.memory.add("assistant",f"[tool:{intent.action.value}] {result}")
                if not running:
                    self.state.move(AgentState.COMPLETED); self.trace.record("request_finished",status="completed")
                    return running,result
                current_request="Continue the user's task from the latest tool result. If complete, use chat and answer concisely. Latest tool result: "+str(result)
            self.state.move(AgentState.FAILED); self.trace.record("request_finished",status="step_limit")
            return True,"I reached the execution limit before finishing the task."
        except CancelledError:
            self.state.move(AgentState.CANCELLED); self.trace.record("request_finished",status="cancelled")
            return True,"Task cancelled."
        except Exception as exc:
            self.state.move(AgentState.FAILED); self.trace.record("request_failed",error=type(exc).__name__)
            raise

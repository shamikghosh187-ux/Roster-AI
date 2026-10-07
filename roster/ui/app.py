from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtGui import QAction, QColor, QFont
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QDialogButtonBox, QFrame, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPlainTextEdit,
    QPushButton, QSplitter, QStatusBar, QVBoxLayout, QWidget
)
from roster.config import settings
from roster.events import EventBus
from roster.runtime import AssistantRuntime
from roster.security import PermissionGate
from roster.tools.builtin import ToolExecutor
from roster.memory import ConversationMemory
from roster.providers.factory import create_provider, create_router
from roster.storage import SQLiteMemoryStore
from roster.agent import Agent
from roster.models import Action

class PermissionDialog(QDialog):
    def __init__(self, action, argument, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Roster permission request")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>Roster wants to run:</b> {action.value}"))
        layout.addWidget(QLabel(argument or "No additional argument"))
        buttons = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

class DesktopPermissionGate(PermissionGate):
    def __init__(self, window):
        super().__init__(enabled=True)
        self.window = window

    def request(self, intent):
        import threading
        decision = {"event": threading.Event(), "allowed": False,
                    "action": intent.action.value, "argument": intent.argument}
        self.window.permission_request.emit(decision)
        decision["event"].wait()
        return decision["allowed"]


class MainWindow(QMainWindow):
    permission_request = Signal(object)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Roster — Personal AI")
        self.resize(1280, 800)
        self.setMinimumSize(980, 650)
        self._build_ui()
        self._build_runtime()
        self.permission_request.connect(self._show_permission)

    def _build_ui(self):
        self.setStyleSheet("""
        QWidget { background:#0d0f12; color:#e8eaed; font-family:Segoe UI; }
        QFrame#sidebar { background:#11151a; border-right:1px solid #252a31; }
        QFrame#header { background:#11151a; border-bottom:1px solid #252a31; }
        QPlainTextEdit, QListWidget { background:#0a0c0f; border:1px solid #252a31; border-radius:10px; }
        QPushButton { background:#191e24; border:1px solid #303741; border-radius:9px; padding:10px 14px; }
        QPushButton:hover { background:#222831; }
        QPushButton#send { background:#d8a94e; color:#111; font-weight:700; }
        QLabel#brand { font-size:24px; font-weight:800; }
        QLabel#muted { color:#8b949e; }
        """)
        root=QWidget(); outer=QHBoxLayout(root); outer.setContentsMargins(0,0,0,0)
        side=QFrame(objectName="sidebar"); side.setFixedWidth(235); sl=QVBoxLayout(side)
        brand=QLabel("ROSTER"); brand.setObjectName("brand"); sl.addWidget(brand)
        sub=QLabel("Personal AI workspace"); sub.setObjectName("muted"); sl.addWidget(sub)
        sl.addSpacing(20)
        self.provider_box=QComboBox(); self.provider_box.addItems(["auto"] + ["groq","gemini","xai","claude"])
        sl.addWidget(QLabel("Provider")); sl.addWidget(self.provider_box)
        self.status=QLabel("● Offline"); self.status.setObjectName("muted"); sl.addWidget(self.status)
        sl.addSpacing(12)
        for label in ["Conversation","Memory","Tools","Tasks","Diagnostics"]:
            b=QPushButton(label); b.setEnabled(label=="Conversation"); sl.addWidget(b)
        sl.addStretch()
        self.cancel=QPushButton("Cancel current task"); self.cancel.setEnabled(False); sl.addWidget(self.cancel)
        outer.addWidget(side)

        center=QWidget(); cl=QVBoxLayout(center); cl.setContentsMargins(14,10,14,14)
        header=QFrame(objectName="header"); hl=QHBoxLayout(header)
        self.title=QLabel("Conversation"); self.title.setFont(QFont("Segoe UI",16,QFont.Bold)); hl.addWidget(self.title)
        hl.addStretch(); self.model=QLabel(settings.chat_model); self.model.setObjectName("muted"); hl.addWidget(self.model)
        cl.addWidget(header)

        split=QSplitter(Qt.Vertical)
        self.chat=QListWidget(); split.addWidget(self.chat)
        self.trace=QListWidget(); self.trace.setMaximumHeight(220); split.addWidget(self.trace)
        cl.addWidget(split,1)

        composer=QHBoxLayout()
        self.input=QPlainTextEdit(); self.input.setPlaceholderText("Talk to Roster…  (Ctrl+Enter to send)"); self.input.setMaximumHeight(100)
        send=QPushButton("Send"); send.setObjectName("send"); composer.addWidget(self.input,1); composer.addWidget(send)
        cl.addLayout(composer)
        self.send_button=send
        send.clicked.connect(self.submit)
        self.input.keyPressEvent=self._key_press
        self.cancel.clicked.connect(self._cancel)
        self.provider_box.currentTextChanged.connect(self._provider_changed)

        outer.addWidget(center,1)
        self.setCentralWidget(root)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

    def _build_runtime(self):
        try:
            self.events=EventBus()
            memory=ConversationMemory(store=SQLiteMemoryStore(settings.memory_db_path))
            tools=ToolExecutor()
            provider=create_router()
            self.agent=Agent(provider, tools, memory, DesktopPermissionGate(self))
            self.runtime=AssistantRuntime(self.agent, self.events)
            self.thread=QThread(self)
            self.worker=__import__("roster.ui.worker", fromlist=["AgentWorker"]).AgentWorker(self.runtime)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(lambda: None)
            self.worker.started.connect(self._on_started)
            self.worker.finished.connect(self._on_finished)
            self.worker.failed.connect(self._on_failed)
            self.worker.trace.connect(self._on_trace)
            self.thread.start()
            self.status.setText("● Ready")
            self.status.setStyleSheet("color:#8bd49c")
        except Exception as exc:
            self._on_failed(str(exc))

    def _show_permission(self, decision):
        dialog = PermissionDialog(decision["action"], decision["argument"], self)
        decision["allowed"] = dialog.exec() == QDialog.Accepted
        decision["event"].set()

    def _key_press(self,event):
        if event.key()==Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
            self.submit(); return
        QPlainTextEdit.keyPressEvent(self.input,event)

    def submit(self):
        if not hasattr(self,"worker") or self.worker is None: return
        text=self.input.toPlainText().strip()
        if not text: return
        if getattr(self,"busy",False): return
        self.busy=True; self.input.clear(); self.send_button.setEnabled(False); self.cancel.setEnabled(True)
        self._add_message("You",text)
        from PySide6.QtCore import QMetaObject, Q_ARG
        QMetaObject.invokeMethod(self.worker,"run",Qt.QueuedConnection,Q_ARG(str,text))

    def _cancel(self):
        if hasattr(self,"runtime"): self.runtime.cancel()
        self.cancel.setEnabled(False)

    def _on_started(self,text):
        self.status.setText("● Thinking…")

    def _on_finished(self,running,result):
        self._add_message("Roster",result)
        self.busy=False; self.send_button.setEnabled(True); self.cancel.setEnabled(False)
        self.status.setText("● Ready")
        self.statusBar().showMessage("Task complete")
        if not running:
            self.close()
        elif getattr(self, "close_pending", False):
            self.close_pending = False
            self.close()

    def _on_failed(self,error):
        self.busy=False; self.send_button.setEnabled(True); self.cancel.setEnabled(False)
        self.status.setText("● Error")
        self.statusBar().showMessage(error)
        self._add_message("System","Error: "+error)
        if getattr(self, "close_pending", False):
            self.close_pending = False
            self.close()

    def _on_trace(self,event,data):
        item=QListWidgetItem(f"{event}  {data}")
        self.trace.addItem(item); self.trace.scrollToBottom()

    def _add_message(self,role,text):
        item=QListWidgetItem(f"{role}\n{text}")
        item.setForeground(QColor("#d8a94e" if role=="You" else "#e8eaed"))
        self.chat.addItem(item); self.chat.scrollToBottom()

    def _provider_changed(self,name):
        if getattr(self, "busy", False):
            self.provider_box.blockSignals(True)
            self.provider_box.setCurrentText("auto")
            self.provider_box.blockSignals(False)
            self.statusBar().showMessage("Finish the current task before changing providers.")
            return

        try:
            self.agent.provider = create_router() if name == "auto" else create_provider(name)
            self.model.setText(
                settings.chat_model if name == "auto"
                else f"Provider: {name}"
            )
            self.statusBar().showMessage(
                "Automatic provider routing enabled."
                if name == "auto"
                else f"Provider switched to {name}."
            )
        except Exception as exc:
            self.provider_box.blockSignals(True)
            self.provider_box.setCurrentText("auto")
            self.provider_box.blockSignals(False)
            self.agent.provider = create_router()
            self.model.setText(settings.chat_model)
            self.statusBar().showMessage(f"Provider switch failed: {exc}")

    def closeEvent(self,event):
        if getattr(self, "busy", False):
            self.runtime.cancel()
            self.close_pending = True
            self.statusBar().showMessage("Cancelling current task before exit…")
            event.ignore()
            return
        if self._shutdown_thread():
            event.accept()
        else:
            self.statusBar().showMessage(
                "Task thread is still shutting down. Please close again when it is ready."
            )
            event.ignore()

    def _shutdown_thread(self):
        if not hasattr(self, "thread") or not self.thread.isRunning():
            return True
        self.thread.quit()
        return self.thread.wait(5000)

def launch():
    app=QApplication.instance() or QApplication([])
    window=MainWindow(); window.show()
    return app.exec()

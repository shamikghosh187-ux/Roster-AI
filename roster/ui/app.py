from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QDialogButtonBox, QFrame, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPlainTextEdit,
    QPushButton, QSplitter, QStackedWidget, QStatusBar, QVBoxLayout, QWidget
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


class PermissionDialog(QDialog):
    def __init__(self, action, argument, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Roster permission request")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>Roster wants to run:</b> {action}"))
        layout.addWidget(QLabel(argument or "No additional argument"))
        warning = QLabel("Only approve this action if you recognize and trust it.")
        warning.setWordWrap(True)
        layout.addWidget(warning)
        buttons = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        buttons.button(QDialogButtonBox.Yes).setText("Allow once")
        buttons.button(QDialogButtonBox.No).setText("Deny")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class DesktopPermissionGate(PermissionGate):
    def __init__(self, window):
        super().__init__(enabled=True)
        self.window = window

    def request(self, intent):
        import threading

        decision = {
            "event": threading.Event(),
            "allowed": False,
            "action": intent.action.value,
            "argument": intent.argument,
        }
        self.window.permission_request.emit(decision)
        # The worker waits while the GUI thread displays the confirmation dialog.
        decision["event"].wait()
        return decision["allowed"]


class MainWindow(QMainWindow):
    permission_request = Signal(object)

    NAV_ITEMS = ("Conversation", "Memory", "Tools", "Tasks", "Diagnostics")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Roster — Personal AI")
        self.resize(1280, 800)
        self.setMinimumSize(980, 650)
        self.pages = {}
        self.nav_buttons = {}
        self.store = None
        self.tools = None
        self.runtime = None
        self.agent = None
        self.busy = False
        self._build_ui()
        self._build_runtime()
        self.permission_request.connect(self._show_permission)
        self.refresh_memory()
        self.refresh_tools()
        self.refresh_tasks()
        self.refresh_diagnostics()

    def _build_ui(self):
        self.setStyleSheet("""
        QWidget { background:#0d0f12; color:#e8eaed; font-family:Segoe UI; }
        QFrame#sidebar { background:#11151a; border-right:1px solid #252a31; }
        QFrame#header { background:#11151a; border-bottom:1px solid #252a31; }
        QPlainTextEdit, QListWidget { background:#0a0c0f; border:1px solid #252a31; border-radius:10px; padding:6px; }
        QPushButton { background:#191e24; border:1px solid #303741; border-radius:9px; padding:10px 14px; }
        QPushButton:hover { background:#222831; }
        QPushButton:checked, QPushButton#send { background:#d8a94e; color:#111; font-weight:700; }
        QLabel#brand { font-size:24px; font-weight:800; }
        QLabel#muted { color:#8b949e; }
        """)

        root = QWidget()
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        side = QFrame(objectName="sidebar")
        side.setFixedWidth(235)
        sl = QVBoxLayout(side)
        brand = QLabel("ROSTER")
        brand.setObjectName("brand")
        sl.addWidget(brand)
        sub = QLabel("Personal AI workspace")
        sub.setObjectName("muted")
        sl.addWidget(sub)
        sl.addSpacing(20)

        sl.addWidget(QLabel("AI provider"))
        self.provider_box = QComboBox()
        self.provider_box.addItems(["auto", "groq", "gemini", "xai", "claude"])
        sl.addWidget(self.provider_box)
        self.status = QLabel("● Starting…")
        self.status.setObjectName("muted")
        sl.addWidget(self.status)
        sl.addSpacing(12)

        for label in self.NAV_ITEMS:
            button = QPushButton(label)
            button.setCheckable(True)
            button.setChecked(label == "Conversation")
            button.clicked.connect(lambda checked=False, name=label: self.show_page(name))
            self.nav_buttons[label] = button
            sl.addWidget(button)

        sl.addStretch()
        self.cancel = QPushButton("Cancel current task")
        self.cancel.setEnabled(False)
        self.cancel.clicked.connect(self._cancel)
        sl.addWidget(self.cancel)
        outer.addWidget(side)

        center = QWidget()
        cl = QVBoxLayout(center)
        cl.setContentsMargins(14, 10, 14, 14)
        header = QFrame(objectName="header")
        hl = QHBoxLayout(header)
        self.title = QLabel("Conversation")
        self.title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        hl.addWidget(self.title)
        hl.addStretch()
        self.model = QLabel(settings.chat_model)
        self.model.setObjectName("muted")
        hl.addWidget(self.model)
        cl.addWidget(header)

        self.stack = QStackedWidget()
        self._build_conversation_page()
        self._build_memory_page()
        self._build_tools_page()
        self._build_tasks_page()
        self._build_diagnostics_page()
        cl.addWidget(self.stack, 1)

        outer.addWidget(center, 1)
        self.setCentralWidget(root)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")
        self.provider_box.currentTextChanged.connect(self._provider_changed)

    def _register_page(self, name, widget):
        self.pages[name] = widget
        self.stack.addWidget(widget)

    def _build_conversation_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        split = QSplitter(Qt.Vertical)
        self.chat = QListWidget()
        self.chat.setAccessibleName("Conversation history")
        split.addWidget(self.chat)
        self.trace = QListWidget()
        self.trace.setMaximumHeight(190)
        self.trace.setAccessibleName("Execution trace")
        split.addWidget(self.trace)
        layout.addWidget(split, 1)

        composer = QHBoxLayout()
        self.input = QPlainTextEdit()
        self.input.setPlaceholderText("Talk to Roster…  (Ctrl+Enter to send)")
        self.input.setMaximumHeight(100)
        self.input.keyPressEvent = self._key_press
        composer.addWidget(self.input, 1)
        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("send")
        self.send_button.clicked.connect(self.submit)
        composer.addWidget(self.send_button)
        layout.addLayout(composer)
        self._register_page("Conversation", page)

    def _build_memory_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        intro = QLabel("Long-term memories saved by Roster. Review a memory before deleting it.")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        actions = QHBoxLayout()
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh_memory)
        actions.addWidget(refresh)
        delete = QPushButton("Delete selected memory")
        delete.clicked.connect(self.delete_selected_memory)
        actions.addWidget(delete)
        actions.addStretch()
        layout.addLayout(actions)
        self.memory_list = QListWidget()
        self.memory_list.currentItemChanged.connect(self._show_memory_detail)
        layout.addWidget(self.memory_list, 1)
        self.memory_detail = QPlainTextEdit()
        self.memory_detail.setReadOnly(True)
        self.memory_detail.setPlaceholderText("Select a memory to inspect its details.")
        self.memory_detail.setMaximumHeight(150)
        layout.addWidget(self.memory_detail)
        self._register_page("Memory", page)

    def _build_tools_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        intro = QLabel("Tools registered in this session. Sensitive actions require a confirmation prompt.")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        refresh = QPushButton("Refresh tools")
        refresh.clicked.connect(self.refresh_tools)
        layout.addWidget(refresh, 0, Qt.AlignLeft)
        self.tools_list = QListWidget()
        layout.addWidget(self.tools_list, 1)
        self._register_page("Tools", page)

    def _build_tasks_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        intro = QLabel("Runtime activity and execution trace.")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        refresh = QPushButton("Refresh task status")
        refresh.clicked.connect(self.refresh_tasks)
        layout.addWidget(refresh, 0, Qt.AlignLeft)
        self.tasks_summary = QPlainTextEdit()
        self.tasks_summary.setReadOnly(True)
        self.tasks_summary.setMaximumHeight(180)
        layout.addWidget(self.tasks_summary)
        self.tasks_trace = QListWidget()
        layout.addWidget(self.tasks_trace, 1)
        self._register_page("Tasks", page)

    def _build_diagnostics_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        intro = QLabel("Local configuration and dependency checks. API-key values are never displayed.")
        intro.setWordWrap(True)
        layout.addWidget(intro)
        refresh = QPushButton("Run diagnostics")
        refresh.clicked.connect(self.refresh_diagnostics)
        layout.addWidget(refresh, 0, Qt.AlignLeft)
        self.diagnostics_output = QPlainTextEdit()
        self.diagnostics_output.setReadOnly(True)
        layout.addWidget(self.diagnostics_output, 1)
        self._register_page("Diagnostics", page)

    def show_page(self, name):
        if name not in self.pages:
            return
        self.stack.setCurrentWidget(self.pages[name])
        self.title.setText(name)
        for item, button in self.nav_buttons.items():
            button.setChecked(item == name)
        if name == "Memory":
            self.refresh_memory()
        elif name == "Tools":
            self.refresh_tools()
        elif name == "Tasks":
            self.refresh_tasks()
        elif name == "Diagnostics":
            self.refresh_diagnostics()

    def _build_runtime(self):
        try:
            self.events = EventBus()
            self.store = SQLiteMemoryStore(settings.memory_db_path)
            memory = ConversationMemory(store=self.store)
            self.tools = ToolExecutor()
            provider = create_router()
            self.agent = Agent(provider, self.tools, memory, DesktopPermissionGate(self))
            self.runtime = AssistantRuntime(self.agent, self.events)
            self.thread = QThread(self)
            self.worker = __import__("roster.ui.worker", fromlist=["AgentWorker"]).AgentWorker(self.runtime)
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
            self.status.setText("● Needs setup")
            self.status.setStyleSheet("color:#e6b85c")
            self._on_failed(str(exc))

    def _show_permission(self, decision):
        try:
            dialog = PermissionDialog(decision["action"], decision["argument"], self)
            decision["allowed"] = dialog.exec() == QDialog.Accepted
        finally:
            decision["event"].set()

    def _key_press(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
            self.submit()
            return
        QPlainTextEdit.keyPressEvent(self.input, event)

    def submit(self):
        if not getattr(self, "worker", None):
            self.statusBar().showMessage("Roster runtime is unavailable. Open Diagnostics for details.")
            return
        text = self.input.toPlainText().strip()
        if not text or self.busy:
            return
        self.busy = True
        self.input.clear()
        self.send_button.setEnabled(False)
        self.cancel.setEnabled(True)
        self._add_message("You", text)
        from PySide6.QtCore import QMetaObject, Q_ARG
        QMetaObject.invokeMethod(self.worker, "run", Qt.QueuedConnection, Q_ARG(str, text))
        self.refresh_tasks()

    def _cancel(self):
        if self.runtime:
            self.runtime.cancel()
            self.statusBar().showMessage("Cancellation requested…")
        self.cancel.setEnabled(False)

    def _on_started(self, text):
        self.status.setText("● Thinking…")
        self.status.setStyleSheet("color:#d8a94e")
        self.statusBar().showMessage("Working on your request…")
        self.refresh_tasks()

    def _on_finished(self, running, result):
        self._add_message("Roster", str(result))
        self.busy = False
        self.send_button.setEnabled(True)
        self.cancel.setEnabled(False)
        self.status.setText("● Ready")
        self.status.setStyleSheet("color:#8bd49c")
        self.statusBar().showMessage("Task complete")
        self.refresh_tasks()
        if not running:
            self.close()
        elif getattr(self, "close_pending", False):
            self.close_pending = False
            self.close()

    def _on_failed(self, error):
        self.busy = False
        if hasattr(self, "send_button"):
            self.send_button.setEnabled(True)
        if hasattr(self, "cancel"):
            self.cancel.setEnabled(False)
        if hasattr(self, "status"):
            self.status.setText("● Error")
            self.status.setStyleSheet("color:#e07a7a")
        if hasattr(self, "statusBar"):
            self.statusBar().showMessage(str(error))
        if hasattr(self, "chat"):
            self._add_message("System", "Error: " + str(error))
        if hasattr(self, "tasks_summary"):
            self.refresh_tasks()

    def _on_trace(self, event, data):
        item = QListWidgetItem(f"{event}  {data}")
        self.trace.addItem(item)
        self.trace.scrollToBottom()
        if hasattr(self, "tasks_trace"):
            self.tasks_trace.addItem(QListWidgetItem(item.text()))
            self.tasks_trace.scrollToBottom()

    def _add_message(self, role, text):
        item = QListWidgetItem(f"{role}\n{text}")
        item.setForeground(QColor("#d8a94e" if role == "You" else "#e8eaed"))
        self.chat.addItem(item)
        self.chat.scrollToBottom()

    def _provider_changed(self, name):
        if self.busy:
            self.provider_box.blockSignals(True)
            self.provider_box.setCurrentText("auto")
            self.provider_box.blockSignals(False)
            self.statusBar().showMessage("Finish the current task before changing providers.")
            return
        if not self.agent:
            self.statusBar().showMessage("Configure a provider and restart Roster.")
            return
        try:
            self.agent.provider = create_router() if name == "auto" else create_provider(name)
            self.model.setText(settings.chat_model if name == "auto" else f"Provider: {name}")
            self.statusBar().showMessage(
                "Automatic provider routing enabled." if name == "auto"
                else f"Provider switched to {name}."
            )
        except Exception as exc:
            QMessageBox.warning(self, "Provider switch failed", str(exc))
            self.provider_box.blockSignals(True)
            self.provider_box.setCurrentText("auto")
            self.provider_box.blockSignals(False)
            try:
                self.agent.provider = create_router()
                self.model.setText(settings.chat_model)
            except Exception as fallback_exc:
                self.agent = None
                self.status.setText("● Needs setup")
                self.statusBar().showMessage(f"Provider unavailable: {fallback_exc}")

    def refresh_memory(self):
        if not hasattr(self, "memory_list"):
            return
        self.memory_list.clear()
        self.memory_detail.clear()
        if not self.store:
            self.memory_list.addItem("Memory store unavailable. Check Diagnostics.")
            return
        try:
            for row in self.store.all_memories():
                memory_id, key, category, content, confidence, importance, access_count, created, updated = row
                item = QListWidgetItem(f"{category}  ·  {key}\n{content}")
                item.setData(Qt.UserRole, key)
                item.setData(Qt.UserRole + 1, {
                    "id": memory_id, "key": key, "category": category, "content": content,
                    "confidence": confidence, "importance": importance,
                    "access_count": access_count, "created": created, "updated": updated,
                })
                self.memory_list.addItem(item)
            if self.memory_list.count() == 0:
                self.memory_list.addItem("No long-term memories saved yet.")
                self.memory_list.setEnabled(False)
            else:
                self.memory_list.setEnabled(True)
        except Exception as exc:
            self.memory_list.addItem(f"Could not load memories: {exc}")

    def _show_memory_detail(self, current, previous=None):
        if not current:
            self.memory_detail.clear()
            return
        data = current.data(Qt.UserRole + 1)
        if not isinstance(data, dict):
            self.memory_detail.clear()
            return
        self.memory_detail.setPlainText(
            f"Key: {data['key']}\nCategory: {data['category']}\n"
            f"Confidence: {data['confidence']}\nImportance: {data['importance']}\n"
            f"Access count: {data['access_count']}\nCreated: {data['created']}\n"
            f"Updated: {data['updated']}\n\n{data['content']}"
        )

    def delete_selected_memory(self):
        item = self.memory_list.currentItem()
        if not item or not self.store:
            return
        key = item.data(Qt.UserRole)
        if not key:
            QMessageBox.information(self, "No memory selected", "Select a saved memory first.")
            return
        answer = QMessageBox.question(
            self, "Delete memory",
            f"Delete the saved memory '{key}'? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        try:
            deleted = self.store.delete_memory(key)
            self.refresh_memory()
            self.statusBar().showMessage("Memory deleted." if deleted else "That memory was already removed.")
        except Exception as exc:
            QMessageBox.warning(self, "Delete failed", str(exc))

    def refresh_tools(self):
        if not hasattr(self, "tools_list"):
            return
        self.tools_list.clear()
        if not self.tools:
            self.tools_list.addItem("Tool registry unavailable. Check Diagnostics.")
            return
        for spec in self.tools.registry.all():
            security = "CONFIRMATION REQUIRED" if spec.requires_confirmation else "No confirmation flag"
            retry = "Retry-safe" if spec.retry_safe else "Not marked retry-safe"
            item = QListWidgetItem(
                f"{spec.action.value}  ·  {security}\n{spec.description}\n{retry}"
            )
            self.tools_list.addItem(item)

    def refresh_tasks(self):
        if not hasattr(self, "tasks_summary"):
            return
        if not self.runtime:
            self.tasks_summary.setPlainText("Runtime unavailable. Check Diagnostics for setup details.")
            return
        metrics = self.runtime.metrics.as_dict()
        duration = metrics["last_duration_ms"]
        self.tasks_summary.setPlainText(
            f"Active: {'Yes' if metrics['active'] else 'No'}\n"
            f"Submitted: {metrics['submitted']}\nCompleted: {metrics['completed']}\n"
            f"Failed: {metrics['failed']}\nCancelled: {metrics['cancelled']}\n"
            f"Last duration: {duration if duration is not None else '—'} ms"
        )

    def refresh_diagnostics(self):
        if not hasattr(self, "diagnostics_output"):
            return
        try:
            from roster.doctor import diagnose, format_report
            report = diagnose()
            self.diagnostics_output.setPlainText(format_report(report))
        except Exception as exc:
            self.diagnostics_output.setPlainText(
                "Diagnostics could not complete.\n"
                f"{type(exc).__name__}: {exc}\n\n"
                "Check your Python environment and installed dependencies."
            )

    def closeEvent(self, event):
        if self.busy and self.runtime:
            self.runtime.cancel()
            self.close_pending = True
            self.statusBar().showMessage("Cancelling current task before exit…")
            event.ignore()
            return
        self._shutdown_thread()
        event.accept()

    def _shutdown_thread(self):
        if hasattr(self, "thread") and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait(5000)


def launch():
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    return app.exec()

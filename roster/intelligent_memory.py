"""Selective long-term memory with relevance-ranked recall."""
from __future__ import annotations

import re
from dataclasses import dataclass


_SECRET_PATTERNS = (
    r"(?i)(api[_ -]?key|access[_ -]?token|secret|password|passwd|private[_ -]?key)",
    r"(?i)\bsk-[A-Za-z0-9_-]{12,}\b",
    r"(?i)\bghp_[A-Za-z0-9]{20,}\b",
)


@dataclass(frozen=True)
class MemoryItem:
    memory_id: int
    key: str
    category: str
    content: str
    confidence: float
    importance: float
    score: float = 0.0


class IntelligentMemory:
    """Promotes stable user knowledge and retrieves only relevant memories."""

    def __init__(self, store, max_recall=8):
        self.store = store
        self.max_recall = max(1, int(max_recall))

    @staticmethod
    def _secret_like(text: str) -> bool:
        return any(re.search(pattern, text) for pattern in _SECRET_PATTERNS)

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {
            token.lower()
            for token in re.findall(r"[A-Za-z0-9_'-]{2,}", text)
            if token.lower() not in {"that", "this", "with", "from", "have", "your"}
        }

    @classmethod
    def _key(cls, category: str, content: str) -> str:
        tokens = sorted(cls._tokens(content))[:12]
        return f"{category}:{'-'.join(tokens)}"

    def remember(self, content, *, category="fact", key=None, confidence=0.85, importance=0.65):
        content = str(content).strip()
        if not content or self._secret_like(content):
            return False
        memory_key = key or self._key(category, content)
        self.store.upsert_memory(
            memory_key,
            category,
            content[:1000],
            max(0.0, min(1.0, confidence)),
            max(0.0, min(1.0, importance)),
        )
        return True

    def learn_from_user(self, text):
        """Promote explicit/stable facts; ordinary chat stays ephemeral."""
        text = (text or "").strip()
        if not text or self._secret_like(text):
            return 0

        patterns = [
            (r"(?i)^remember(?: that)? (.+)$", "instruction", 0.98, 0.9),
            (r"(?i)^my name is (.+)$", "identity", 0.99, 1.0),
            (r"(?i)^i(?:'m| am) called (.+)$", "identity", 0.99, 1.0),
            (r"(?i)^i prefer (.+)$", "preference", 0.9, 0.8),
            (r"(?i)^i like (.+)$", "preference", 0.85, 0.7),
            (r"(?i)^i don't like (.+)$", "preference", 0.9, 0.8),
            (r"(?i)^i dislike (.+)$", "preference", 0.9, 0.8),
        ]
        for pattern, category, confidence, importance in patterns:
            match = re.match(pattern, text)
            if match:
                value = match.group(1).strip()
                key = self._key(category, value)
                return int(self.remember(
                    value,
                    category=category,
                    key=key,
                    confidence=confidence,
                    importance=importance,
                ))
        return 0

    def recall(self, query):
        query_tokens = self._tokens(query)
        candidates = []
        for row in self.store.all_memories():
            memory_id, key, category, content, confidence, importance, access_count, *_ = row
            tokens = self._tokens(f"{category} {key} {content}")
            overlap = len(query_tokens & tokens)
            exact_bonus = 0.35 if query.lower() in content.lower() else 0.0
            score = (
                overlap * 1.0
                + exact_bonus
                + float(importance) * 0.8
                + float(confidence) * 0.5
                + min(int(access_count), 10) * 0.03
            )
            if overlap or exact_bonus or float(importance) >= 0.9:
                candidates.append(MemoryItem(
                    int(memory_id), key, category, content,
                    float(confidence), float(importance), score,
                ))

        candidates.sort(key=lambda item: item.score, reverse=True)
        selected = candidates[: self.max_recall]
        self.store.touch_memories([item.memory_id for item in selected])
        return selected

    def context(self, query):
        memories = self.recall(query)
        if not memories:
            return ""
        lines = ["Relevant long-term memory:"]
        for item in memories:
            lines.append(
                f"- [{item.category}] {item.content} "
                f"(confidence={item.confidence:.2f})"
            )
        return "\n".join(lines)

    def forget(self, query):
        """Forget the strongest matching memory for an explicit user request."""
        matches = self.recall(query)
        if not matches:
            return False
        return self.store.delete_memory(matches[0].key)

    def learn_from_user(self, text):
        """Promote explicit/stable facts; ordinary chat stays ephemeral."""
        text = (text or "").strip()
        if not text or self._secret_like(text):
            return 0

        forget_match = re.match(r"(?i)^forget(?: that)? (.+)$", text)
        if forget_match:
            return int(self.forget(forget_match.group(1).strip()))

        patterns = [

"""Deterministic character-window chunker for local knowledge."""
from roster.knowledge_chunk import KnowledgeChunk

def chunk(source_id,text,size=1000):
    if size<1: raise ValueError("size must be positive")
    return tuple(KnowledgeChunk(source_id,index,text[i:i+size]) for index,i in enumerate(range(0,len(text),size)))

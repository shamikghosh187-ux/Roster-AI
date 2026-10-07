from pathlib import Path
import difflib
class FileEditor:
    def __init__(self,root): self.root=Path(root).resolve()
    def path(self,name):
        p=(self.root/name).resolve()
        if p!=self.root and self.root not in p.parents: raise PermissionError('path escapes workspace')
        return p
    def read(self,name): return self.path(name).read_text(encoding='utf-8')
    def write(self,name,text):
        p=self.path(name); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding='utf-8')
    def diff(self,name,new_text):
        old=self.read(name).splitlines(True) if self.path(name).exists() else []
        return ''.join(difflib.unified_diff(old,new_text.splitlines(True),fromfile=name,tofile=name))

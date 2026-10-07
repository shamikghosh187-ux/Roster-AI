from pathlib import Path
IGNORED={'.git','node_modules','__pycache__','.venv','dist','build'}
class Workspace:
    def __init__(self,root): self.root=Path(root).expanduser().resolve()
    def files(self,limit=500):
        out=[]
        if not self.root.exists(): return out
        for p in self.root.rglob('*'):
            if len(out)>=limit: break
            if p.is_file() and not any(x in IGNORED for x in p.parts): out.append(p)
        return out
    def summary(self): return {'root':str(self.root),'files':len(self.files())}

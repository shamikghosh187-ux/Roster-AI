import subprocess
from pathlib import Path
class GitWorkspace:
    def __init__(self,root): self.root=Path(root).resolve()
    def run(self,*args): return subprocess.run(['git',*args],cwd=self.root,text=True,capture_output=True,timeout=20)
    def status(self): return self.run('status','--short').stdout
    def diff(self): return self.run('diff','--').stdout
    def log(self,limit=10): return self.run('log',f'-{max(1,limit)}','--oneline').stdout

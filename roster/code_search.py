class CodeSearch:
    def __init__(self,workspace): self.workspace=workspace
    def search(self,query,limit=50):
        q=query.lower(); hits=[]
        for path in self.workspace.files():
            try: lines=path.read_text(encoding='utf-8',errors='ignore').splitlines()
            except OSError: continue
            for n,line in enumerate(lines,1):
                if q in line.lower():
                    hits.append({'path':str(path),'line':n,'text':line.strip()})
                    if len(hits)>=limit:return hits
        return hits

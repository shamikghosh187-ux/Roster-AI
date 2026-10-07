from urllib.parse import urlparse
from urllib.request import Request,urlopen
class Browser:
    def open(self,url,max_bytes=200000):
        u=urlparse(url)
        if u.scheme not in {'http','https'} or not u.netloc: raise ValueError('only public HTTP(S) URLs are allowed')
        with urlopen(Request(url,headers={'User-Agent':'Roster-AI/1.0'}),timeout=10) as r:
            body=r.read(max_bytes).decode('utf-8','ignore')
            return {'url':url,'content_type':r.headers.get('content-type',''),'body':body}

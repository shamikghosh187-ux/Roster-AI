import importlib.util
class Diagnostics:
    def check(self,names):
        return [{'name':n,'ok':importlib.util.find_spec(n) is not None} for n in names]
    def report(self):
        return {'runtime':'python','checks':self.check(['groq','sounddevice','pyttsx3','numpy'])}

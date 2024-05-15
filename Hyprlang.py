from typing import List, Union 
def clamp(value, min_value=-float('inf'), max_value=float('inf')):
    return max(min(value, max_value), min_value)
class RGBA:
    """Represents a color in RGBA format"""
    def __init__(self, r:int, g:int, b:int, a:float=-1):
        self.r = clamp(r,0,255)
        self.g = clamp(g,0,255)
        self.b = clamp(b,0,255)
        if a != -1:
            self.a = clamp(a,0,1)
    @classmethod
    def from_hex(cls, hex:str):
        """Creates an RGBA instance from a hexadecimal color code."""
        hex = hex.lstrip('#')
        return cls(*[int(hex[i:i+2], 16) for i in (0, 2, 4)])

    def __str__(self):
        return f"rgb{'a' if self.a!=-1 else ''}({self.r}, {self.g}, {self.b}{f', {self.a}' if self.a!=-1 else ''})"

class Gradient:
    def __init__(self, s:RGBA, e:RGBA, angle:int):
        self.s =s
        self.e = e
        self.angle = angle

    def __str__(self):
        return f"{self.s} {self.e} {self.angle}deg"

class Vec2:
    """Represents a 2-dimensional vector."""
    def __init__(self, x:int, y:int):
        self.x = x
        self.y = y

    def __str__(self):
        return f"{self.x} {self.y}"
class Parameters:
    """It's just list to be passed in a handler"""
    def __init__(self, *args):
        self.params = args
    def __str__(self):
        return ", ".join(str(param) for param in self.params)

class Handler:
    """A line in hyprlang"""
    def __init__(self, keyword:str,*params:Parameters):
        self.keyword = keyword
        self.params= params
    def __str__(self):
        res = ""
        for param in self.params:
            res += f"{self.keyword} = {str(param)}\n"
        return res

class Category:
    """A category in hyprlang, it a dictionary like structure"""
    def __init__(self, name:str, *props:Union[ 'Handler' ,'Category']):
        self.name = name
        self.props= props
    def __nested(self):
        """Returns the category as a string with 4 spaces before each line."""
        res = str(self).split('\n')
        res = [f"{' '*4}{line}" for line in res[:-1]] + [res[-1]]
        return '\n'.join(res) 
    @classmethod
    def from_dict(cls, name:str, config:dict):
        """Creates a Category instance from a dictionary"""
        res = []
        for key, value in config.items():
            if isinstance(value, List):
                res.append(Handler(key, Parameters(*value)))
            elif isinstance(value, dict):
                res.append(cls.from_dict(key, value))
        return cls(name, *res)
                
    def __str__(self):
        res = f"{self.name} {{\n"
        for prop in self.props:
            if isinstance(prop, Handler):
                res += f"{' '*4}{prop}"
            else:
                res += f"{prop.__nested()}"
        res += "}\n"
        return res

class Hyprlang_config:
    """Just to store the config of the hyprlang
    Only one instance of class should be created per file and stored in a variable named `config`.
    """
    def __init__(self, file_name:str):
        self.file_name = file_name
        self.config = []
    @classmethod
    def from_file(cls, file_name:str):
        """Creates a Hyprlang instance from a python file.
        Put all Hyprlang_config instances in a variable named `config` in the file for this to work and also under same directory
        """
        from time import sleep
        import os
        import importlib
        while True:
            if not file_name.endswith('.py') or not os.path.exists(file_name):
                os.system("notify-send 'File should be a python file'")
                os.system('notify-send "Waiting for 10 seconds"')
                sleep(10)
            else:
                break
        
        import sys
        
        path = os.path.dirname(file_name)
        name = os.path.basename(file_name).split('.')[0]
        
        if path not in sys.path:
            sys.path.append(path)
        
        while True:
            try:
                module = importlib.import_module(name)
                importlib.reload(module)  # Reload the module to get a fresh instance
                break
            except Exception as e:
                os.system(f'notify-send "{e}"')
                os.system('notify-send "Error in config file, waiting for 10 seconds"')
                sleep(10)
        return module.config
    def add_via_primitive(self, **kwargs):
        """Adds a handler or category to the hyprlang"""
        for key, value in kwargs.items():
            if isinstance(value, dict):
                self.config.append(Category.from_dict(key, value))
            elif isinstance(value, list):
                self.config.append(Handler(key, *[Parameters(*v) for v in value]))
    def add(self, *obj:Union['Handler','Category']):
        """Adds a handler or category to the hyprlang"""
        for o in obj:
            self.config.append(o)
    def add_config(self, config:'Hyprlang_config'):
        """Adds a config to the hyprlang"""
        self.config.extend(config.config)
    def __str__(self):
        res = ""
        for obj in self.config:
            if isinstance(obj, Hyprlang):
                for o in obj.config:
                    res += str(o) + '\n'
            else:
                res += str(obj) + '\n'
        return res

class Hyprlang:
    """The main class for the hyprlang.
    One file file named config"""
    def __init__(self,config_path:str,file_name:str):
        self.config_path = config_path
        self.file_name = file_name
        self.config = [] # Hyprlang_config object will be stored here
        self.observer = None
    def add(self, *config:Hyprlang_config):
        """Adds a config to the hyprlang"""
        for c in config:
            self.config.append(c)

    def watch(self):
        import os
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        class Handler(FileSystemEventHandler):
            def __init__(self, hyprlang):
                self.hyprlang = hyprlang
            def on_modified(self, event):
                if event.is_directory:
                    return
                if os.path.basename(event.src_path) == os.path.basename(self.hyprlang.file_name):
                    config = Hyprlang_config.from_file(self.hyprlang.file_name)
                    self.hyprlang.config = config.config
                for c in self.hyprlang.config:
                    if event.src_path == c.file_name:
                        c.config = Hyprlang_config.from_file(c.file_name).config
                self.hyprlang.write()
        if self.observer and self.observer.is_alive():
            return  
        self.observer = Observer()
        self.observer.schedule(Handler(self), path=os.path.dirname(self.file_name) ,recursive=False)
        self.observer.start()

    def __str__(self):
        res = ""
        for c in self.config:
            res += str(c)
        return res

    def write(self):
        """Writes the config to the file"""
        import os
        if not os.path.exists(self.config_path):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            open(self.config_path, 'w').close()
        with open(self.config_path, 'w') as f:
            f.write(str(self))


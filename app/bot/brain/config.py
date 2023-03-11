class Config:
    def __init__(self, **kwargs):  
        self._attributes = kwargs  

    def __getattr__(self, name):  
        try:                       
            return self._attributes[name]  
        except KeyError as e:       
            raise AttributeError("'{}' not found in config.".format(name))

    def __setattr__(self, name, value):  
        if name == '_attributes':    
            super().__setattr__(name, value) # attributes is actually an attribute - see __init__
        else:
            self._attributes[name] = value 
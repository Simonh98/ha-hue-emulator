from datetime import datetime

class User:
    uuid: str
    name: str
    hueapplicationkey: str
    clientkey: str
    created: str
    lastused: str
    
    def __init__(self, uuid: str, name: str, clientkey: str) -> None:
        self.uuid = uuid
        self.name = name
        self.clientkey = clientkey
        self.created = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        self.lastused = self.created
        
    def __str__(self) -> str:
        return f'uuid={self.uuid}, name={self.name}, clientkey={self.clientkey}'
        
    def __repr__(self) -> str:
        return f'uuid={self.uuid}, name{self.name}, clientkey={self.clientkey}'
    
    def getV1Api(self):
        return {"name": self.name, "create date": self.created, "last use date": self.lastused}

    def save(self):
        return {"name": self.name, "client_key": self.clientkey, "create_date": self.created, "last_use_date": self.lastused}

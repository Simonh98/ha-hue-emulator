import queue

class Messaging:
    
    def __init__(self) -> None:
        self.v2eventstream = queue.Queue()
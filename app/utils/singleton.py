from threading import Lock

def singleton(cls):
    _instances = {}
    _lock = Lock()
    
    def get_instance(*args, **kwargs):
        if cls not in _instances:
            with _lock:
                if cls not in _instances:
                    _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]
    
    return get_instance
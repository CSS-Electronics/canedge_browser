from typing import Callable, List, Optional, TypeVar

T = TypeVar("T")


class FuncBackedList(list):
    """List implementation, which generates values based on a backing function.
    
    """
    def __init__(self, func: Callable, items: Optional[List[T]] = None):
        self._keys = []
        self._values = []
        
        self._func = func
        
        if self._func is None:
            raise ValueError("Func is not set")
        
        if items is not None:
            self._keys = items
            self._values = [None] * len(self._keys)
        
        super(FuncBackedList, self).__init__()
        
        return
    
    def append(self, value: T) -> None:
        self._keys.append(value)
        self._values.append(None)
        return
    
    def __getitem__(self, item):
        # If a cached value exists, return that. Else, callback to the backing function to generate a value.
        result = self._values[item]
        
        if result is None:
            key = self._keys[item]
            self._values[item] = self._func(key)
            result = self._values[item]
        
        return result
    
    def __len__(self):
        return len(self._keys)
    
    pass

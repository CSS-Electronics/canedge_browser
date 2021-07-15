import copy

import fsspec

from pathlib import Path, PurePath
from typing import Union


class RelativeFileSystem(fsspec.AbstractFileSystem):
    """RelativeFileSystem implements a subset of the AbstractFileSystem from fsspec, such that all calls are
    forwarded to the implementation from fsspec, but with another root dir.
    
    """
    
    def __init__(self, protocol: str, base_path: Union[str, Path, PurePath], *args, **storage_options):
        super().__init__(*args, **storage_options)
        self.protocol = protocol
        
        self._paths_with_leading_slash = storage_options.get("paths_with_leading_slash", False)
        
        # Use the corresponding filesystem under the hood.
        self._fs = fsspec.filesystem(protocol=protocol, **storage_options)  # type: fsspec.AbstractFileSystem

        # Use the base path as the root, and translate all calls relative to this.
        self._base_path = PurePath(base_path)
        
        return

    def ls(self, path, **kwargs):
        detail = kwargs.get("detail", False)
        
        # Translate path forward.
        path = self._translate_path_forward(path)
        
        # Perform wrapped call.
        result = self._fs.ls(path, **kwargs)
        
        if detail:
            # NOTE: Since the paths are changed and the objects are shared globally, it is imperative that the objects
            #       are copied before any changed are made, else the internal state/cache of the fs can contaminated.
            result = copy.deepcopy(result)
            
            # List of dictionary objects. Entries can be replaces within the dictionary.
            for entry in result:
                entry["name"] = self._translate_path_reverse(entry["name"])
        else:
            # List of strings, need to replace in list.
            for i, entry in enumerate(result):
                result[i] = self._translate_path_reverse(entry)
        
        return result
    
    def open(self, path, mode="rb", block_size=None, cache_options=None, **kwargs):
        # Translate path forward.
        path = self._translate_path_forward(path)
        
        return self._fs.open(path, mode, block_size, cache_options, **kwargs)
    
    def _translate_path_forward(self, path) -> str:
        # Remove the leading "/" if present.
        if path.startswith("/"):
            path = "." + path
    
        # Translate to a full absolute path.
        translated_path = self._base_path / PurePath(path)
        
        # Remove any "." and ".." operators.
        if self.protocol == "file":
            translated_path = Path(translated_path).absolute()
        else:
            translated_path = translated_path.as_posix()
        
        return str(translated_path)

    def _translate_path_reverse(self, path) -> str:
        full_path = PurePath(path)
        
        # Extract the relative component.
        relative_path = full_path.relative_to(self._base_path)
        
        # Append a leading slash and present to the user as a POSIX path.
        translated_path = relative_path.as_posix()
        
        if self._paths_with_leading_slash:
            translated_path = "/" + translated_path
    
        return translated_path
    
    pass

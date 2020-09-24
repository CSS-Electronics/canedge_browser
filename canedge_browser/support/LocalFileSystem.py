import fsspec

from pathlib import Path, PurePath
from fsspec.implementations.local import LocalFileSystem as fslfs


class LocalFileSystem(fsspec.AbstractFileSystem):
    """LocalFileSystem implements a subset of the AbstractFileSystem from fsspec, such that all calls are forwarded to
    the implementation from fsspec, but with another root dir.
    
    """
    def __init__(self, base_path, *args, **storage_options):
        super().__init__(*args, **storage_options)
        
        # Use a local filesystem under the hood.
        self._fs = fslfs(*args, **storage_options)

        # Use the base path as the root, and translate all calls relative to this.
        self._base_path = Path(base_path).absolute()
        
        return

    def ls(self, path, detail=True, **kwargs):
        # Translate path forward.
        path = self._translate_path_forward(path)
        
        # Perform wrapped call.
        result = self._fs.ls(path, detail, **kwargs)
        
        if detail:
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
        translated_path = self._base_path / Path(path)
        
        # Remove any "." and ".." operators.
        translated_path = translated_path.absolute()
        
        return str(translated_path)

    def _translate_path_reverse(self, path) -> str:
        full_path = PurePath(path)
        
        # Extract the relative component.
        relative_path = full_path.relative_to(self._base_path)
        
        # Append a leading slash and present to the user as a POSIX path.
        translated_path = "/" + relative_path.as_posix()
    
        return translated_path
    pass

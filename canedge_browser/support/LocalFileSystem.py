from canedge_browser.support.AbstractFileSystemWithBucket import AbstractFileSystemWithBucket


class LocalFileSystem(AbstractFileSystemWithBucket):
    """LocalFileSystem implements a subset of the AbstractFileSystem from fsspec, such that all calls are forwarded to
    the implementation from fsspec, but with another root dir.
    
    """
    def __init__(self, base_path, *args, **storage_options):
        storage_options["paths_with_leading_slash"] = True
        super().__init__("file", base_path, *args, **storage_options)
        
        return
    
    pass

import bisect
import fsspec
import functools

from datetime import datetime, timezone
from typing import List, Optional, Union, Callable, Set

import canedge_browser.config as config

from canedge_browser.support.FuncBackedList import FuncBackedList


def get_first_timestamp(
        fs: fsspec.AbstractFileSystem,
        path: str = "/",
        file_extensions=None,
        *args,
        **kwargs) -> Optional[datetime]:
    """With the given path, either look for the first file (if a folder) or get the timestamp directly (if a file).
    
    :keyword extract_date:      Function which takes a path to a log file and returns the timestamp of the first
                                measurement.
    
    :param fs:                  Filesystem to operate on.
    :param path:                Path to either file or folder to extract the first timestamp from.
    :param file_extensions:     List of extensions to search for, ignoring case. Defaults to ["MF4"].
    :return:                    The timestamp or None in case of error.
    """
    
    # Sanity check.
    if fs is None:
        raise ValueError("fs cannot be None")
    if path is None:
        raise ValueError("path cannot be None")

    # To avoid mutable default arguments.
    if file_extensions is None:
        file_extensions = ["MF4"]

    # Ensure patterns a lower case
    extensions = {ext.lower() for ext in file_extensions}

    local_path = path
    extract_date = kwargs.get("extract_date", _extract_date_mdf4)
    
    # If the input is a list, return a list.
    if isinstance(path, list):
        result = []
        
        for entry in path:
            result.append(_extract_date_helper(fs, entry, extensions, extract_date))
        
    else:
        result = _extract_date_helper(fs, path, extensions, extract_date)
    
    return result


def get_log_files(
        fs: fsspec.AbstractFileSystem,
        devices: Union[List[str], str],
        path: str = "/",
        file_extensions=None,
        *args,
        **kwargs
) -> []:
    """Get all log files.
    If an interval is specified, this is used to search for files.
    If more than one device is specified, the result will contain the merged results.
    
    :keyword start_date:        Optional start date to select files from.
    :keyword stop_date:         Optional stop date to select files up to.
    :keyword extract_date:      Function which takes a path to a log file and returns the timestamp of the first
                                measurement.
    
    :param fs:                  Filesystem to extract data through.
    :param devices:             Single device or list of devices to find log files for. Requires the full path.
    :param path:                Path to prepend on all the devices.
    :param file_extensions:     List of extensions to search for, ignoring case. Defaults to ["MF4"].
    :return:                    List of log file paths.
    """
    # Validate input.
    if fs is None:
        raise ValueError("Expected a filesystem instance to work on")
    elif not isinstance(fs, fsspec.AbstractFileSystem):
        raise TypeError("Passed filesystem does not implement fsspec.AbstractFileSystem")
    
    # To avoid mutable default arguments.
    if file_extensions is None:
        file_extensions = ["MF4"]
    
    # Ensure patterns a lower case
    extensions = {ext.lower() for ext in file_extensions}
    
    # Determine if the input is a single argument or a list.
    if devices is None:
        raise TypeError("Devices must be either a string or an iterable of strings")
    
    if isinstance(devices, str):
        devices = [devices]
    
    # Create a proper device list, by merging the passed devices with the path.
    for i, device in enumerate(devices):
        devices[i] = "{}/{}".format(path, device)
    
    # If the required arguments are supplied, enable support for searching between dates.
    start_date = kwargs.get("start_date", None)
    stop_date = kwargs.get("stop_date", None)
    extract_date = kwargs.get("extract_date", _extract_date_mdf4)
    
    # Wrap the extractor such that it receives a file handle.
    extract_date_wrapper = functools.partial(
        _extract_date_wrapper,
        extract_date=extract_date,
        fs=fs,
    )
    extract_date_from_session_wrapper = functools.partial(
        _extract_date_from_session_wrapper,
        extract_date=extract_date,
        fs=fs,
        extensions=extensions,
    )
    
    result = []
    
    for device in devices:
        # Get all folders.
        try:
            sessions = _get_objects_in_path(fs, device, target_type="directory")
        except FileNotFoundError:
            continue

        # If dates are supplied, perform binary search for the correct session and log file.
        selected_sessions = _bisect_list(
            sorted_objects=sessions,
            lower_bound=start_date,
            upper_bound=stop_date,
            extractor=extract_date_from_session_wrapper
        )
        
        # For each session folder, list all matching files.
        if len(selected_sessions) == 1:
            # Only a single session. Extract all files and bisect in the folder.
            log_file_list = _get_objects_in_path(fs, selected_sessions[0], target_type="file", extensions=extensions)
            result.extend(
                _bisect_list(
                    sorted_objects=log_file_list,
                    lower_bound=start_date,
                    upper_bound=stop_date,
                    extractor=extract_date_wrapper
                )
            )
        elif len(selected_sessions) > 1:
            # The start and stop sessions does not overlap. Find the start in one, the end in the other and include all
            # entries in between. First, handle start session.
            log_file_list = _get_objects_in_path(fs, selected_sessions[0], target_type="file", extensions=extensions)
            if len(log_file_list) == 1:
                result.extend(log_file_list)
            else:
                result.extend(
                    _bisect_list(
                        sorted_objects=log_file_list,
                        lower_bound=start_date,
                        extractor=extract_date_wrapper
                    )
                )
            
            # Find all files in between.
            for session in selected_sessions[1:-1]:
                result.extend(_get_objects_in_path(fs, session, target_type="file", extensions=extensions))

            # Handle stop session.
            log_file_list = _get_objects_in_path(fs, selected_sessions[-1], target_type="file", extensions=extensions)
            if len(log_file_list) == 1:
                result.extend(log_file_list)
            else:
                result.extend(
                    _bisect_list(
                        sorted_objects=log_file_list,
                        upper_bound=stop_date,
                        extractor=extract_date_wrapper
                    )
                )

    # Assume the files have a counter in the file name, such that the sorted list is the correct ordering.
    return sorted(result)


def _extract_date_helper(fs, path, extensions, extract_date):
    result = None

    if fs.isdir(path):
        # Get all log files sorted by name.
        log_file_list = _get_objects_in_path(fs, path, target_type="file", extensions=extensions)
    
        if len(log_file_list) > 0:
            path = log_file_list[0]
        pass

    if fs.isfile(path):
        # Attempt to open the file using the mdf iterator.
        with fs.open(path) as handle:
            result = extract_date(handle)
        pass
    
    return result
    

def _extract_date_mdf4(path):
    """Default extract date function
    
    """
    import mdf_iter
    
    mdf_file = mdf_iter.MdfFile(path)
    date_of_first_measurement = mdf_file.get_first_measurement()
    date_of_first_measurement = datetime.utcfromtimestamp(date_of_first_measurement * 1E-9)
    date_of_first_measurement = date_of_first_measurement.replace(tzinfo=timezone.utc)
    
    return date_of_first_measurement


def _get_objects_in_path(
        fs: fsspec.AbstractFileSystem,
        path: str,
        target_type: Optional[str] = None,
        extensions: Optional[Set[str]] = None
) -> List[str]:
    """Get all objects of a specific type in the supplied path on the target file system.
    
    """
    result = []
    
    if target_type is not None:
        # List all objects with detailed information.
        files = fs.ls(path, detail=True)  # type: List[dict]

        for entry in files:
            if entry.get("type") != target_type:
                continue
            
            result.append(entry.get("name"))
    else:
        # List all objects without detailed information.
        result = fs.ls(path, detail=False)

    # If extensions are supplied, apply these as well.
    if extensions is not None:
        entries = result
        result = []
        
        for entry in entries:
            try:
                base, ext = entry.rsplit(".", 1)
            except ValueError:
                continue

            if ext.lower() not in extensions:
                continue
            
            result.append(entry)
    
    # Assume the files have a counter in the file name, such that the sorted list is the correct ordering.
    return sorted(result)
    

def _extract_date_wrapper(path: str, extract_date: Callable, fs: fsspec.AbstractFileSystem) -> datetime:
    # Use the supplied file path and filesystem to get a handle.
    with fs.open(path, "rb", block_size=config.S3FS_DEFAULT_BLOCK_SIZE, fill_cache=False) as handle:
        # Pass the handle to the wrapped extract date function.
        result = extract_date(handle)
    
    return result


def _extract_date_from_session_wrapper(
        path: str,
        extract_date: Callable,
        fs: fsspec.AbstractFileSystem,
        extensions: Set[str]
) -> datetime:
    result = datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc)
    
    # Ensure all the extensions are lowercase.
    extensions = {ext.lower() for ext in extensions}
    
    # Use the supplied file path and filesystem to get a list of files in the session.
    session_log_files = _get_objects_in_path(fs, path, target_type="file", extensions=extensions)
    
    # Open the first valid file.
    if len(session_log_files) > 0:
        with fs.open(session_log_files[0], "rb", block_size=config.S3FS_DEFAULT_BLOCK_SIZE, fill_cache=False) as handle:
            # Pass the handle to the wrapped extract date function.
            result = extract_date(handle)
    
    return result


def _bisect_list(
        sorted_objects: List[str],
        extractor: Optional[Callable] = None,
        lower_bound: Optional[datetime] = None,
        upper_bound: Optional[datetime] = None
):
    """Search through all entries in a list, extracting those within the date range.
    
    :param sorted_objects: Sorted list of objects to apply the function on.
    :param extractor: Function to apply. The current item in the list will be passed as the first arg, so any other
                      arguments should be inserted using functools.partial or similar.
    :param lower_bound: Lower bound to find items above.
    :param upper_bound: Upper bound to find items below.
    """
    # Populate default values.
    start_index = 0
    stop_index = len(sorted_objects)
    
    # Perform extraction if a valid callable is passed.
    if extractor is not None and callable(extractor):
        bisect_list = FuncBackedList(extractor, sorted_objects)
        
        # Only check for lower bound if present.
        if lower_bound is not None:
            start_index = bisect.bisect_left(bisect_list, lower_bound)
            
            if start_index != len(bisect_list) and start_index != 0:
                start_index -= 1

        # Only check for upper bound if present.
        if upper_bound is not None:
            stop_index = bisect.bisect_right(bisect_list, upper_bound)
            
            if stop_index > len(sorted_objects):
                stop_index = len(sorted_objects)
    
    return sorted_objects[start_index:stop_index]

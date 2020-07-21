import bisect

import fsspec

from datetime import datetime, timezone
from fsspec.implementations.local import LocalFileSystem
from pathlib import Path
from typing import List, Optional, Union

from canedge_browser.FuncBackedList import FuncBackedList


def get_log_files(
        fs: fsspec.AbstractFileSystem,
        devices: Union[List[str], str],
        path: Optional[str] = None,
        file_pattern=None,
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
    :param file_pattern:
    :return:                    List of log file paths.
    """
    # Validate input.
    if fs is None:
        raise ValueError("Expected a filesystem instance to work on")
    elif not isinstance(fs, fsspec.AbstractFileSystem):
        raise TypeError("Passed filesystem does not implement fsspec.AbstractFileSystem")
    
    # To avoid mutable default arguments.
    if file_pattern is None:
        file_pattern = ["MF4"]
        
    # Determine if the input is a single argument or a list.
    if isinstance(devices, str):
        devices = [devices]
    
    # If no path is passed, and the filesystem is local, assume current path.
    if isinstance(fs, fsspec.implementations.local.LocalFileSystem) and path is None:
        path = Path("__file__").parent.absolute()
    
    for i, device in enumerate(devices):
        devices[i] = "{}/{}".format(path, device)
    
    # If the required arguments are supplied, enable support for searching between dates.
    start_date = kwargs.get("start_date", None)
    stop_date = kwargs.get("stop_date", None)
    extract_date = kwargs.get("extract_date", None)
    
    if extract_date is None:
        # Use the default date extractor. Works with MDF4 files.
        def extract_date_default(file_path: str):
            import mdf_iter

            with fs.open(file_path) as handle:
                mdf_file = mdf_iter.MdfFile(handle)
                date_of_first_measurement = mdf_file.get_first_measurement()
            date_of_first_measurement = datetime.utcfromtimestamp(date_of_first_measurement * 1E-9)
            date_of_first_measurement = date_of_first_measurement.replace(tzinfo=timezone.utc)
            return date_of_first_measurement
        
        extract_date = extract_date_default

    def extract_date_sessions(session: str) -> datetime:
        """Helper function utilized when listing a session.
        
        :param session: Full path to the session to handle.
        :return: Date for the first log file in the session, or 0 epoch.
        """
        session_log_files = fs.ls(session)
        session_timestamp = datetime.utcfromtimestamp(0)
        
        if len(session_log_files) > 0:
            session_timestamp = extract_date(session_log_files[0])
        return session_timestamp
    
    result = []
    
    for device in devices:
        # Get all folders matching the pattern.
        session_list = fs.ls(device, detail=True)
        
        sessions = []
        
        for entry in session_list:  # type: dict
            if entry.get("type") != "directory":
                continue
            sessions.append(entry.get("name"))
        
        # If dates are supplied, perform binary search for the correct session and log file.
        start_index_session = 0
        stop_index_session = len(sessions) - 1
        
        if extract_date is not None:
            bisect_list = FuncBackedList(extract_date_sessions, sessions)
            
            if start_date is not None:
                # Determine a coarse start index.
                start_index_session = bisect.bisect_left(bisect_list, start_date) - 1
                if start_index_session < 0:
                    start_index_session = 0
                pass
            
            if stop_date is not None:
                # Determine a coarse stop index.
                stop_index_session = bisect.bisect_left(bisect_list, stop_date)
                if stop_index_session >= len(sessions):
                    stop_index_session = len(sessions) - 1
                pass
        
        # For each session folder, list all matching files.
        if start_index_session == stop_index_session:
            # Only a single session.
            log_file_list = []
            log_file_list_raw = fs.ls(sessions[start_index_session], detail=True)

            for entry in log_file_list_raw:  # type: dict
                if entry.get("type") == "directory":
                    continue
                log_file_list.append(entry.get("name"))

            start_index = 0
            stop_index = len(log_file_list)
            
            if extract_date is not None:
                bisect_list = FuncBackedList(extract_date, log_file_list)
            
                if start_date is not None:
                    start_index = bisect.bisect_left(bisect_list, start_date) - 1
                    if start_index < 0:
                        start_index = 0
                
                if stop_date is not None:
                    stop_index = bisect.bisect_right(bisect_list, stop_date)
                    if stop_index > len(log_file_list):
                        stop_index = len(log_file_list)
            
            result.extend(log_file_list[start_index:stop_index])
        else:
            # Handle when the start and stop session does not overlap.
            log_file_list = []
            
            # Handle start.
            log_file_list_raw = fs.ls(sessions[start_index_session], detail=True)

            for entry in log_file_list_raw:  # type: dict
                if entry.get("type") == "directory":
                    continue
                log_file_list.append(entry.get("name"))

            start_index = 0
            if extract_date is not None:
                bisect_list = FuncBackedList(extract_date, log_file_list)

                if start_date is not None:
                    start_index = bisect.bisect_left(bisect_list, start_date) - 1
                    if start_index < 0:
                        start_index = 0
            
            result.extend(log_file_list[start_index:])
            
            # Handle files in between the start and stop sessions.
            for session in range(start_index_session + 1, stop_index_session):
                log_file_list = []
                log_file_list_raw = fs.ls(sessions[session], detail=True)
    
                for entry in log_file_list_raw:  # type: dict
                    if entry.get("type") == "directory":
                        continue
                    log_file_list.append(entry.get("name"))
                
                result.extend(log_file_list)

            # Handle stop.
            log_file_list_raw = fs.ls(sessions[stop_index_session], detail=True)

            for entry in log_file_list_raw:  # type: dict
                if entry.get("type") == "directory":
                    continue
                log_file_list.append(entry.get("name"))

            stop_index = 0
            if extract_date is not None:
                bisect_list = FuncBackedList(extract_date, log_file_list)

                if stop_date is not None:
                    stop_index = bisect.bisect_right(bisect_list, stop_date)
                    if stop_index >= len(log_file_list):
                        stop_index = len(log_file_list) - 1

            result.extend(log_file_list[:stop_index])
        pass
    
    return result

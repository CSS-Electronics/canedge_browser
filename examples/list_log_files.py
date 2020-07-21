import canedge_browser

from datetime import datetime, timezone


def setup_fs():
    """Helper function to setup the file system for the examples.
    
    :return: filesystem abstraction base path
    """
    from fsspec.implementations.local import LocalFileSystem
    
    fs = LocalFileSystem()
    
    return fs


def setup_fs_s3():
    """Helper function demonstrating the required parameters to setup a remote S3 filesystem connection.
    
    :return: filesystem abstraction base path
    """
    import s3fs

    fs = s3fs.S3FileSystem(
        key="<key>",
        secret="<secret>",
        client_kwargs={
            "endpoint_url": "http://address.of.remote.s3.server:9000",
        },
    )
    
    return fs


def example_list_all_files_for_devices():
    """This examples lists all available log file for a set of devices between two dates.

    Expects file hierarchy to follow that of CANedge loggers.
    Note that a large session count will result in a long listing time.
    """
    fs = setup_fs()

    devices = [
        "LOG/EEEE0001",
        "LOG/EEEE0002",
        "LOG/EEEE0003",
        "LOG/EEEE0004",
    ]

    log_files = canedge_browser.get_log_files(fs, devices)

    print("Found a total of {} log files".format(len(log_files)))
    for log_file in log_files:
        print(log_file)

    return


def example_list_files_for_devices_between_dates():
    """This examples lists all available log file for a set of devices between two dates.

    Expects file hierarchy to follow that of CANedge loggers.
    Note that a large session count will result in a long listing time.
    """
    fs = setup_fs()

    devices = [
        "LOG/EEEE0001",
        "LOG/EEEE0002",
        "LOG/EEEE0003",
        "LOG/EEEE0004",
    ]

    start_date = datetime(year=2020, month=6, day=5, hour=10, tzinfo=timezone.utc)
    stop_date = datetime(year=2021, month=3, day=4, tzinfo=timezone.utc)

    log_files = canedge_browser.get_log_files(
        fs, devices, start_date=start_date, stop_date=stop_date
    )

    print("Found a total of {} log files".format(len(log_files)))
    for log_file in log_files:
        print(log_file)

    return


if __name__ == "__main__":
    print("Listing all files for the selected devices:")
    example_list_all_files_for_devices()
    
    print("")
    print("Listing files between two select dates:")
    example_list_files_for_devices_between_dates()
    pass

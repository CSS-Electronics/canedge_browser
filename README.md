# CANedge Browser - List Log Files (Local, S3)
This package lets you easily list [CANedge](https://www.csselectronics.com/) CAN data log files. Simply specify the source (local disk or S3 server) and the start/stop period. The listed log files can then be used with other packages such as `mdf_iter` and `can_decoder`.

---
### Key features
```
1. Extract a subset of log files between a start/stop date & time
```

---
### Installation
Use pip to install the `canedge_browser` module:
```
pip install canedge_browser
```

---
### Dependencies
* `fsspec` (required)
* `mdf_iter` (required)

---
### Module usage example
In the below example, we list log files between two dates from a [MinIO](https://min.io/) S3 server:
```
import canedge_browser
import s3fs
from datetime import datetime, timezone

fs = s3fs.S3FileSystem(
    key="<key>",
    secret="<secret>",
    client_kwargs={
        "endpoint_url": "http://address.of.remote.s3.server:9000",
    },
)

devices = ["<bucket>/23AD1AEA", "<bucket>/86373F4D"]
start = datetime(year=2020, month=8, day=4, hour=10, tzinfo=timezone.utc)
stop = datetime(year=2020, month=9, day=9, tzinfo=timezone.utc)

log_files = canedge_browser.get_log_files(fs, devices, start_date=start, stop_date=stop)

print("Found a total of {} log files".format(len(log_files)))
for log_file in log_files:
    print(log_file)

```

---

### Regarding timezone
NOTE: All time inputs into the library must include a timezone. If in doubt, set this to UTC (+00:00).

---

### Regarding S3 server types
If you need to connect to e.g. an AWS S3 server, simply use the relevant endpoint (e.g. `https://s3.amazonaws.com`). Similarly, for MinIO servers, you would use the relevant endpoint (e.g. `http://192.168.0.1:9000`).

#### HTTP vs. HTTPS
To connect to a MinIO S3 server where TLS is enabled via a self-signed certificate, you can connect by adding the path to your public certificate in the `verify` field in the `setup_fs_s3` function.

---

### Regarding path syntax 
Note that all paths are relative to the root `/`. For POSIX systems, this will likely follow the normal filesystem structure. Windows systems gets a slightly mangled syntax, such that `C:\Some folder\a subfolder\the target file.MF4` becomes `/C:/Some folder/a subfolder/the target file.MF4`.

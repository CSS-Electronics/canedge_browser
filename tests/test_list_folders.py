import canedge_browser
import pytest

from datetime import datetime, timezone
from fsspec import AbstractFileSystem
from pathlib import Path


class TestListLogFiles(object):
    
    @pytest.fixture()
    def fs(self) -> AbstractFileSystem:
        # Use the files already present in the examples section for testing.
        test_data_path = Path(__file__).parent.parent / "examples" / "LOG"
        
        fs = canedge_browser.LocalFileSystem(base_path=test_data_path)
        
        return fs
    
    def test_get_log_files_with_no_filesystem(self):
        """Sending invalid input should raise an exception.
        """
        fs = None
        devices = "AABBCCDD"
        
        with pytest.raises(ValueError):
            canedge_browser.get_log_files(fs, devices)
        
        return

    def test_get_log_files_with_invalid_filesystem(self):
        """Sending invalid input should raise an exception.
        """
        class InvalidFileSystem(object):
            pass
        
        fs = InvalidFileSystem()
        devices = "AABBCCDD"
    
        with pytest.raises(TypeError):
            canedge_browser.get_log_files(fs, devices)
    
        return
    
    def test_get_log_files_with_no_devices(self, fs):
        """Sending invalid input should raise an exception.
        """
        devices = None
        
        with pytest.raises(TypeError):
            canedge_browser.get_log_files(fs, devices)
        return

    def test_get_log_files_with_invalid_device(self, fs):
        """With a invalid/non-existing device name, ensure that no exceptions are thrown but merely an empty set of
         results is received.
        """
        devices = "abcdefghijkl"
    
        result = canedge_browser.get_log_files(fs, devices)
        
        assert len(result) == 0
        return

    def test_get_log_files_single_device_as_str(self, fs):
        """With a single valid device passed as a string, ensure that the expected log files are returned.
        """
        devices = "EEEE0001"
        
        expected_files = {
            "/EEEE0001/00000001/00000001.MF4",
            "/EEEE0001/00000001/00000002.MF4",
            "/EEEE0001/00000001/00000003.MF4",
            "/EEEE0001/00000001/00000004.MF4",
            "/EEEE0001/00000001/00000005.MF4",
            "/EEEE0001/00000001/00000006.MF4",
            "/EEEE0001/00000001/00000007.MF4",
            "/EEEE0001/00000001/00000008.MF4",
            "/EEEE0001/00000001/00000009.MF4",
            "/EEEE0001/00000002/00000257.MF4",
            "/EEEE0001/00000003/00000513.MF4",
            "/EEEE0001/00000004/00000769.MF4",
            "/EEEE0001/00000005/00001025.MF4",
        }
    
        result = canedge_browser.get_log_files(fs, devices)
        
        assert expected_files == set(result)
        return

    def test_get_log_files_single_device_as_list(self, fs):
        """With a single valid device passed as a list, ensure that the expected log files are returned.
        """
        devices = ["EEEE0001"]

        expected_files = {
            "/EEEE0001/00000001/00000001.MF4",
            "/EEEE0001/00000001/00000002.MF4",
            "/EEEE0001/00000001/00000003.MF4",
            "/EEEE0001/00000001/00000004.MF4",
            "/EEEE0001/00000001/00000005.MF4",
            "/EEEE0001/00000001/00000006.MF4",
            "/EEEE0001/00000001/00000007.MF4",
            "/EEEE0001/00000001/00000008.MF4",
            "/EEEE0001/00000001/00000009.MF4",
            "/EEEE0001/00000002/00000257.MF4",
            "/EEEE0001/00000003/00000513.MF4",
            "/EEEE0001/00000004/00000769.MF4",
            "/EEEE0001/00000005/00001025.MF4",
        }

        result = canedge_browser.get_log_files(fs, devices)

        assert expected_files == set(result)
        return
    
    def test_get_log_files_with_custom_extension(self, fs):
        """Attempt to use a non-default extension. Test for both upper- and lower-case variants.
        """
        devices = ["EEEE0001"]

        expected_files = {
            "/EEEE0001/00000001/ignore.me",
        }

        result_a = canedge_browser.get_log_files(fs, devices, file_extensions=["me"])
        result_b = canedge_browser.get_log_files(fs, devices, file_extensions=["ME"])

        assert expected_files == set(result_a)
        assert expected_files == set(result_b)
        return
        
    def test_get_log_files_with_multiple_extensions(self, fs):
        """Attempt to use a set of extensions.
        """
        devices = ["EEEE0001"]

        expected_files = {
            "/EEEE0001/00000001/00000001.MF4",
            "/EEEE0001/00000001/00000002.MF4",
            "/EEEE0001/00000001/00000003.MF4",
            "/EEEE0001/00000001/00000004.MF4",
            "/EEEE0001/00000001/00000005.MF4",
            "/EEEE0001/00000001/00000006.MF4",
            "/EEEE0001/00000001/00000007.MF4",
            "/EEEE0001/00000001/00000008.MF4",
            "/EEEE0001/00000001/00000009.MF4",
            "/EEEE0001/00000002/00000257.MF4",
            "/EEEE0001/00000003/00000513.MF4",
            "/EEEE0001/00000004/00000769.MF4",
            "/EEEE0001/00000005/00001025.MF4",
            "/EEEE0001/00000001/ignore.me",
        }

        result = canedge_browser.get_log_files(fs, devices, file_extensions=["me", "MF4"])
        
        assert expected_files == set(result)
        return
    
    def test_get_log_files_with_multiple_devices(self, fs):
        """Use a device list with multiple devices.
        """
        devices = [
            "EEEE0001",
            "EEEE0002",
        ]

        expected_files = {
            "/EEEE0001/00000001/00000001.MF4",
            "/EEEE0001/00000001/00000002.MF4",
            "/EEEE0001/00000001/00000003.MF4",
            "/EEEE0001/00000001/00000004.MF4",
            "/EEEE0001/00000001/00000005.MF4",
            "/EEEE0001/00000001/00000006.MF4",
            "/EEEE0001/00000001/00000007.MF4",
            "/EEEE0001/00000001/00000008.MF4",
            "/EEEE0001/00000001/00000009.MF4",
            "/EEEE0001/00000002/00000257.MF4",
            "/EEEE0001/00000003/00000513.MF4",
            "/EEEE0001/00000004/00000769.MF4",
            "/EEEE0001/00000005/00001025.MF4",
            '/EEEE0002/00000001/00000001.MF4',
        }

        result = canedge_browser.get_log_files(fs, devices)

        assert expected_files == set(result)
        return
    
    def test_get_log_files_with_multiple_devices_and_non_existing_devices(self, fs):
        """Use a device list with multiple devices, some of which are not present. Should only show the files for the
        devices present.
        """
        devices = [
            "EEEE0011",
            "EEEE0001",
            "EEEE0002",
            "EEEE0012",
        ]

        expected_files = {
            "/EEEE0001/00000001/00000001.MF4",
            "/EEEE0001/00000001/00000002.MF4",
            "/EEEE0001/00000001/00000003.MF4",
            "/EEEE0001/00000001/00000004.MF4",
            "/EEEE0001/00000001/00000005.MF4",
            "/EEEE0001/00000001/00000006.MF4",
            "/EEEE0001/00000001/00000007.MF4",
            "/EEEE0001/00000001/00000008.MF4",
            "/EEEE0001/00000001/00000009.MF4",
            "/EEEE0001/00000002/00000257.MF4",
            "/EEEE0001/00000003/00000513.MF4",
            "/EEEE0001/00000004/00000769.MF4",
            "/EEEE0001/00000005/00001025.MF4",
            '/EEEE0002/00000001/00000001.MF4',
        }

        result = canedge_browser.get_log_files(fs, devices)

        assert expected_files == set(result)
        return
    
    def test_get_log_files_with_start_date(self, fs):
        """Test all files are returned when the start date is outside the range.
        """
        devices = ["EEEE0001"]
        start_date = datetime(year=2020, month=1, day=5, hour=10, tzinfo=timezone.utc)
        
        expected_files = {
            "/EEEE0001/00000001/00000001.MF4",
            "/EEEE0001/00000001/00000002.MF4",
            "/EEEE0001/00000001/00000003.MF4",
            "/EEEE0001/00000001/00000004.MF4",
            "/EEEE0001/00000001/00000005.MF4",
            "/EEEE0001/00000001/00000006.MF4",
            "/EEEE0001/00000001/00000007.MF4",
            "/EEEE0001/00000001/00000008.MF4",
            "/EEEE0001/00000001/00000009.MF4",
            "/EEEE0001/00000002/00000257.MF4",
            "/EEEE0001/00000003/00000513.MF4",
            "/EEEE0001/00000004/00000769.MF4",
            "/EEEE0001/00000005/00001025.MF4",
        }

        result = canedge_browser.get_log_files(fs, devices, start_date=start_date)

        assert expected_files == set(result)
        return

    def test_get_log_files_with_start_date_limiting_a(self, fs):
        """Test only a subset of files are returned when the start date is inside the range.
        """
        devices = ["EEEE0001"]
        start_date = datetime(year=2021, month=5, day=12, hour=0, tzinfo=timezone.utc)
    
        expected_files = {
            "/EEEE0001/00000004/00000769.MF4",
            "/EEEE0001/00000005/00001025.MF4",
        }
    
        result = canedge_browser.get_log_files(fs, devices, start_date=start_date)
    
        assert expected_files == set(result)
        return

    def test_get_log_files_with_start_date_limiting_b(self, fs):
        """Test only a subset of files are returned when the start date is inside the range.
        """
        devices = ["EEEE0001"]
        start_date = datetime(year=2020, month=6, day=5, hour=0, tzinfo=timezone.utc)
    
        expected_files = {
            "/EEEE0001/00000001/00000003.MF4",
            "/EEEE0001/00000001/00000004.MF4",
            "/EEEE0001/00000001/00000005.MF4",
            "/EEEE0001/00000001/00000006.MF4",
            "/EEEE0001/00000001/00000007.MF4",
            "/EEEE0001/00000001/00000008.MF4",
            "/EEEE0001/00000001/00000009.MF4",
            "/EEEE0001/00000002/00000257.MF4",
            "/EEEE0001/00000003/00000513.MF4",
            "/EEEE0001/00000004/00000769.MF4",
            "/EEEE0001/00000005/00001025.MF4",
        }
    
        result = canedge_browser.get_log_files(fs, devices, start_date=start_date)
    
        assert expected_files == set(result)
        return

    def test_get_log_files_with_stop_date(self, fs):
        """Test all files are returned when the stop date is outside the range.
        """
        devices = ["EEEE0001"]
        stop_date = datetime(year=2022, month=1, day=5, hour=10, tzinfo=timezone.utc)
    
        expected_files = {
            "/EEEE0001/00000001/00000001.MF4",
            "/EEEE0001/00000001/00000002.MF4",
            "/EEEE0001/00000001/00000003.MF4",
            "/EEEE0001/00000001/00000004.MF4",
            "/EEEE0001/00000001/00000005.MF4",
            "/EEEE0001/00000001/00000006.MF4",
            "/EEEE0001/00000001/00000007.MF4",
            "/EEEE0001/00000001/00000008.MF4",
            "/EEEE0001/00000001/00000009.MF4",
            "/EEEE0001/00000002/00000257.MF4",
            "/EEEE0001/00000003/00000513.MF4",
            "/EEEE0001/00000004/00000769.MF4",
            "/EEEE0001/00000005/00001025.MF4",
        }
    
        result = canedge_browser.get_log_files(fs, devices, stop_date=stop_date)
    
        assert expected_files == set(result)
        return

    def test_get_log_files_with_stop_date_limiting_a(self, fs):
        """Test only a subset of files are returned when the stop date is inside the range.
        """
        devices = ["EEEE0001"]
        stop_date = datetime(year=2020, month=6, day=6, hour=7, tzinfo=timezone.utc)
    
        expected_files = {
            "/EEEE0001/00000001/00000001.MF4",
            "/EEEE0001/00000001/00000002.MF4",
            "/EEEE0001/00000001/00000003.MF4",
            "/EEEE0001/00000001/00000004.MF4",
            "/EEEE0001/00000001/00000005.MF4",
            "/EEEE0001/00000001/00000006.MF4"
        }
    
        result = canedge_browser.get_log_files(fs, devices, stop_date=stop_date)
    
        assert expected_files == set(result)
        return

    def test_get_log_files_with_stop_date_limiting_b(self, fs):
        """Test only a subset of files are returned when the stop date is inside the range.
        """
        devices = ["EEEE0001"]
        stop_date = datetime(year=2020, month=8, day=29, hour=7, tzinfo=timezone.utc)
    
        expected_files = {
            "/EEEE0001/00000001/00000001.MF4",
            "/EEEE0001/00000001/00000002.MF4",
            "/EEEE0001/00000001/00000003.MF4",
            "/EEEE0001/00000001/00000004.MF4",
            "/EEEE0001/00000001/00000005.MF4",
            "/EEEE0001/00000001/00000006.MF4",
            "/EEEE0001/00000001/00000007.MF4",
            "/EEEE0001/00000001/00000008.MF4",
            "/EEEE0001/00000001/00000009.MF4",
            "/EEEE0001/00000002/00000257.MF4",
        }
    
        result = canedge_browser.get_log_files(fs, devices, stop_date=stop_date)
    
        assert expected_files == set(result)
        return

    def test_get_log_files_with_start_and_stop_date_limiting_a(self, fs):
        """Test only a subset of files are returned when the start and stop dates are inside the range.
        """
        devices = ["EEEE0001"]
        start_date = datetime(year=2020, month=6, day=5, hour=0, tzinfo=timezone.utc)
        stop_date = datetime(year=2020, month=6, day=6, hour=7, tzinfo=timezone.utc)
    
        expected_files = {
            "/EEEE0001/00000001/00000003.MF4",
            "/EEEE0001/00000001/00000004.MF4",
            "/EEEE0001/00000001/00000005.MF4",
            "/EEEE0001/00000001/00000006.MF4",
        }
    
        result = canedge_browser.get_log_files(fs, devices, start_date=start_date, stop_date=stop_date)
    
        assert expected_files == set(result)
        return

    def test_get_log_files_with_start_and_stop_date_limiting_b(self, fs):
        """Test only a subset of files are returned when the start and stop dates are inside the range.
        """
        devices = ["EEEE0001"]
        start_date = datetime(year=2020, month=6, day=5, hour=0, tzinfo=timezone.utc)
        stop_date = datetime(year=2020, month=8, day=29, hour=7, tzinfo=timezone.utc)
    
        expected_files = {
            "/EEEE0001/00000001/00000003.MF4",
            "/EEEE0001/00000001/00000004.MF4",
            "/EEEE0001/00000001/00000005.MF4",
            "/EEEE0001/00000001/00000006.MF4",
            "/EEEE0001/00000001/00000007.MF4",
            "/EEEE0001/00000001/00000008.MF4",
            "/EEEE0001/00000001/00000009.MF4",
            "/EEEE0001/00000002/00000257.MF4",
        }
    
        result = canedge_browser.get_log_files(fs, devices, start_date=start_date, stop_date=stop_date)
    
        assert expected_files == set(result)
        return
    
    pass

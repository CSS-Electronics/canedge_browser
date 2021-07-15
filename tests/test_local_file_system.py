import canedge_browser
import pytest

from pathlib import Path


class TestLocalFileSystem(object):
    
    @pytest.fixture()
    def setup_folders(self):
        from tempfile import TemporaryDirectory
        
        with TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # Create some temporary files.
            temp_files = [
                temp_dir_path / "file_without_extension",
                temp_dir_path / "file_with_extension.txt",
                temp_dir_path / "folder" / "with_file.a",
            ]
            
            for temp_file in temp_files:
                if not temp_file.parent.exists():
                    temp_file.parent.mkdir(parents=True)
                temp_file.touch()
            
            yield temp_dir_path
        
        return
    
    @pytest.fixture()
    def uut(self, setup_folders):
        return canedge_browser.LocalFileSystem(base_path=setup_folders)
    
    def test_ls_with_details(self, uut):
        expected_names = {
            "/file_without_extension",
            "/file_with_extension.txt",
            "/folder",
        }
        
        result = uut.ls("", detail=True)
        
        extracted_names = set()
        for entry in result:
            extracted_names.add(entry["name"])
        
        assert extracted_names == expected_names
        
        return
    
    def test_ls_without_details(self, uut):
        expected_names = {
            "/file_without_extension",
            "/file_with_extension.txt",
            "/folder",
        }
    
        result = uut.ls("", detail=False)
        extracted_names = set(result)
        
        assert extracted_names == expected_names
    
        return
    
    pass

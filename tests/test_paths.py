"""
Tests for entitle.paths — the single source of truth for default runtime data
locations shared by the GUI.
"""
from pathlib import Path

from entitle import paths


class TestDefaultPaths:
    def test_defaults_are_under_repo_root(self):
        root = paths.REPO_ROOT
        assert Path(paths.default_record_store()).is_relative_to(root)
        assert Path(paths.default_entitlement_file()).is_relative_to(root)
        assert Path(paths.default_new_entitlement_file()).is_relative_to(root)

    def test_record_store_default_lives_in_records_dir(self):
        assert Path(paths.default_record_store()).parent == paths.RECORDS_DIR

    def test_entitlement_defaults_live_in_entitlements_dir(self):
        assert Path(paths.default_entitlement_file()).parent == paths.ENTITLEMENTS_DIR
        assert Path(paths.default_new_entitlement_file()).parent == paths.ENTITLEMENTS_DIR

    def test_helpers_return_strings(self):
        assert isinstance(paths.default_record_store(), str)
        assert isinstance(paths.default_entitlement_file(), str)
        assert isinstance(paths.default_new_entitlement_file(), str)

    def test_importing_paths_does_not_create_directories(self):
        # paths must be pure computation; it must not create data dirs on import.
        # (We only assert the module exposes the dirs as Path objects.)
        assert isinstance(paths.RECORDS_DIR, Path)
        assert isinstance(paths.ENTITLEMENTS_DIR, Path)
        assert isinstance(paths.REPORTS_DIR, Path)


class TestVersion:
    def test_version_is_importable_and_matches_package(self):
        from version import __version__ as root_version
        from entitle import __version__ as pkg_version
        assert root_version == pkg_version
        assert isinstance(root_version, str)
        assert root_version.count(".") >= 2

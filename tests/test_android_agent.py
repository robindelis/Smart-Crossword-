"""
Automated unit tests for Android Specialist Agent configuration and environment.
"""

import os
import pytest
from pathlib import Path

def test_android_environment():
    sdk_path = Path("/home/robin/Android/Sdk")
    assert sdk_path.is_dir(), f"Android SDK directory not found: {sdk_path}"
    
    adb_path = sdk_path / "platform-tools" / "adb"
    assert adb_path.is_file(), f"adb executable not found: {adb_path}"

    jbr_path = Path("/opt/android-studio/jbr/bin/java")
    assert jbr_path.is_file(), f"Java executable not found: {jbr_path}"

    studio_path = Path("/opt/android-studio/bin/studio.sh")
    assert studio_path.is_file(), f"Android Studio executable not found: {studio_path}"

def test_android_cli_tool():
    android_bin = Path("/home/robin/.local/bin/android")
    assert android_bin.is_file(), "android CLI tool not found in ~/.local/bin"
    assert os.access(android_bin, os.X_OK), "android CLI is not executable"

def test_antigravity_sdk_agent_config():
    from scripts.android_agent import create_agent_config
    config = create_agent_config()
    assert config is not None
    assert config.skills_paths is not None
    assert len(config.skills_paths) > 0
    assert "android-cli" in config.skills_paths[0]

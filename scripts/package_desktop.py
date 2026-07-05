#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create desktop release archives from PyInstaller output."""
import argparse
import os
import shutil
import stat
import tarfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / 'dist_package'


def normalize_version(value):
    version = (value or 'dev').strip()
    return version[1:] if version.startswith('v') else version


def write_text(path, content):
    path.write_text(content, encoding='utf-8')


def executable_path(platform_name):
    name = 'FinDataHub.exe' if platform_name == 'windows' else 'FinDataHub'
    return ROOT / 'backend' / 'dist' / name


def create_readme(platform_label):
    return f"""FinDataHub - 金融数据管理系统
===============================

适用系统: {platform_label}

使用说明
--------
1. 解压本发布包到任意文件夹。
2. Windows 双击 start.bat；macOS 双击 start.command，或在终端运行 ./FinDataHub。
3. 程序启动后会自动打开浏览器；也可以手动访问 http://127.0.0.1:5001。

数据存储
--------
默认数据库目录为发布包运行目录下的 data/，可通过 FINDATA_DATA_DIR 环境变量改写。

退出程序
--------
在启动窗口或终端中按 Ctrl+C。
"""


def package_windows(version):
    release_name = f'FinDataHub_v{version}_Windows'
    release_dir = DIST_DIR / release_name
    archive_path = DIST_DIR / f'{release_name}.zip'
    prepare_dir(release_dir)

    shutil.copy2(executable_path('windows'), release_dir / 'FinDataHub.exe')
    write_text(release_dir / 'README.txt', create_readme('Windows 10/11'))
    write_text(
        release_dir / 'start.bat',
        '@echo off\r\n'
        'chcp 65001 >nul\r\n'
        'title FinDataHub\r\n'
        'echo Starting FinDataHub...\r\n'
        'FinDataHub.exe\r\n'
        'pause\r\n',
    )

    if archive_path.exists():
        archive_path.unlink()
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(release_dir.rglob('*')):
            archive.write(file_path, file_path.relative_to(DIST_DIR))
    return archive_path


def package_macos(version):
    release_name = f'FinDataHub_v{version}_macOS'
    release_dir = DIST_DIR / release_name
    archive_path = DIST_DIR / f'{release_name}.tar.gz'
    prepare_dir(release_dir)

    binary = release_dir / 'FinDataHub'
    shutil.copy2(executable_path('macos'), binary)
    binary.chmod(binary.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    write_text(release_dir / 'README.txt', create_readme('macOS'))
    launcher = release_dir / 'start.command'
    write_text(
        launcher,
        '#!/bin/bash\n'
        'cd "$(dirname "$0")"\n'
        './FinDataHub\n',
    )
    launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    if archive_path.exists():
        archive_path.unlink()
    with tarfile.open(archive_path, 'w:gz') as archive:
        archive.add(release_dir, arcname=release_dir.name)
    return archive_path


def prepare_dir(path):
    DIST_DIR.mkdir(exist_ok=True)
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--platform', choices=['windows', 'macos'], required=True)
    parser.add_argument('--version', default='dev')
    args = parser.parse_args()

    version = normalize_version(args.version)
    source = executable_path(args.platform)
    if not source.exists():
        raise SystemExit(f'PyInstaller output not found: {source}')

    archive = package_windows(version) if args.platform == 'windows' else package_macos(version)
    print(archive)


if __name__ == '__main__':
    main()

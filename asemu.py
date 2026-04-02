# https://developer.android.com/studio/emulator_archive
# https://developer.android.com/tools/releases/platform-tools
# https://developer.android.com/studio#command-line-tools-only

import requests
from tqdm import tqdm
import os
import shutil
import subprocess
import typer
import shlex
import re
import sys

PLATFORM = {"win32": "win", "linux": "linux"}.get(sys.platform)
EMU_EXTENSION = ".exe" if PLATFORM == "win" else ""
CLI_EXTENSION = ".bat" if PLATFORM == "win" else ""

def get_cmdline_tool_url(platform: str):
    data = requests.get("https://dl.google.com/android/repository/repository2-3.xml").text
    latest = max(re.findall(fr"commandlinetools-{platform}-(\d+)_latest\.zip", data), key=int)
    return f"https://dl.google.com/android/repository/commandlinetools-{platform}-{latest}_latest.zip"

DOWNLOAD_COMMANDLINETOOLS = get_cmdline_tool_url(PLATFORM)

SDK_ROOT_PATH = "sdk_root"
AVD_PATH = "avd"

# Настройки
# ANDROID_SDK_VERSION = 36
# ANDROID_ARCH = "x86_64"
# ANDROID_IMAGE = "google_apis" #"google_apis_playstore"
# ADV_NAME = "phone"

os.makedirs(SDK_ROOT_PATH, exist_ok=True)
os.makedirs(AVD_PATH, exist_ok=True)

os.environ["ANDROID_SDK_ROOT"] = os.path.abspath(os.path.join('.', SDK_ROOT_PATH))
os.environ["ANDROID_AVD_HOME"] = os.path.abspath(os.path.join('.', AVD_PATH))

app = typer.Typer()

@app.command()
def run(
    name: str = typer.Option("phone", help="AVD name"),
    arch: str = typer.Option("x86_64", help="Architecture"),
    image: str = typer.Option("google_apis", help="System image"),
    sdk: int = typer.Option(36, help="Android SDK version"),
    extra: str = typer.Option("", "--extra", help="Additional flags for launch"),
):
    def download_file(url, filename):
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        with open(filename, 'wb') as file:
            with tqdm(desc=filename, total=total_size, unit='iB', unit_scale=True, unit_divisor=1024) as bar:
                for data in response.iter_content(chunk_size=1024):
                    size = file.write(data)
                    bar.update(size)
        return os.path.abspath(filename)

    if not os.path.exists("cmdline-tools"):
        cmdlinetools_zip = download_file(DOWNLOAD_COMMANDLINETOOLS, DOWNLOAD_COMMANDLINETOOLS.rsplit("/")[-1])
        shutil.unpack_archive(cmdlinetools_zip, './')
        os.remove(cmdlinetools_zip)
    
    sdkmanager_path = os.path.join(".", "cmdline-tools", "bin", f"sdkmanager{CLI_EXTENSION}")
    avdmanager_path = os.path.join(".", "cmdline-tools", "bin", f"avdmanager{CLI_EXTENSION}")
    emu_path = os.path.join(".", SDK_ROOT_PATH, "emulator", f"emulator{EMU_EXTENSION}")

    # Accept license
    print("Accept license...")
    subprocess.run([sdkmanager_path, f"--sdk_root={SDK_ROOT_PATH}", "--licenses"], input="y\n" * 20, text=True,)
    # Download the required packages
    if not os.path.exists(emu_path):
        print("Download the required packages...")
        subprocess.run([sdkmanager_path, f"--sdk_root={SDK_ROOT_PATH}", r"platform-tools", r"emulator"])
    # Installing the SDK
    image_path = os.path.join("sdk_root", "system-images", f"android-{sdk}", image, arch)
    if not os.path.exists(image_path):
        print("Installing the SDK...")
        subprocess.run([sdkmanager_path, f"--sdk_root={SDK_ROOT_PATH}", fr"system-images;android-{sdk};{image};{arch}"])
    # Creating an AVD
    avd_path = os.path.join("avd", f"{name}.avd")
    if not os.path.exists(avd_path):
        print("Creating an AVD...")
        subprocess.run([avdmanager_path, "create", "avd", "--name", name, "--package", fr"system-images;android-{sdk};{image};{arch}", "--device", "pixel"])
    # Launch AVD
    print("Launch AVD...")
    sys_dir = os.path.abspath(os.path.join(".", SDK_ROOT_PATH, "system-images", f"android-{sdk}", image, arch))
    #, "-no-boot-anim", "-memory", "4096", "-gpu", "host"
    subprocess.run([emu_path, "-avd", name, "-sysdir", sys_dir, *shlex.split(extra)])

@app.command()
def delete(name: str = typer.Option(help="AVD name to delete")):
    avdmanager_path = os.path.join(".", "cmdline-tools", "bin", f"avdmanager{CLI_EXTENSION}")
    print("Removing AVD...")
    subprocess.run([avdmanager_path, "delete", "avd", "-n", name])

@app.command()
def list():
    avdmanager_path = os.path.join(".", "cmdline-tools", "bin", f"avdmanager{CLI_EXTENSION}")
    subprocess.run([avdmanager_path, "list", "avd"])

if __name__ == "__main__":
    app()
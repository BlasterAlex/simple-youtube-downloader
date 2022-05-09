# Simple YouTube Downloader

Application with GUI for downloading videos from YouTube in mp3/mp4 format using the [PyTube](https://github.com/pytube/pytube) library.

## Features

* Graphical interface;
* Ability to download audio only;
* Multiple videos can be downloaded in parallel;
* Load progress display;
* Displays basic video information before uploading (thumbnail, title, channel, video duration).

## Installation

1. (Optional) Create virtual environment in project directory:

    ```shell
    python -m pip install --user virtualenv
    python -m venv env
    ```
    
    And activate virtualenv:
    
    ```shell
    ./env/Scripts/activate
    ```

2. Install the required packages:

    ```shell
    pip install -r requirements.txt
    ```

## Usage

Run simple-youtube-downloader in terminal:

```shell
python -m downloader
```

Or use [scripts/run.vbs](scripts/run.vbs) to run the application without a terminal. You can create a desktop shortcut for this script.

To select the download folder, set DOWNLOAD_DIR variable in the configuration file [config/settings.yml](config/settings.yml).

```yaml
DOWNLOAD_DIR: D:\Downloads
FORMAT: mp3
```

In the same file you can set the FORMAT of the downloaded files (supported values are **mp3** and **mp4**).
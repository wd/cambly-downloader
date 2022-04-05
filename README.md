# Cambly Downloader

Download your videos on Cambly to local so that you can easily review them.

# Install

```
pip install -r requirements.txt
brew install wget
```

# Usage

```
python main.py --help
Usage: main.py [OPTIONS]

Options:
  -s, --session TEXT            Your session id  [required]
  -d, --date [%Y%m%d|%Y-%m-%d]  Download videos after this date
  -v, --verbose                 Show debug messages.
  --help                        Show this message and exit.
```

First, you need to get a session id from the website. Visit and log in to Cambly, then toggle the `Developer Tools` for Chrome. See the image below.
![step1](https://github.com/wd/cambly-downloader/blob/main/images/1.png?raw=true)
![step2](https://github.com/wd/cambly-downloader/blob/main/images/2.png?raw=true)

Then you can use a command like the below to download all the videos since `2022-01-04`. The video's name will be something like `2022-02-15_Teacher.Mark.mp4`.

```
python main.py -s '<session id>' -d '2022-01-04'
```

The outputs will be something like the below. We can see some retries from the results. It is ok to run the script multiple times. It will continue on the last time it stopped.
```
2022-03-31_Mark.mp4
2022-03-31_Mark.mp4           0%[                 ]   3.09K  --.-KB/s    in 30s
2022-03-31_Mark.mp4           2%[=>               ]   3.00M  --.-KB/s    in 72s
2022-03-31_Mark.mp4           2%[++               ]   3.00M  --.-KB/s    eta 3d 22h
```


# Known issues

Sometimes Cambly may limit the download bandwidth for you. You may see that the download speed is very slow. That's fine, and you just need to wait and try again at another time. The script will also retry automatically when an error occurs.

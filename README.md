Run a cronjob with the following commands:

(1) capture 10 seconds of the live stream, write to capture.mp3
> python3 capture_stream.py https://wmbr.org:8002/hi -o capture.mp3


(2) read capture.mp3, query shazamio, and write to templates/track_info.json
> python3 shazam.py


Also, run the flask, app.py, which only serves the json file, but which can do other things.

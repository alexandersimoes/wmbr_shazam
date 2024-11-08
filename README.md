# Installation

(1) create a virtual environment and install the dependencies

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

# Run the script

Run a cronjob with the following commands:

(1) capture 10 seconds of the live stream, write to capture.mp3

```bash
$ python3 capture_stream.py https://wmbr.org:8002/hi -o capture.mp3
```

(Note: this used to work without https but now seems to require https.)

(2) read capture.mp3, query shazamio, and write to templates/track_info.json

```bash
$ python3 shazam.py
```

(3) run the flask, app.py, which only currently serves the json file.

```bash
$ python3 app.py
```

will by default run the flask server at localhost:5000. Then

```bash
$ wget 127.0.0.1:5000
```

will by default write the json object to index.html

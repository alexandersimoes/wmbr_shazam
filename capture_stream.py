import sys
import io
import time
import argparse
import requests as rq
from pydub import AudioSegment

def capture_stream(url, duration, chunk_size=(2**16)):
    # capture slightly more raw audio than we need
    duration_padded = duration + 1
    duration_ms = 1000 * duration # pydub uses milliseconds
    with rq.Session() as s: # ensures session is kept open
        # timeout of 5 seconds so that we won't hang indefinitely
        # if there is a network problem
        with s.get(url, stream=True, timeout=5) as response:
            start_time = time.monotonic()
            buf = io.BytesIO() # buffer to store incoming mp3 data
            for chunk in response.iter_content(chunk_size=chunk_size):
                buf.write(chunk) # append next chunk to buffer
                if time.monotonic() >= duration_padded + start_time:
                    # read into pydub from start of buffer
                    buf.seek(0)
                    audio = AudioSegment.from_mp3(buf)
                    # make sure we actually have enough audio
                    if len(audio) < duration_ms:
                        buf.seek(0, 2)
                        continue
                    # cut to requested duration
                    return audio[:duration_ms]


def main(argv):
    parser = argparse.ArgumentParser(description='Capture an MP3 audio stream.')
    parser.add_argument('url', help='the URL hosting the audio stream')
    parser.add_argument('-o', dest='outfile', metavar='OUTFILE.mp3', required=False, help='file to save the audio to (default stdout)')
    parser.add_argument('-D', '--duration', metavar='secs', required=False, type=float, default=10.0, help='duration in seconds')
    args = parser.parse_args(argv)

    audio = capture_stream(args.url, args.duration)
    if args.outfile:
        audio.export(args.outfile)
    else:
        audio.export(sys.stdout.buffer)

if __name__ == '__main__':
    main(sys.argv[1:])
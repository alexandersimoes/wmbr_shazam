import asyncio
import argparse
import os
import sys
from shazamio import Shazam
import datetime


def parse_args():
  parser = argparse.ArgumentParser(description='Recognize song from an MP3 file.')
  parser.add_argument('filename', nargs='?', default='capture.mp3', help='MP3 file to recognize')
  return parser.parse_args()


async def main(filename):
  shazam = Shazam()
  D = await shazam.recognize(filename)
  if not len(D["matches"]):
    print("No matches found!")
    sys.exit()
  album_info = [f"{d['title']}: {d['text']}" for d in D['track']['sections'][0]['metadata']]

  # Initialize stream_link with a default message
  stream_link = 'Stream link not available'

  # Check if 'actions' key exists in D['track']['hub']
  if 'actions' in D['track']['hub']:
    actions = D['track']['hub']['actions']
    # Filter actions for type 'uri'
    uri_actions = [d for d in actions if d['type'] == 'uri']
    if uri_actions:
      stream_link = uri_actions[0]['uri']

  # Ensure the 'templates' directory exists
  os.makedirs('templates', exist_ok=True)

  # Generate timestamp for filenames
  timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

  # Create dynamic output file name for results
  results_filename = f"templates/results_{timestamp}.txt"

  with open(results_filename, "w") as f:
    print(f"Title: {D['track']['title']}")
    print(f"Artist: {D['track']['subtitle']}")
    f.write(f"Title: {D['track']['title']}; Artist: {D['track']['subtitle']}\n")
    f.write(f"{'; '.join(album_info)}\n")
    f.write(f"Apple stream link: {stream_link}\n")
    tz = str(datetime.datetime.now().astimezone().tzinfo)
    f.write(
        f'Last updated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {tz}')

if __name__ == '__main__':
  args = parse_args()
  filename = args.filename
  # Use asyncio.run() instead of get_event_loop()
  asyncio.run(main(filename))

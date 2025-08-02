import asyncio
from shazamio import Shazam
import datetime
import json
import sys
import os


async def main():
  shazam = Shazam()
  script_dir = os.path.dirname(os.path.abspath(__file__))
  capture_path = os.path.join(script_dir, 'capture.mp3')
  templates_dir = os.path.join(script_dir, 'templates')
  json_file_path = os.path.join(templates_dir, 'track_info.json')
  
  D = await shazam.recognize(capture_path)
  if not len(D["matches"]):
    print("No matches found!")
    sys.exit()
  album_info = dict([(f"{d['title']}", f"{d['text']}") for d in D['track']['sections'][0]['metadata']])
  stream_link = [d for d in D['track']['hub']['actions'] if d['type'] == 'uri'][0]['uri']
  tz = str(datetime.datetime.now().astimezone().tzinfo)
  info_dict = {
      "Title": D['track']['title'], "Artist": D['track']['subtitle'],
      "Apple Stream Link": stream_link,
      "Last Updated": f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {tz}"
  }
  for k, v in album_info.items():
    info_dict[k] = v

  # Create templates directory if it doesn't exist
  os.makedirs(templates_dir, exist_ok=True)

  # Read existing data first
  try:
    with open(json_file_path, "r") as infile:
      existing_data = json.load(infile)
      if not isinstance(existing_data, list):
        existing_data = []
  except (FileNotFoundError, json.JSONDecodeError):
    existing_data = []

  # Append new info to the list
  existing_data.append(info_dict)

  # Write back the combined data
  with open(json_file_path, "w") as outfile:
    outfile.write(json.dumps(existing_data))

if __name__ == "__main__":
  asyncio.run(main())

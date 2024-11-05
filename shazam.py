import asyncio
from shazamio import Shazam
import datetime
import json
import sys
import os


async def main():
  shazam = Shazam()
  D = await shazam.recognize('capture.mp3')
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
  os.makedirs('templates', exist_ok=True)

  # Read existing data first
  try:
    with open("templates/track_info.json", "r") as infile:
      existing_data = json.load(infile)
      if not isinstance(existing_data, list):
        existing_data = []
  except (FileNotFoundError, json.JSONDecodeError):
    existing_data = []

  # Append new info to the list
  existing_data.append(info_dict)

  # Write back the combined data
  with open("templates/track_info.json", "w") as outfile:
    outfile.write(json.dumps(existing_data))

if __name__ == "__main__":
  asyncio.run(main())

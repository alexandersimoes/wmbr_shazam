import asyncio
from shazamio import Shazam
import datetime

async def main():
  shazam = Shazam()
  D = await shazam.recognize('capture.mp3')  
  album_info = [f"{d['title']}: {d['text']}" for d in D['track']['sections'][0]['metadata']]
  stream_link  = [d for d in D['track']['hub']['actions'] if d['type'] == 'uri'][0]['uri']
  f = open("templates/results.txt", "w")
  f.write(f"Title: {D['track']['title']}; Artist: {D['track']['subtitle']}\n")
  f.write(f"{'; '.join(album_info)}\n")
  f.write(f"Apple stream link: {stream_link}\n")
  tz = str(datetime.datetime.now().astimezone().tzinfo)
  f.write(f'Last updated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {tz}')
  f.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())

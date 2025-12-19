from flask import Flask, render_template, request
import json
from datetime import datetime, timedelta
import re
import requests
from bs4 import BeautifulSoup
app = Flask(__name__)


@app.route('/')
def home():
  try:
    with open('templates/track_info.json', 'r') as file:
      data = json.load(file)
  except (FileNotFoundError, json.JSONDecodeError):
    # Return empty data if file doesn't exist or is invalid JSON
    data = []

  # Apply date filtering
  filtered_data = filter_data_by_date(data)

  response = app.response_class(
      response=json.dumps(filtered_data),
      status=200,
      mimetype='application/json'
  )
  return response


def parse_datetime_with_timezone(timestamp_str):
  """Parse datetime string with various timezone formats"""
  timezone_patterns = [
      (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) UTC', '%Y-%m-%d %H:%M:%S'),
      (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) EST', '%Y-%m-%d %H:%M:%S'),
      (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) EDT', '%Y-%m-%d %H:%M:%S'),
      (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) PST', '%Y-%m-%d %H:%M:%S'),
      (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) PDT', '%Y-%m-%d %H:%M:%S'),
      (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) MST', '%Y-%m-%d %H:%M:%S'),
      (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) MDT', '%Y-%m-%d %H:%M:%S'),
      (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) CST', '%Y-%m-%d %H:%M:%S'),
      (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) CDT', '%Y-%m-%d %H:%M:%S'),
      (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', '%Y-%m-%d %H:%M:%S')
  ]

  for pattern, date_format in timezone_patterns:
    match = re.match(pattern, timestamp_str)
    if match:
      return datetime.strptime(match.group(1), date_format)

  raise ValueError(f"Unable to parse timestamp: {timestamp_str}")


def filter_data_by_date(data):
  """Filter data by date parameter or last 24 hours by default"""
  date_param = request.args.get('date')

  if date_param:
    # Show data for specific date
    try:
      target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
      filtered_data = []
      for row in data:
        try:
          row_datetime = parse_datetime_with_timezone(row['Last Updated'])
          if row_datetime.date() == target_date:
            filtered_data.append(row)
        except (ValueError, KeyError):
          continue
      return filtered_data
    except ValueError:
      # Invalid date format, return empty data
      return []
  else:
    # Show data from last 24 hours by default
    now = datetime.now()
    twenty_four_hours_ago = now - timedelta(hours=24)
    filtered_data = []
    for row in data:
      try:
        row_datetime = parse_datetime_with_timezone(row['Last Updated'])
        if row_datetime >= twenty_four_hours_ago:
          filtered_data.append(row)
      except (ValueError, KeyError):
        continue
    return filtered_data


@app.route('/table')
def show_table():
  try:
    with open('templates/track_info.json', 'r') as file:
      data = json.load(file)
  except (FileNotFoundError, json.JSONDecodeError):
    data = []

  # Apply date filtering
  filtered_data = filter_data_by_date(data)

  return render_template('table.html', data=filtered_data, datetime=datetime)


@app.route('/get_playlist')
def get_playlist():
  show_name = request.args.get('show_name')
  date = request.args.get('date')

  if not show_name or not date:
    return app.response_class(
        response=json.dumps({"error": "Both show_name and date parameters are required"}),
        status=400,
        mimetype='application/json'
    )

  # Show name to ID mapping
  show_mapping = {
      "All Shows": 0,
      "-9.8 m/s²": 311,
      "{Empty Set}": 259,
      "00XTC": 361,
      "1001": 269,
      "2GroovE": 323,
      "323H": 214,
      "The Show Formerly Known as 323H": 346,
      "401 Unauthorized": 320,
      "88 Rewound": 79,
      "A Change of Scenery": 422,
      "A Day In Jazz": 127,
      "A Distorted Reality": 13,
      "A E S T H E T I C": 439,
      "A Little Bit Imaginary": 285,
      "A Map, a String, a Light": 400,
      "A Program of Jazz": 484,
      "A Shot of Exprezzo": 151,
      "A Tempo": 180,
      "A-rhythmic": 240,
      "A-side B-side": 420,
      "Abstractions": 287,
      "Abundance of Caution": 503,
      "Africa Kabisa": 55,
      "AfroBeat MIT": 260,
      "Afterhours Memories": 540,
      "All Night Broadcast": 122,
      "All Things Africa": 290,
      "Alternating Current": 322,
      "Alternative Definition": 205,
      "American Primitive": 66,
      "Amorphous": 308,
      "An Average Attempt at Philosophy": 482,
      "An Eccentric Universe": 406,
      "An Hour Wasted with Fuzzy and Leonid": 140,
      "Analog Bubblebath": 164,
      "Analogue Bubblebath": 349,
      "Anarchist Agenda": 182,
      "Annual Top 100 Countdown": 14,
      "Antoxicated Radio": 233,
      "Anything Goes": 263,
      "Anything with a Beat": 432,
      "Around the World in One Summer": 410,
      "Art & Freight": 493,
      "Ashwaganda Matcha": 606,
      "Astral Signal": 571,
      "Astral Traveller": 215,
      "Atlas Method": 15,
      "the auracle": 496,
      "Aural Fixation": 9,
      "Avant-Garden": 174,
      "BABEs: The Radio Experience": 359,
      "Back to Normal": 369,
      "Back to the Garden": 227,
      "Background Music": 136,
      "Backpacks and Magazines": 265,
      "Backwoods": 67,
      "Bag Hours": 502,
      "Band Theory": 507,
      "Bangers and Banter": 367,
      "The Basement Scene": 168,
      "Basementality": 341,
      "Bass Case": 342,
      "Bats in the Belfry": 10,
      "Beat-Deprived": 446,
      "Beats By Sapa Inca": 585,
      "Bengali Beats and Tales": 360,
      "Benny's Playlists": 497,
      "Better Off Dead": 189,
      "Better Than Elvis": 16,
      "The Big Beat": 511,
      "Bike Talk": 258,
      "Bird Listening": 165,
      "Bleeps + Bloops": 551,
      "Bombastic & Stochastic": 357,
      "Boners And Groaners": 17,
      "Bonkerz": 445,
      "Books on the Radio": 103,
      "Bookshop Casanova": 563,
      "Boomerang": 185,
      "Boots and Cats": 195,
      "Boston Talks": 276,
      "Bottom of the Record Bin": 450,
      "Box of Maniacs": 525,
      "Boy in a Dress": 18,
      "Brain Waves": 500,
      "Brainworms Radio": 192,
      "Breakfast of Champions": 1,
      "The Broken Leg Cafe": 448,
      "Broken Records": 382,
      "Burnt Biscuits": 220,
      "Calling the Cranes": 453,
      "Cambridge Happy Hour": 268,
      "Can of Worms": 582,
      "Carbon Dioxide": 19,
      "Casual Encounters": 177,
      "Ceangal Ceilteach": 77,
      "Cha Chaan Teng": 383,
      "Charles River Variety": 241,
      "Cheese Patrol": 8,
      "Chemistry 101": 298,
      "Chicken Soup for the MIT Soul": 433,
      "Chika and the Trash": 318,
      "Chill Vibes with Aayush and Ritaank": 435,
      "The Choice is Yourz": 89,
      "Chopsticks": 144,
      "Claire²": 330,
      "Classical & Sundry": 81,
      "The Clinton Years": 480,
      "Clueless Clubhouse": 11,
      "Cocktail Hour": 327,
      "Coffeetime": 68,
      "Coherence": 468,
      "CoLab Radio on Air": 397,
      "Colourless Green Ideas Sleep Furiously": 358,
      "Community Conduit": 538,
      "Compact Cassettes": 604,
      "Compas sur FM": 142,
      "Confusion Corner": 333,
      "Connect the Dot.": 368,
      "Connect the Tracks": 569,
      "The Cosmic Deadbeat Radio Hour": 539,
      "The Cosmic Hearse": 256,
      "CPR": 181,
      "Crazy Overnight Fill-In": 201,
      "Crosscurrents": 78,
      "Crossdressed Lullabies": 499,
      "Crunchy Plastic Dinosaurs": 543,
      "Cryptid Office Hours": 393,
      "Cuéntame": 355,
      "Czech For Rabbits": 20,
      "Dancing Days": 275,
      "Danfoolery": 191,
      "Dangerous Things": 412,
      "Day Break": 159,
      "The Daydream Company": 415,
      "Dealer's Choice": 145,
      "Death Car For QT": 587,
      "Deep Dive Down": 519,
      "Dewey Decibel System": 529,
      "Diamond Hearts Club": 390,
      "Differential RIYL": 161,
      "Digital After Dark": 474,
      "Digital.Trash": 443,
      "Disjecta Membra": 166,
      "Diss-oh-nonsense": 303,
      "Dissonance": 216,
      "Dizzy Magenta Bananas": 204,
      "DJ Awesome and the Wonderfriends": 69,
      "Do the Chisel": 3,
      "Don't Take Me Seriously": 232,
      "Dos Platanos": 235,
      "Down River": 288,
      "Drink Spot Radio Hour": 464,
      "Droppin Knowledge": 80,
      "Drunking Funk": 156,
      "Duality and Paradox": 302,
      "Dude, Where's My Capo?": 343,
      "Dumping Ground": 21,
      "Early in the Morning": 296,
      "Eaters' Digest": 194,
      "Eclectic Café": 264,
      "Effa's Lounge": 516,
      "El Gringo Bacano": 336,
      "Electile Dysfunction": 498,
      "Electronic Bubblebath": 354,
      "Ellipsis": 438,
      "Empathy Street": 421,
      "Empirical Observations": 347,
      "Entrepreneurs Of The World, Unite!": 339,
      "Entropy": 379,
      "Evolutions": 384,
      "Excommunicated by the Catholic Church": 169,
      "Exit Tangent": 338,
      "Exposure Therapy": 334,
      "Fall Fiddle": 572,
      "Fall/Winter Soulstice": 457,
      "Faves Uncategorized": 141,
      "Feeling Cavalier": 573,
      "Femmes at the Front": 486,
      "Fermat's Last Album": 183,
      "Firehose Chat": 229,
      "First Cup": 22,
      "Flailing About": 508,
      "Fluid•Mecha•Sonics": 536,
      "Flying Ruckus": 92,
      "FM Road": 456,
      "Folk is Dead": 196,
      "Food Spot Radio Hour": 459,
      "For Your Pleasure": 51,
      "Founder's Couch": 461,
      "Fourier Transform": 599,
      "Freddy the Piano Man": 490,
      "Free of Form": 53,
      "Freezer Jams": 463,
      "Frek[ENS] 88.1": 501,
      "French Toast": 52,
      "From Bindu to Ojas": 506,
      "From Paradise to Hell, MI": 45,
      "The Froot Loops": 533,
      "Fuel for MIT": 337,
      "Fun Hazard": 197,
      "Funk in the Trunk": 391,
      "Futbol Fever": 408,
      "Generoso's Bovine Ska and Rocksteady": 58,
      "GesamkunsTwerk": 252,
      "Girls Only": 120,
      "Global Frequency": 50,
      "Global Soundclash": 546,
      "gloRap": 112,
      "Gojira Schmojira": 398,
      "Good Stuff": 405,
      "Gorilla Got Me": 44,
      "Grab Bag": 407,
      "Green (In the Margin)": 65,
      "Greg Reibman School of Broadcasting": 4,
      "Grey Matters": 317,
      "Grinds My Gears": 462,
      "Grit & Glass": 403,
      "Gritty City Radio": 427,
      "The Grunch Hour": 522,
      "Güibiri": 110,
      "Hairy Bugs": 335,
      "Haiti Focus": 143,
      "Happy Hour": 217,
      "Hard Bop Café": 126,
      "Hardcore Hour": 273,
      "Heartbreak & Footwork": 94,
      "Heavenly High Notes": 429,
      "Hello World": 179,
      "Henry's Hard Drive": 139,
      "Hi Friend": 190,
      "Hi-Fi Lo-Fi": 23,
      "Hi, How Are You?": 99,
      "The Hidden Capital": 109,
      "Hidden Gems in Plain Sight": 48,
      "High Frequency": 364,
      "High School's Over": 575,
      "The Hip Hop Head Variety Hour": 418,
      "Hip To Be Square": 291,
      "Hipster Happy Hour": 107,
      "Historiographone": 175,
      "Hit with Soft Rocks": 310,
      "The Hole": 247,
      "Hollie's Hipster Hour": 184,
      "Holly Would": 218,
      "Honey Mustard": 595,
      "Hook Heavy": 24,
      "Horny Harmonics": 207,
      "The Hot Rat Sessions": 528,
      "The Hotspot": 505,
      "House Therapy": 95,
      "Howlin' the Blues": 97,
      "Human Music": 353,
      "The Human Spark": 115,
      "I Love a Parade": 128,
      "I Saw a Dog Today": 352,
      "The I-5 Connection": 157,
      "If 6 Was 9": 162,
      "Ignition with PYR": 171,
      "Ill Vibes": 212,
      "The Illest Villains": 203,
      "Improbability Field": 121,
      "In Diaspora": 277,
      "In Five Colors": 228,
      "In the Margin": 113,
      "In The Margin Of The Other": 25,
      "In Transit": 530,
      "Inches from the Abyss—A Charcuterie Board of Music": 477,
      "Indie Tra$h": 301,
      "Indy Cindie": 199,
      "insert label here": 292,
      "Insomnia Sounds": 316,
      "Instrumental Surroundings": 111,
      "The Intercontinental": 57,
      "The Intergalactic Witching Hour with Crood >Boi> and Lorinda": 350,
      "Interplanetary Mind": 282,
      "Interstate Escapism": 591,
      "Inverse Lullabies": 124,
      "The iPod Shuffle Kerfuffle": 56,
      "It's College, No Parents": 286,
      "Jam Jam Yams": 319,
      "Jam Session": 82,
      "James Dean Death Car Experience": 6,
      "Jazz Me Blues": 74,
      "Jazz on a Summer's Afternoon": 451,
      "The Jazz Train": 70,
      "Jazz Train": 70,
      "The Jazz Volcano": 63,
      "Jazz Volcano": 63,
      "The Juice Box": 236,
      "Juicebox Hero": 370,
      "Just Can't Get Enough": 570,
      "The Kaleidoscope": 469,
      "kawaiibeats": 426,
      "KGBeats": 375,
      "Kind of Blue": 101,
      "King Ghidorah": 117,
      "Kingston Vibrations": 374,
      "Kook of the Cosmos": 479,
      "Kumquat Robot": 138,
      "Kurbaba": 593,
      "La Casa del Perreo": 137,
      "The LA Times": 454,
      "The Land of Sand and Birds": 46,
      "Last Call Radio": 26,
      "Last Dance at the Death Disco": 27,
      "Latchkey Sounds": 305,
      "Late Night Jazz": 226,
      "Late Night Jazz Abstractions with Crood Bot and Lorindex": 401,
      "Late Night Space Jazz with Crood >Boi> and Lorinda": 377,
      "Late Night Thoughts with Kosi Aroh": 300,
      "Late Risers' Club": 2,
      "Lattice Vibrations": 132,
      "Leaves Turn Inside You": 596,
      "Lemonade": 430,
      "Lentil and Stone": 470,
      "Let Them Eat Chlake!": 340,
      "Let's Get Started": 255,
      "Let's Pray About It!": 605,
      "Let's Talk About Sax": 542,
      "The Lethal List": 386,
      "The Listen": 532,
      "Listening Watching": 71,
      "The Living Room": 239,
      "Loose Talk": 123,
      "Lost and Found": 12,
      "Lost Highway": 28,
      "Lost in my Bedroom": 213,
      "Luau in the Attic": 473,
      "Lucid Dreams": 243,
      "Lunie Tunes": 552,
      "M^2": 580,
      "mad μz": 553,
      "Madame Resistance": 149,
      "Robby and Kiana's Magic Carpet Ride": 202,
      "Magic is Real": 396,
      "Magic Lantern": 304,
      "The Magik Bus": 59,
      "Mama Cass' House": 526,
      "Mare Nubium": 324,
      "Mark & Evelyn's American Top 41": 458,
      "Mass Jazz and Blues": 478,
      "Massachusetts Baywatch Nights with Crood >Boi> and Lorinda": 402,
      "Mayan Mix Masters": 489,
      "Meandering Mentality": 211,
      "The Meaning of the Blues": 512,
      "Mecha Shuffle": 351,
      "Megalopolis": 187,
      "Mellow Madness": 83,
      "Meraviglioso!": 603,
      "Michiana Noise": 5,
      "The Middleground": 556,
      "Midnight Air": 467,
      "Midwest Pizzeria": 547,
      "Mighty Close to Heaven": 387,
      "Mindblown": 495,
      "Missed Connections": 160,
      "The Mix": 466,
      "Moody Food": 193,
      "Moon Monster": 61,
      "The Morning After": 91,
      "Morning Wood": 537,
      "The Mothership": 531,
      "Mouthfeel": 329,
      "Multiple Choice": 274,
      "Musenomix": 154,
      "Music by Dead People": 135,
      "Music For Eels": 517,
      "Music Is Healing": 409,
      "Music Therapy": 509,
      "Mystery Flavor": 280,
      "Mythical Grooves": 356,
      "Mythical Moving Movies": 373,
      "Mythos and Monsters": 436,
      "Near and Far": 395,
      "Nebulosity": 413,
      "Necroticism": 245,
      "The Neutral Theory": 98,
      "The New Edge": 54,
      "New Wave New Year": 29,
      "Night Owl": 30,
      "Nightclubs Where They Only Play Tchaikovsky": 476,
      "No Sleep Club": 248,
      "Noise.Pollution": 437,
      "Nonstop Ecstatic Screaming": 49,
      "Not Brahms and Liszt": 251,
      "Not So Average Cabbage": 133,
      "NUMTOT Radio": 399,
      "Ode To Melanie": 326,
      "Of Moments and Melodies": 371,
      "oh no": 345,
      "On the Dark Side of the Moon": 230,
      "Only New Music": 564,
      "Ontem, Hoje, Sempre": 388,
      "Opus Magnum": 223,
      "Out for the Count": 150,
      "Out of Your Orbit": 460,
      "Ozymandias Melancholia": 380,
      "Painful Hip": 131,
      "Paisanos en un Mundo Extrano": 186,
      "Palpitations": 381,
      "Papaya": 597,
      "The Paradox Box": 116,
      "Part Time Punks": 170,
      "Party Shuffle": 114,
      "Permanent Phase": 598,
      "PhD Offense": 504,
      "The Philharmonic Is My Backup Band": 424,
      "Pickle Sounds": 447,
      "Pieces of What": 210,
      "Pink Bullets": 119,
      "Pipeline!": 85,
      "Plalist": 404,
      "The Playground": 590,
      "Playing with Sticks": 549,
      "Playlistener": 558,
      "Poeddictions": 152,
      "Politics and the African Pulse": 328,
      "The Pontoon Palace": 31,
      "Porcelain Cow": 541,
      "The Post ER": 278,
      "Post-It Wall": 325,
      "Post-Patriarchal": 452,
      "Post-Pipeline": 32,
      "post-tentious": 524,
      "Pourin' a Graphic": 209,
      "Premature Anticipation": 188,
      "Pretty": 206,
      "Prompt Corner": 297,
      "Propulsion": 208,
      "Psychomania": 534,
      "Pulsewidth": 521,
      "Punk-Alt-Del": 172,
      "Purl Jam": 515,
      "The Pursuit of Happiness": 234,
      "QJams": 231,
      "QPR": 362,
      "Quarters": 423,
      "QV Noise": 167,
      "R.S.V.P.": 372,
      "R&B Jukebox": 33,
      "Radical Euphoria": 581,
      "Radio Ninja": 100,
      "Radio Ninja: Long Play": 607,
      "Radio Radio": 158,
      "Radio with a View": 86,
      "RADIO with a VIEW: A History Lesson": 560,
      "Radio X": 281,
      "RBG Radio @ MIT": 592,
      "Real Talk with Jennah Haque": 434,
      "REALAX": 249,
      "Really Really Ridiculously Good-Sounding Music": 155,
      "Recreation": 449,
      "Reel to Reel": 34,
      "Refracted Frequency": 455,
      "Remixed Signals": 271,
      "Research & Development": 87,
      "Revolutionary Rhymes": 548,
      "Riding the Norse Horse": 125,
      "The Right Now Show": 270,
      "Riverside Chats": 376,
      "The Roarin' Twenties": 441,
      "Rocks, Pops, Kilts and Alternatives": 200,
      "Rodents of Unusual Size": 225,
      "Rookie Mistakes": 244,
      "Rough and Ready": 262,
      "RPS": 392,
      "RRR: Rhythm & Rhyme Radio": 579,
      "The Rude Show": 147,
      "Running Returning": 64,
      "Sad Boys Soundbox": 527,
      "Sad Succulent": 313,
      "Salvation Corner": 492,
      "Sans Serif": 35,
      "Sarah and Stephanie's Infinite Playlist": 279,
      "The Scene": 75,
      "Scheduled Broadcast": 425,
      "Sci Fidelity": 104,
      "Seasonal Soulstice": 465,
      "Second Fiddle": 219,
      "Second Hand Reporting": 394,
      "Secret Heartbeats": 76,
      "See the Music, Hear the Dance": 238,
      "Sewersounds": 134,
      "Shadows of the Common": 586,
      "Shape-Shift & Trick": 419,
      "Sharratives with XhiDae": 378,
      "Shelium": 72,
      "The Show Show": 36,
      "Si No Hay Material": 108,
      "Sick Packages": 7,
      "Silicon Gothic": 307,
      "Sin on Saturday, Pray on Sunday": 510,
      "Sixer Mixer": 544,
      "Sixty Minutes More or Less with Madame Psychosis": 428,
      "Slow and Unsteady": 129,
      "Snapshots": 583,
      "So Phisticated": 221,
      "Sometime After 7": 562,
      "The Song Remains the Same": 163,
      "Sonic Mood Ring": 481,
      "Sound and Fury": 283,
      "Sound Principles": 102,
      "Sounds That Will Make Your Mother Say 'Okay I Approve'": 321,
      "Soundscapes": 148,
      "Soundtracks of Bilitis": 389,
      "Sour City": 37,
      "Southern Exposure": 332,
      "Space at the End of Joy": 523,
      "Space is Deep": 488,
      "Space Is The Place": 266,
      "Spelunking": 348,
      "Spherio": 47,
      "Spin Control": 491,
      "Spit Happens": 513,
      "Still Sane": 242,
      "The Stitching Hour": 153,
      "Stop the World": 514,
      "Stormy Weather": 561,
      "Story Time with Ru and Trevor": 294,
      "Strangers with Candy": 88,
      "String Theory": 475,
      "Strolls down the 'Splanade": 520,
      "Study Break": 176,
      "stuff & things": 293,
      "Stun Gun Lullaby": 344,
      "Subject to Change": 38,
      "Sublimation Station": 566,
      "Subtly Submerging Submarines": 363,
      "Summer Soul Revue": 39,
      "Summer Soulstice": 414,
      "Summertime Clothes": 224,
      "Sunset Beats": 440,
      "The SurreaList": 494,
      "Takeoff": 431,
      "Talkin' Tunes": 385,
      "Tasteless": 315,
      "Tasty Beats": 146,
      "Taxonomix": 577,
      "Tender Hooligans": 237,
      "Tenure Traxx": 444,
      "Terminal Swirlie": 565,
      "TERMS and CONDITIONS": 472,
      "Terravoice": 90,
      "The ...": 559,
      "The Theme of the Week": 312,
      "There and Back Again": 250,
      "This Is Not a Safe Space": 173,
      "This Musical Life": 555,
      "Three Ring Circus": 130,
      "Time Traveling": 93,
      "Todo Mundo": 60,
      "Tonto's Fury": 105,
      "Totes McGoats": 118,
      "Train to Bexley": 178,
      "Transistor Radio": 284,
      "Treaty of Tordesillas": 417,
      "Troubadour": 73,
      "Trunk Full of Pearl": 331,
      "Two Broke Memes": 289,
      "Tyunes": 594,
      "Uncommon Grounds": 487,
      "Under the Sun": 602,
      "Uneasy Listening": 84,
      "Unpredictable": 365,
      "Vagabond Noise": 267,
      "Vegan Soulfood": 261,
      "Vibe Check": 518,
      "Vibe Killers": 567,
      "Vinyl Rays of Sun": 253,
      "Virgin Radio": 40,
      "Vitamin Sneve": 483,
      "Voice Box": 309,
      "Voo Doo": 222,
      "Voyage of the Bagel": 574,
      "Wake Up Knowing": 246,
      "Warehouse Hour": 589,
      "Wave Wandering Highway": 554,
      "Wavelength": 257,
      "We Are All Immigrants": 416,
      "Welcome to the Jungle": 471,
      "West Coast Vibes": 254,
      "what just happened": 568,
      "What's Left": 106,
      "What's Your Weird?": 545,
      "Whatever Forever": 601,
      "Where's Patriarchy?": 442,
      "The White Tiger": 411,
      "Who It Is": 41,
      "The Willows": 584,
      "Window Tint the Sun": 42,
      "Windows 2000": 485,
      "Word Spacing": 366,
      "Worldbeat": 96,
      "The Wrong Generation": 198,
      "Yawnie": 272,
      "You Are Here": 43,
      "Zero Monthly Listeners": 550,
      "ZoëRadio": 62,
  }


  # Case insensitive matching
  show_id = None
  for show_key, id_value in show_mapping.items():
    if show_key.lower() == show_name.lower():
      show_id = id_value
      break

  if not show_id:
    return app.response_class(
        response=json.dumps({"error": f"Show '{show_name}' not found. Available shows: {list(show_mapping.keys())}"}),
        status=404,
        mimetype='application/json'
    )

  try:
    # Parse the date and format it for matching
    target_date = datetime.strptime(date, '%Y-%m-%d')
    formatted_date = target_date.strftime('%A, %B %d, %Y').replace(' 0', ' ')

    # Step 1: Scrape the program page
    program_url = f"https://track-blaster.com/wmbr/index.php?program={show_id}"
    response = requests.get(program_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the date header
    date_found = False
    playlist_id = None

    for h4 in soup.find_all('h4', class_='index-h4'):
      print(h4.get_text())
      if formatted_date in h4.get_text():
        date_found = True
        # Find the next sibling div with playlist link
        next_div = h4.find_parent('div').find_parent('div').find_next_sibling('div')
        if next_div:
          playlist_link = next_div.find('a', href=lambda x: x and 'playlist.php?id=' in x)
          if playlist_link:
            href = playlist_link.get('href')
            playlist_id = href.split('id=')[1]
            break

    if not date_found:
      return app.response_class(
          response=json.dumps({"error": f"No show found for {show_name} on {date}"}),
          status=404,
          mimetype='application/json'
      )

    if not playlist_id:
      return app.response_class(
          response=json.dumps({"error": "Playlist link not found"}),
          status=404,
          mimetype='application/json'
      )

    # Step 2: Scrape the playlist page
    playlist_url = f"https://track-blaster.com/wmbr/playlist.php?id={playlist_id}"
    playlist_response = requests.get(playlist_url)
    playlist_response.raise_for_status()

    playlist_soup = BeautifulSoup(playlist_response.content, 'html.parser')

    # Find all song entries
    songs = []
    playlist_data = playlist_soup.find('div', id='playlist_data')

    if playlist_data:
      # Loop through each song row
      for row in playlist_soup.select(".row.print_song_in_set"):

        # --- Time ---
        time_full = None
        for div in row.find_all("div", class_="col-Time"):
          if div.has_attr("fulltime"):
            time_full = div["fulltime"]
            break

        # --- Artist ---
        artist_name = None
        for div in row.find_all("div", class_="col-Artist"):
          classes = div.get("class", [])
          if not any(cls.startswith("hidden-") for cls in classes):
            anchors = div.find_all("a")
            if anchors:
              artist_name = anchors[-1].get_text(strip=True)
            break

        # --- Song ---
        song_name = None
        for div in row.find_all("div", class_="col-Song"):
          classes = div.get("class", [])
          if not any(cls.startswith("hidden-") for cls in classes):
            anchors = div.find_all("a")
            if anchors:
              song_name = anchors[-1].get_text(strip=True)
            break

        # --- Album ---
        album_name = None
        for div in row.find_all("div", class_="col-AlbumFormat"):
          classes = div.get("class", [])
          anchors = div.find_all("a")
          if anchors:
            album_name = anchors[-1].get_text(strip=True)
          break

        # Only add if we have at least artist and song
        if artist_name and song_name:
          songs.append({
              "time": time_full,
              "artist": artist_name,
              "song": song_name,
              "album": album_name
          })

    return app.response_class(
        response=json.dumps({
            "show_name": show_name,
            "date": date,
            "playlist_id": playlist_id,
            "songs": songs
        }),
        status=200,
        mimetype='application/json'
    )

  except ValueError:
    return app.response_class(
        response=json.dumps({"error": "Invalid date format. Use YYYY-MM-DD"}),
        status=400,
        mimetype='application/json'
    )
  except requests.RequestException as e:
    return app.response_class(
        response=json.dumps({"error": f"Failed to fetch data: {str(e)}"}),
        status=500,
        mimetype='application/json'
    )
  except Exception as e:
    return app.response_class(
        response=json.dumps({"error": f"An error occurred: {str(e)}"}),
        status=500,
        mimetype='application/json'
    )


if __name__ == '__main__':
  app.run(debug=True, port=5001)

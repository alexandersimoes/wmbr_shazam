from flask import Flask, render_template, request
import json
from datetime import datetime, timedelta
import re
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


if __name__ == '__main__':
  app.run(debug=True, port=5001)

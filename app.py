from flask import Flask, render_template, request
import json

app = Flask(__name__)


@app.route('/')
def home():
  try:
    with open('templates/track_info.json', 'r') as file:
      data = json.load(file)
  except (FileNotFoundError, json.JSONDecodeError):
    # Return empty data if file doesn't exist or is invalid JSON
    data = {}

  response = app.response_class(
      response=json.dumps(data),
      status=200,
      mimetype='application/json'
  )
  return response


if __name__ == '__main__':
  app.run(debug=True)

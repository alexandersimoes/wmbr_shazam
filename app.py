from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("results.txt", mimetype='text/plain')


if __name__ == '__main__':
    app.run(debug=True)

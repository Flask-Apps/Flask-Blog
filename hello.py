from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World!"

@app.route("/user/<name>")
def user(name):
    return f"<h1>Hello , {name}!"


if __name__ == "__main__":
    app.run(debug=True)

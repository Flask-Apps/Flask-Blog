from flask import Flask, render_template
from flask_bootstrap import Bootstrap



app = Flask(__name__)
Bootstrap = Bootstrap(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/user/<name>")
def user(name):
    comments = [
        "When the horizon is at the top it's interesting",
        "When the horizon is at the bottom it's interesting",
        "When the horizon is at the middle it's not interesting",
    ]
    return render_template("user.html", name=name, comments=comments)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)

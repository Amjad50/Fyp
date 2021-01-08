from flask import Flask, render_template

__app = Flask(__name__, template_folder="../templates")


@__app.route('/')
def hello_world():
    return render_template("index.html")


def run_server():
    __app.run(debug=True)


if __name__ == "__main__":
    run_server()

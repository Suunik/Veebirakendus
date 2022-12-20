from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def avaleht():
    return render_template("avaleht.html")


@app.route('/Osaühingu_andmete_vaade')
def osaühingu_andmete_vaade():
    return render_template("Osaühingu_andmete_vaade.html")


@app.route('/Osaühingu_asutamise_vorm')
def osaühingu_asutamise_vorm():
    return render_template("Osaühingu_asutamise_vorm.html")


if __name__ == '__main__':
    app.run()

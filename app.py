from flask import Flask, render_template
import database


app = Flask(__name__)


@app.route('/')
def main_page():
    return render_template("avaleht.html")


@app.route('/Osaühingu_andmete_vaade')
def company_data_view():
    company_data = database.get_company_data('database.db', 18)
    return render_template("Osaühingu_andmete_vaade.html", company=company_data)


@app.route('/Osaühingu_asutamise_vorm')
def company_founding_form():
    return render_template("Osaühingu_asutamise_vorm.html")


if __name__ == '__main__':
    app.run()

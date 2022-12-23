from flask import Flask, render_template, request, url_for, flash, redirect
import database


app = Flask(__name__)
database_name = 'database.db'

@app.route('/', methods=["GET", "POST"])
def main_page():
    companies = []
    people = []
    search = ""
    if request.method == "POST":
        # first get the IDs of all the companies and people the search finds.
        search = dict(request.form)['search']
        company_ids = database.search_ids(database_name, search, 'company')
        people_ids = database.search_ids(database_name, search, 'people')

        # then make a list of all the companies and people
        for company_id in company_ids:
            companies.append(database.get_company_data(database_name, company_id[0]))
        for person_id in people_ids:
            people.append(database.get_person_data_from_id(database_name, person_id[0]))

    return render_template("avaleht.html", companies=companies, people=people, search=search)


@app.route('/Osaühingu_andmete_vaade', methods=['GET'])
def company_data_view():
    id = request.args.get('id')
    company_data = database.get_company_data(database_name, id)
    return render_template("Osaühingu_andmete_vaade.html", company=company_data)


@app.route('/Osaühingu_asutamise_vorm')
def company_founding_form():
    return render_template("Osaühingu_asutamise_vorm.html")


if __name__ == '__main__':
    app.run()

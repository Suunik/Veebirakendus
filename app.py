from flask import Flask, render_template, request, url_for, flash, redirect
import database
from datetime import date


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Test'
database_name = 'database.db'

# used in company founding form
# need to keep all the founder data before submitting company data
founder_data = []


@app.route('/', methods=["GET", "POST"])
def main_page():
    companies = []
    people = []
    search = ""
    if request.method == "POST":
        # first get the IDs of all the companies and people that the search finds.
        search = dict(request.form)['search']
        company_ids = []
        people_ids = []

        # find ids from numbers
        if search.isnumeric():
            if len(search) == 7:
                company_ids = database.search_ids_from_numbers(database_name, search)
            if len(search) == 11:
                people_ids = database.search_ids_from_numbers(database_name, search)
        # find ids from given characters
        else:
            company_ids = database.search_ids(database_name, search, 'company')
            people_ids = database.search_ids(database_name, search, 'people')

        # then make a list of all the companies and people
        for company_id in company_ids:
            companies.append(database.get_company_data(database_name, company_id))
        for person_id in people_ids:
            people.append(database.get_person_data_from_id(database_name, person_id))

    return render_template("avaleht.html", companies=companies, people=people, search=search)


@app.route('/Osaühingu_andmete_vaade', methods=['GET'])
def company_data_view():
    id = request.args.get('id')
    company_data = database.get_company_data(database_name, id)
    return render_template("Osaühingu_andmete_vaade.html", company=company_data)


@app.route('/Osaühingu_asutamise_vorm', methods=["GET", "POST"])
def company_founding_form():
    # used so that user can't set company founding date to future
    today_date = date.today()
    company_data = {}
    if request.method == "POST":
        data = dict(request.form)
        # gather company data
        company_data['company_name'] = data['company_name']
        company_data['registry_code'] = data['registry_code']
        company_data['start_date'] = data['start_date']
        company_data['total_capital'] = data['total_capital']

        # means that user wants to submit the form
        if 'submit' in data.keys():
            # first check if total founder share is the same as company total capital
            total_founder_share = 0
            for founder in founder_data:
                total_founder_share += int(founder['capital_share'])

            if total_founder_share != int(company_data['total_capital']):
                flash('Osanike kapital ei ole võrdne ettevõtte kapitaliga')
            elif not founder_data:
                flash('Osanikud puuduvad')
            # means that everything should be fine and we can add the data to database
            else:
                company_data['founders'] = founder_data
                database.add_company_to_database(database_name, company_data)

                # empty the list so users can add new companies if wished
                company_data = {}
                founder_data.clear()

        # means that we got person info
        else:
            # check if all the inputs were done
            if data['first_name'] == "":
                flash('Osaniku eesnimi puudu')
            elif data['last_name'] == "":
                flash('Osaniku perekonnanimi puudu')
            elif data['id_code'] == "":
                flash('Osaniku isikukood puudu')
            elif data['capital_share'] == "":
                flash('Osaniku osa puudu')
            else:
                # gather person_data and add it to the overall list
                founder_data.append({'first_name': data['first_name'],
                                     'last_name': data['last_name'],
                                     'id_code': data['id_code'],
                                     'capital_share': data['capital_share']})

    return render_template("Osaühingu_asutamise_vorm.html",
                           company_data=company_data,
                           person_data=founder_data,
                           today_date=today_date)


if __name__ == '__main__':
    app.run()

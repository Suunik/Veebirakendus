from flask import Flask, render_template, request, url_for, flash, redirect
import database
from datetime import date, datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Test'
database_name = 'database.db'

# used in company founding form
# need to keep all the founder data before submitting company data
founder_data = []
legal_founder_data = []


def get_total_shareholder_capital():
    """Calculate total shareholder capital."""
    # calculate total shareholder capital for later comparison
    total_shareholder_capital = 0
    for person in founder_data:
        total_shareholder_capital += person['capital_share']
    for legal_person in legal_founder_data:
        total_shareholder_capital += legal_person['capital_share']

    return total_shareholder_capital


@app.route('/', methods=["GET", "POST"])
def main_page():
    companies = []
    people = []
    legal_people = []
    search = ""
    if request.method == "POST":
        # first get the IDs of all the companies and people that the search finds.
        search = dict(request.form)['search']
        companies = database.search_engine(database_name, search, 'company')
        people = database.search_engine(database_name, search, 'people')
        legal_people = database.search_engine(database_name, search, 'company', True)
    return render_template("avaleht.html", companies=companies, people=people, search=search, legal_people=legal_people)


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
    legal_people = []
    people = []
    search = ""
    if request.method == "POST":
        data = dict(request.form)
        data_keys = list(data.keys())
        print(data)
        # means that user is searching for shareholders
        if data['search']:
            search = dict(request.form)['search']
            legal_people = database.search_engine(database_name, search, 'company')
            people = database.search_engine(database_name, search, 'people')

        # means that user is trying to add a shareholder to the company
        elif 'add_button' in data_keys:
            # means that user is trying to add a legal person
            if data['legal_person_capital']:
                legal_person_data = eval(data['add_button'])
                legal_person_data['capital_share'] = int(data['legal_person_capital'])
                legal_founder_data.append(legal_person_data)
            # means that user is trying to add physical person
            elif data['person_capital']:
                if int(data['person_capital']) < 1:
                    flash('Osaniku algkapital on liiga väike!')
                else:
                    person_data = eval(data['add_button'])
                    person_data['capital_share'] = int(data['person_capital'])
                    founder_data.append(person_data)
            # user must have forgotten to add capital share
            else:
                flash("Osanikul tuleb lisada osaniku osa suurus!")

        # means that user is trying to submit the company founding form
        elif 'button' in data_keys:
            # gather all the data
            company_data = {'company_name': data['company_name'], 'registry_code': data['registry_code'],
                            'start_date': data['start_date'], 'total_capital': data['total_capital'],
                            'founders': founder_data, 'legal_founders': legal_founder_data}

            # check if every input field of company form is filled correctly

            # length of the name
            if len(company_data['company_name']) < 3:
                flash('Ettevõtte nimi on liiga lühike!')
            elif len(company_data['company_name']) > 100:
                flash('Ettevõtte nimi on liiga pikk!')

            # length on the registry code
            elif len(company_data['registry_code']) < 7:
                flash('Registrikood on liiga lühike!')
            elif len(company_data['registry_code']) > 7:
                flash('Registrikood on liiga pikk!')

            # start date field must be filled
            elif not company_data['start_date']:
                flash('Asutamiskuupäev puudu!')
            # start date must be smaller or equal to todays date
            elif today_date < datetime.strptime(company_data['start_date'], '%Y-%m-%d').date():
                flash('Ettevõtte asutamise kuupäev peab olema väiksem või võrdne tänase kuupäevaga!')

            # total capital must be more than 2500€
            elif int(company_data['total_capital']) < 2500:
                flash('Ettevõtte algkapital peab olema vähemalt 2500€')

            # must have at least one founder
            elif not company_data['founders'] and not company_data['legal_founders']:
                flash('Ettevõttel peab olema vähemalt üks osanik!')

            # total capital must be equal to the sum of every shareholder capital
            elif int(company_data['total_capital']) != get_total_shareholder_capital():
                flash('Ettevõtte kogukapital peab olema võrdne osanike kapitalidega!')

            # check if company already exists in database
            elif database.check_if_company_name_exists(company_data['company_name']):
                flash('Sellise nimega ettevõte on juba varem asutatud!')

            elif database.check_if_company_registry_code_exists(company_data['registry_code']):
                flash('Sellise registrikoodiga ettevõte on juba varem asutatud!')

            # submit the form and add company to database
            else:
                database.add_company_to_database(database_name, company_data)
                company_id = database.get_last_id_in_table(database_name, 'company')
                # also empty the global variables
                founder_data.clear()
                legal_founder_data.clear()
                return redirect(url_for('company_data_view', id=company_id))

    return render_template("Osaühingu_asutamise_vorm.html",
                           person_data=founder_data,
                           legal_person_data=legal_founder_data,
                           people=people,
                           legal_people=legal_people)


if __name__ == '__main__':
    app.run()

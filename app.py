from flask import Flask, render_template, request, url_for, flash, redirect
import database
from datetime import date


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Test'
database_name = 'database.db'

# used in company founding form
# need to keep all the founder data before submitting company data
founder_data = []
legal_founder_data = []


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
        print(legal_people)
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
        # gather company data so the user doesnt have to type it again
        company_data['company_name'] = data['company_name']
        company_data['registry_code'] = data['registry_code']
        company_data['start_date'] = data['start_date']
        company_data['total_capital'] = data['total_capital']
        # means that user wants to search for legal person
        if data['search']:
            search = dict(request.form)['search']
            legal_people = database.search_engine(database_name, search, 'company')
            people = database.search_engine(database_name, search, 'people')

        # means that we got new person info
        elif data['button'] == 'add_person':
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

        # means that user wants to submit the form
        elif data['button'] == 'submit':
            # first check if total founder share is the same as company total capital
            total_founder_share = 0
            for founder in founder_data:
                total_founder_share += int(founder['capital_share'])
            for legal_founder in legal_founder_data:
                total_founder_share += int(legal_founder['capital_share'])
            # if not, flash an error
            if total_founder_share != int(company_data['total_capital']):
                flash('Osanike kapital ei ole võrdne ettevõtte kapitaliga')
            elif not founder_data and not legal_founder_data:
                flash('Osanikud puuduvad')
            # means that everything should be fine and we can add the data to database
            else:
                company_data['founders'] = founder_data
                company_data['legal_founders'] = legal_founder_data
                database.add_company_to_database(database_name, company_data)

                # empty the list so users can add new companies if wished
                company_data = {}
                founder_data.clear()
                legal_founder_data.clear()

        # means that user wants to add company from the database into list
        elif 'company_name' in eval(data['button']).keys():
            legal_person_data = eval(data['button'])
            legal_person_data['capital_share'] = data['legal_person_capital']
            print(legal_person_data)
            legal_founder_data.append(legal_person_data)
        # means that user wants to add a person from the database into list
        elif 'first_name' in eval(data['button']).keys():
            person_data = eval(data['button'])
            founder_data.append({'first_name': person_data['first_name'],
                                 'last_name': person_data['last_name'],
                                 'id_code': person_data['id_code'],
                                 'capital_share': data['person_capital']})


    return render_template("Osaühingu_asutamise_vorm.html",
                           company_data=company_data,
                           person_data=founder_data,
                           legal_person_data=legal_founder_data,
                           legal_people=legal_people,
                           today_date=today_date,
                           people=people,
                           search=search)

if __name__ == '__main__':
    app.run()

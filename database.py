import sqlite3
import os
import time
from datetime import date
import random


# random date generator code from:
# https://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates
def str_time_prop(start, end, time_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, '%d/%m/%Y', prop)


def create_people_table(database_name: str):
    """
    Create person database with 100 persons inside it.

    This function requires two text files named "first_names.txt" and "last_names.txt"
    """
    # get a connection to person database
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS people")
    cursor.execute("""CREATE TABLE people(
                                    first_name TEXT,
                                    last_name TEXT,
                                    id_code INTEGER,
                                    UNIQUE(id_code)
                        )""")

     # get a list of names from text files as tuples
    directory = os.path.dirname(__file__)

    names = []
    with open(f"{directory}\\first_names.txt") as f:
        for first_name in f:
            names.append(first_name.strip("\n"))

    with open(f"{directory}\\last_names.txt") as f:
        index = 0
        id_code = 12345678901
        for last_name in f:
            names[index] = (names[index], last_name.strip("\n"), id_code + index)
            index += 1
    # add names to the database
    cursor.executemany("INSERT INTO people VALUES (?,?,?)", names)

    conn.commit()
    conn.close()


def create_company_table(database_name: str):
    """
    Create company database.

    This function needs "company_names.txt" file to get the company names from.
    """
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS company")
    cursor.execute("""CREATE TABLE company (
                                company_name TEXT COLLATE NOCASE,
                                registry_code INTEGER,
                                start_date DATE,
                                total_capital INTEGER,
                                UNIQUE(registry_code)
                    )""")

    company_data = []
    registry_code = 7654321
    today = date.today().strftime("%d/%m/%Y")

    directory = os.path.dirname(__file__)
    with open(f"{directory}\company_names.txt") as file:
        for name in file:
            company_data.append((name.strip("\n"), registry_code, random_date("20/08/1991", today, random.random()), 0))
            registry_code += 1
    cursor.executemany("""INSERT INTO company VALUES (?,?,?,?)""", company_data)

    conn.commit()
    conn.close()


def create_shareholder_table(database_name: str):
    """Create shareholder database."""
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    cursor.execute("""DROP TABLE IF EXISTS shareholder""")
    cursor.execute("""CREATE TABLE shareholder(
                            company_id INTEGER,
                            shareholder_id INTEGER,
                            capital_share INTEGER,
                            founder INTEGER,
                            legal_person
                            )""")

    cursor.execute("""SELECT rowid FROM people""")
    person_ids = cursor.fetchall()
    number_of_persons = len(person_ids)

    cursor.execute("""SELECT rowid FROM company""")
    company_ids = cursor.fetchall()

    person_id = 1
    for company_id in company_ids:
        # get random number as a share of the person
        # minimum 1250 because company must have starting capital atleast 2500€
        person1_share = random.randint(1250, 10000)
        person2_share = random.randint(1250, 10000)
        # create a list of shareholders with two members
        shareholders = [(company_id[0], person_id, person1_share, 1, 0),
                        (company_id[0], person_id + 1, person2_share, 1, 0)
                        ]

        # insert data into the table
        for shareholder in shareholders:
            cursor.execute("INSERT INTO shareholder VALUES (?,?,?,?,?)", shareholder)
        conn.commit()

        # add 2 to the person_id variable for each person inserted
        person_id += 2
        # if for some reason person_id becomes larger than the size of the people table
        # start from the begginning of the list again
        if number_of_persons <= person_id:
            person_id = 1

    conn.close()


def add_company_total_capital():
    """Add total capital to company table using data from shareholder table."""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""SELECT DISTINCT company_id FROM shareholder""")
    shareholders = cursor.fetchall()

    company_id = 1
    while company_id <= len(shareholders):
        cursor.execute(f"SELECT capital_share FROM shareholder WHERE company_id = {company_id}")
        all_capitals = cursor.fetchall()
        total_capital = 0
        for capital in all_capitals:
            total_capital += capital[0]
        cursor.execute(f"UPDATE company SET total_capital = {total_capital} WHERE rowid = {company_id}")

        company_id += 1
    conn.commit()
    conn.close()


def create_database(database_name: str):
    """
    Create database.

    Where person table has first name, last name and id code.
    Where company table has company name, registry code, start date and total capital.

    Where shareholder table binds them together and holds information about which person
    is shareholder at which company with how much shares in euros.
    """
    create_people_table(database_name)
    create_company_table(database_name)
    create_shareholder_table(database_name)
    add_company_total_capital()


def get_last_id_in_table(database_name: str, table_name: str):
    """Return the last rowid in company table."""
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    cursor.execute(f"SELECT rowid FROM {table_name} ORDER BY rowid DESC LIMIT 1;")
    return cursor.fetchone()


def check_if_company_name_exists(company_name: str):
    "Check if there is a company with the same name or registry code in database."
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM company WHERE company_name = ?", (company_name,))
    companies = cursor.fetchall()

    return companies


def check_if_company_registry_code_exists(registry_code: str):
    "Check if there is a company with the same name or registry code in database."
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM company WHERE registry_code = ?", (registry_code,))
    companies = cursor.fetchall()

    return companies


def search_ids(database_name: str, search: str, table: str):
    """Get companies or persons id from given search string inside given table."""
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    # find out what table we are searching and execute the right command
    if table == 'company':
        cursor.execute(f"SELECT rowid FROM {table} WHERE company_name LIKE '%{search}%'")
    elif table == 'people':
        cursor.execute(f"SELECT rowid FROM {table} WHERE (first_name LIKE '%{search}%' OR last_name LIKE '%{search}%')")
    else:
        print("wrong table name")
        return
    data = cursor.fetchall()

    id_list = []
    for id in data:
        id_list.append(id[0])
    return id_list


def search_ids_from_numbers(database_name: str, search: str):
    """
    Get companies or persons id from given search string(numbers).

    7 numbers mean that we are looking for companyd ids
    11 number mean that we are looking for person ids
    """
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # find out what table we are searching and execute the right command
    if len(search) == 7:
        cursor.execute(f"SELECT rowid FROM company WHERE registry_code = {search}")
    elif len(search) == 11:
        cursor.execute(f"SELECT rowid FROM people WHERE id_code = {search}")
    else:
        print("wrong number length")
        return
    data = cursor.fetchall()

    id_list = []
    for id in data:
        id_list.append(id[0])
    return id_list


def get_shareholder_data(database_name: str, shareholder_id: int, legal_person: bool):
    """Get all the companies the person is shareholder in."""
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    if not legal_person:
        cursor.execute(f"SELECT * FROM shareholder WHERE (shareholder_id, legal_person) = ({shareholder_id}, 0)")
    if legal_person:
        cursor.execute(f"SELECT * FROM shareholder WHERE (shareholder_id, legal_person) = ({shareholder_id}, 1)")
    shareholder_data = cursor.fetchall()
    list_of_companies = []
    # loop through every company the person is shareholder in
    for data in shareholder_data:
        # means that it is a person not legal person and we can add the company to list
        dict_of_company = {}
        # get company data from the current company id
        company_data = get_company_data(database_name, data[0])
        # add company name and id to a dict
        dict_of_company['company_name'] = company_data['company_name']
        dict_of_company['id'] = company_data['id']
        # then add the dict to a list
        list_of_companies.append(dict_of_company)
    return list_of_companies


def get_person_data_from_id(database_name: str, person_id: int):
    """Get person name from person_id."""
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM people WHERE rowid={person_id}")
    # get the persons data
    data = cursor.fetchall()
    # get all the companies person is shareholder in
    shareholder_data = get_shareholder_data(database_name, person_id, False)
    # add it to a dict
    person_data = {'first_name': data[0][0], 'last_name': data[0][1],
                   'id_code': data[0][2], 'companies': shareholder_data}
    return person_data


def get_legal_person_data_from_id(database_name: str, legal_person_id: int):
    """Get person name from person_id."""
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM company WHERE rowid={legal_person_id}")
    # get the persons data
    data = cursor.fetchall()
    # get all the companies person is shareholder in
    shareholder_data = get_shareholder_data(database_name, legal_person_id, True)
    # add it to a dict
    legal_person_data = {'company_name': data[0][0], 'registry_code': data[0][1], 'companies': shareholder_data}
    return legal_person_data


def get_company_data(database_name: str, company_id: int):
    """
    Get company data from given database name.

    Convert the data to dictionary with all the information.

    Keys: company_name, registry_code, start_date, total_capital, shareholders

    Shareholders key consists of dictionaries.

    Shareholders keys: first_name, last_name, id_code, founder
    """
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # get company data from company table, make a dictionary with the data
    company_data = cursor.execute(f'SELECT *, rowid FROM company WHERE rowid = ?',
                        (company_id,)).fetchone()

    data = {"company_name": company_data[0], "registry_code": company_data[1],
            "start_date": company_data[2], "total_capital": company_data[3], 'id': company_data[4]}

    shareholders = {}
    # get shareholder data from shareholder table ( find person(s) tied with the company_id )
    shareholders = conn.execute(f'SELECT * FROM shareholder WHERE (company_id, legal_person )= (?,?)',
                        (company_id, 0)).fetchall()

    legal_shareholders = conn.execute(f'SELECT * FROM shareholder WHERE (company_id, legal_person )= (?,?)',
                                          (company_id, 1)).fetchall()

    # finally get rowid's from shareholder data to get the information about shareholders.
    # add shareholder info to data dict as an additional dictionary.
    shareholders_data = []
    for person in shareholders:
        cursor.execute(f'SELECT * FROM people WHERE rowid = {person[1]}')
        person_data = cursor.fetchall()
        person_dict = {}
        person_dict['first_name'] = person_data[0][0]
        person_dict['last_name'] = person_data[0][1]
        person_dict['id_code'] = person_data[0][2]
        # person[3] is a slot in shareholder table that holds
        # if person was the founder of the company (1) or not (0)
        person_dict['founder'] = 'Jah' if person[3] == 1 else 'Ei'
        person_dict['share'] = person[2]
        shareholders_data.append(person_dict)

    data['shareholders'] = shareholders_data

    legal_shareholders_data = []
    for legal_person in legal_shareholders:
        cursor.execute(f'SELECT * FROM company WHERE rowid = {legal_person[1]}')
        legal_person_data = cursor.fetchall()
        legal_person_dict = {}
        legal_person_dict['company_name'] = legal_person_data[0][0]
        legal_person_dict['registry_code'] = legal_person_data[0][0]
        legal_person_dict['share'] = legal_person[2]
        legal_person_dict['founder'] = 'Jah' if legal_person[3] == 1 else 'Ei'
        legal_shareholders_data.append(legal_person_dict)
    data['legal_shareholders'] = legal_shareholders_data
    conn.close()
    return data


def search_engine(database_name: str, search: str, table: str, legal_person_search=False):
    """Get a list of data from database with given search string."""
    result_ids = []
    result_list = []
    # find ids from numbers
    if search.isnumeric():
        if len(search) == 7 and table == 'company':
            result_ids = search_ids_from_numbers(database_name, search)
        if len(search) == 11 and table == 'people':
            result_ids = search_ids_from_numbers(database_name, search)
    # find ids from given characters
    else:
        result_ids = search_ids(database_name, search, table)

    # then make a list of all the companies and people
    if table == 'company':
        for company_id in result_ids:
            if not legal_person_search:
                result_list.append(get_company_data(database_name, company_id))
                continue

            # if we are looking for legal person data (not all companies are shareholders in a company)
            legal_person_data = get_legal_person_data_from_id(database_name, company_id)
            # dont display legal people that are not a shareholder in any companies
            if not legal_person_data['companies']:
                continue
            result_list.append(legal_person_data)
    if table == 'people':
        for people_id in result_ids:
            result_list.append(get_person_data_from_id(database_name, people_id))
    return result_list


def add_company_to_database(database_name: str, company_data: dict):
    """Add data to database"""
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # first add company data to database
    company_tuple = (company_data['company_name'], company_data['registry_code'],
                     company_data['start_date'], company_data['total_capital'])

    cursor.execute("INSERT OR IGNORE INTO company VALUES (?,?,?,?)", company_tuple)

    # add persons to person table and remember their id_codes and capital shares ( used in shareholder table )
    id_codes = []
    capital_shares = []
    for person in company_data['founders']:
        id_codes.append(person['id_code'])
        capital_shares.append(person['capital_share'])
        person_tuple = (person['first_name'], person['last_name'], person['id_code'])
        cursor.execute("INSERT OR IGNORE INTO people VALUES (?,?,?)", person_tuple)
    conn.commit()

    print(f"capital shares: {capital_shares}")
    registry_codes = []
    legal_person_capital_shares = []
    for legal_person in company_data['legal_founders']:
        registry_codes.append(legal_person['registry_code'])
        legal_person_capital_shares.append(legal_person['capital_share'])

    # update shareholder data

    # get company rowid using company registry code ( should be unique for every company )
    cursor.execute(f"SELECT rowid FROM company WHERE registry_code = {company_data['registry_code']}")
    company_id = cursor.fetchone()

    print(f"company id: {company_id}")

    if id_codes:
        # get person rowid's using person id_code
        # use different queries depending on the amound of id's
        if len(id_codes) > 1:
            cursor.execute(f"SELECT rowid FROM people WHERE id_code in {tuple(id_codes)}")
        else:
            cursor.execute(f"SELECT rowid FROM people WHERE id_code = {id_codes[0]}")
        person_ids = cursor.fetchall()
        # now add person data to shareholder table
        for index, id in enumerate(person_ids):
            shareholder_data = (int(company_id[0]), id[0], capital_shares[index], 1, 0)
            cursor.execute(f"INSERT INTO shareholder VALUES (?,?,?,?,?)", shareholder_data)

    if registry_codes:
        # get legal person rowid's using registry code
        if len(registry_codes) > 1:
            cursor.execute(f"SELECT rowid FROM company WHERE registry_code in {tuple(registry_codes)}")
        else:
            cursor.execute(f"SELECT rowid FROM company WHERE registry_code = {registry_codes[0]}")
        legal_person_ids = cursor.fetchall()
        print(f"legal person ids: {legal_person_ids}")
        # now add legal person data to shareholder table
        for index, id in enumerate(legal_person_ids):
            shareholder_data = (int(company_id[0]), id[0], legal_person_capital_shares[index], 1, 1)
            cursor.execute(f"INSERT INTO shareholder VALUES (?,?,?,?,?)", shareholder_data)

    conn.commit()
    conn.close()

company_data = {'company_name': 'kala', 'registry_code': '1234567', 'start_date': '1212-12-12', 'total_capital': '2500', 'founders': [], 'legal_founders': [{'company_name': 'Block, Fadel and Maggio', 'registry_code': 7654321, 'start_date': '11/04/1997', 'total_capital': 8299, 'id': 1, 'shareholders': [{'first_name': 'Michael', 'last_name': 'Suarez', 'id_code': 12345678901, 'founder': 'Jah', 'share': 6721}, {'first_name': 'Christopher', 'last_name': 'Osborn', 'id_code': 12345678902, 'founder': 'Jah', 'share': 1578}], 'legal_shareholders': [], 'capital_share': 2500}]}

add_company_to_database('database.db', company_data)

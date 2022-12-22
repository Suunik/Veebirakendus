import sqlite3
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
                                    id_code INTEGER
                        )""")

     # get a list of names from text files as tuples
    names = []
    with open("first_names.txt") as f:
        for first_name in f:
            names.append(first_name.strip("\n"))

    with open("last_names.txt") as f:
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
                                company_name TEXT,
                                registry_code INTEGER,
                                start_date DATE,
                                total_capital INTEGER
                    )""")

    company_data = []
    registry_code = 7654321
    today = date.today().strftime("%d/%m/%Y")

    with open("company_names.txt") as file:
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
                            person_id INTEGER,
                            capital_share INTEGER,
                            founder INTEGER
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
        shareholders = [(company_id[0], person_id, person1_share, 1),
                        (company_id[0], person_id + 1, person2_share, 1)
                        ]
        # insert data into the table
        cursor.executemany("INSERT INTO shareholder VALUES (?,?,?,?)", shareholders)
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


def get_company_data(database_name: str, company_id: int):
    """
    Get company database from given database name.

    Convert the data to dictionary with all the information.

    Keys: company_name, registry_code, start_date, total_capital, shareholders

    Shareholders key consists of dictionaries.

    Shareholders keys: first_name, last_name, id_code, founder
    """
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # get company data from company table, make a dictionary with the data
    company_data = cursor.execute(f'SELECT * FROM company WHERE rowid = ?',
                        (company_id,)).fetchone()

    data = {"company_name": company_data[0], "registry_code": company_data[1],
            "start_date": company_data[2], "total_capital": company_data[3]}

    # get shareholder data from shareholder table ( find person(s) tied with the company_id )
    shareholders = conn.execute(f'SELECT * FROM shareholder WHERE company_id = ?',
                        (company_id,)).fetchall()

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
        # information if person was the founder of the company (1) or not (0)
        person_dict['founder'] = 'Jah' if person[3] == 1 else 'Ei'
        person_dict['share'] = person[2]
        shareholders_data.append(person_dict)
    data['shareholders'] = shareholders_data

    conn.close()
    return data


print(get_company_data('database.db', 5))

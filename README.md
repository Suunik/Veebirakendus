# Veebirakendus
Veebirakendus

Veebirakenduse tööle panemiseks on vaja pythonit.
Pythoni saab veebilehelt: https://www.python.org/

Kui python on alla laetud ja installitud, tuleb avada terminal.
Windows + R, run boxi kirjutada "cmd" ja siis enter

Terminalis tuleb kirjutada command:
`py -m pip install flask`
Command tõmbab flaski _webframe_-i mis on vajalik veebirakenduse käivitamiseks.

Siis tuleb andmebaas luua.
Selleks tuleb avada create database fail kirjutades commandi reale: 
`py \file\location`
Näiteks: "D:\Programmid\Veebirakendus-main\create_database.py"
Avades peaks file looma veebirakenduse kausta databaasi kasutades kolme tekst faili. (First_names, last_names ja company_names)

Järgmiseks tuleb terminalis käskida pythonil avada pythoni file "app.py".
Selleks tuleb kirjutada commandi reale:
`py \file\location`
Näiteks: "D:\Programmid\Veebirakendus-main\app.py"

Siis käivitatakse development server.
Terminalis on kirjas ka aadress kus veebirakendust näeb.
Näiteks http://127.0.0.1:5000

Aadressi browseris avades näeb veebirakendust.

Serveri saab kinni panna terminalis olles klaviatuuril vajutades `CTRL+C` või terminali akna sulgemisel

import os
import sqlite3
import random
import string
import time

os.remove("elokuvat.db")

db = sqlite3.connect("elokuvat.db")
db.isolation_level = None

# luo tietokantaan tarvittavat taulut
def create_table():
    # elokuva: nimi, vuosi
    db.execute('''
    CREATE TABLE Elokuvat (
    id INTEGER PRIMARY KEY,
    nimi TEXT,
    vuosi TEXT
    )
    ''')

def add_random_movies(number):
    kirjaimet = string.ascii_lowercase
    for i in range(number):
        nimi = ''.join(random.choice(kirjaimet) for j in range(8))
        vuosi = random.randint(1900,2000)  
        db.execute('''
        INSERT INTO
            Elokuvat (nimi, vuosi)
        VALUES
            (?,?)
        ''', [nimi,vuosi])
    

def count_movies(vuosi):
    count = db.execute('''
    SELECT
        COUNT(*)
    FROM
        Elokuvat E
    WHERE
        E.vuosi = ?
    ''', [vuosi])
    return count

#---------------------------------------------

ans = int(input('Choose test. Either 1, 2 or 3: '))

if ans == 1:

    create_table()

    db.execute('BEGIN')

    t1 = time.time()
    add_random_movies(1000000)
    t2 = time.time()
    print(f'Time of adding movies = {round(t2-t1,5)} seconds.')

    t1 = time.time()
    for i in range(1000):
        x = random.randint(1900,2000)
        count = count_movies(x)
    t2 = time.time()
    print(f'Time of counting movies = {round(t2-t1,5)} seconds.')

    db.execute('COMMIT')
    

elif ans == 2:

    create_table()

    db.execute('BEGIN')

    db.execute('CREATE INDEX idx_vuosi ON Elokuvat (vuosi)')

    t1 = time.time()
    add_random_movies(1000000)
    t2 = time.time()
    print(f'Time of adding movies = {round(t2-t1,5)} seconds.')

    t1 = time.time()
    for i in range(1000):
        x = random.randint(1900,2000)
        count = count_movies(x)
    t2 = time.time()
    print(f'Time of counting movies = {round(t2-t1,5)} seconds.')

    db.execute('COMMIT')

elif ans == 3:

    create_table()

    db.execute('BEGIN')

    t1 = time.time()
    add_random_movies(1000000)
    t2 = time.time()
    print(f'Time of adding movies = {round(t2-t1,5)} seconds.')

    db.execute('CREATE INDEX idx_vuosi ON Elokuvat (vuosi)')

    t1 = time.time()
    for i in range(1000):
        x = random.randint(1900,2000)
        count = count_movies(x)
    t2 = time.time()
    print(f'Time of counting movies = {round(t2-t1,5)} seconds.')

    db.execute('COMMIT')
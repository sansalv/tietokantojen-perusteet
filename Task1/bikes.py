import sqlite3

db = sqlite3.connect('bikes.db')
db.isolation_level = None

def distance_of_user(user):
    distance = db.execute('''
    SELECT SUM(T.distance)
    FROM Users U LEFT JOIN Trips T ON U.id = T.user_id
    WHERE U.name = ?
    ''', [user]).fetchone()[0]
    return distance

def speed_of_user(user):
    meters = distance_of_user(user)
    kilometers = meters/1000
    minutes = db.execute('''
    SELECT SUM(T.duration)
    FROM Users U LEFT JOIN Trips T ON U.id=T.user_id
    WHERE U.name = ?
    ''', [user]).fetchone()[0]
    hours = minutes/60
    speed = round(kilometers/hours, 2)
    return speed

def duration_in_each_city(day):
    duration = db.execute('''
    SELECT C.name, SUM(T.duration)
    FROM Trips T, Cities C, Stops S
    WHERE
    C.id = S.city_id AND S.id = T.from_id AND T.day = ?
    GROUP BY C.name
    ''', [day]).fetchall()
    return duration

def users_in_city(city):
    users = db.execute('''
    SELECT COUNT(DISTINCT T.user_id)
    FROM Trips T, Cities C, Stops S
    WHERE
    S.city_id = C.id AND
    S.id = T.from_id AND
    C.name = ?
    ''', [city]).fetchone()[0]
    return users

def trips_on_each_day(city):
    trips = db.execute('''
    SELECT T.day, COUNT(*)
    FROM Trips T, Cities C, Stops S
    WHERE
    S.city_id = C.id AND
    S.id = T.from_id AND
    C.name = ?
    GROUP BY
    T.day
    ''', [city]).fetchall()
    return trips

def most_popular_start(city):
    stop = db.execute('''
    SELECT S.name, COUNT(T.from_id)
    FROM Trips T, Cities C, Stops S
    WHERE
    S.city_id = C.id AND
    S.id = T.from_id AND
    C.name = ?
    GROUP BY
    S.name
    ORDER BY
    COUNT(T.from_id) DESC
    LIMIT 1
    ''', [city]).fetchone()
    return stop
from datetime import datetime, timedelta
import threading

from flask import Flask
import requests


cache = threading.local()
cache.timestamp = None
cache.data = {}


BASE_URL = "https://ghibliapi.herokuapp.com"
CACHE_EXPIRE = timedelta(seconds=60)

app = Flask(__name__)


def fetch_data():
    print('Fetching data')
    r = requests.get(BASE_URL + "/films?fields=url,title")
    r.raise_for_status()
    films = r.json()

    r = requests.get(BASE_URL + "/people?fields=name,films")
    r.raise_for_status()
    people = r.json()

    data = {film['url']: {'title': film['title'], 'people': set()} for film in films}

    for person in people:
        for film_url in person['films']:
            if film_url in data:
                data[film_url]['people'].add(person['name'])
            else:
                print(f"Unknown film for {person['name']}: {film_url}")

    return data


def get_data():
    utcnow = datetime.utcnow()
    if cache.timestamp is None or utcnow - cache.timestamp > CACHE_EXPIRE:
        cache.data = fetch_data()
        cache.timestamp = utcnow
    return cache.data


def render_data(data):
    movies = "".join(f"<li>{film['title']}: {film['people']}</li>\n" for film in data.values())
    return f"<html>Movies:<ul>{movies}</ul></html>"


@app.route("/movies")
def movies():
    data = get_data()
    return render_data(data)

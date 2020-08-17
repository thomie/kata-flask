from datetime import datetime, timedelta

from flask import Flask
import requests


app = Flask(__name__)


def log(s):
    print(s)


class Ghibli():
    BASE_URL = "https://ghibliapi.herokuapp.com"
    REQUESTS_TIMEOUT = 10  # seconds
    CACHE_EXPIRE = timedelta(seconds=60)

    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.cache = {}

    def _get(self, url):
        r = self.session.get(self.BASE_URL + url, timeout=self.REQUESTS_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def get(self, url):
        utcnow = datetime.utcnow()
        if url in self.cache:
            timestamp, result = self.cache[url]
            if utcnow - timestamp < self.CACHE_EXPIRE:
                return result
        result = self._get(url)
        self.cache[url] = (utcnow, result)
        return result

    def get_films(self):
        return self.get("/films?fields=url,title")

    def get_people(self):
        return self.get("/people?fields=name,films")


ghibli = Ghibli()


def get_films_with_people(ghibli):
    films = ghibli.get_films()
    people = ghibli.get_people()

    films_with_people = {film['url']: {'title': film['title'], 'people': set()} for film in films}

    for person in people:
        for film_url in person['films']:
            if film_url in films_with_people:
                films_with_people[film_url]['people'].add(person['name'])
            else:
                log(f"Unknown film for person='{person['name']}': '{film_url}'")

    return films_with_people


def render(films):
    # "You don’t have to worry about the styling of that page."
    movies = "".join(f"<li>{film['title']}: {film['people']}</li>\n" for film in films.values())
    return f"<html>Movies:<ul>{movies}</ul></html>"


@app.route("/movies")
def movies(ghibli=ghibli):
    try:
        films = get_films_with_people(ghibli)
    except requests.RequestException as e:
        log(repr(e))
        return "Error connecting to Ghibli API", 500
    else:
        return render(films)


if __name__ == "__main__":
    app.run(port=8000)

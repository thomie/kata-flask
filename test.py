import logging
import time

import vcr

import app

my_vcr = vcr.VCR(
    cassette_library_dir='fixtures/vcr_cassettes',
    decode_compressed_response=True,
    record_mode='once',
)


app.app.config['TESTING'] = True


class FakeGhibli():
    def __init__(self, films, people):
        self.films = films
        self.people = people

    def get_films(self):
        if isinstance(self.films, Exception):
            raise self.films
        else:
            return self.films

    def get_people(self):
        if isinstance(self.people, Exception):
            raise self.people
        else:
            return self.people


def test_get_films_with_people():
    fg = FakeGhibli(
        films=[{'url': 'some_film', 'title': 'some_title'}],
        people=[{'name': 'some_name', 'films': ['some_film']}]
    )
    assert app.get_films_with_people(fg) == {'some_film': {'title': 'some_title', 'people': {'some_name'}}}


def test_unknown_film():
    fg = FakeGhibli(
        films=[],
        people=[{'name': 'some_name', 'films': ['unknown_film']}]
    )
    assert app.get_films_with_people(fg) == {}  # Should not raise KeyError


def test_request_exception():
    fg = FakeGhibli(
        films=app.requests.HTTPError(),
        people=[]
    )
    assert app.movies(fg) == ("Error connecting to Ghibli API", 500)

    fg = FakeGhibli(
        films=[],
        people=app.requests.ConnectionError()
    )
    assert app.movies(fg) == ("Error connecting to Ghibli API", 500)


def test_render():
    films = {'some_film': {'title': 'some_title', 'people': {'some_name'}}}
    html = "<html>Movies:<ul><li>some_title: {'some_name'}</li>\n</ul></html>"
    assert app.render(films) == html 


@my_vcr.use_cassette('test_ghibli')
def test_ghibli():
    films = app.ghibli.get_films()
    assert len(films) == 20
    people = app.ghibli.get_people()
    assert len(people) == 31


def test_ghibli_should_cache():
    class FakeResponse():
        def raise_for_status(self):
            pass

        def json(self):
            return []

    class FakeSession():
        def __init__(self):
            self.n_requests = 0

        def get(self, *args, **kwargs):
            self.n_requests += 1
            return FakeResponse()

    s = FakeSession()
    g = app.Ghibli(session=s)
    g.CACHE_EXPIRE = app.timedelta(seconds=0.1)

    g.get_films()
    assert s.n_requests == 1
    g.get_films()  # Should use cache.
    assert s.n_requests == 1

    time.sleep(0.1)

    g.get_films() # Should make a new request.
    assert s.n_requests == 2


@my_vcr.use_cassette('test_ghibli')
def test_app_integration():
    with app.app.test_client() as c:
        r = c.get("/movies")
        assert r.status_code == 200
        assert r.data

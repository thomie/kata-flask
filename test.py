import logging

import vcr

my_vcr = vcr.VCR(
    cassette_library_dir='fixtures/vcr_cassettes',
    decode_compressed_response=True,
    record_mode='once',
)


from app import app
app.config['TESTING'] = True


@my_vcr.use_cassette()
def test_movies():
    with app.test_client() as c:
        html = c.get("/movies").data.decode()
        print()
        print(html)
    #assert False

import os
from wtwapi.config import config
from wtwapi import wtwapi
import json
import unittest
import tempfile

class wtwapiTestCase(unittest.TestCase):

    def setUp(self):
        with wtwapi.app.app_context():
            self.app = wtwapi.app.test_client()
            wtwapi.app.config.from_object(config.TestConfig)
            wtwapi.init_db()

    def tearDown(self):
        with wtwapi.app.app_context():
            # os.unlink(wtwapi.app.config['DATABASE'])
            pass

    # general tests over tables

    def test__tables_are_empty_at_the_start(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/garments')
            assert b'No entries here so far' in rv.data
            rv = self.app.get('/brands')
            assert b'No entries here so far' in rv.data
            rv = self.app.get('/garment_types')
            assert b'No entries here so far' in rv.data
            rv = self.app.get('/combos')
            assert b'No entries here so far' in rv.data
            # The only table that is not empty from init!
            rv = self.app.get('/use_in_combos')
            assert b'Found 8 entries' in rv.data

    # tests over garment brands

    def test__adding_a_new_brand(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/brands')
            assert b'No entries here so far' in rv.data
            data = dict(brand_name='Test Brand', website_url='https://www.testbrand.com.au/')
            rmess = self.app.post('/brand', data=data)
            assert rmess.status_code == 201
            rv2 = self.app.get('/brands')
            assert b'Found 1 entries' in rv2.data


    def test__brand_cannot_be_added_because_no_name_is_provided(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/brands')
            assert b'No entries here so far' in rv.data
            data = dict(wiki_article='https://en.wikipedia.org/wiki/TestBrand', website_url='https://www.testbrand.com.au/')
            rmess = self.app.post('/brand', data=data)
            assert rmess.status_code == 200
            rv2 = self.app.get('/brands')
            assert b'No entries here so far' in rv.data


    def test__add_two_brands_same_name_fails_only_first_brand_is_inserted(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/brands')
            assert b'No entries here so far' in rv.data
            data = dict(brand_name='Test Brand', website_url='https://www.testbrand.com.au/')
            rmess = self.app.post('/brand', data=data)
            assert rmess.status_code == 201
            rmess2 = self.app.post('/brand', data=data)
            assert rmess2.status_code == 200
            rv2 = self.app.get('/brands')
            rv2_json = json.loads(rv2.data)
            assert rv2_json['results'][0]['brand_id'] == 1
            assert b'Found 1 entries' in rv2.data


    def test__add_three_brands(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/brands')
            assert b'No entries here so far' in rv.data
            data = dict(
                    brand_name='Test Brand',
                    website_url='https://www.testbrand.com.au/'
                    )
            data2 = dict(brand_name='Test Brand2', website_url='https://www.testbrand2.com.au/')
            data3 = dict(brand_name='Test Brand3', website_url='https://www.testbrand3.com.au/')
            rmess = self.app.post('/brand', data=data)
            assert rmess.status_code == 201
            rmess2 = self.app.post('/brand', data=data2)
            assert rmess2.status_code == 201
            rmess3 = self.app.post('/brand', data=data3)
            assert rmess3.status_code == 201
            rv2 = self.app.get('/brands')
            rv2_json = json.loads(rv2.data)
            assert rv2_json['results'][0]['brand_id'] == 1
            assert rv2_json['results'][1]['brand_id'] == 2
            assert b'Found 3 entries' in rv2.data


    # tests over garment types table

    def test__adding_a_new_garment_type(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/garment_types')
            assert b'No entries here so far' in rv.data
            data = dict(
                    type_name='Test Type',
                    type_description='Something to wear',
                    use_in_combo_as=3
                    )
            rmess = self.app.post('/garment_type', data=data)
            assert rmess.status_code == 201
            rv2 = self.app.get('/garment_types')
            assert b'Found 1 entries' in rv2.data

    # tests over garment combos table

    def test__adding_a_new_combo(self):
        from datetime import datetime
        with wtwapi.app.app_context():
            rv = self.app.get('/combos')
            assert b'No entries here so far' in rv.data
            data = dict(
                    used_on=datetime(2014, 12, 17),
                    head_id=0,
                    upper_cov_id=0,
                    upper_ext_id=0,
                    upper_int_id=0,
                    lower_ext_id=0,
                    lower_acc_id=0,
                    foot_int_id=0,
                    foot_ext_id=0
                    )
            rmess = self.app.post('/combo', data=data)
            assert rmess.status_code == 201
            rv2 = self.app.get('/combos')
            assert b'Found 1 entries' in rv2.data


    # tests over garment table

    # tests over garment types table

    def test__adding_a_new_garment_type(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/garments')
            assert b'No entries here so far' in rv.data
            data = dict(
                    garment_type_id=5,
                    garment_brand_id=3
                    )
            rmess = self.app.post('/garment', data=data)
            assert rmess.status_code == 201
            rv2 = self.app.get('/garments')
            assert b'Found 1 entries' in rv2.data

    # tests pover use_in_combo table


if __name__ == '__main__':
    unittest.main()

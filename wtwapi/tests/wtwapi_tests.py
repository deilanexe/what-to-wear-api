import os
from wtwapi.config import config
from wtwapi import wtwapi
import json
import unittest
import tempfile
from datetime import datetime

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

    def add_brand(
            self,
            brand_name='Test Brand',
            wiki_article='https://en.wikipedia.org/wiki/TestBrand',
            website_url='https://www.testbrand.com.au/'
            ):
        data = dict(
            brand_name=brand_name,
            wiki_article=wiki_article,
            website_url=website_url
        )
        return self.app.post('/brand', data=data)

    def test__adding_a_new_brand(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/brands')
            assert b'No entries here so far' in rv.data
            rmess = self.add_brand(wiki_article='')
            assert rmess.status_code == 201
            rv2 = self.app.get('/brands')
            assert b'Found 1 entries' in rv2.data


    def test__brand_cannot_be_added_because_no_name_is_provided(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/brands')
            assert b'No entries here so far' in rv.data
            rmess = self.add_brand(brand_name=None)
            assert rmess.status_code == 200
            rv2 = self.app.get('/brands')
            assert b'No entries here so far' in rv.data


    def test__adding_two_brands_same_name_fails_only_first_brand_is_inserted(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/brands')
            assert b'No entries here so far' in rv.data
            rmess = self.add_brand(wiki_article='')
            assert rmess.status_code == 201
            rmess2 = self.add_brand(wiki_article='')
            assert rmess2.status_code == 200
            rv2 = self.app.get('/brands')
            rv2_json = json.loads(rv2.data)
            assert rv2_json['results'][0]['brand_id'] == 1
            assert b'Found 1 entries' in rv2.data


    def test__adding_three_brands(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/brands')
            assert b'No entries here so far' in rv.data
            rmess = self.add_brand(wiki_article='')
            assert rmess.status_code == 201
            rmess2 = self.add_brand(brand_name='Test Brand2', website_url='https://www.testbrand2.com.au/')
            assert rmess2.status_code == 201
            rmess3 = self.add_brand(brand_name='Test Brand3', website_url='https://www.testbrand3.com.au/')
            assert rmess3.status_code == 201
            rv2 = self.app.get('/brands')
            rv2_json = json.loads(rv2.data)
            assert rv2_json['results'][0]['brand_id'] == 1
            assert rv2_json['results'][1]['brand_id'] == 2
            assert b'Found 3 entries' in rv2.data


    # tests over garment types table

    def add_garment_type(
            self,
            type_name='Test Type',
            type_description='Something to wear',
            use_in_combo_as=3
            ):
        data=dict(
                type_name=type_name,
                type_description=type_description,
                use_in_combo_as=use_in_combo_as
                )
        return self.app.post('/garment_type', data=data)

    def test__adding_a_new_garment_type(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/garment_types')
            assert b'No entries here so far' in rv.data
            rmess = self.add_garment_type()
            assert rmess.status_code == 201
            rv2 = self.app.get('/garment_types')
            assert b'Found 1 entries' in rv2.data

    # tests over garment combos table

    def add_combo(
            self,
            used_on=datetime(2014, 12, 17),
            head_id=0,
            upper_cov_id=0,
            upper_ext_id=0,
            upper_int_id=0,
            lower_ext_id=0,
            lower_acc_id=0,
            foot_int_id=0,
            foot_ext_id=0
            ):
        data = dict(
                used_on=used_on,
                head_id=head_id,
                upper_cov_id=upper_cov_id,
                upper_ext_id=upper_ext_id,
                upper_int_id=upper_int_id,
                lower_ext_id=lower_ext_id,
                lower_acc_id=lower_acc_id,
                foot_int_id=foot_int_id,
                foot_ext_id=foot_ext_id
                )
        return self.app.post('/combo', data=data)


    def test__adding_a_new_combo(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/combos')
            assert b'No entries here so far' in rv.data
            rmess = self.add_combo()
            assert rmess.status_code == 201
            rv2 = self.app.get('/combos')
            print rv2.data
            assert b'Found 1 entries' in rv2.data


    def test__request_items_to_make_combos(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/garmentsForCombos')
            assert b'No entries here so far' in rv.data
            rmess = self.add_garment_type()
            assert rmess.status_code == 201
            rmess = self.add_garment()
            assert rmess.status_code == 201
            rv2 = self.app.get('/garmentsForCombos')
            print rv2.data
            assert b'Found 1 entries' in rv2.data


    # tests over garment table

    def add_garment(
            self,
            garment_type_id=1,
            garment_brand_id=1,
            garment_color='000000',
            garment_secondary_color='ffffff',
            garment_image_url='/img/test.png',
            last_washed_on=datetime(2017, 1, 1),
            purchased_on=datetime(2016, 1, 1)
            ):
        data = dict(
                garment_type_id=garment_type_id,
                garment_brand_id=garment_brand_id,
                garment_color=garment_color,
                garment_secondary_color=garment_secondary_color,
                garment_image_url=garment_image_url,
                last_washed_on=last_washed_on,
                purchased_on=purchased_on
                )
        return self.app.post('/garment', data=data)


    def test__adding_a_new_garment(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/garments')
            assert b'No entries here so far' in rv.data
            rmess = self.add_garment_type()
            assert rmess.status_code == 201
            rmess = self.add_brand(wiki_article='')
            assert rmess.status_code == 201
            # cannot insert garment without referring to type or brand
            rmess = self.add_garment()
            print rmess.data
            assert rmess.status_code == 201
            rv2 = self.app.get('/garments')
            # print rv2.data
            assert b'Found 1 entries' in rv2.data


    def test__adding_a_new_garment_without_brand(self):
        with wtwapi.app.app_context():
            print 'test__adding_a_new_garment_without_brand'
            rv = self.app.get('/garments')
            assert b'No entries here so far' in rv.data
            rmess = self.add_garment_type()
            assert rmess.status_code == 201
            rmess = self.add_brand(wiki_article='')
            assert rmess.status_code == 201
            # cannot insert garment without referring to type or brand
            rmess = self.add_garment(garment_brand_id=None)
            print rmess.data
            assert rmess.status_code == 201
            rv2 = self.app.get('/garments')
            # print rv2.data
            assert b'Found 1 entries' in rv2.data


    def test__updating_a_garment_washed_date(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/garments')
            assert b'No entries here so far' in rv.data
            rmess = self.add_garment_type()
            assert rmess.status_code == 201
            rmess = self.add_brand(wiki_article='')
            assert rmess.status_code == 201
            # cannot insert garment without referring to type or brand
            rmess = self.add_garment()
            print rmess.data
            assert rmess.status_code == 201
            rv2 = self.app.get('/garments')
            # print rv2.data
            assert b'Found 1 entries' in rv2.data
            rupd = self.app.put('/garment/1', data={'lastWashedOn': datetime(2017, 2, 20)})
            assert rupd.status_code == 201
            rv2 = self.app.get('/garments')
            j_data = json.loads(rv2.data)
            assert b'Found 1 entries' in rv2.data
            assert j_data['results'][0]['last_washed_on'] == '2017/02/20'


    def test__deleting_a_garment(self):
        with wtwapi.app.app_context():
            rv = self.app.get('/garments')
            assert b'No entries here so far' in rv.data
            rmess = self.add_garment_type()
            assert rmess.status_code == 201
            rmess = self.add_brand(wiki_article='')
            assert rmess.status_code == 201
            # cannot insert garment without referring to type or brand
            rmess = self.add_garment()
            print rmess.data
            assert rmess.status_code == 201
            rv2 = self.app.get('/garments')
            # print rv2.data
            assert b'Found 1 entries' in rv2.data
            rdel = self.app.delete('/garment/1')
            assert rdel.status_code == 201
            rv2 = self.app.get('/garments')
            assert b'No entries here so far' in rv2.data

    # tests over use_in_combo table

    def test__adding_a_new_use_in_combo(self):
        # is this required???
        pass

if __name__ == '__main__':
    unittest.main()

import os
import sqlite3
import config
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.types import Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, aliased
from db_classes import base
from db_classes.garment import Garment
from db_classes.garment_brand import GarmentBrand
from db_classes.garment_type import GarmentType
from db_classes.combos import Combo
from db_classes.use_in_combo import UseInCombo


app = Flask(__name__)
app.config.from_object(config.DevConfig)
engine = None


def connect_db():
    """Connects to the specied database."""
    eng = create_engine(
            '{}://{}:{}@{}:{}/{}'.format(
                    app.config['MYSQL_DATABASE_CONNECTOR'],
                    app.config['MYSQL_DATABASE_USER'],
                    app.config['MYSQL_DATABASE_PASSWORD'],
                    app.config['MYSQL_DATABASE_HOST'],
                    app.config['MYSQL_DATABASE_PORT'],
                    app.config['MYSQL_DATABASE_DB']
                    )
            )
    base.Base.metadata.create_all(eng, checkfirst=True)
    return eng


def init_db():
    """Initializes the database."""
    global engine
    if engine is None:
        engine = connect_db()
    connection = engine.connect()
    session = get_db()
    sql_command = ''
    with app.open_resource('schema.sql', mode='r') as f:
        for line in f:
            line = line.rstrip()
            sql_command += '\n' if line == '' else line
        session.execute(sql_command)
        session.commit()
    session.close()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    global engine
    return scoped_session(sessionmaker(bind=engine))


def get_last_uses (use_conditions):
    last_five_uses = []
    global engine
    if engine is None:
        engine = connect_db()
    session = get_db()
    result_set = session.query(GarmentCombo.used_on).filter_by(
            use_conditions
            ).order_by(GarmentCombo.used_on.desc()).all
    session.close()
    if result_set is None:
        return {'error': "Something went wrong"}
    else:
        for item in result_set:
            last_five_uses.append(item.used_on)
        return last_five_uses


@app.route('/garments', methods=['GET'])
def get_garments():
    global engine
    if engine is None:
        engine = connect_db()
    session = get_db()
    garments = []
    ga = aliased(Garment)
    gt = aliased(GarmentType)
    gb = aliased(GarmentBrand)
    results = session.query(
            Garment, GarmentType, GarmentBrand, UseInCombo
            ).join(GarmentType).join(GarmentBrand).join(UseInCombo).filter(
                    GarmentType.type_id==Garment.garment_type_id
            ).filter(
                    GarmentBrand.brand_id==Garment.garment_brand_id
            ).filter(
                    GarmentType.use_in_combo_as==UseInCombo.use_in_combo_id
            ).all()
    print results
    session.close()
    if len(results) == 0:
        return jsonify({'message': 'No entries here so far'})
    for gar, gty, gbr, uic in results:
        last_five_uses=[]
        garments.append(dict(
                garment_id=gar.garment_id,
                type_id=gty.type_id,
                type_name=gty.type_name,
                brand_name=gbr.brand_name,
                garment_color='#{}'.format(gar.garment_color),
                use_id=gty.use_in_combo_as,
                garment_secondary_color='#{}'.format(gar.garment_secondary_color),
                last_five_uses=[],
                last_washed_on=gar.last_washed_on,
                purchase_date=gar.purchased_on,
                use_name=uic.use_name,
                garment_image_url=gar.garment_image_url
                ))
    return jsonify({'results': garments, 'message': 'Found {} entries.'.format(len(results))})


@app.route('/garment', methods=['POST'])
def add_garment():
    global engine
    if engine is None:
        engine = connect_db()
    try:
        garment_type_id = request.form.get('garment_type_id', None)
        garment_brand_id = request.form.get('garment_brand_id', None)
        garment_color = request.form.get('garment_color', '')
        garment_secondary_color = request.form.get('garment_secondary_color', '')
        garment_image_url = request.form.get('garment_image_url', '')
        last_washed_on = request.form.get('last_washed_on', '')
        purchased_on = request.form.get('purchased_on', '')
        if garment_type_id is not None:
            garment = Garment(
                    garment_type_id, garment_brand_id, garment_color,
                    garment_secondary_color, garment_image_url, last_washed_on,
                    purchased_on
                    )
            session = get_db()
            session.add(garment)
            session.commit()
            session.close()
            return jsonify ({'message': "Garment Created Successfully!!!", 'status': 201}), 201
        else:
            return jsonify({'message': 'ERROR: Garment type ID not provided!', 'status': 200}), 200
    except Exception as e:
        return jsonify({'message': 'ERROR: Something strange happened!!!', 'status': 400}), 400


@app.route('/brands', methods=['GET'])
def get_brands():
    global engine
    if engine is None:
        engine = connect_db()
    session = get_db()
    garment_brands = []
    results = session.query(GarmentBrand).all()
    session.close()
    if len(results) == 0:
        return jsonify({'message': 'No entries here so far'}), 200
    for item in results:
        garment_brands.append({'brand_id': item.brand_id, 'brand_name': item.brand_name, 'wikipedia_article': item.wiki_article, 'website_url': item.website_url})
    return jsonify({'results': garment_brands, 'message': 'Found {} entries.'.format(len(results))}), 200


@app.route('/brand', methods=['POST'])
def add_brand():
    global engine
    if engine is None:
        engine = connect_db()
    try:
        brand_name = request.form.get('brand_name', None)
        wiki_article = request.form.get('wiki_article', '')
        website_url = request.form.get('website_url', '')
        if brand_name is not None:
            session = get_db()
            results = session.query(GarmentBrand).filter_by(brand_name=brand_name).first()
            session.close()
            if results is None:
                brand = GarmentBrand(brand_name, wiki_article, website_url)
                session = get_db()
                session.add(brand)
                session.commit()
                session.close()
                return jsonify ({'message': "Brand Created Successfully!!!", 'status': 201}), 201
            return jsonify({'message': 'ERROR: Brand name already exists!', 'status': 200}), 200
        return jsonify({'message': 'ERROR: Brand name not provided!', 'status': 200}), 200
    except Exception as e:
        return jsonify({'message': 'ERROR: Something strange happened!!!', 'status': 200}), 200


@app.route('/garment_types', methods=['GET'])
def get_garment_types():
    global engine
    if engine is None:
        engine = connect_db()
    session = get_db()
    garment_types = []
    results = session.query(GarmentType).all()
    session.close()
    if len(results) == 0:
        return jsonify({'message': 'No entries here so far'}), 200
    for item in results:
        garment_types.append(dict(
                type_id=item.type_id,
                type_name=item.type_name,
                type_description=item.type_description,
                use_in_combo_as=item.use_in_combo_as
                ))
    return jsonify({'results': garment_types, 'message': 'Found {} entries.'.format(len(results))}), 200

@app.route('/garment_type', methods=['POST'])
def add_garment_type():
    global engine
    if engine is None:
        engine = connect_db()
    try:
        type_name = request.form.get('type_name', None)
        type_description = request.form.get('type_description', '')
        use_in_combo_as = request.form.get('use_in_combo_as', 0)
        if type_name is not None:
            session = get_db()
            results = session.query(GarmentType).filter_by(type_name=type_name).first()
            session.close()
            if results is None:
                g_type = GarmentType(type_name, type_description, use_in_combo_as)
                session = get_db()
                session.add(g_type)
                session.commit()
                session.close()
                return jsonify ({'message': "Garment Type Created Successfully!!!", 'status': 201}), 201
            return jsonify({'message': 'ERROR: Garment Type name already exists!', 'status': 200}), 200
        return jsonify({'message': 'ERROR: Garment Type name not provided!', 'status': 200}), 200
    except Exception as e:
        return jsonify({'message': 'ERROR: Something strange happened!!!', 'status': 200}), 200


@app.route('/combos', methods=['GET'])
def get_garments_for_combos():
    global engine
    if engine is None:
        engine = connect_db()
    session = get_db()
    combos = []
    results = session.query(Combo).all()
    session.close()
    if len(results) == 0:
        return jsonify({'message': 'No entries here so far'}), 200
    for item in results:
        combos.append(dict(
                used_on=item.used_on,
                head_id=item.head_id,
                upper_cov_id=item.upper_cov_id,
                upper_ext_id=item.upper_ext_id,
                upper_int_id=item.upper_int_id,
                lower_ext_id=item.lower_ext_id,
                lower_acc_id=item.lower_acc_id,
                foot_int_id=item.foot_int_id,
                foot_ext_id=item.foot_ext_id
                ))
    return jsonify({'results': combos, 'message': 'Found {} entries.'.format(len(results))}), 200


@app.route('/combo', methods=['POST'])
def add_combo():
    global engine
    if engine is None:
        engine = connect_db()
    try:
        used_on = request.form.get('used_on', None)
        head_id = request.form.get('head_id', 0)
        upper_cov_id = request.form.get('upper_cov_id', 0)
        upper_ext_id = request.form.get('upper_ext_id', 0)
        upper_int_id = request.form.get('upper_int_id', 0)
        lower_ext_id = request.form.get('lower_ext_id', 0)
        lower_acc_id = request.form.get('lower_acc_id', 0)
        foot_int_id = request.form.get('foot_int_id', 0)
        foot_ext_id = request.form.get('foot_ext_id', 0)
        if used_on is not None:
            session = get_db()
            results = session.query(Combo).filter_by(used_on=used_on).first()
            session.close()
            if results is None:
                combo = Combo(
                        used_on, head_id, upper_cov_id, upper_ext_id,
                        upper_int_id, lower_ext_id, lower_acc_id,
                        foot_ext_id, foot_int_id
                        )
                session = get_db()
                session.add(combo)
                session.commit()
                session.close()
                return jsonify ({'message': "Combo Created Successfully!!!", 'status': 201}), 201
            return jsonify({'message': 'ERROR: Combo name already exists!', 'status': 200}), 200
        return jsonify({'message': 'ERROR: Combo name not provided!', 'status': 200}), 200
    except Exception as e:
        return jsonify({'message': 'ERROR: Something strange happened!!!', 'status': 200}), 200


@app.route('/use_in_combos', methods=['GET'])
def get_uses_in_combos():
    global engine
    if engine is None:
        engine = connect_db()
    session = get_db()
    uses_in_combos = []
    results = session.query(UseInCombo).all()
    session.close()
    if len(results) == 0:
        return jsonify({'message': 'No entries here so far'}), 200
    for item in results:
        uses_in_combos.append(dict(
                use_in_combo_id=item.use_in_combo_id,
                use_name=item.use_name,
                use_description=item.use_description,
                field_in_db=item.field_in_db
                ))
    return jsonify({'results': uses_in_combos, 'message': 'Found {} entries.'.format(len(results))}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

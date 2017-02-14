import os
import sqlite3
import config
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.types import Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from db_classes import base
from db_classes.garment import Garment
from db_classes.garment_brand import GarmentBrand
from db_classes.garment_type import GarmentType


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


@app.route('/garments', methods=['GET'])
def get_garments():
    global engine
    if engine is None:
        engine = connect_db()
    session = get_db()
    garments = []
    results = session.query(Garment).all()
    session.close()
    if len(results) == 0:
        return jsonify({'message': 'No entries here so far'})
    for item in results:
        garments.append({'id': item.garment_id})
    return jsonify({'results': garments, 'message': 'Found {} entries.'.format(len(results))})


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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

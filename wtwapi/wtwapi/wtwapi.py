import os
import sqlite3
import config
from datetime import datetime
from sqlalchemy import func
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.types import Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, aliased
from sqlalchemy import text
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


def get_last_uses(use_conditions):
    global engine
    last_five_uses = []
    if engine is None:
        engine = connect_db()
    session = get_db()
    results = session.query(Combo).filter(
            text(use_conditions)
            ).order_by(Combo.used_on.desc()).all()
    session.close()
    for item in results:
        last_five_uses.append(item.used_on)
    return last_five_uses


def get_all_garments(session, branded):
    items = []
    query = "select g.garment_id, g.garment_image_url, \
            g.garment_brand_id, g.last_washed_on, \
            g.purchased_on, {}\
            g.garment_type_id as type_id, gt.type_name, \
            gt.use_in_combo_as, g.garment_color, g.garment_secondary_color,\
            uc.use_name, uc.field_in_db \
            from garment g join garment_type gt on g.garment_type_id=gt.type_id join use_in_combo uc on gt.use_in_combo_as=uc.use_in_combo_id {} where g.available=1 and g.garment_brand_id {} order by use_in_combo_as".format(
                    'gb.brand_name,' if branded else '',
                    'join garment_brands gb on g.garment_brand_id = gb.brand_id' if branded else '',
                    '<> 0' if branded else '= 0'
                    )
    ga = aliased(Garment)
    gt = aliased(GarmentType)
    gb = aliased(GarmentBrand)
    if branded:
        results = session.query(
                ga.garment_id, gt.type_id, gt.type_name,
                ga.garment_color, gt.use_in_combo_as,
                ga.garment_secondary_color, ga.last_washed_on,
                ga.purchased_on, UseInCombo.use_name,
                ga.garment_image_url, UseInCombo.field_in_db, gb.brand_name
                ).from_statement(
                        text(query)
                ).all()
    else:
        results = session.query(
                ga.garment_id, gt.type_id, gt.type_name,
                ga.garment_color, gt.use_in_combo_as,
                ga.garment_secondary_color, ga.last_washed_on,
                ga.purchased_on, UseInCombo.use_name,
                ga.garment_image_url, UseInCombo.field_in_db
                ).from_statement(
                        text(query)
                ).all()
    session.close()
    for item in results:
        garment_id, use_name, field_in_db = item[0], item[8], item[10]
        use_string = '{} = {}'.format(field_in_db, garment_id)
        if use_name == 'upper_ext_id':
            use_string += ' OR upper_int_id = {0} OR upper_cov_id = {0}'.format(garment_id)
        elif use_name == 'upper_cov_id':
            use_string += ' OR upper_ext_id = {}'.format(garment_id)
        elif use_name == 'upper_int_id':
            use_string += ' OR upper_ext_id = {}'.format(garment_id)
        last_five_uses = get_last_uses(use_string)
        items.append(dict(
                garment_id=garment_id,
                type_id=item[1],
                type_name=item[2],
                garment_color='#{}'.format(item[3]),
                use_id=item[4],
                garment_secondary_color='#{}'.format(item[5]),
                last_five_uses=last_five_uses,
                last_washed_on=item[6].strftime("%Y/%m/%d"),
                purchase_date=item[7].strftime("%Y/%m/%d"),
                use_name=use_name,
                garment_image_url=item[9],
                brand_name=item[11] if branded else ''
                ))
    return items

@app.route('/garments', methods=['GET'])
def get_garments():
    global engine
    if engine is None:
        engine = connect_db()
    garments = []
    garments.extend(get_all_garments(get_db(), True))
    garments.extend(get_all_garments(get_db(), False))
    if len(garments) == 0:
        return jsonify({'message': 'No entries here so far'})
    else:
        return jsonify({'results': garments, 'message': 'Found {} entries.'.format(len(garments))})


@app.route('/garment', methods=['POST'])
def add_garment():
    global engine
    if engine is None:
        engine = connect_db()
    try:
        garment_type_id = request.form.get('garment_type_id', None)
        garment_brand_id = request.form.get('garment_brand_id', 0)
        garment_color = request.form.get('garment_color', '')
        garment_secondary_color = request.form.get('garment_secondary_color', '')
        garment_image_url = request.form.get('garment_image_url', '')
        last_washed_on = request.form.get('last_washed_on', '')
        purchased_on = request.form.get('purchased_on', '')
        if garment_type_id is not None:
            garment = Garment(
                    garment_type_id, garment_color,
                    garment_secondary_color, garment_image_url, last_washed_on,
                    purchased_on, garment_brand_id
                    )
            session = get_db()
            session.add(garment)
            session.commit()
            session.close()
            return jsonify ({'message': "Garment Created Successfully!!!", 'status': 201}), 201
        else:
            return jsonify({'message': 'ERROR: Garment type ID not provided!', 'status': 200}), 200
    except Exception as e:
        return jsonify({'message': 'ERROR: Something strange happened!!! {}'.format(e), 'status': 400}), 400


@app.route('/garment/<int:garment_id>', methods=['PUT'])
def update_garment(garment_id):
    global engine
    if engine is None:
        engine = connect_db()
    session = get_db()
    last_washed_date = request.form.get('lastWashedOn', datetime.today().strftime("%Y/%m/%d"))
    try:
        garment = session.query(Garment).get(garment_id)
        garment.last_washed_on = last_washed_date
        session.commit()
        return jsonify ({'message': "Garment Last Washed Date Updated Successfully!!!", 'status': 200}), 201
    except Exception as e:
        return jsonify({'message': 'ERROR: Something strange happened!!!', 'status': 200}), 200


@app.route('/garment/<int:garment_id>', methods=['DELETE'])
def retire_garment(garment_id):
    global engine
    if engine is None:
        engine = connect_db()
    session = get_db()
    try:
        garment = session.query(Garment).get(garment_id)
        garment.available=0
        retire_date=datetime.today().strftime("%Y/%m/%d")
        session.commit()
        return jsonify ({'message': "Garment Retired Successfully!!!", 'status': 200}), 201
    except Exception as e:
        return jsonify({'message': 'ERROR: Something strange happened!!!', 'status': 200}), 201


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
def get_combos():
    global engine
    if engine is None:
        engine = connect_db()
    session = get_db()
    combos = []
    results = session.query(Combo).all()
    session.close()
    if len(results) == 0:
        return jsonify({'message': 'No entries here so far'}), 200
    else:
        for item in results:
            combos.append(dict(
                    used_on=item.used_on.strftime("%Y/%m/%d"),
                    head_id=item.head_id,
                    upper_cov_id=item.upper_cov_id,
                    upper_ext_id=item.upper_ext_id,
                    upper_int_id=item.upper_int_id,
                    lower_ext_id=item.lower_ext_id,
                    lower_acc_id=item.lower_acc_id,
                    foot_int_id=item.foot_int_id,
                    foot_ext_id=item.foot_ext_id
                    ))
    return jsonify({'results': combos, 'message': 'Found {} entries.'.format(len(combos))}), 200


@app.route('/garmentsForCombos', methods=['GET'])
def get_garments_for_combos():
    global engine
    if engine is None:
        engine = connect_db()
    session = get_db()
    ga = aliased(Garment)
    gt = aliased(GarmentType)
    uc = aliased(UseInCombo)
    combos = []
    results = session.query(
            ga.garment_id, ga.garment_image_url,
            gt.type_name, gt.use_in_combo_as,
            uc.use_name
            ).from_statement(
            text('select \
                        g.garment_id, \
                        g.garment_image_url, \
                        gt.type_name, \
                        gt.use_in_combo_as, \
                        uc.use_name \
                    from \
                        garment g \
                    join \
                        garment_type gt on g.garment_type_id=gt.type_id \
                    join \
                        use_in_combo uc on gt.use_in_combo_as=uc.use_in_combo_id \
                    where \
                        g.available=1 \
                    order by use_in_combo_as'
                    )
            ).all()
    session.close()
    if len(results) == 0:
        return jsonify({'message': 'No entries here so far'}), 200
    uses = {}
    for item in results:
        use_name = item[4]
        use = [] if use_name not in uses else uses[use_name]
        use.append(dict(
                garment_id=item[0],
                garment_name=item[0],
                garment_image_url=item[1]
                ))
        uses[use_name] = use
    if 'UPPER_COVER' in uses:
        uses['UPPER_COVER'] += uses.get('UPPER_EXTERNAL', [])
    if 'UPPER_EXTERNAL' in uses:
        uses['UPPER_EXTERNAL'] += uses.get('UPPER_COVER', []) + uses.get('UPPER_INTERNAL', [])
    if 'UPPER_INTERNAL' in uses:
        uses['UPPER_INTERNAL'] += uses.get('UPPER_EXTERNAL', [])
    for use, garments in uses.items():
        combos.append({'name': use, 'garments': garments})
    return jsonify({'results': combos, 'message': 'Found {} entries.'.format(len(results))}), 200


@app.route('/garment_types/count', methods=['GET'])
def get_garment_types_counts():
    global engine
    if engine is None:
        engine = connect_db()
    session = get_db()
    results = session.query(
            Garment.garment_type_id,
            GarmentType.type_name,
            func.count('*')
            ).filter_by(
                    available=1
            ).group_by(GarmentType.type_name).all()
    session.close()
    garment_count = 0
    if len(results) == 0:
        return jsonify({'message': 'No entries here so far'}), 200
    else:
        records = []
        for entry in results:
            (type_id, type_name, count_garments) = entry
            garment_count += count_garments
            records.append({'type_id': type_id, 'type_name':type_name, \
                    'count_garments':count_garments})
    return jsonify({'results': records, 'status': 200, 'time': datetime.now(), 'message': 'Found {} entries'.format(count_garments)}), 200


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

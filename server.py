from flask import Flask, render_template, request
import requests
import re
import os
import json
import config
from sqlalchemy import or_, and_
from datetime import datetime

AGE_OF_BUILDINGS = 2
ADS_PER_PAGE = 15
app = Flask(__name__)
app.config.from_object('config')
from models import db, Ads
db.create_all()


def get_json(filepath):
    if re.match(r'^http[s]?://', filepath):
        resp = requests.get(filepath)
        if resp.status_code == requests.codes.ok:
            return resp.json()
    else:
        if os.path.isfile(filepath):
            with open(filepath) as json_file:
                return json.load(json_file)


def make_inactive_old_ads(id_new_ads):
    old_ads = Ads.query.filter(Ads.id.notin_(id_new_ads))
    for old_ad in old_ads:
        old_ad.active = False
    db.session.commit()


def load_data_into_ads(new_ads):
    for ad in new_ads:
        ad_in_base = Ads.query.filter_by(id=ad.get('id')).first()
        if ad_in_base is None:
            ad_in_base = Ads()
        for key, value in ad.items():
            if hasattr(ad_in_base, key):
                setattr(ad_in_base, key, value)
            setattr(ad_in_base, 'active', True)
        db.session.add(ad_in_base)
    db.session.commit()


@app.route('/')
def ads_list():
    page = request.args.get('page', 1, type=int)
    oblast_district = request.args.get('oblast_district')
    min_price = request.args.get('min_price', 0, type=int)
    max_price = request.args.get('max_price', 0, type=int)
    new_building = request.args.get('new_building', None)
    ads_filtered = \
        Ads.query.filter(Ads.active,
                         or_(oblast_district is None,
                             Ads.oblast_district == oblast_district),
                         or_(min_price == 0, Ads.price >= min_price),
                         or_(max_price == 0, Ads.price <= max_price),
                         or_(new_building is None,
                             or_(Ads.under_construction,
                                 and_(Ads.construction_year,
                                      datetime.now().year -
                                      Ads.construction_year <= AGE_OF_BUILDINGS)
                                 )
                             )
                         )
    return render_template('ads_list.html',
                           ads=ads_filtered.paginate(page, ADS_PER_PAGE, False),
                           oblast_district=oblast_district,
                           min_price=min_price,
                           max_price=max_price,
                           new_building=new_building,
                           page=page)


@app.route('/update_ads/', methods=['GET', 'POST'])
def update_ads():
    if request.method == 'POST':
        json_file_path = request.form.get('json')
        if request.form.get('password') != config.password_for_update_db:
            return render_template('update_ads.html',
                                   json=json_file_path,
                                   error=('password',
                                          'Error: incorrect password!'))
        json_data = get_json(json_file_path) if json_file_path else None
        if json_data is None:
            return render_template('update_ads.html',
                                   json=json_file_path,
                                   error=('json', 'Error: failed to retrieve '
                                                  'data from {}'
                                                  .format(json_file_path)))
        id_new_ads = [ad.get('id', None) for ad in json_data]
        make_inactive_old_ads(id_new_ads)
        load_data_into_ads(json_data)
        return 'status OK: data from the JSON file loaded into the database!'
    return render_template('update_ads.html', error=None)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

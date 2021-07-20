from flask import render_template, jsonify, abort
from app import app
from flask_paginate import Pagination, get_page_args
import json
import random

f = open('app/data/listing.json')
data = json.load(f)
data = [d for d in data if d['status'] == 'Active']
data = data[:100]
# print(data)

def get_data(offset=0, per_page=9):
    return data[offset: offset + per_page]

def filterData(dic, listing_id):
    return dic['id'] == int(listing_id)

@app.template_filter()
def numberFormat(value):
    return format(int(value), ',d')

@app.route('/')
def index():

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    per_page = 9
    total = 90
    pagination_data = get_data(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('index.html', 
                            data=pagination_data,
                            page=page,
                            per_page=per_page,
                            pagination=pagination)

@app.route('/detail/<listing_id>', methods=['GET'])
def listing_page(listing_id):
    filtered_data = [d for d in data if filterData(d, listing_id)]
    image = str(random.randint(1,9))
    if len(filtered_data) == 0:
        abort(404)
    return render_template('listing.html',
                            data=filtered_data[0],
                            image=image)
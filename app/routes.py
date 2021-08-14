from re import search
from flask import render_template, jsonify, abort, request
from app import app
from flask_paginate import Pagination, get_page_args
import json
import random

f = open('app/data/listing.json')
data = json.load(f)
data = [d for d in data if d['status'] == 'Active']

def get_key(q):
    if "mls" in q:
        return 'mlNo'
    elif 'address' in q:
        return 'address'

def get_default_data():
    return data

def get_data(data, offset=0, per_page=50):
    return data[offset: offset + per_page]

def filterData(dic, listing_id):
    return dic['id'] == int(listing_id)

@app.template_filter()
def numberFormat(value):
    return format(int(value), ',d')

@app.route('/')
def index():
    q = request.args.get('q')
    data = get_default_data()[:1500]

    page, per_page, offset = get_page_args(page_parameter='page',
                                            per_page_parameter='per_page')
    per_page = 50
    if not q:
        total = len(data)
        pagination_data = get_data(data, offset=offset, per_page=per_page)
        pagination = Pagination(page=page, per_page=per_page, total=total,
                                css_framework='bootstrap4')

        return render_template('index.html', 
                                data=pagination_data,
                                page=page,
                                per_page=per_page,
                                pagination=pagination,
                                search=None)
    else:
        if ':' in q:
            keyword = q.split(':')
            key = get_key(keyword[0].lower())
            data = [d for d in data if keyword[1].lower() in d[key].lower()]
            
            total = len(data)
            pagination_data = get_data(data, offset=offset, per_page=per_page)
            pagination = Pagination(page=page, per_page=per_page, total=total,
                                    css_framework='bootstrap4')

            return render_template('index.html', 
                                    data=pagination_data,
                                    page=page,
                                    per_page=per_page,
                                    pagination=pagination,
                                    search=q)
        else:
            abort(400)


@app.route('/detail/<listing_id>', methods=['GET'])
def listing_page(listing_id):
    filtered_data = [d for d in data if filterData(d, listing_id)]
    image = str(random.randint(1,9))
    if len(filtered_data) == 0:
        abort(404)
    return render_template('listing.html',
                            data=filtered_data[0],
                            image=image,
                            search=None)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(400)
def invalid_input(e):
    return render_template('400.html', search=request.args.get('q')), 400


# @app.route('/search', methods = ['GET'])
# def search_data():
#     filter_arg = {
#         'key': request.args.get('key'),
#         'value': request.args.get('value')
#     }
#     if not filter_arg['key'] and not filter_arg['value']:

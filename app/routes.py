from flask import render_template
from app import app
from flask_paginate import Pagination, get_page_args
import json

f = open('app/data/listing.json')
data = json.load(f)

def get_data(offset=0, per_page=10):
    return data[offset: offset + per_page]

@app.route('/')
def index():

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    per_page = 9
    total = len(data)
    pagination_data = get_data(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('index.html', 
                            data=pagination_data,
                            page=page,
                            per_page=per_page,
                            pagination=pagination)

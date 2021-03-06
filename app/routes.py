from flask import render_template, jsonify, abort, request, url_for, redirect, session
from app import app
from flask_paginate import Pagination, get_page_args
from google.cloud import storage
from app.helper import *
from dotenv import load_dotenv
import json
import requests as r
import re
import random
import os

load_dotenv()
storage_client = storage.Client.from_service_account_json('app/db/gcreds.json')
baseUrl = os.environ.get('STORAGE_URL')
bucket = storage_client.bucket(os.environ.get('BUCKET_NAME'))

def getContent(blobName):
    print('Please wait, We are downloading the data')
    blobContent = bucket.get_blob(blobName)
    stringContent = blobContent.download_as_string()
    # print(stringContent)
    print('Please wait, We are extracting the data')
    decodedContent = json.loads(stringContent, strict=False)
    return decodedContent

data = getContent(os.environ.get('BLOB_NAME'))

def verify_session():
    return True if session.get('user') else False

def get_key(q):
    mlsRegex = re.compile(r'^R\d{7}')
    if mlsRegex.search(q):
        return 'mlNo'
    else:
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
    status = request.args.get('status')
    data = get_default_data()

    if status == 'Sold':
        if not verify_session():
            return redirect('/login')
        data = [d for d in data if d['status'] == 'Sold']
        data = data[:500]
    else:
        data = [d for d in data if d['status'] == 'Active']
        data = data[:500]
    
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
                                search=None,
                                user=session.get('user'))
    else:
        key = get_key(q)
        data = [d for d in data if q.lower() in (d[key]+d['city']).lower()] if key == 'address' else [d for d in data if q == d[key]]
        
        total = len(data)
        pagination_data = get_data(data, offset=offset, per_page=per_page)
        pagination = Pagination(page=page, per_page=per_page, total=total,
                                css_framework='bootstrap4')

        return render_template('index.html', 
                                data=pagination_data,
                                page=page,
                                per_page=per_page,
                                pagination=pagination,
                                search=q,
                                user=session.get('user'))


@app.route('/detail/<listing_id>', methods=['GET'])
def listing_page(listing_id):
    filtered_data = [d for d in data if filterData(d, listing_id)]
    image = str(random.randint(1,9))
    if len(filtered_data) == 0:
        abort(404)
    if filtered_data[0]['status'] != 'Active':
        if not verify_session():
            return redirect('/login')
    return render_template('listing.html',
                            data=filtered_data[0],
                            image=image,
                            search=None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if verify_session():
        return redirect('/profile')
    try:
        if request.method == 'GET':
            return render_template('login.html')
        else:
            user = helper_login(request)
            session['user'] = {
                'fullName': user[0],
                'email': user[1],
                'mobile': user[5],
            }
            return redirect('/')
    except Exception as e:
        return render_template('login.html', error=e.args[1])


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if verify_session():
            return redirect('/profile')
        if request.method == 'POST':
            register_result = helper_register(request)
            if register_result:
                return render_template('register.html', success='Registered Successfully, Please Check Your Email to Verify Your Account')
        else:
            return render_template('register.html')
    except Exception as e:
        if e.args[0] != 1062:
            return render_template('register.html', error=e.args[1], is_duplicated=False)
        else:
            return render_template('register.html', error='Email Already Registered', is_duplicated=True)


@app.route('/profile', methods=['GET'])
def profile():
    if not verify_session():
        return redirect('/login')
    return render_template('profile.html', user=session.get('user'))


@app.route('/logout', methods=['POST'])
def logout():
    if verify_session():
        session.clear()
        return redirect('/')


@app.route('/verify', methods=['GET'])
def verify_email():
    email = request.args.get('user')
    account_verification = verify_account(email)
    return render_template('accountVerification.html', verified=account_verification['verified'], message=account_verification['message'])


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(400)
def invalid_input(e):
    return render_template('400.html', search=request.args.get('q')), 400
            
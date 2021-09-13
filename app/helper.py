import mysql.connector as db
import os
from uuid import uuid4
from datetime import datetime
from mysql.connector import cursor
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

connection = db.connect(
  host=os.environ.get('MYSQL_HOST'),
  user=os.environ.get('MYSQL_USER'),
  password=os.environ.get('MYSQL_PASSWORD'),
  database=os.environ.get('MYSQL_DB')
)

def send_email_verification(user):
    email = user['email']
    email_body = f'''<h4>Hi {user['fullname']},</h4>
        <p>
            Thank you for registering to our website. Please click <a href="https://etebarian.ca/verify?user={email}">here</a> to activate your account.
        </p>
        Best,<br>
        Hamid'''
    message = Mail(from_email='hamid@etebarian.ca',
                    to_emails=email,
                    subject='Email Verification for ' + user['fullname'],
                    html_content=email_body)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        sg.send(message)
        print('Email sent!')
        return True
    except Exception as e:
        print(e)
        return False

def verify_account(email):
    try:
        cursor = connection.cursor()
        query = f'update etebarianca.users set is_active = 1 where email = "{email}"'

        cursor.execute(query)
        connection.commit()
        return {
            'verified': True,
            'message': 'Your account has been successfully verified'
        }
    except Exception as e:
        print(e)
        return {
            'verified': False,
            'message': e.args[1]
        }
    finally:
        cursor.close()

def helper_login(request):
    email = request.form.get('emailaddress')
    password = request.form.get('password')
    cursor = connection.cursor()

    query = f'select * from etebarianca.users where email="{email}"'
    cursor.execute(query)

    result = cursor.fetchone()
    cursor.close()
    if not result:
        raise Exception(400, 'Email Not Found')

    stored_password = result[2] 
    if not check_password_hash(stored_password, password):
        raise Exception(400, 'Wrong Password')
    
    if result[7]:
        raise Exception(403, 'Your account has expired')

    if not result[4]:
        raise Exception(403, 'Your email is not verified yet')
    
    return result

def helper_register(request):
    cursor = connection.cursor()

    fullname = request.form.get('fullname')
    email = request.form.get('emailaddress')
    phone = request.form.get('mobile')
    password = generate_password_hash(request.form.get('password'))
    created_at = datetime.now()

    query = f'insert into etebarianca.users(id, fullname, email, password, phone, created_at) values("{uuid4()}", "{fullname}", "{email}", "{password}", "{phone}", "{created_at}")'

    cursor.execute(query)

    is_email_sent = send_email_verification({
        'fullname': fullname,
        'email': email
    })

    if not is_email_sent:
        raise Exception('Something went wrong with our server, please try again later')
    connection.commit()
    cursor.close()

    return True
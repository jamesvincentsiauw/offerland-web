import mysql.connector as db
import os
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

connection = db.connect(
  host=os.environ.get('MYSQL_HOST'),
  user=os.environ.get('MYSQL_USER'),
  password=os.environ.get('MYSQL_PASSWORD'),
  database=os.environ.get('MYSQL_DB')
)

def check_account_expiration():
    try:
        cursor = connection.cursor()
        query = f'select created_at, email from etebarianca.users where is_expired=0'
        cursor.execute(query)

        result = cursor.fetchall()

        if not result:
            print('No Account Found')
        else:
            now = datetime.now()
            for data in result:
                created_at = data[0]
                email = data[1]
                if (now - created_at).days >= 30:
                    query = f'update etebarianca.users set is_expired=1, email="{email}-expired" where email="{email}"'
                    cursor.execute(query)

                    connection.commit()
                    print(f'{email}''s account expired')
        cursor.close()
    except Exception as e:
        print(e.args)
# Function to check the service is running well
def health_check():
    print('Health Checked at '+str(datetime.now()))

# Schedule
schedule.every().day.at('00:00').do(check_account_expiration)
schedule.every().minutes.do(health_check)

while True:
    schedule.run_pending()
    time.sleep(1)
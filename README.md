# SMSE Onboarding Web Application

Authors: Shayna Bello, Long Pham, Nick Zhou

Description: The SMSE Web Application is a web-based onboarding application that allows new hire users to view and manage their onboarding tasks. The project aims to provide a simple, user-friendly platform where users can check on upcoming tasks and mark them as complete, which will update their overal tasks progress. 

Table of Contents:

1. Features
2. Requirments
3. Install Dependencies
4. Database Setup
5. Run Migrations
6. Run Development Server
7. Testing
8. Load Test Data
9. URLs
10. Test Users usernames and passwords
11. UI Design

Features:

Requirements:

Python (version 3.10 or higher)
PostgreSQL (latest version)
pip
Setup:

Clone Repository
cd smse_onboarding_main_project
Install Dependencies:

pip install -r requirements.txt (installs Django, psycopg2, and other required Python packages)
Database Setup:

bash# psql -U postgres (login to postgresql, i used username:postgres and password: password)

sql# CREATE DATABASE smse_onboarding_db;

sql# CREATE USER postgres WITH PASSWORD password; (this is the username and password we're all using)

sql# GRANT ALL PRIVILEGES ON DATABASE intro_project_db TO postgres;

The database settings under settings.py should look like this: DATABASES = { 'default': { 'ENGINE': 'django.db.backends.postgresql', 'NAME': 'intro_project_db', 'USER': 'postgres', 'PASSWORD': 'password', 'HOST': 'localhost', 'PORT': '5432', } }

Run Migrations: 5. bash# python manage.py makemigrations (then make sure to set up the database model objects ) 6. bash# python manage.py migrate 7. python manage.py createsuperuser (made a superuser) - username: admin - email address: admin@gmail.com - password: password Run Development Server: 8. python manage.py runserver (runs the app)

Testing: python manage.py test (runs the tests)

Load Test Data:

Make sure PostgreSql is running
python manage.py loaddata fixtures/test_data.json
The test data is called test_data.json and is under posts/fixtures
check the admin page to make sure all the users and their posts are there.
URLs (http://127.0.0.1:8000/admin/) directs to the django admin panel (http://127.0.0.1:8000/posts/) shows a list of all posts /posts/create_post/ should create a new post but not working right now (or need to login first) /login/ should redirect for non logged in users but not working right now

Test Users

username: user1

email: user1@sandiego.edu

password: user1password

username: admin

email: admin@sandiego.edu

password: adminpassword

UI Design

Figma UI design for the project: https://www.figma.com/design/YVS33HH5t2CeZHXbrviOy6/SMSE-Intro-Project-Design?node-id=2304-963&t=B59YOP0OfzPS1Udq-1

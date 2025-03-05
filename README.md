# SMSE Onboarding Web Application

Authors: Shayna Bello, Long Pham, Nick Zhou

Description: The SMSE Web Application is a web-based onboarding application that allows new hire users to view and manage their onboarding tasks. The project aims to provide a simple, user-friendly platform where users can check on upcoming tasks and mark them as complete, which will update their overal tasks progress. 

Table of Contents:
-
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

sql# CREATE DATABASE "smse-db";

sql# CREATE USER postgres WITH PASSWORD 'password'; (this is the username and password we're all using)

sql# GRANT ALL PRIVILEGES ON DATABASE "smse-db" TO postgres;

The database settings under settings.py should look like this: DATABASES = { 'default': { 'ENGINE': 'django.db.backends.postgresql', 'NAME': 'smse-db', 'USER': 'postgres', 'PASSWORD': 'password', 'HOST': 'localhost', 'PORT': '5432', } }

Run Migrations: 5. bash# python manage.py makemigrations (then make sure to set up the database model objects ) 6. bash# python manage.py migrate 7. python manage.py createsuperuser (made a superuser) - username: admin - email address: admin@gmail.com - password: password Run Development Server: 8. python manage.py runserver (runs the app)

Testing: python manage.py test (runs the tests)

Load Test Data:

Make sure PostgreSql is running
python manage.py loaddata fixtures/test_data.json
The test data is called test_data.json and is under posts/fixtures
check the admin page to make sure all the users and their posts are there.
URLs (http://127.0.0.1:8000/admin/) directs to the django admin panel (http://127.0.0.1:8000/posts/) shows a list of all posts /posts/create_post/ should create a new post but not working right now (or need to login first) /login/ should redirect for non logged in users but not working right now

Test Data

The following test data is used in the unit tests for the SMSE Onboarding application. These include sample Faculty and Task data to validate the functionality of models and their relationships.

Faculty User:
- 
Faculty User 1
- First Name: Jane
- Last Name: Doe
- Email:jane.doe@example.com
- Job Role: Professor
- Department: Computer Science
- Password: securepassword
- Phone: 1234567890
- Zoom Phone: 0987654321
- Office Room: CS101
- Hire Date:2024-01-01
- Mailing List Status: Subscribed
- Bio: Expereinced computer science professor

Faculty User 2
- First Name: John
- Last Name: Smith
- Email:john.smith@example.com
- Job Role: Assitance Professor
- Department: Electrical Engineering
- Password: password123
- Phone: 987654321
- Zoom Phone: 0123456789
- Office Room: EE102
- Hire Date:2024-01-02
- Mailing List Status: Not Subscribed
- Bio: New hire in Electrical Engineering
---
Tasks
-
Task 1
- Task Name: Setup Email
- Assigned To: John Smith
- Description: Set up your university email account
- Due Date: 2024-02-01
- Created Date: 2024-01-01
- Completed Status: False
---
Task Progress
-
- Progress Status: In Progress
- Associated Faculty: John Smith
- Associated Task: Setup Email
---

Figma UI design for the project: https://www.figma.com/design/YVS33HH5t2CeZHXbrviOy6/SMSE-Intro-Project-Design?node-id=2304-963&t=B59YOP0OfzPS1Udq-1

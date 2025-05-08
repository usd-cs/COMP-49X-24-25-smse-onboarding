# SMSE Onboarding Web Application

**Authors:** Shayna Bello, Long Pham, Nick Zhou

**Description:** The SMSE Web Application is a web-based onboarding application that allows new hire users to view and manage their onboarding tasks. The project aims to provide a simple, user-friendly platform where users can check on upcoming tasks and mark them as complete, which will update their overal tasks progress.

## Table of Contents

**1.** Features
**2.** Requirements
**3.** Setup
**4.** Install Dependencies
**5.** Database Setup
**6.** Run Migrations
**7.** Run Development Server
**8.** Testing
**9.** Load Test Data
**10.** URLs
**11.** Test Data
**12.** UI Design

## 1. Features

- New hire dashboard that displays the user's name and role
- Quick links that direct the user to the SMSE directory, campus map, and other resources
- Checklists for keeping track of upcoming and completed tasks

## 2. Requirements

- Python (version 3.10 or higher)
- PostgreSQL (latest version)
- pip

## 3. Setup

**1.** Clone repository by typing `git clone https://github.com/usd-cs/COMP-49X-24-25-smse-onboarding.git` into the command line.
**2.** `cd smse_onboarding_main_project`

## 4. Install Dependencies

**1.** `pip install -r requirements.txt` (installs Django, psycopg2, and other required Python packages)

## 5. Database Setup

**1.** In Bash, type `psql -U postgres`
**2.** Login to PostgreSQL. Use `postgres` for the username and `password` for the password.
**3.** In PostgreSQL, type `CREATE DATABASE "smse-db";`
**4.** In PostgreSQL, type `CREATE USER postgres WITH PASSWORD 'password';` (this is the username and password we're all using)
**5.** In PostgreSQL, type `GRANT ALL PRIVILEGES ON DATABASE "smse-db" TO postgres;`

The database settings under `settings.py` should look like this:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'smse-db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 6. Run Migrations

**1.** In Bash, type `python manage.py makemigrations` (then make sure to set up the database model objects )
**2.** In Bash, type `python manage.py migrate`
**3.** In Bash, type `python manage.py createsuperuser` (makes a superuser)
**4.** When prompted, enter `admin` for the username, `admin@gmail.com` for the email address, and `password` for the password.

## 7. Run Development Server

**1.** In Bash, type `python manage.py runserver` (runs the app)

## 8. Testing

**1.** In Bash, type `python manage.py test` (runs the tests)

## 9. Load Test Data

**1.** Make sure PostgreSQL is running.
**2.** In Bash, type `python manage.py loaddata fixtures/test_data.json`.
The test data is called `test_data.json` and is under `posts/fixtures`.
Check the admin page to make sure all the users and tasks are there.

## 10. URLs

- (http://127.0.0.1:8000/admin/) - directs to the Django admin panel
- (http://127.0.0.1:8000/) - directs to the login page of the onboarding portal

## 11. Test Data

The following test data is used in the unit tests for the SMSE Onboarding application. These include sample Faculty and Task data to validate the functionality of models and their relationships.

### Faculty User 1

```
"model": "tasks.faculty",
"pk": 1,
"fields": {
    "user": null,
    "faculty_id": 1,
    "first_name": "Jane",
    "last_name": "Doe",
    "job_role": "Professor",
    "engineering_dept": "Computer Science",
    "email": "jane.doe@example.com",
    "phone": "1234567890",
    "zoom_phone": "0987654321",
    "office_room": "CS101",
    "hire_date": "2024-01-15T08:00:00-08:00",
    "mailing_list_status": false,
    "bio": "Test bio",
    "completed_onboarding": false
}
```

### Faculty User 2

```
"model": "tasks.faculty",
"pk": 2,
"fields": {
    "user": null,
    "faculty_id": 2,
    "first_name": "John",
    "last_name": "Smith",
    "job_role": "Assistant Professor",
    "engineering_dept": "Electrical Engineering",
    "email": "john.smith@example.com",
    "phone": "987654321",
    "zoom_phone": "0123456789",
    "office_room": "EE102",
    "hire_date": "2024-02-01T08:00:00-08:00",
    "mailing_list_status": true,
    "bio": "Another test bio",
    "completed_onboarding": false
}
```

### Task 1

```
"model": "tasks.task",
"pk": 1,
"fields": {
    "title": "Attend New Hire Orientation",
    "description": "Attend the onboarding orientation session for new hires.",
    "created_at": "2024-11-01T09:00:00-08:00",
    "completed": false,
    "deadline": "2024-12-15T17:00:00-08:00",
    "assigned_to":[2]
}
```

### Task 2

```
"model": "tasks.task",
"pk": 2,
"fields": {
    "title": "Upload Resume",
    "description": "Upload your resume to the onboarding portal or email to SMSE admin.",
    "created_at": "2024-11-02T10:30:00-08:00",
    "completed": false,
    "deadline": "2024-12-20T17:00:00-08:00",
    "assigned_to":[2]
}
```

### Task 3

```
"model": "tasks.task",
"pk": 3,
"fields": {
    "title": "Computer Request",
    "description": "Request computer from IT and pick up at IT office.",
    "created_at": "2024-11-03T15:45:00-08:00",
    "completed": true,
    "deadline": "2024-11-30T12:00:00-08:00",
    "assigned_to": [1, 2]
}
```

### Task 4

```
"model": "tasks.task",
"pk": 4,
"fields": {
    "title": "Pick Up Office Key",
    "description": "Collect your office key from the front office.",
    "created_at": "2024-11-04T14:15:00-08:00",
    "completed": true,
    "deadline": "2024-12-23T17:00:00-08:00",
    "assigned_to":[1, 2]
}
```

### Task 5

```
"model": "tasks.task",
"pk": 5,
"fields": {
    "title": "Set Up Direct Deposit",
    "description": "Provide banking details to payroll for direct deposit setup.",
    "created_at": "2024-11-05T09:30:00-08:00",
    "completed": false,
    "deadline": "2024-12-04T17:00:00-08:00",
    "assigned_to":[1, 2]
}
```

### Task 6

```
"model": "tasks.task",
"pk": 6,
"fields": {
    "title": "Enroll in Benefits",
    "description": "Choose health, dental, and vision benefits and submit enrollment forms.",
    "created_at": "2024-11-06T13:00:00-08:00",
    "completed": false,
    "deadline": "2025-01-05T17:00:00-08:00",
    "prerequisite_task": 5,
    "assigned_to":[1, 2]
}
```

### Task 7

```
"model": "tasks.task",
"pk": 7,
"fields": {
    "title": "Complete Security Training",
    "description": "Complete cybersecurity training and submit certificate.",
    "created_at": "2024-11-07T11:00:00-08:00",
    "completed": false,
    "deadline": "2025-01-10T17:00:00-08:00",
    "prerequisite_task": 3,
    "assigned_to":[1, 2]
}
```

### Task 8

```
"model": "tasks.task",
"pk": 8,
"fields": {
    "title": "Meet with Manager",
    "description": "Schedule and attend an initial meeting with your manager.",
    "created_at": "2024-11-08T15:30:00-08:00",
    "completed": false,
    "deadline": "2025-01-01T17:00:00-08:00",
    "assigned_to":[1, 2]
}
```

## 12. UI Design

Figma UI design for the project: https://www.figma.com/design/YVS33HH5t2CeZHXbrviOy6/SMSE-Intro-Project-Design?node-id=2304-963&t=B59YOP0OfzPS1Udq-1

## 13. Pre-Merge Steps
Before merging to the main production branch, run the pre-merge script pre_merge.sh OR manually follow these steps:

1. **Backup the database:**
    - In Bash, type `docker compose -f compose.yaml exec db pg_dump -U postgres -d smse-db > ./backups/pre_merge_backup_$(date +%Y%m%d_%H%M%S).sql`
    - This will create a backup of the database before making any changes

2. **Check for any pending migrations:**
    - In Bash, type `docker compose -f compose.yaml exec web python manage.py showmigrations | grep "\[ \]"`
    - If there are pending migrations, you will see output like `[ ]`
    - If there are no pending migrations, you will see output like `[X]`
    - If there are pending migrations, you can apply them with `docker compose -f compose.yaml exec web python manage.py migrate`

3. **Run any tests:**
    - In Bash, type `docker compose -f compose.yaml exec web python manage.py test`
    - This will run the tests and check for any errors

4. **Check for expired sessions:**
    - In Bash, type `docker compose -f compose.yaml exec web python manage.py check_expired_sessions`
    - This will check for any expired sessions and delete them

## 14. Post-Merge Steps
After merging to the main production branch, run the post-merge script post_merge.sh OR manually follow these steps:

1. **Pull the latest changes:**
    - In Bash, type `git pull origin main`
    - This will pull the latest changes from the main production branch

2. **Backup the database:**
    - In Bash, type `docker compose -f compose.yaml exec db pg_dump -U postgres -d smse-db > ./backups/post_merge_backup_$(date +%Y%m%d_%H%M%S).sql`

3. **Create and apply migrations:**
    - In Bash, type `docker compose -f compose.yaml exec web python manage.py makemigrations`
    - In Bash, type `docker compose -f compose.yaml exec web python manage.py migrate`
    - This will create and apply any migrations that are needed

4. **Collect static files:**
    - In Bash, type `docker compose -f compose.yaml exec web python manage.py collectstatic --noinput`
    - This will collect all the static files into the `staticfiles` directory

5. **Clear expired sessions:**
    - In Bash, type `docker compose -f compose.yaml exec web python manage.py clear_expired_sessions`
    - This will clear any expired sessions

6. **Restart services and cleanup   :**
    - In Bash, type `docker compose -f compose.yaml down`
    - In Bash, type `docker compose -f compose.yaml up -d --remove-orphans`
    - This will restart the Docker containers and remove any orphaned containers

7. **Verify services are running:**
    - In Bash, type `docker ps | grep "smse_onboarding_main_project"`
    - This will check that the Docker containers are running

8. **Check logs:**
    - In Bash, type `docker compose -f compose.yaml logs`
    - This will check the logs for any errors

9. **Check the application:**
    - In your browser, go to `smse-onboarding.dedyn.io`
    - This will check that the application is running





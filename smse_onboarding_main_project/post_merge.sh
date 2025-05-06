#!/bin/bash
# Post-merge script to use after merging to the main production branch.

echo "============ Post-Merge Deployment ============"

# 1. Pull the latest changes
echo "Pulling latest changes..."
git pull origin main

# 2. Backup the database before applying changes
echo "Creating database backup..."
BACKUP_FILENAME="post_merge_backup_$(date +%Y%m%d_%H%M%S).sql"
docker compose -f compose.yaml exec db pg_dump -U postgres -d smse-db > ./backups/$BACKUP_FILENAME
echo "Backup created: ./backups/$BACKUP_FILENAME"

# 3. Create and apply migrations
echo "Creating migrations..."
docker compose -f compose.yaml exec web python manage.py makemigrations

echo "Applying migrations..."
docker compose -f compose.yaml exec web python manage.py migrate

# 4. Collect static files
echo "Collecting static files..."
docker compose -f compose.yaml exec web python manage.py collectstatic --noinput

# 5. Clear expired sessions
echo "Clearing expired sessions..."
docker compose -f compose.yaml exec web python manage.py clearsessions

# 6. Restart services with cleanup
echo "Restarting services..."
docker compose -f compose.yaml down
docker compose -f compose.yaml up -d --remove-orphans

# 7. Verify services are running
echo "Verifying services..."
docker ps | grep "smse_onboarding_main_project"

# 8. Check application health
echo "Checking application health..."
sleep 10  # Wait for services to fully start
curl -s -o /dev/null -w "%{http_code}" http://localhost:80/
if [ $? -eq 0 ]; then
    echo "Application is responding."
else
    echo "WARNING: Just in case. Check logs with 'docker compose -f compose.yaml logs'."
fi

echo "Post-merge deployment completed. Check the application for any issues."

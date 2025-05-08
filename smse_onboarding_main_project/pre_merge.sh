#!/bin/bash
# Pre-merge script to prepare for merging changes to the main production branch

echo "============ Pre-Merge Preparation ============"

# 1. Backup the database before making any changes
echo "Creating database backup..."
BACKUP_FILENAME="pre_merge_backup_$(date +%Y%m%d_%H%M%S).sql"
docker compose -f compose.yaml exec db pg_dump -U postgres -d smse-db > ./backups/$BACKUP_FILENAME
echo "Backup created: ./backups/$BACKUP_FILENAME"

# 2. Check for any pending migrations locally
echo "Checking for any local pending migrations..."
docker compose -f compose.yaml exec web python manage.py showmigrations | grep "\[ \]"
if [ $? -eq 0 ]; then
    echo "WARNING: You have pending migrations that haven't been applied. Consider applying them before merging."
else
    echo "All migrations appear to be applied locally."
fi

# 3. Run any tests
echo "Running tests..."
docker compose -f compose.yaml exec web python manage.py test || { echo "Tests failed! Consider fixing issues before merging."; exit 1; }

# 4. Check for expired sessions
echo "Checking for expired sessions..."
docker compose -f compose.yaml exec web python -c "
from django.contrib.sessions.models import Session
from django.utils import timezone
expired = Session.objects.filter(expire_date__lt=timezone.now()).count()
print(f'Found {expired} expired sessions.')
"

echo "Pre-merge checks completed. If everything looks good, proceed with  merge."
echo "After merging, run the post_merge.sh script to complete ."

#!/bin/bash

# Install venv
echo '[INSTALL] Using python virtualenv'
if [ $? -eq 0 ]; then
    echo '[INSTALL] Activating virtualenv'
    source venv/bin/activate
else
    echo '[ERROR] Failed to create virtualenv. Please install USP App requirements mentioned in Documentation.'
    exit 1
fi

echo '[INSTALL] Migrating Database'
# python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
# python manage.py loaddata initial_data.json
echo '[INSTALL] Installation Complete'
python scripts/check_install.py


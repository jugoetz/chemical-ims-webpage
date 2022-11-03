#!/bin/bash

# This script needs to be located in <django_source_dir>/utilities/ to work properly
# Run the database update of chemical-ims-webpage by calling the management command parseexpereact

# get the django project directory and cd there
PROJECT_DIR="$( dirname "$( dirname "${BASH_SOURCE[0]}" )" )"
cd "$PROJECT_DIR" || exit 1

# execute task
/instances/home/cbs/.poetry/bin/poetry run python manage.py parseexpereact --local

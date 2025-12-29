#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run database migrations (creates tables)
python -c "from database import engine; import models; models.Base.metadata.create_all(bind=engine)"
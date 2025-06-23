#!/bin/bash

# Run database migrations if needed
flask db upgrade

# Start the application using Gunicorn with Eventlet worker
gunicorn --worker-class eventlet -w 1 app:app

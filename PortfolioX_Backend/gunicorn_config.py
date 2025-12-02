"""Gunicorn configuration for production"""
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/portfoliox/gunicorn-access.log"
errorlog = "/var/log/portfoliox/gunicorn-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "portfoliox"

# Server mechanics
daemon = False
pidfile = "/var/run/portfoliox/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if terminating SSL at Gunicorn)
# keyfile = '/etc/ssl/private/portfoliox.key'
# certfile = '/etc/ssl/certs/portfoliox.crt'

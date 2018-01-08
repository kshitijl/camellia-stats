FROM weihan/webdriver-python

RUN pip install lxml python-json-logger
RUN apt-get install -y cron

# Add crontab file in the cron directory
ADD crontab /etc/cron.d/hello-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/hello-cron

WORKDIR /repo-root
# Tempest Tool

This is a tool to check the logs of openstack tempest, and sent an email to a
list of interested people when something goes wrong with the results.

# Install

Download the source code from [Github](https://github.com/arxcruz/tempest-tool)

```bash
cd tempest-tool
virtualenv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -r test-requirements.txt

python setup.py install
```

This will create two binaries, one tempestmail and temepstmaild. The first one
is intend to be executed once, in command line. the second is to run as a daemon
every x hours that you can setup as a cron job.

## The config file

Let's assume the following config file:

```yaml
mail_username: auser
mail_password: password
smtp_server: smtp.gmail.com:587
mail_from: auser@gmail.com
template_path: /etc/tempest-tool/templates/mail
cron:
    check: '10 18 15 * *'
jobs:
    - name: 'periodic-tripleo-ci-centos-7-ovb-ha-tempest'
      log_url: 'http://logs.openstack.org/periodic/'
      tempest_results: console.html
      emails:
          - mail: 'johndoe@gmail.com'
            name: 'John Doe'
      subject: 'Job periodic-tripleo-ci-centos-7-ovb-ha-tempest results'
      message: template.html
      is_template: True

```

In this config file we set the username, password and smtp server that
tempest-tool will use to send the email, as well as the path to where to look
for mail templates to be sent. These templates can be Jinja2 templates, and the
data parsed to it contains the follwing:

1. date - The date the job runs
1. link - The link in logs.openstack.org for the run
1. failed - List of failures test
1. covered - Tests who fails but it's covered by some bugzilla
1. new - List of new failures
1. errors - List of errors

All of this are inside a dictionary called data, so in your template you can
have something like this:

```html
{% if data.get('new') %}
    <h2>New failures</h2>
{% elif data.get('failed') %}
    <h2>Success</h2>
{% else %}
    <h2>unexpected failures</h2>
{% endif %}
```

Under jobs section you can add which jobs you want to keep an eye, and you can
set the list of users who you want to send these emails.

## Usage

### Command line
If you want to run the tool once just call:

```bash
tempestmail -c config.yaml --upstream
```
This will execute the tempest-tool once, and exit at the end. A bunch of output
will appear on your screen showing it checking for the logs, downloading, and
parsing it.

### Daemon
Same principle as a daemon:

```bash
tempestmaild -c config.yaml --upstream
```

Except that in this case, the script will keep running forever, until you kill
it, and every x amount of time, configured in the config.yaml file in the option
cron > check.

# TODO
Here some ideas I have:
1. Right now only support gmail with application password, create modules for
other emails
1. Create support for both html and text mails
1. Documentation
1. Auotmated tests
1. API to incorporate in other projects

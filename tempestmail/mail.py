import smtplib

from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader


class Mail(object):
    def __init__(self, config):
        self.config = config
        self.mail_from = config.mail_from
        self.username = config.username
        self.password = config.password
        self.smtp = config.smtp
        self.template_path = config.template_path

    def render_template(self, template, data):
        env = Environment(loader=FileSystemLoader(self.template_path))
        template = env.get_template(template)
        return template.render(data=data)

    def send_mail(self, job, data):
        if job.is_template:
            message = self.render_template(job.message, data)
        else:
            message = job.message

        addresses = [m.mail for m in job.emails]
        msg = MIMEText(message)
        msg['Subject'] = job.subject
        msg['From'] = self.mail_from
        msg['To'] = ",".join(addresses)
        s = smtplib.SMTP(self.smtp)
        s.ehlo()
        s.starttls()
        s.login(self.username, self.password)
        s.sendmail(self.mail_from, addresses, msg.as_string())
        s.quit()

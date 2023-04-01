from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv

load_dotenv()


# for the purpose of this app, you can call sendEmail function with the three parameters, to, subject and content and an email will be sent.
def sendEmail(to, subject, content):
    if os.getenv('APP_ENV') != 'test':
        message = Mail(
            from_email='info@budgetlens.tech',
            to_emails=to,
            subject=subject,
            html_content=content)

        try:
            # TODO: make this a little more secure, currently, is using is my own sendgrid code, but later on we figure something out
            sg = SendGridAPIClient(os.getenv('SEND_GRID_TOKEN'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)

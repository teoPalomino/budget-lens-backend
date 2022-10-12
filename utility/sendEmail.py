from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# for the purpose of this app, you can call sendEmail function with the three parameters, to, subject and content and an email will be sent.
def sendEmail(to, subject, content):
    message = Mail(
        from_email='info@budgetlens.tech',
        to_emails=to,
        subject=subject,
        html_content=content)

    try:
        # TODO: make this a little more secure, currently, is using is my own sendgrid code, but later on we figure something out
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

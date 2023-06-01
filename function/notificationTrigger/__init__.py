import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)


    # TODO: Get connection to database
    connection = psycopg2.connect(os.environ['PostgreConnection'])

    try:
        # TODO: Get notification message and subject from database using the notification_id
        logging.info('Start get notification by notification_id')

        cursor = connection.cursor()
        get_notificcation_query = "SELECT message, subject FROM notification WHERE ID = {0}".format(str(notification_id))
        cursor.execute(get_notificcation_query)
        notifications = cursor.fetchall()

        for notification in notifications:
            email_message = notification[0]
            email_subject = notification[1]

        logging.info('End get notification by notification_id')

        # TODO: Get attendees email and name
        logging.info('Start get attendees email and name')

        get_attendee_query = "SELECT first_name, email FROM attendee"
        cursor.execute(get_attendee_query)
        attendees = cursor.fetchall()

        logging.info('End get attendees email and name')

        # TODO: Loop through each attendee and send an email with a personalized subject
        for attendee in attendees:
            send_mail_to_attendees(attendee[1],email_subject,email_message,attendee[0])
        logging.info('Send email to list attendees')

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        total_attendees = len(attendees)
        update_notification_records(connection=connection, cursor=cursor, total_attendees=total_attendees, notification_id=str(notification_id))

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        cursor.close()
        connection.close()

def send_mail_to_attendees(email_to, subject, message, attendee_name):
    message = Mail(
        from_email='tridp.it@gmail.com',
        to_emails=email_to,
        subject=subject + ' ' + attendee_name,
        html_content=message
    )

    try:
        logging.info('Start function send email to attendees')
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)

        logging.info('Send mail response status code: {0}'.format(str(response.status_code)))
    except Exception as e:
        logging.error(e)

def update_notification_records(connection, cursor, total_attendees, notification_id):
    try:
        current_date = datetime.now()
        update_notification_query = 'UPDATE notification SET status = Number of attendees notified: {0} , completed_date = {1} WHERE notification_id = {2}'.format(total_attendees, current_date, notification_id)
        cursor.excute(update_notification_query)
        connection.commit()
    except Exception as e:
        logging.error(e)
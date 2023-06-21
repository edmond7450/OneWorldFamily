import base64
import mimetypes
import pickle
import os

from django.conf import settings
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from my_settings import GMAIL_TOKEN_NAME


class SendGmail:
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def get_service(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(settings.BASE_DIR.joinpath(f'{GMAIL_TOKEN_NAME}.pickle')):
            with open(settings.BASE_DIR.joinpath(f'{GMAIL_TOKEN_NAME}.pickle'), 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(settings.BASE_DIR.joinpath('credentials.json'), self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(settings.BASE_DIR.joinpath(f'{GMAIL_TOKEN_NAME}.pickle'), 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)

        return service

    def create_message(self, sender, to, subject, message_text, content_subtype='plain', threadId=None):
        """Create a message for an email.
        Args:
          sender: Email address of the sender.
          to: Email address of the receiver.
          subject: The subject of the email message.
          message_text: The text of the email message.
        Returns:
          An object containing a base64url encoded email object.
        """
        message = MIMEText(message_text, content_subtype)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        if threadId:
            message['In-Reply-To'] = threadId['in_reply_to']
            message['References'] = threadId['references']
            return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode(), 'threadId': threadId['threadId']}
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def create_message_with_attachment(self, sender, to, subject, message_text, files, content_subtype='plain'):
        message = MIMEMultipart()
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject

        msg = MIMEText(message_text, content_subtype)
        message.attach(msg)

        for file in files:
            attachment = self.build_file_part(file)
            message.attach(attachment)

        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def build_file_part(self, file):
        """Creates a MIME part for a file.
        Args:
          file: The path to the file to be attached.
        Returns:
          A MIME part that can be attached to a message.
        """
        content_type, encoding = mimetypes.guess_type(file)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        main_type, sub_type = content_type.split('/', 1)
        if main_type == 'text':
            with open(file, 'r') as f:
                msg = MIMEText(f.read(), _subtype=sub_type)
        elif main_type == 'image':
            with open(file, 'rb') as f:
                msg = MIMEImage(f.read(), _subtype=sub_type)
        elif main_type == 'audio':
            with open(file, 'rb') as f:
                msg = MIMEAudio(f.read(), _subtype=sub_type)
        elif main_type == 'application' and sub_type == 'pdf':
            with open(file, 'rb') as f:
                msg = MIMEApplication(f.read(), _subtype=sub_type)
        else:
            with open(file, 'rb') as f:
                msg = MIMEBase(main_type, sub_type)
                msg.set_payload(f.read())
        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        return msg

    def send_message(self, service, user_id, message):
        """Send an email message.
        Args:
          service: Authorized Gmail API service instance.
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          message: Message to be sent.
        Returns:
          Sent Message.
        """
        try:
            message = (service.users().messages().send(userId=user_id, body=message).execute())

            return message
        except Exception as e:
            print('An error occurred: %s' % repr(e))


def send_mail(sender, to, subject, message, content_subtype='plain', attachment_files=None):
    if isinstance(to, list):
        to = ', '.join(to)

    gmail = SendGmail()
    service = gmail.get_service()
    user_id = 'me'
    if attachment_files:
        msg = gmail.create_message_with_attachment(sender, to, subject, message, attachment_files, content_subtype)
    else:
        msg = gmail.create_message(sender, to, subject, message, content_subtype)
    gmail.send_message(service, user_id, msg)

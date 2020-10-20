from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendMail(filename, ownername, ownermail):
    CLIENT_SECRET_FILE = 'gmail.json'
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    SCOPES = ['https://mail.google.com/']
 
    service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    emailMsg = 'Estimado ' + ownername + ', el archivo  ' + filename + ' se encontraba público y fue modificado a privado.'
    mimeMessage = MIMEMultipart()
    mimeMessage['to'] = ownermail
    mimeMessage['subject'] = 'Un archivo de su Google Drive ha sido modificado'
    mimeMessage.attach(MIMEText(emailMsg, 'plain'))
    raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
 
    message = service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
    #print(message)
#sendMail('archivo.doc', 'Maria Lujan Tissera', 'mtisser1@directvla.com.ar')
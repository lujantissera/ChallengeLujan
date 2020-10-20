from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from gmail import sendMail

import mysql.connector
import datetime

#---------conexión a la DDBB------
db= mysql.connector.connect (
    host="localhost",
    user="root",
    passwd="3596lulu"
    #database="DBMELI"
)
cursor=db.cursor()

#-------Crear DDBB-------------------------


cursor.execute("CREATE  DATABASE IF NOT EXISTS  DBMELI ")
db= mysql.connector.connect (
    host="localhost",
    user="root",
    passwd="3596lulu",
    database="DBMELI"
)
cursor=db.cursor()

#--------Crear Primera tabla de archivos--------
cursor.execute("""CREATE TABLE IF NOT EXISTS  FILES ( 
                                        filesname VARCHAR(100),
                                        extension VARCHAR (10),
                                        ownername VARCHAR(100),
                                        visibility TINYINT(1),
                                        lastchangedate DATETIME
                                        )""")

#-------Crear tabla de archivos que fueron públicos------
cursor.execute("""CREATE TABLE IF NOT EXISTS publicfiles (                                        
                                        filesname VARCHAR(100),
                                        extension VARCHAR (10),
                                        ownername VARCHAR(100),
                                        visibility TINYINT(1),
                                        lastchangedate DATETIME
                                        )""")

# --- conectar con URL de la API If modifying these scopes, delete the file token.pickle. --> lastchange
#SCOPES = ['https://www.googleapis.com/auth/drive.metadata']
SCOPES =[ 'https://www.googleapis.com/auth/drive' ]
#SCOPES=['https://www.googleapis.com/drive/v3/files/fileId/permissions/permissionId']    

def main():
    """ Imprime los nombres e identificadores de los primeros 10 archivos a los que tiene acceso el usuario..
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    #----Si ya esta creada, que actualice. Sino que la instale----
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    #If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # que guarde las credenciales para la proxima entrada--- 
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)            

    service = build('drive', 'v3', credentials=creds)

    #---- Llamo a la Api Drive v3, le pongo los items que quiero que me traiga---
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name, fullFileExtension, owners, shared, modifiedTime)").execute()
    items = results.get('files', [])      
    if not items:
        print('No files found.')
    else:
        print('Files:')
        cursor.execute("TRUNCATE TABLE FILES")
        for item in items:            
            #-------variables a almacenar en la tabla--------------------
            #--nombre---
            filenames= item['name'].rsplit('.', 1)[0]

            #----extención----
            fileExtension='N/A'            
            print(item)
            try:
                fileExtension=item['fullFileExtension']
            except:
                pass
            #---------Owner----------
            for owner in item['owners']:                
                ownerName=owner['displayName']
                ownermail=owner['emailAddress']            

            #-----última modificacion---
            lastchange=item['modifiedTime']            
            lastchange=datetime.datetime.strptime(lastchange, "%Y-%m-%dT%H:%M:%S.%fZ")
            lastchange=lastchange.strftime("%Y-%m-%dT%H:%M:%S")     

            #-------visibilidad------    
            shared=int(item['shared'])        
                      
            #print(service.permissions())
            print(shared)
            if shared == True:
                cursor.execute("INSERT INTO  Publicfiles (filesname, extension,ownername,visibility,lastchangedate) VALUES ('%s','%s','%s','%s','%s')" %(filenames, fileExtension,ownerName,shared,lastchange))
                service.permissions().delete(fileId=item['id'],permissionId="anyoneWithLink").execute()
                sendMail(filenames, ownerName, ownermail)      
                                                         
            cursor.execute(" INSERT INTO  FILES (filesname, extension,ownername,visibility,lastchangedate) VALUES ('%s','%s','%s','%s','%s')" %(filenames, fileExtension,ownerName,shared,lastchange))
            db.commit()

if __name__ == '__main__':
    main()          
import smtplib
import hmac
import hashlib
from email.message import EmailMessage
import ssl
import imaplib
import email

def login(email,password):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com','465', context=context) as server:
        try:
            server.login(email, password)
            print("Login successful!")
            return True  
        except smtplib.SMTPAuthenticationError:
            print("Login failed.")
            return False

def send_email_with_mac(sender, recipient, subject, message, key,password):
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(message)
    context = ssl.create_default_context()
    byte_text = sender.encode()+recipient.encode()+subject.encode()+msg.get_content().encode()
    mac = hmac.new(key.encode(), byte_text, hashlib.sha256).hexdigest()
    msg['MAC'] = mac

    with smtplib.SMTP_SSL('smtp.gmail.com','465', context = context) as smtp:
        try:
            smtp.login(sender, password)
            text = msg.as_string()
            smtp.sendmail(sender , recipient, text)
            print("Email sent successfully.")
        except smtplib.SMTPException as e:
            print("Recipient email address is not valid.")
        

def verify_email_with_mac(email, key):
    try:
        mac = email.get('MAC')
        del email['MAC']
        From = email.get('From')
        To = email.get('To')
        Subject = email.get('Subject')
        content = email.get_payload()
        content = content.replace('\r', '')
        byte_email = From.encode()+To.encode()+Subject.encode()+content.encode()
        calculated_mac = hmac.new(key.encode(), byte_email, hashlib.sha256).hexdigest()
        if hmac.compare_digest(mac, calculated_mac):
            print("Email is authentic.")
            return True
        else:
            print("Email has been tampered with!")
            return False
    except Exception as e:
        print("Something Wrong!")

def read_email(EMAIL,PASSWORD,key):
    IMAP_SERVER = 'imap.gmail.com'
    with imaplib.IMAP4_SSL(IMAP_SERVER) as server:
        server.login(EMAIL, PASSWORD)  
        server.select('Inbox')
        
        status, messages = server.search(None, 'ALL')
        if len(messages[0])==0:
            print("Dont have message now.")
            return
        for num in messages[0].split():
            status, data = server.fetch(num, '(RFC822)')
            message = email.message_from_bytes(data[0][1])
            print("====================")
            if verify_email_with_mac(message,key):
                print(f"Message Number: {num}")
                print(f"From : {message.get('From')}")
                print(f"To : {message.get('To')}")
                print(f"Date : {message.get('Date')}")
                print(f"Subject : {message.get('Subject')}")
                print("Content : \n")
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        content = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
                        print(content)
            print("====================")
    
def menulogin():
    print(f"""<====================>\n1. Login\n2. Exit\n<====================>""")
    option = input("Select your option( 1, 2) : ")
    return option

def menu():
    print(f"""<====================>\n1. Send Email\n2. Read Email\n3. Logout\n<====================>""")
    option = input("Select your option( 1, 2, 3) : ")
    return option

key = 'super_secret_keys'
while True:
    loginoption = menulogin()
    if loginoption =='1':
        emailaccount = input("Enter your email account(@gmail) : ")
        password = input("Enter your app password(Ex. abcd efgh igkl mnop) : ")
        if login(emailaccount,password):
            while True:
                menuoption = menu()
                if menuoption== '1':
                    receiver = input("To : ")
                    subject = input("Subject : ")
                    message = input("Content : ")
                    send_email_with_mac(emailaccount,receiver,subject,message,key,password)
                elif menuoption =='2':
                    read_email(emailaccount,password,key)
                elif menuoption =='3':
                    break
                else:
                    print("Please select the correct option.")
    elif loginoption =='2':
        print("Program exited")
        break
    else:
        print("Please select the correct option.")
 
#junenesudsuay@gmail.com
#vyyd ihsd apwu zxto

#shuya.goaenji@gmail.com
#mapo uhkc jycn wbnt 

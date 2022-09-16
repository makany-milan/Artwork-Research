import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os.path
from userData import address, password
import pandas as pd
import numpy as np


smtp_server = 'smtp-mail.outlook.com'
smtp_port = 587
PRICELOC = r'C:\Users\Milán\OneDrive\Desktop\SBS\Mailbox Automation\Mailbox Automation\Gallery Messages\data\prices.xlsx'
CONTACTLOC = r'C:\Users\Milán\OneDrive\Desktop\SBS\Mailbox Automation\Mailbox Automation\Gallery Messages\data\contacts.xlsx'


def compileMessage(artwork1, artist1, artwork2, artist2, gallery):
    if artist1 == artist2:
        msg = f'To the Manager of {gallery}\n\nI like some of the work you are featuring on Artsy. I submitted a price request for these artworks but did not receive a response. I would be interested in finding out prices for {artwork1} and {artwork2} by {artist1}.\n\nWould you be able to send me any price information on these or related pieces?\n\nI would also be interested in receiving information on current exhibitions in your gallery with accompanying price lists, if you are able to send these to me.\nThanks a lot.\n\nRegards\nRenée B. Adams\n\n========================================================================================\nRenée B. Adams\nProfessor of Finance, Saïd Business School, University of Oxford\nSenior Research Fellow, Jesus College\n\nW:       renee-adams, Google Scholar, SSRN\nP:         : +44 (0)1865 288 824\nA:         Saïd Business School, University of Oxford, Park End Street, Oxford, OX1 1HP, UK\n========================================================================================'
        html = f'''\
        <html>
            <body>
                <p>
                    To the Manager of {gallery}<br><br>
                    I like some of the work you are featuring on Artsy. I submitted a price request for these artworks but did not receive a response. I would be interested in finding out prices for {artwork1} and {artwork2} by {artist1}.<br><br>
                    Would you be able to send me any price information on these or related pieces? <br><br>
                    I would also be interested in receiving information on current exhibitions in your gallery with accompanying price lists, if you are able to send these to me.<br><br>
                    Thanks a lot.<br><br>
                    Regards<br>
                    Renée B. Adams<br><br>
                    ========================================================================================<br>
                    Renée B. Adams<br>
                    &#9;Professor of Finance, Saïd Business School, University of Oxford<br>
                    &#9;Senior Research Fellow, Jesus College<br>
                    W:&#9;<a href='https://www.renee-adams.com'>renee-adams</a>, 
                    <a href='https://scholar.google.co.uk/citations?user=BEPk_skAAAAJ&hl=en'>Google Scholar</a>, 
                    <a href='https://ssrn.com/author=248065'>SSRN</a><br>
                    P:&#9;+44 (0)1865 288 824<br>
                    A:&#9;Saïd Business School, University of Oxford, Park End Street, Oxford, OX1 1HP, UK<br>
                    ========================================================================================
                </p>
            </body>
        </html>
        '''
    else:
        msg = f'To the Manager of {gallery}\n\nI like some of the work you are featuring on Artsy. I submitted a price request for these artworks but did not receive a response. I would be interested in finding out prices for {artwork1} by {artist1} and {artwork2} by {artist2}.\n\nWould you be able to send me any price information on these or related pieces?\n\nI would also be interested in receiving information on current exhibitions in your gallery with accompanying price lists, if you are able to send these to me.\nThanks a lot.\n\nRegards\nRenée B. Adams\n\n========================================================================================\nRenée B. Adams\nProfessor of Finance, Saïd Business School, University of Oxford\nSenior Research Fellow, Jesus College\n\nW:       renee-adams, Google Scholar, SSRN\nP:         : +44 (0)1865 288 824\nA:         Saïd Business School, University of Oxford, Park End Street, Oxford, OX1 1HP, UK\n========================================================================================'
        html = f'''\
        <html>
            <body>
                <p>
                    To the Manager of {gallery}<br><br>
                    I like some of the work you are featuring on Artsy. I submitted a price request for these artworks but did not receive a response. I would be interested in finding out prices for {artwork1} by {artist1} and {artwork2} by {artist2}.<br><br>
                    Would you be able to send me any price information on these or related pieces? <br><br>
                    I would also be interested in receiving information on current exhibitions in your gallery with accompanying price lists, if you are able to send these to me.<br><br>
                    Thanks a lot.<br><br>
                    Regards<br>
                    Renée B. Adams<br><br>
                    ========================================================================================<br>
                    Renée B. Adams<br>
                    &#9;Professor of Finance, Saïd Business School, University of Oxford<br>
                    &#9;Senior Research Fellow, Jesus College<br>
                    W:&#9;<a href='https://www.renee-adams.com'>renee-adams</a>, 
                    <a href='https://scholar.google.co.uk/citations?user=BEPk_skAAAAJ&hl=en'>Google Scholar</a>, 
                    <a href='https://ssrn.com/author=248065'>SSRN</a><br>
                    P:&#9;+44 (0)1865 288 824<br>
                    A:&#9;Saïd Business School, University of Oxford, Park End Street, Oxford, OX1 1HP, UK<br>
                    ========================================================================================
                </p>
            </body>
        </html>
        '''

   
    return msg, html


def compileEmail(recipient, subject, message, html):
    msg = MIMEMultipart('alternative')
    msg['From'] = address
    msg['To'] = recipient
    msg['Subject'] = subject
    text = MIMEText(message, 'plain')
    html = MIMEText(html, 'html')
    msg.attach(text)
    msg.attach(html)

    return msg
    

def connectToServer():
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        server.starttls()
        server.login(address, password)
    except:
        print('There was an issue connecting to the server.')
        server = ''

    return server


def importData(priceloc, contactloc):
    prices = pd.read_excel(priceloc, header=0)
    contacts = pd.read_excel(contactloc, header=0)

    return prices, contacts


def getArtworks(price:pd.DataFrame):
    relevant = price['currency'] == 'REQUESTED'
    relevant2 = price['currency'] == 'NO DATA AVAILABLE'
    data1 = price[relevant | relevant2]
    data2 = data1[['gallery', 'artist', 'title']]
    data = data2.groupby(by='gallery').head(2).reset_index(drop=True)

    return data


def getEmail(art:pd.DataFrame, contact:pd.DataFrame):
    mails = []
    for indx, gal in enumerate(art['gallery']):
        mail = contact[contact['Title'] == gal]['Email address'].values
        mails.append(mail)
    art['maillist'] = mails
    art['mail'] = [','.join(map(str, l)) for l in art['maillist']]
    art = art.drop(['maillist'], axis=1).dropna()
    art = art[art.mail != '']
    art = art[art.mail != np.NAN]

    for ind, r in enumerate(art['mail']):
        prim = r.split(',')[0]
        art.at[ind, 'mail'] = prim

    return art




if __name__ == '__main__':
    pricedata, contacts = importData(PRICELOC, CONTACTLOC)
    artworks = getArtworks(pricedata)
    artworks = getEmail(artworks, contacts)
    emails = artworks.mail.unique()
    CURRENTMAX = 0

    server = connectToServer()
    if server != '':
        print('Connected to server.')
    else:
        print('Error connecting to the server.')


    for x in range(1):
        mail = emails[x+CURRENTMAX]
        set = artworks[artworks['mail'] == mail].reset_index(drop=True)
        select = set.sample(n=2)

        try:
            work1 = select.at[0, 'title']
            artist1 = select.at[0, 'artist']
            work2 = select.at[1, 'title']
            artist2 = select.at[1, 'artist']
            gallery = select.at[0, 'gallery']

            # Artwork1, Artist1, Artwork2, Artist2,  Status
            text, htmltext = compileMessage(work1, artist1, work2, artist2, gallery)
            # recipient, subject, message, html
            message = compileEmail(mail,'Artwork Price Inquiry', text, htmltext)

            server.sendmail(address, 'makanym@gmail.com', message.as_string())
            
            print(f'Message sent to: {mail}')

        except:
            continue



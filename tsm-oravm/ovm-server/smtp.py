#!/usr/bin/python

import smtplib

sender = 'tgphelps@acbl.net'
receivers = ['terry.phelps@aclines.com']

f = open('mail.txt', 'r')
file_data = f.read()
f.close()

message = """From: Terry <tgphelps@acbl.net>
To: terry.phelps@aclines.com
Subject: VM disk cloning

"""

message += file_data
try:
   smtpObj = smtplib.SMTP('smtp.acbl.net')
   smtpObj.sendmail(sender, receivers, message)         
   print "Successfully sent email"
except SMTPException:
   print "Error: unable to send email"

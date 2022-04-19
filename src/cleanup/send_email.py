# from logging import warning
# import os # for interacting with operating system
# import smtplib 
# from email.message import EmailMessage


# EMAIL_SENDER = os.environ.get('EMAIL_SENDER')
# EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
# EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER')
# first_warning = EmailMessage()
# first_warning['Subject'] = "Directory Cleanup Warning"
# first_warning['From'] = EMAIL_SENDER
# first_warning['To'] = os.environ.get('EMAIL_RECEIVER') #TOD0 figure out how to obtain this email that's not 'EMAIL_ADDRESS'

# #first_warning.set_content(first_email.txt)

# with smtplib.smtplib.SMTP_SSL('smtp.rt.hgsc.bcm.edu/', 465) as smtp:
#      smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
#      smtp.send_message(first_warning)

# argparse is a command line argument processing

# import library
import argparse

# creating parser
parser = argparse.ArgumentParser(description='Adding Emails')

# add the argument
parser.add_argument('--email_from', type=str)
parser.add_argument('--rt_number', type=str)
parser.add_argument('--email_send',type=str)



# parse the argument
args = parser.parse_args()

# print [requirement] + user input argument
print('Email from: ' + args.email_from)
print('For RT#: ' + args.rt_number)
print('Sending to: ' + args.email_send)



# parser.add_argument("From", type= str, help = "Receive")

# args = parser.parse_args("Adding Emails")

# print(args.To)
# print(args.From)

# TODO  missing arguments for "To:" and "From"


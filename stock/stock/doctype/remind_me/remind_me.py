# Copyright (c) 2025, mugangasacco and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime


class Remindme(Document):
    pass
    
#     # def on_change(self):
#     #     self.remind_me()
#     def on_change(self):
#         self.remind_me()
        
#     def send_notification_supervisor(self):
#         """
#         Sends an email notification to the supervisor.
#         Returns True if the email is sent successfully, otherwise False.
#         """
#         frappe.throw("Ndotification sent successfully")
#         try:
#             # Send email using Frappe's sendmail function
#             frappe.sendmail(
#                 recipients=self.owner,
#                 subject="Test Subject",
#                 message="Test Message",
#                 now=True  # Ensures the email is sent immediately
#             )
#             return True  # Email sent successfully
#         except Exception as e:
#             # Log any errors that occur during email sending
#             frappe.log_error(f"Error sending email")
#             return False  # Email failed
    
#     def test(self):
#         print("Test")
#     def remind_me(self):
#         """
#         Checks if the provided date matches the current system date.
#         If they match, sends an email notification.
        
#         :param date: A string or datetime object representing the reminder date
#         :return: None
#         """
#         try:
#             # Convert the input date to a datetime object if it's a string
#             # if isinstance(date, str):
#             #     date = datetime.strptime(date, "%Y-%m-%d").date()
#             # elif isinstance(date, datetime):
#             #     date = date.date()  # Extract only the date part
            
#             # Get the current system date
#             today = datetime.today().date()
#             date = datetime.strptime(date, "%Y-%m-%d").date()
            
#             # Compare the provided date with the current system date
#             if date == self.remind_me_at:
#                 # If dates match, send the email notification
#                 if self.send_notification_supervisor():
#                     frappe.msgprint("Email notification sent successfully.")
#                 else:
#                     frappe.msgprint("Failed to send email notification.")
#         except Exception as e:
#             # Log any errors that occur during the process
#             frappe.log_error(f"Error in remind_me function: {str(e)}")
            
            

# @frappe.whitelist()
# def send_reminder_email(doc):
#     today = datetime.today().date()
#     print(doc)

#     if today >= doc.reminder_time:
#         subject = f"Reminder: {doc.title}"
#         message = f"Reminder: {doc.details}"
#         frappe.sendmail(
#             recipients=doc.owner_email,
#             subject=subject,
#             message=message
#         )
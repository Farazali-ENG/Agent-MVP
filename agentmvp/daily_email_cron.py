
from django.utils.timezone import now
from .models import Customer, Agent, Visitor, Chat
from .serializers import ChatSerializer
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# Set up logging
logger = logging.getLogger(__name__)

# Function to send email with PDF attachment
def send_email_with_attachment(smtp_settings, recipient_email, subject, body, attachment_path):
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_settings['sender_email']
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with open(attachment_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(attachment_path)}'
            )
            msg.attach(part)

        with smtplib.SMTP(smtp_settings['smtp_server'], smtp_settings['smtp_port']) as server:
            server.starttls()
            server.login(smtp_settings['sender_email'], smtp_settings['password'])
            server.send_message(msg)

        logger.info(f"Email sent successfully to {recipient_email}")

    except Exception as e:
        logger.error(f"Error sending email to {recipient_email}: {e}")


# Function to create a PDF report

def create_agent_table_pdf(agent_data, conversations_data, pdf_file):
    try:
        end_time = datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)
        start_time = end_time - timedelta(days=1)

        document = SimpleDocTemplate(pdf_file, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Agent details table
        table_data = [["Chatbot Name", "Start Date", "End Date"]]
        for agent in agent_data:
            table_data.append([
                agent.get("agent_name", "N/A"),
                start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time.strftime("%Y-%m-%d %H:%M:%S"),
            ])

        table = Table(table_data, colWidths=[200, 115, 115])
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ])
        table.setStyle(table_style)
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Conversations
        elements.append(Paragraph("Conversations", styles['Heading2']))
        if not conversations_data:
            elements.append(Paragraph("No conversations available.", styles['BodyText']))
        else:
            for conversation in conversations_data:
                elements.append(Paragraph(f"Chatbot Name: {conversation['agent_name']}, Conversation ID: {conversation['visitor_uuid']}", styles['BodyText']))
                elements.append(Spacer(1, 12))

                role_message_data = [["Role", "Message", "Timestamp"]]
                for message in conversation["messages"]:
                    role = "Assistant" if message.get("role", "").lower() == "agent" else "User"
                    timestamp = datetime.fromisoformat(message.get("timestamp", datetime.now().isoformat())).strftime("%Y-%m-%d %H:%M:%S")
                    role_message_data.append([
                        role,
                        Paragraph(message.get("chat_content", "No message available"), styles['BodyText']),
                        timestamp
                    ])
                
                table = Table(role_message_data, colWidths=[80, 320, 150])
                table_style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('VALIGN', (0, 1), (-1, -1), 'TOP'),
                ])
                
                for i, row in enumerate(role_message_data[1:], start=1):
                    if row[0] == "Assistant":
                        table_style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
                
                table.setStyle(table_style)
                elements.append(table)
                elements.append(Spacer(1, 12))

        document.build(elements)
    except Exception as e:
        logger.error(f"Error creating the agent table PDF: {e}")


# Function for daily email report
def daily_email_report():
    try:
        customers = Customer.objects.all()

        if not customers:
            return

        smtp_settings = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "lindac4cs@gmail.com",
            "password": "ryvu fiop hatm inwr" 
        }

        for customer in customers:
            if not hasattr(customer, "email") or not customer.email:
                continue

            agents = Agent.objects.filter(customer=customer)
            agent_data = [{"agent_name": agent.name} for agent in agents]  

            conversations_data = []
            for agent in agents:
                visitors = Visitor.objects.filter(agent=agent)
                for visitor in visitors:
                    chats = Chat.objects.filter(visitor=visitor).order_by("created_at")
                    serialized_chats = ChatSerializer(chats, many=True).data

                    conversation_data = {
                        "visitor_uuid": str(visitor.uuid),
                        "agent_name": agent.name,  
                        "messages": serialized_chats
                    }

                    if conversation_data["messages"]:
                        conversations_data.append(conversation_data)

            if not agent_data or not conversations_data:
                continue

            pdf_file = f"customer_{customer.id}_report.pdf"
            create_agent_table_pdf(agent_data, conversations_data, pdf_file)

            if os.path.exists(pdf_file):
                send_email_with_attachment(smtp_settings, customer.email, "Daily Agent Table Report", "Please find the attached report.", pdf_file)
                logger.info(f"Report emailed to {customer.email}")
                os.remove(pdf_file)
            else:
                logger.warning(f"Skipping email to {customer.email}: Report file not found.")

    except Exception as e:
        logger.error(f"Error generating daily email report: {e}")


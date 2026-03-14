import database
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def generate_digest_html(opportunities):
    """
    Creates a simple HTML for the email digest.
    """
    html = "<h2>Seu Assistente de Oportunidades - Daily Digest 🤖</h2>"
    html += "<p>Aqui estão as melhores oportunidades encontradas hoje:</p><br>"
    
    for opp in opportunities:
        html += f"<div>"
        html += f"<h3>{opp['title']}</h3>"
        html += f"<p><b>Fonte:</b> {opp['source']} | <b>Tipo:</b> {opp['type']}</p>"
        html += f"<p><a href='{opp['url']}'>Ver mais detalhes</a></p>"
        html += f"</div><hr>"
    
    html += "<br><p>Fique atento para mais novidades amanhã!</p>"
    return html

def send_daily_digest():
    """
    Fetches latest opportunities and sends them via email.
    Note: Requires SMTP configuration in .env
    """
    print("📧 Generating daily digest...")
    opportunities = database.get_latest_opportunities(10)
    
    if not opportunities:
        print("No new opportunities to send.")
        return

    # SMTP Configuration (Placeholder values in .env)
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = os.environ.get("SMTP_PORT", 587)
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    recipient_email = os.environ.get("DIGEST_RECIPIENT")

    if not all([smtp_server, smtp_user, smtp_pass, recipient_email]):
        print("⚠️ SMTP not fully configured. Email digest skipped.")
        # Print the digest to console for demonstration
        print("--- DIGEST PREVIEW ---")
        for opp in opportunities:
            print(f"- {opp['title']} ({opp['source']})")
        return

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = recipient_email
    msg['Subject'] = "Oportunidades do Dia 🚀"

    body = generate_digest_html(opportunities)
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print("✅ Email digest sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    send_daily_digest()

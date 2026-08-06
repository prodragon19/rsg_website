import os
import resend

resend.api_key = os.environ.get("RESEND_API_KEY")

def send_welcome_email(to_email, name):
    try:
        resend.Emails.send({
            "from": "RSG Software <tornqvisteliaz@gmail.com>",
            "to": [to_email],
            "subject": "Welcome to RSG Software!",
            "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Welcome {name}!</h2>
                    <p>Thank you for creating an account at <strong>RSG Software</strong>.</p>
                    <p>We're happy to have you with us.</p>
                    <br>
                    <p>Best regards,<br>
                    The RSG Software Team</p>
                </div>
            """
        })
        return True
    except Exception as e:
        print("Email error:", e)
        return False
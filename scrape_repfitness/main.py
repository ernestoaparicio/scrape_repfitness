import datetime
import smtplib
import ssl
from twilio.rest import Client
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pytz
from bs4 import BeautifulSoup
import asyncio
import time
import aiohttp

from scrape_repfitness import config


def gmail_send_email(text):
    port = 465
    message = MIMEMultipart("alternative")
    message["Subject"] = "repfitness check"
    message["From"] = config.GMAIL_EMAIL
    message["To"] = config.RECEIVER_EMAIL
    context = ssl.create_default_context()

    part1 = MIMEText(text, "plain")
    message.attach(part1)

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(config.GMAIL_EMAIL, config.GMAIL_PW)
        server.sendmail(config.GMAIL_EMAIL,
                        config.RECEIVER_EMAIL.split(','), message.as_string())
        print(
            f"Email sent to {config.RECEIVER_EMAIL}")


def twilio_send_sms(to_number, text):
    client = Client(config.TWILIO_SID, config.TWILIO_TOKEN)
    client.api.account.messages.create(
        to=to_number,
        from_=config.TWILIO_PHONE_NUMBER,
        body=text)


async def check_product(session, url):
    async with session.get(url) as response:
        content = await response.text()
        soup = BeautifulSoup(content, 'html.parser')
        if not soup.find("p", class_="out-of-stock"):
            return f"In stock {url}"
        else:
            return f"Out of stock {url}"


async def check_all_products(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.ensure_future(
                check_product(session, url))
            tasks.append(task)
        tasks_completed = await asyncio.gather(*tasks, return_exceptions=True)

        for task_completed in tasks_completed:
            print({task_completed})
            if task_completed.startswith('In stock'):
                msg = " \n".join(
                    [task if task is not None else "None" for task in tasks_completed])
                try:
                    # gmail_send_email(msg)
                    if config.SMS_RECIPIENTS is not None:
                        for number in config.SMS_RECIPIENTS.split(","):
                            twilio_send_sms(
                                number, "Repfitness in stock, check your email sucka.")
                except Exception as e:
                    print(f"Unable to send message {e.__class__}")
                break


if __name__ == "__main__":
    urls = ["http://repfitness.com/strength-equipment/power-racks/pr-4000-power-rack",
            "https://www.repfitness.com/strength-equipment/power-racks/pr-5000-v2",
            "https://www.repfitness.com/strength-equipment/power-racks/rep-pr-1100",
            "https://www.repfitness.com/strength-equipment/power-racks/rep-power-rack",
            "https://www.repfitness.com/strength-equipment/strength-training/benches/rep-fb-5000-competition-flat-bench",
            "https://www.repfitness.com/strength-equipment/strength-training/benches/rep-ab3000-fid-adj-bench",
            "https://www.repfitness.com/strength-equipment/strength-training/benches/rep-ab-3100-fi-bench",
            "https://www.repfitness.com/rep-power-push-sled",
            "https://www.repfitness.com/free-standing-landmine"
            # "https://www.repfitness.com/in-stock-items/rep-premium-leather-lifting-belt"
            ]
    start_time = time.time()
    asyncio.get_event_loop().run_until_complete(
        check_all_products(urls))
    duration = time.time() - start_time
    print(f"Checked {len(urls)} urls in {duration} seconds")

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
                        config.RECEIVER_EMAIL, message.as_string())


async def check_product(session, url):
    async with session.get(url) as response:
        content = await response.text()
        soup = BeautifulSoup(content, 'html.parser')
        if not soup.find("p", class_="out-of-stock"):
            return f"In stock {url}"


async def check_all_products(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.ensure_future(
                check_product(session, url))
            tasks.append(task)
        tasks_completed = await asyncio.gather(*tasks, return_exceptions=True)

        print(tasks_completed)

        for task_completed in tasks_completed:
            if task_completed is not None:
                msg = " \n".join(tasks_completed)
                gmail_send_email(msg)
                break


if __name__ == "__main__":
    urls = ["http://repfitness.com/strength-equipment/power-racks/pr-4000-power-rack",
            "https://www.repfitness.com/strength-equipment/power-racks/pr-5000-v2",
            "https://www.repfitness.com/strength-equipment/power-racks/rep-pr-1100",
            "https://www.repfitness.com/strength-equipment/power-racks/rep-power-rack",
            "https://www.repfitness.com/strength-equipment/strength-training/benches/rep-fb-5000-competition-flat-bench",
            "https://www.repfitness.com/strength-equipment/strength-training/benches/rep-ab3000-fid-adj-bench",
            "https://www.repfitness.com/strength-equipment/strength-training/benches/rep-ab-3100-fi-bench"
            ]
    start_time = time.time()
    asyncio.get_event_loop().run_until_complete(
        check_all_products(urls))
    duration = time.time() - start_time
    print(f"Checked {len(urls)} urls in {duration} seconds")

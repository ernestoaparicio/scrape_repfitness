import smtplib
import ssl

from bs4 import BeautifulSoup
import asyncio
import time
import aiohttp

from scrape_repfitness import config


def gmail_connect():
    port = 465
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(config.GMAIL_EMAIL, config.GMAIL_PW)
        return server


async def check_product(session, url, email_server):
    async with session.get(url) as response:
        content = await response.text()
        soup = BeautifulSoup(content, 'html.parser')
        if soup.find("p", class_="out-of-stock"):
            print(f"Out of stock {url}")
            email_server.sendmail(config.GMAIL_EMAIL,
                                  "ea@launchoc.com", f"Out of stock {url}")
        else:
            print(f"In stock!!! {url}")
            email_server.sendmail(config.GMAIL_EMAIL,
                                  "ea@launchoc.com", f"Out of stock {url}")


async def check_all_products(urls, email_server):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.ensure_future(
                check_product(session, url, email_server))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)


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
    email_server = gmail_connect()
    asyncio.get_event_loop().run_until_complete(
        check_all_products(urls, email_server))
    duration = time.time() - start_time
    print(f"Checked {len(urls)} urls in {duration} seconds")

from bs4 import BeautifulSoup
import asyncio
import time
import aiohttp


async def check_product(session, url):
    async with session.get(url) as response:
        content = await response.text()
        soup = BeautifulSoup(content, 'html.parser')
        if soup.find("p", class_="out-of-stock"):
            print(f"Out of stock {url}")
        else:
            print(f"In stock!!! {url}")


async def check_all_products(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.ensure_future(check_product(session, url))
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
    asyncio.get_event_loop().run_until_complete(check_all_products(urls))
    duration = time.time() - start_time
    print(f"Checked {len(urls)} urls in {duration} seconds")

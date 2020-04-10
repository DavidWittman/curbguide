#!/usr/bin/env python

import argparse
import asyncio

import aiohttp

from prettytable import PrettyTable

API_URL_BASE = "https://www.heb.com/commerce-api/v1"

HEADERS = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'Sec-Fetch-Dest': 'empty',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'DNT': '1',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://www.heb.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Referer': 'https://www.heb.com/',
    'Accept-Language': 'en-US,en;q=0.9',
}

async def get_timeslots(sem, store_id, days):
    params = dict(store_id=store_id, days=days, fulfillment_type="pickup")
    async with sem:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(API_URL_BASE + '/timeslot/timeslots', params=params) as resp:
                return await resp.json()

async def main(args):
    data = {
        'address': args.zip_code,
        'curbsideOnly': True,
        'radius': args.radius,
        'nextAvailableTimeslot': True
    }

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        async with session.post(API_URL_BASE + '/store/locator/address', json=data) as resp:
            if resp.status != 200:
                raise Exception(f"Bad response from store locator: {resp.status}")

            respj = await resp.json()

    # I kinda hate this lookup map but the distance isn't in the timeslot response
    # and I don't want to iterate through stores to look up the distance every time
    store_distances = {store['store']['id']: store['distance'] for store in respj['stores'][:args.stores]}

    pt = PrettyTable()
    pt.field_names = ["Store Name", "Distance (mi)", "Next Available Time"]
    pt.align["Store Name"] = "l"
    pt.sortby = "Distance (mi)"

    sem = asyncio.Semaphore(args.concurrency)

    futures = [
        asyncio.create_task(get_timeslots(sem, store_id, args.days))
        for store_id in store_distances
    ]
    done, _ = await asyncio.wait(futures)
    results = [r.result() for r in done]

    for r in done:
        result = r.result()
        store = result['pickupStore']

        if len(result['items']):
            next_pickup = result['items'][0]['timeslot']['startTime']
        else:
            next_pickup = "N/A"

        pt.add_row([
            store['name'],
            round(store_distances[store['id']], 2),
            next_pickup,
        ])

    print(pt)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--days', '-d', default=7, type=int, help="Number of days to search")
    p.add_argument('--radius', '-r', default=15, type=int, help="Max radius (distance) in miles")    
    p.add_argument('--stores', '-s', default=5, type=int, help="Maximum number of stores to check")
    p.add_argument('--concurrency', '-c', default=5, type=int)
    p.add_argument('zip_code')
    args = p.parse_args()

    asyncio.run(main(args))

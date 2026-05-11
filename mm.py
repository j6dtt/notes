"""
# Polling for new objects

The RFeye Mission Manager API does not provide a push-style interface for subscribing to new objects. However, it is
possible to use the *filtering* and *ordering* features to regularly poll the API for new objects.

The ``id`` property of objects is auto-incrementing, and guaranteed to increase for each newly-added object.
By keeping track of the latest ``id`` received from the API, it is possible to request only new objects.

This example demonstrates how to poll the server for new ``sweep.SweepData``.
"""
import asyncio
import json
import aiohttp
from pathlib import Path


# The URL of the RFeye Mission Manager API server.
SERVER_URL = "http://214.26.71.131"

# An active RFeye Mission Manager user.
AUTHENTICATION = aiohttp.BasicAuth(
    login="",
    password="",
)



# The number of seconds between API polls.
POLL_INTERVAL = 5

# File where results will be stored (overwritten each poll)
OUTPUT_FILE = Path("sweep_data.json")


def save_objects(objects):
    """Overwrite JSON file with latest objects."""
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(objects, f, indent=4)


async def main():
    # Keep track of the latest ``sweep.SweepData.id`` so we can request only new objects.
    latest_id = 3
    # Open a HTTP connection to the API server.
    async with aiohttp.ClientSession(auth=AUTHENTICATION) as session:
        while True:
            # Create a JSON query that requests only objects more recent than the latest ``id``.
            query = json.dumps({
                "id__gt": latest_id,
            })
            params = {
                "q": query,
                # Order by ``id`` ascending to receive new objects in the order they were added.
                "ordering": "id",
            }
            # Load a page of ``sweep.SweepData`` objects.
            print("Polling API for new objects...")
            async with await session.get(f"{SERVER_URL}/api/sweep/sweepdata/", params=params) as response:
                objects = await response.json()
            # Store the latest ``sweep.SweepData.id`` so we can request only new objects in the next poll.
            if objects:
                latest_id = objects[-1]["id"]
            save_objects(objects)

            # Print each new ``sweep.SweepData`` to the console.
            #for object in objects:
            #    print(f"Received: {object!r}")
            # Wait a few seconds before polling again.
            await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())

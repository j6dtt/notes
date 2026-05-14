"""
# Resolving relations

Many objects reference other objects. For example, ``sweep.SweepData`` has a ``node`` property that references
``api.Node``.

This example demonstrates how to load a page of ``sweep.SweepData`` and resolve the referenced ``nodes.Node``.
"""
import asyncio
import json
import aiohttp


# The URL of the RFeye Mission Manager API server.
SERVER_URL = "http://server"

# An active RFeye Mission Manager user.
AUTHENTICATION = aiohttp.BasicAuth(
    login="apiservice",
    password="",
)


async def main():
    # Open a HTTP connection to the API server.
    async with aiohttp.ClientSession(auth=AUTHENTICATION) as session:
        # Load a page of ``sweep.SweepData`` objects.
        async with await session.get(f"{SERVER_URL}/api/sweep/sweepdata/") as response:
            sweep_data_list = await response.json()
        # Find unique ``node`` properties on the ``sweep.SweepData`` objects.
        node_id_list = list(set(sweep_data["node"] for sweep_data in sweep_data_list if sweep_data["node"] is not None))
        # Load all ``api.Node`` objects referenced by the ``sweep.SweepData`` objects.
        node_query = json.dumps({
            "id__in": node_id_list,
        })
        async with await session.get(f"{SERVER_URL}/api/nodes/node/", params={"q": node_query}) as response:
            node_list = await response.json()
        # Create a mapping of ``api.Node.id`` to ``api.Node``.
        node_id_map = {node["id"]: node for node in node_list}
        # Print all received ``sweep.SweepData`` objects and the ``api.Node`` they reference.
        #for sweep_data in sweep_data_list:
        #    related_node = node_id_map[sweep_data['node']]
        #    print(f"Sweep data: {sweep_data!r}")
        #    print(f"Related node: {related_node}")

        # Save both datasets to pretty JSON files.
        with open("sweep_data.json", "w") as f:
            json.dump(sweep_data_list, f, indent=2)
        with open("nodes.json", "w") as f:
            json.dump(node_list, f, indent=2)



if __name__ == "__main__":
    asyncio.run(main())

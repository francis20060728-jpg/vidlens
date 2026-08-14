import asyncio
import os
from pathlib import Path
import tempfile

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from PIL import Image


async def main():
    with tempfile.TemporaryDirectory(prefix="vidlens-mcp-smoke-") as temporary:
        media = Path(temporary) / "target.png"
        ignored = Path(temporary) / "node_modules" / "ignored.png"
        ignored.parent.mkdir()
        image = Image.new("RGB", (320, 180), "white")
        image.save(media)
        image.save(ignored)
        await check_tools(media.parent, media)


async def check_tools(directory, media):
    params = StdioServerParameters(command="python", args=["vidlens/server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("tools=" + ",".join(tool.name for tool in tools.tools))
            look = next(tool for tool in tools.tools if tool.name == "look")
            print("look_has_frontend_trigger=" +
                  str("frontend" in look.description).lower())
            print("look_has_verify_hint=" +
                  str("verify_page" in look.description).lower())
            listing = await session.call_tool("list_media", {
                "directory": str(directory),
                "keyword": "target",
            })
            listing_text = listing.content[0].text
            print("list_contains_target=" +
                  str("target.png" in listing_text).lower())
            print("list_skips_node_modules=" +
                  str("ignored.png" not in listing_text).lower())
            result = await session.call_tool("find_and_look", {
                "directory": str(directory),
                "keyword": "target",
                "prompt_name": "verify_page",
                "prompt": "Expected result: a solid white 320x180 canvas with no text or graphics.",
            })
            print("find_file=" + str(media.samefile(
                Path(result.content[0].text.splitlines()[0].replace("File: ", ""))
            )).lower())
            print("verify_result=" + result.content[0].text.split(
                "File: " + str(media), 1)[1].strip())


if __name__ == "__main__":
    asyncio.run(main())

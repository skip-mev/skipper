import asyncio

from src import Bot


async def main():
    """ Main entry point to run bot."""
    bot: Bot = Bot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
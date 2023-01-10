import asyncio

from src.bot import Bot 


async def main():
    """ Main entry point to run bot."""
    bot: Bot = Bot()
    await bot.init()
    await bot.run() 


if __name__ == "__main__":
    asyncio.run(main())
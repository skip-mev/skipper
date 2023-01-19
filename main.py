import asyncio

from src.bot import Bot 


"""#############################################"""
"""@USER TODO: CHOOSE ENVIRONMENT VARIABLES PATH"""
ENV_FILE_PATH = "envs/juno.env"
#ENV_FILE_PATH = "envs/terra.env"
#ENV_FILE_PATH = "envs/evmos.env"
"""#############################################"""


async def main():
    """ Main entry point to run bot."""
    bot: Bot = Bot(env_file_path=ENV_FILE_PATH)
    await bot.init()
    await bot.run() 


if __name__ == "__main__":
    asyncio.run(main())
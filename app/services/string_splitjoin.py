# import asyncio
# from app.core.logging_config import logger

# async def split_and_join(string: str) -> str:
#     try:
#         await asyncio.sleep(0)
#         logger.debug(f"Splitting and joining the string: {string}")
#         result = "-".join(string.split())
#         logger.info(f"Result of split and join: {result}")
#         return result
#     except Exception as e:
#             logger.error(f" Error 3 : {e}")
#             raise

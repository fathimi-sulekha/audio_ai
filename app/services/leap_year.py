# import asyncio
# from app.core.logging_config import logger

# async def is_leap_year(year: int) -> str:
#     try:
#         await asyncio.sleep(0)
#         logger.debug(f"Checking if year {year} is a leap year.")
#         if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
#             logger.info(f"Year {year} is a leap year.")
#             return f"Year {year} is a leap year"
#         else:
#             logger.info(f"Year {year} is not a leap year.")
#             return f"Year {year} is not a leap year"
#     except Exception as e:
#             logger.error(f" Error 1 : {e}")
#             raise

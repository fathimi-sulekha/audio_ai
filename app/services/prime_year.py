# import asyncio
# from app.core.logging_config import logger

# async def is_prime(year: int) -> str:
#     try:
#         await asyncio.sleep(0)
#         logger.debug(f"Checking if year {year} is a prime number.")
#         if year <= 1:
#             logger.info(f"{year} is not a prime number.")
#             return f"{year} is not a prime number"
#         for i in range(2, int(year ** 0.5) + 1):
#             if year % i == 0:
#                 logger.info(f"{year} is not a prime number.")
#                 return f"{year} is not a prime number"
#         logger.info(f"{year} is a prime number.")
#         return f"{year} is a prime number"
#     except Exception as e:
#             logger.error(f" Error 2 : {e}")
#             raise
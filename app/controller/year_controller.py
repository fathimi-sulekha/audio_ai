# from app.services.leap_year import is_leap_year
# from app.services.prime_year import is_prime
# from app.core.config import YearRequest
# from app.utils.util import validate_year

# async def check_leap_year(request: YearRequest):
#     validate_year(request.year)
#     message = await is_leap_year(request.year)
#     return {"message": message}

# async def check_prime(request: YearRequest):
#     validate_year(request.year)
#     message = await is_prime(request.year)
#     return {"message": message}
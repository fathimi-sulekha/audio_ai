# from fastapi import FastAPI, APIRouter
# from app.controller.year_controller import is_leap_year, is_prime
# from app.controller.string_controller import split_and_join
# from app.dependencies.schema import YearRequest
 
# app = FastAPI()
# router = APIRouter()
 
# # Route for checking leap year
# @router.post("/check-leap-year/")
# async def check_leap_year(request: YearRequest):
#     return await is_leap_year(request.year)
 
# # Route for checking prime year
# @router.post("/check-prime/")
# async def check_prime(request: YearRequest):
#     return await is_prime(request.year)
 
# # Route for string split and join
# @router.post("/string-split-join/")
# async def string_split_join(request: YearRequest):
#     return await split_and_join(request.string)
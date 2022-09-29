from flight_loader import load_flights
from datetime import datetime


# I'm not going to enforce that everything is in the correct format right now because I'm lazy
# Just enter it correctly
# I might add it later
airport_a = input("Enter IATA code of airport 1: ")
airport_b = input("Enter IATA code of airport 2: ")
airports = [airport_a, airport_b]

from_date = input("Enter earliest departure date (yyyy-mm-dd): ")
from_date = datetime(*[int(x) for x in from_date.split('-')])

to_date = input("Enter latest return date (yyyy-mm-dd): ")
to_date = datetime(*[int(x) for x in to_date.split('-')])

duration_min = int(input("Enter the minimal number of days abroad: "))
duration_max = int(input("Enter the maximal number of days abroad: "))

print('\n')

load_flights(airports, from_date, to_date, duration_min, duration_max)
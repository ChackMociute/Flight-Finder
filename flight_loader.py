import pandas as pd
from time import sleep
from datetime import datetime, timedelta
from random import randint
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

CHROME_DRIVER_PATH = 'chromedriver.exe'
KAYAK = "https://www.kayak.com/explore/{}-anywhere/"


class FlightLoader:
    def __init__(self, url, airport=None, load_n=3, range=3):
        self.TIME = 0.5
        self.url = url
        self.airport = airport
        self.load_n = load_n
        self.range = range
    
    def get_flights(self):
        self.start_driver()
        return self.to_pandas([x.split('\n') for x in self.collect_flights() if x != ''])
    
    def increase_time(self):
        self.TIME += 0.25
    
    def start_driver(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)
        self.driver.get(self.url)
        
    def collect_flights(self):
        flights = []
        flights += self.add_flights()
        for _ in range(self.range):
            self.zoom_out()
            flights += self.add_flights()
        return flights
    
    def add_flights(self):
        self.load_more_destinations()
        sleep(self.TIME)
        return [x.text for x in self.driver.find_elements(By.XPATH, '//*[@class = "_iae _lc _ss"]')]
    
    def load_more_destinations(self):
        self.press_button('//*[substring(@id, string-length(@id) - string-length("-showMoreButton") +1) = "-showMoreButton"]', n_presses=self.load_n)
        
    def zoom_out(self):
        self.driver.find_element(By.TAG_NAME, "Body").send_keys(Keys.CONTROL + Keys.HOME)
        self.press_button('//*[substring(@id, string-length(@id) - string-length("-zoomControl-minusButton") +1) = "-zoomControl-minusButton"]')
    
    def press_button(self, button, n_presses=1):
        i = 0
        while i < n_presses:
            try:
                self.driver.find_element(By.XPATH, button).click()
                i += 1
                sleep(0.1)
            except Exception:
                self.driver.find_element(By.TAG_NAME, "Body").send_keys(Keys.CONTROL + 'r')
                sleep(0.5)
        
    def to_pandas(self, flight_list):
        flights = pd.DataFrame(flight_list, columns=['City', 'Price', 'Country', 'Date']).loc[:, ['Country', 'City', 'Price', 'Date']]
        flights['Price'] = flights['Price'].map(lambda x: int(x[6:]))
        flights[['Departure date', 'Arrival date']] = flights['Date'].str.split('-', expand=True)
        flights.drop('Date', axis=1, inplace=True)
        if self.airport is not None: flights.rename({'Price': f"Price from {self.airport}"}, inplace=True, axis=1)
        return flights.drop_duplicates()



def load_flights(airports, from_date, to_date, min_duration, max_duration, ipy=False, n_results=20):
    flights = sort_and_format(get_flights_from_all_airports(airports, get_dates(from_date, to_date, min_duration, max_duration)), airports)
    if ipy: display(flights.iloc[:n_results])
    else: print(flights.iloc[:n_results])

def get_dates(from_date, to_date, min_duration, max_duration):
    return [
        (from_date + timedelta(i), from_date + timedelta(i) + delta)
        for i in range((to_date - from_date).days)
        for delta in [timedelta(i) for i in range(min_duration, max_duration+1)]
        if from_date + timedelta(i) + delta <= to_date
    ]

def get_flights_from_all_airports(airports, dates):
    all_flights = []
    for i, airport in enumerate(airports):
        print(f"Step {i+1}/{len(airports)}")
        all_flights.append(get_flights_from_airport(airport, dates))
    return all_flights

def get_flights_from_airport(airport, dates):
    flights = []
    for s_date, e_date in tqdm(dates):
        flights.append(flights_from_loader(FlightLoader(get_url(airport, s_date, e_date), airport)))
        sleep(randint(1, 3))
    return pd.concat(flights).drop_duplicates()

def get_url(airport, start_date, end_date):
    return KAYAK.format(airport) + start_date.strftime("%Y%m%d") + ',' + end_date.strftime("%Y%m%d")

def flights_from_loader(loader):
    flights = None
    while True:
        try: flights = loader.get_flights()
        except Exception: loader.increase_time()
        else: break
    del(loader)
    return flights

def sort_and_format(flights, airports):
    flight_list = flights[0].rename({'Price': f"Price from {airports[0]}"}, axis=1).merge(
        flights[1].rename({'Price': f"Price from {airports[1]}"}, axis=1))
    flight_list['Combined price'] = flight_list[f"Price from {airports[0]}"] + flight_list[f"Price from {airports[1]}"]
    return flight_list.sort_values('Combined price').iloc[:, [0, 1, 2, 5, 6, 3, 4]]
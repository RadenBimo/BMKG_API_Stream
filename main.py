from Iklim import Weather
from datetime import datetime
import time
from requests.exceptions import ConnectionError

def main():
    url="https://ibnux.github.io/BMKG-importer/cuaca/wilayah.json"
    weather= Weather(url)
    weather.get_wilayah_json()
    weather.filter_daerah(["DKIJakarta",
                            "DIYogyakarta",
                            "JawaBarat",
                            "Bali",
                            "KalimantanSelatan",
                            "DKIJakarta"])
    weather.filter_unique_by("id")
    weather.pull_all_weather_json(keywords=['jamCuaca','kodeCuaca','cuaca'])


if __name__ == '__main__':
  dates=[datetime(2023,3,30,23,55,00),datetime(2023,3,31,23,55,00)]
  for date in dates:
    z= False
    count= 0
    while z==False:
      if datetime.now()>=date:
        try:
          main()
          z=True
          count= 0
        except ConnectionError as err:
          if count>2:
            raise SystemExit(err)
          print(count)
          print(f'Something is error, will try again in the next 1 hour')
          time.sleep(1)
          count+=1
      else:
        print(f'not time yet, pls wait until {date}')
        time.sleep(3600*2) 
import requests
import json
import pandas as pd
import os
from datetime import datetime


class Wilayah() :
    
    def __init__(self,url: str):
        self.url_wilayah= url

    def get_json(self,key: str):
        url= f"https://ibnux.github.io/BMKG-importer/cuaca/{key}.json"
        response= requests.get(url)
        if response.status_code == 200: 
            pass
        else:
            raise Exception("Sorry, connection failed. try checking your url or internet connection ")        
        return(response.json())

    def get_wilayah_json(self):
        self.wilayah_json= self.get_json("wilayah")
    
    def filter_by_col(self,json_file,col_name: str,by: list):
        return(list(filter(lambda x: x[col_name] in by,json_file)))
        
    def filter_daerah(self,by):
        self.filtered_json= self.filter_by_col(self.wilayah_json,'propinsi',by)

    def filter_unique_by(self,col: str):
        returnValue = []
        uniqueId = []
        for i,_ in enumerate(self.filtered_json):  
            if(self.filtered_json[i][col] not in uniqueId):
                uniqueId.append(self.filtered_json[i][col]) 
                returnValue.append(self.filtered_json[i])
        self.filtered_json= returnValue

class Weather(Wilayah):
    def __init__(self,url: str):
        super().__init__(url)
        self.wilayah_json= self.get_wilayah_json()
    
    def transform_to_datetime(self,weather_json):
        for i in weather_json:
            i['jamCuaca_trans']=datetime.strptime(i['jamCuaca'], "%Y-%m-%d %H:%M:%S")
            i['date']=i['jamCuaca_trans'].date()
        return(weather_json)
    
    def select_col(self,json_file,keywords):
        list_=[]
        for i in json_file:
            dict_={}
            for keyword in keywords:
                dict_[keyword]= i[keyword]
            list_.append(dict_)
        return(list_)

    def save_to_folder(self,propinsi: str,kota: str, path: str,date: int,data):
        file_name = str(date).replace("-", "")
        path=f"{path}\\{file_name}"
        with open(f"{path}.json", "w") as final:
            json.dump(data, final,default=str)
        
    def create_path(self,propinsi: str,kota: str,data,path: str):
        for obj in ['weather',propinsi,kota]:
            if obj not in os.listdir(path):
                print(f'no folder named {obj} at {path} creating one')
                os.makedirs(f"{path}\\{obj}")    
            path= f'{path}\\{obj}'            
    
    def pull_all_weather_json(self,keywords=None,path=None):
        count_city={x['kota'] : 0 for x in self.filtered_json}
        if path==None:
            oriPath= os.getcwd()
        
        print('start pulling data to',oriPath)
        for i,x in enumerate(self.filtered_json):
            propinsi=x['propinsi']
            kota=x['kota']
            count_city[kota]+=1
            
            weather_json= self.get_json(x['id'])
            weather_json= self.transform_to_datetime(weather_json)            
            
            self.create_path(propinsi, kota, weather_json, oriPath)
            filePath= f"{oriPath}\\weather\\{propinsi}\\{kota}"
            list_dir= os.listdir(filePath)
            
            if len(list_dir)>0:
                last_date= max([datetime.strptime(z, "%Y%m%d.json").date() for z in list_dir])
                weather_json= list(filter(lambda x: x['date'] >= last_date,weather_json))
            
            uniqueDate=set([z['date'] for z in weather_json])
            print(kota)

            for date in uniqueDate:
                json_=self.filter_by_col(weather_json,'date',[date])
                if keywords!=None:
                    self.select_col(json_, keywords)
                    json_=self.select_col(json_, keywords)
                
                self.save_to_folder(propinsi, kota, filePath, date, json_)
        print('Data pull successed')
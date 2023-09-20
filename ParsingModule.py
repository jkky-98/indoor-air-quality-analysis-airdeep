#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from datetime import datetime
import requests

class DataParse:
    def __init__(self, url="https://api.airdeep.co.kr/api/report/ajousw@ajou.ac.kr/daily-data/"):
        self.url = url
        self.validation = False
        self.df_1 = None
        self.df_2 = None
        self.df_3 = None
     
    def request_json(self, date):
        self.date = date
        print(self.url+self.date)
        req_url = self.url + self.date
        response = requests.get(req_url)
        data = response.json()
        df_tmp = pd.DataFrame(data)
        self.df_tmp = df_tmp
        if len(self.df_tmp) < 5:
            print("Unable to parse, Check the date")
            self.df_1 = None
            self.df_2 = None
            self.df_3 = None
        else:
            self.df_1 = df_tmp[df_tmp['device_name'] == '교수님 오피스']
            self.df_2 = df_tmp[df_tmp['device_name'] == '교학팀 사무실']
            self.df_3 = df_tmp[df_tmp['device_name'] == '송재관 실험실']
            columns_to_exclude = ['no']
            self.df_1 = self.df_1.drop(columns=columns_to_exclude).reset_index(drop=True)
            self.df_2 = self.df_2.drop(columns=columns_to_exclude).reset_index(drop=True)
            self.df_3 = self.df_3.drop(columns=columns_to_exclude).reset_index(drop=True)
            self.validation = True
    
    def __call__(self,date):
        self.request_json(date)
        return self.df_1, self.df_2, self.df_3
        


# In[2]:


class MakeRangeData(DataParse):
    def __init__(self,start,end):
        super().__init__(url="https://api.airdeep.co.kr/api/report/ajousw@ajou.ac.kr/daily-data/")
        self.start = start
        self.end = end
        self.range_val = False
        self.range_validation()
        self.date_range()
        self.stack()
        self.convert_to_minute_average()
        
    def range_validation(self):
        self.request_json(self.start)
        val = True
        if self.validation == True:
            pass
        else:
            print('ERROR : startdate is inappropriate')
            val = False
        
        self.request_json(self.end)
        if self.validation == True:
            pass
        else:
            print('ERROR : enddate is inappropriate')
            val = False
            
        if val == True:
            self.range_val = True
            print('-----parsingOK------')
        
            
    def date_range(self):
        start = datetime.strptime(self.start, "%Y-%m-%d")
        end = datetime.strptime(self.end, "%Y-%m-%d")
        dates = [date.strftime("%Y-%m-%d") for date in pd.date_range(start, periods=(end-start).days+1)]
        self.dates = dates
    
    def stack(self):
        if self.range_val == True:
            df_1 = pd.DataFrame()
            df_2 = pd.DataFrame()
            df_3 = pd.DataFrame()
            for i in self.dates:
                self.request_json(i)

                df_1_tmp = self.df_1
                df_2_tmp = self.df_2
                df_3_tmp = self.df_3

                df_1 = pd.concat([df_1,df_1_tmp])
                df_2 = pd.concat([df_2,df_2_tmp])
                df_3 = pd.concat([df_3,df_3_tmp])
            df_1 = df_1.reset_index(drop=True)
            df_2 = df_2.reset_index(drop=True)
            df_3 = df_3.reset_index(drop=True)
            
            self.df_1 = df_1.drop('device_name', axis=1)
            self.df_2 = df_2.drop('device_name', axis=1)
            self.df_3 = df_3.drop('device_name', axis=1)
            
            self.df_1['check_date'] = pd.to_datetime(self.df_1['check_date'])
            self.df_2['check_date'] = pd.to_datetime(self.df_2['check_date'])
            self.df_3['check_date'] = pd.to_datetime(self.df_3['check_date'])
            
            object_columns_1 = self.df_1.select_dtypes(include='object').columns
            self.df_1[object_columns_1] = self.df_1[object_columns_1].astype('float32')
            object_columns_2 = self.df_2.select_dtypes(include='object').columns
            self.df_2[object_columns_2] = self.df_2[object_columns_2].astype('float32')
            object_columns_3 = self.df_3.select_dtypes(include='object').columns
            self.df_3[object_columns_3] = self.df_3[object_columns_3].astype('float32')
            
            # df_1 : 교수님 오피스
            # df_2 : 교학팀 사무실
            # df_3 : 송재관 실험실
        else:
            print("ERROR : validation_error")
            
    def convert_to_minute_average(self):

        value_columns = list(self.df_1.columns[:-1])
        
        self.df_1_1m = self.df_1
        self.df_2_1m = self.df_2
        self.df_3_1m = self.df_3
        
        # 분 단위의 평균 계산
        self.df_1_1m['Minute'] = self.df_1_1m['check_date'].dt.floor('min')

        # 각 피처의 분 단위 평균 계산
        average_columns = []
        for value_col in value_columns:
            average_col = f'{value_col}_Average'
            self.df_1_1m[average_col] = self.df_1_1m.groupby('Minute')[value_col].transform('mean')
            average_columns.append(average_col)

        # 중복되는 행 제거
        self.df_1_1m = self.df_1_1m.drop_duplicates(subset=['Minute'])

        #df_2
        self.df_2_1m['Minute'] = self.df_2_1m['check_date'].dt.floor('min')
        average_columns = []
        for value_col in value_columns:
            average_col = f'{value_col}_Average'
            self.df_2_1m[average_col] = self.df_2_1m.groupby('Minute')[value_col].transform('mean')
            average_columns.append(average_col)
        self.df_2_1m = self.df_2_1m.drop_duplicates(subset=['Minute'])

        #df_3
        self.df_3_1m['Minute'] = self.df_3_1m['check_date'].dt.floor('min')
        average_columns = []
        for value_col in value_columns:
            average_col = f'{value_col}_Average'
            self.df_3_1m[average_col] = self.df_3_1m.groupby('Minute')[value_col].transform('mean')
            average_columns.append(average_col)
        self.df_3_1m = self.df_3_1m.drop_duplicates(subset=['Minute'])
        
        self.df_1_1m = self.df_1_1m.drop(['pm10', 'pm2.5', 'co2', 'tvoc'], axis=1)
        self.df_2_1m = self.df_2_1m.drop(['pm10', 'pm2.5', 'co2', 'tvoc'], axis=1)
        self.df_3_1m = self.df_3_1m.drop(['pm10', 'pm2.5', 'co2', 'tvoc'], axis=1)

        ## 빈데이터 보정(시간 개수 맞추기)
        self.df_1_1m = self.df_1_1m.set_index('Minute')
        self.df_1_1m = self.df_1_1m.resample('1T').asfreq().reset_index().drop('check_date', axis=1)
        self.df_2_1m = self.df_2_1m.set_index('Minute')
        self.df_2_1m = self.df_2_1m.resample('1T').asfreq().reset_index().drop('check_date', axis=1)
        self.df_3_1m = self.df_3_1m.set_index('Minute')
        self.df_3_1m = self.df_3_1m.resample('1T').asfreq().reset_index().drop('check_date', axis=1)



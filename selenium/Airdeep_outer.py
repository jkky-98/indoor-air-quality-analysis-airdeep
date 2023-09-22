import get_weather as gw
import pandas as pd
import os

A = gw.KMA(time=60 * 3)
# A=KMA(time=60*3)
A.setting()
A.login_loof()

start_day = "2023-09-01"
end_day = "2023-09-01"
data_type = "Asos"  # Asos,Aws
time_type = "분 자료"
down_dir = "C:\workSpace\Python\selenium\data"
over_write = False

start_day = pd.Timestamp(start_day)
end_day = pd.Timestamp(end_day)

date_list = pd.date_range(start_day, end_day, freq="d")

# start_day = pd.Timestamp(start_day)
# download_day=start_day
# query=download_day.strftime('%Y%m%d')
# move_file_name=f'{data_type}_{query}_{time_type}.csv'
# new_path = f'{down_dir}/{move_file_name}'
# A.download(data_type,download_day,new_path)

down_error_list = A.download_range(
    date_list,
    data_type="Asos",
    kma_id="leeja20001@ajou.ac.kr",
    kma_pass="na110200034*",
    n_download_login_loof=20,
    time_type="분 자료",
    down_dir="C:\workSpace\Python\selenium\data",
)

# query=download_day.strftime('%Y%m%d')
set(A.date_to_filename(date_list, down_dir, data_type, time_type)) - set(
    os.listdir(down_dir)
)
A.quit()

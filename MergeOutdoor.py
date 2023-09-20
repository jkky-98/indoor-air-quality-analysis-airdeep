######### Initial Setting ###########

######## 실행 경로에 폴더 두개가 필요합니다. ########


import os
import pandas as pd

def CheckFolder():
    current_directory = os.getcwd()

    # 현재 경로에 두 개의 폴더가 존재하는지 확인
    folder1_exists = os.path.exists(os.path.join(current_directory, 'out_door_air_data'))
    folder2_exists = os.path.exists(os.path.join(current_directory, 'out_door_air_data_update'))

    # 결과 출력
    if folder1_exists and folder2_exists:
        print("현재 경로:", current_directory)
        print("out_door_air_data:", folder1_exists)
        print("out_door_air_data_update:", folder2_exists)
    else:
        print('폴더 구성 여부를 재확인 해주세요.')

def MergeOutdoorData():
    folder_path = './out_door_air_data_update/'
    out_path = './out_door_air_data/'
    # 모든 CSV 파일을 저장할 빈 DataFrame 생성
    combined_data = pd.DataFrame()

    # 폴더 내의 모든 파일 목록을 가져와 처리
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)

            # CSV 파일을 읽어와 DataFrame에 추가
            df = pd.read_csv(file_path, encoding='euc-kr')
            combined_data = pd.concat([combined_data, df], ignore_index=True)

    # 날짜 열을 기준으로 정렬 (날짜 열 이름을 '날짜'로 가정)
    combined_data['일시'] = pd.to_datetime(combined_data['일시'])
    combined_data = combined_data.sort_values(by='일시')

    # 데이터 누락시 보간
    # 데이터프레임의 날짜/시간 열을 인덱스로 설정합니다.
    combined_data.set_index('일시', inplace=True)

    # 1분 간격으로 리샘플링합니다. 이때 누락된 데이터는 NaN으로 표시됩니다.
    combined_data = combined_data.resample('1T').mean()

    # 보간을 사용하여 누락된 데이터를 채웁니다. 여기서 method에는 적절한 보간 방법을 선택합니다.
    # 예: linear, time, nearest, 등
    combined_data = combined_data.interpolate(method='linear')
    combined_data.reset_index(inplace=True)
    
    # 데이터프레임에서 '일시' 열의 차이를 계산하여 1분 간격인지 확인
    time_diff = combined_data['일시'].diff()
    is_one_minute_interval = all(time_diff[1:] == pd.Timedelta(minutes=1))

    # 데이터프레임에서 null 값이 있는지 확인
    has_null_values = combined_data.isnull().values.any()

    if is_one_minute_interval:
        print("모든 행이 1분 간격으로 존재합니다.")
    else:
        print("행들 사이에 1분 간격이 아닌 경우가 있습니다.")
        non_one_minute_intervals = combined_data[time_diff != pd.Timedelta(minutes=1)]

        if non_one_minute_intervals.empty:
            print("모든 행이 1분 간격으로 존재합니다.")
        else:
            print("1분 간격이 아닌 부분:")
            print(non_one_minute_intervals)

    if not has_null_values:
        print("데이터프레임에 null 값이 없습니다.")
    else:
        print("데이터프레임에 null 값이 있습니다.")

    # 결과를 원하는 파일로 저장 (예: merged_data.csv)
    combined_data.to_csv(out_path + 'merged_data.csv', index=False, encoding='euc-kr')
    
    return combined_data



def main():
    CheckFolder()
    MergeOutdoorData()

if __name__ == "__main__":
    main()
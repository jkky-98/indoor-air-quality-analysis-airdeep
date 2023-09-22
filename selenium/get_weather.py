from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

import os
import re
import warnings
import pandas as pd
import shutil
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import threading

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


class KMA:
    def __init__(
        self,
        download_path=r"C:\workSpace\Python\selenium\data",
        options=Options(),
        time=5,
    ):
        self.down_dir = download_path
        self.options = options
        options.add_experimental_option(
            "prefs", {"download.default_directory": self.down_dir}
        )
        self.time = time
        # self.thread=threading.Timer(time,self.auto_login)

    def setting(self):
        try:
            self.driver.quit()
        except:
            1
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.action = ActionChains(self.driver)
        self.driver.get("https://data.kma.go.kr/cmmn/main.do")

    def login(self, kma_id="leeja20001@ajou.ac.kr", kma_pass="na110200034*"):
        try:
            self.driver.maximize_window()
            self.driver.find_element(By.CSS_SELECTOR, "a#loginBtn").click()
            self.driver.find_element(By.CSS_SELECTOR, "input#loginId.inp").send_keys(
                kma_id
            )
            self.driver.find_element(By.CSS_SELECTOR, "input#passwordNo.inp").send_keys(
                kma_pass
            )
            self.driver.find_element(
                By.CSS_SELECTOR, "button#loginbtn.btn_login"
            ).click()
            return True
        except:
            print("이미 로그인 중입니다.")
            return False

    def logout(self):
        try:
            self.driver.maximize_window()
            self.driver.find_element(By.CSS_SELECTOR, "a#logoutBtn").click()
            return True
        except:
            print("이미 로그아웃 되어있습니다.")
            return False

    def login_loof(self, kma_id="leeja20001@ajou.ac.kr", kma_pass="na110200034*"):
        self.logout()
        self.login(kma_id, kma_pass)

    def close(self):
        self.driver.close()

    def quit(self):
        self.driver.quit()

    def download(self, data_type, download_day, new_path, query, time_type):
        """사이트 이동"""
        try:
            if data_type in ["Aws", "Asos", "Agr"]:  # Asos,Aws,Agr
                self.driver.get(
                    f"https://data.kma.go.kr/data/grnd/select{data_type}RltmList.do?pgmNo="
                )
            elif data_type in [
                "FargoBuoy",
                "Buoy",
                "Rh",
            ]:  # data_type='FargoBuoy'#Buoy,lb(Rh),FargoBuoy
                self.driver.get(
                    f"https://data.kma.go.kr/data/sea/select{data_type}RltmList.do?pgmNo="
                )
            else:
                raise
        except:
            print("Asos, Aws, Agr, FargoBuoy, Buoy, Rh")
        sleep(0.5)

        """ 시간 타입 """
        Select(self.driver.find_element(By.ID, "dataFormCd")).select_by_visible_text(
            time_type
        )
        sleep(0.5)

        """ 변수 선택 """
        self.driver.find_element(By.ID, "ztree1_3_check").click()  # 기온
        sleep(0.5)
        self.driver.find_element(By.ID, "ztree1_6_check").click()  # 누적강수량
        sleep(0.5)
        self.driver.find_element(By.ID, "ztree1_8_check").click()  # 풍향
        sleep(0.5)
        self.driver.find_element(By.ID, "ztree1_10_check").click()  # 풍속
        sleep(0.5)
        self.driver.find_element(By.ID, "ztree1_13_check").click()  # 습도
        sleep(0.5)

        """ 전체 지점 선택 """
        self.driver.find_element(By.ID, "ztree_18_switch").click()  # 경기도
        sleep(0.5)
        self.driver.find_element(By.ID, "ztree_20_check").click()  # 수원
        sleep(0.5)

        # if self.driver.find_element_by_css_selector('a#ztree_1_check').get_attribute('title')=='전체선택 안됨':
        #     self.driver.find_element_by_css_selector('a#ztree_1_check').click()

        """ 시작 기간 설정 """
        self.driver.execute_script(
            'document.querySelector("input[id=startDt_d]").removeAttribute("readonly")'
        )
        sleep(0.5)
        self.driver.execute_script(
            f'document.querySelector("input[id=startDt_d]").value = "{query}"'
        )
        sleep(0.5)

        """ 끝 기간 설정 """
        self.driver.execute_script(
            'document.querySelector("input[id=endDt_d]").removeAttribute("readonly")'
        )
        sleep(0.5)
        self.driver.execute_script(
            f'document.querySelector("input[id=endDt_d]").value = "{query}"'
        )
        sleep(0.5)

        # if time_type=='시간 자료':
        #     self.driver.find_element_by_xpath(f'//select[@name="startHh"]/option[@value="{st_time}"]').click()
        #     self.driver.find_element_by_xpath(f'//select[@name="endHh"]/option[@value="{ed_time}"]').click()

        """ 조회 """
        # //*[@id="dsForm"]/div[3]/button
        self.driver.execute_script("goSearch();")
        sleep(30)
        if data_type == "FargoBuoy":
            pd.read_html(
                self.driver.find_element(By.CSS_SELECTOR, "table.tbl")[0].get_attribute(
                    "outerHTML"
                )
            )
        else:
            pd.read_html(
                self.driver.find_element(By.CSS_SELECTOR, "table.tbl")[1].get_attribute(
                    "outerHTML"
                )
            )

        """ 다운로드 """
        # wrap_content > div.wrap_itm.area_data > div.hd_itm > div > a:nth-child(1)
        self.driver.execute_script("downloadRltmCSVData();")
        # sleep(15)

        "원본 코드"
        # try:
        #     self.driver.find_element(
        #         By.CSS_SELECTOR, "div#divPopupTemp.back_layer"
        #     ).get_attribute("id")
        #     self.driver.find_element(By.ID, "reqstPurposeCd7").click()
        # except:
        #     1

        try:
            dwld = self.driver.find_element(
                By.XPATH,
                "/html/body/div[2]/div[1]/div/div[2]/div[3]/div[4]/div[1]/div/a[1]",
            )
            print(dwld)

            self.driver.execute_script("arguments[0].click();", dwld[1])
            self.action.send_keys(Keys.RETURN)

            # self.driver.find_element(By.ID, "reqstPurposeCd7").click()
        except:
            1
            print("fail click CSV")

        self.driver.execute_script("fnRltmRequest();")
        sleep(0.5)
        # A.quit()

        before_files = [
            i for i in os.listdir(self.down_dir) if re.compile(".csv").findall(i)
        ]

        before = len(before_files)
        sleep(5)
        after_files = [
            i for i in os.listdir(self.down_dir) if re.compile(".csv").findall(i)
        ]
        after = len(after_files)
        if before != after:
            down_file = list(set(after_files) - set(before_files))[0]
            shutil.move(f"{self.down_dir}/{down_file}", new_path)

    def download_range(
        self,
        date_list,
        data_type,
        kma_id,
        kma_pass,
        n_download_login_loof,
        time_type,
        down_dir,
        over_write=False,
    ):
        _n_download_login_loof = 0
        down_error = list()
        old_down_dir = os.listdir(down_dir)

        for download_day in date_list:
            _n_download_login_loof = _n_download_login_loof + 1
            if _n_download_login_loof % n_download_login_loof == 1:
                self.login_loof(kma_id, kma_pass)
                sleep(3)
            query = download_day.strftime("%Y%m%d")
            move_file_name = f"{data_type}_{query}_{time_type}.csv"
            new_path = f"{down_dir}/{move_file_name}"
            n_download_login_loof = n_download_login_loof + 1

            if over_write == False:
                if not move_file_name in old_down_dir:
                    try:
                        print(download_day)
                        self.download(
                            data_type, download_day, new_path, query, time_type
                        )
                    except:
                        down_error.append(download_day)
            else:
                try:
                    print(download_day)
                    self.download(data_type, download_day, new_path, query, time_type)
                except:
                    down_error.append(download_day)
        return down_error

    def date_to_filename(self, date_list, down_dir, data_type, time_type):
        return [
            f'{data_type}_{i.strftime("%Y%m%d")}_{time_type}.csv' for i in date_list
        ]

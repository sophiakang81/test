import re
import numpy as np
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup


def get_area(area_nm):
    df_areacode = pd.read_csv('https://goo.gl/tM6r3v', sep='\t', dtype={'법정동코드': str, '법정동명': str})
    df_areacode = df_areacode[df_areacode['폐지여부'] == '존재']
    df_areacode = df_areacode[['법정동코드', '법정동명']]

    mydict = dict(zip(df_areacode['법정동명'], df_areacode['법정동코드']))

#서울특별시의 법정동명과 법정동코드 가져옴
    seoul_list = {}
    for key, val in mydict.items():
        a = key.split(' ')
        a = a[0]
        if a == '서울특별시':
            seoul_list[key] = val

#area_nm에 해당하는 법정코드와 그 법정명을 가져옴
    final = {}
    for key, val in seoul_list.items():
        if area_nm in key:
            final[key] = val    
#해당 area_nm에 해당되는 법정코드를 리스트화함       
    area_code_list=list(final.values())
#리스트를 함수밖으로 송출함      
    return area_code_list


def get_naver_realasset(area_code,page=1):         
    
    url = 'http://land.naver.com/article/articleList.nhn?' \
          + 'rletTypeCd=A01&tradeTypeCd=A1&hscpTypeCd=A01%3AA03%3AA04' \
          + '&cortarNo=' + area_code \
          + '&page=' + str(page)
    
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
        
    table = soup.find('table')
    trs = table.tbody.find_all('tr')
    if '등록된 매물이 없습니다' in trs[0].text:
        return pd.DataFrame()
        
         # 거래, 종류, 확인일자, 매물명, 매물명, 면적(㎡), 층, 매물가(만원), 연락처
    value_list = []
    for tr in trs[::2]:
        tds = tr.find_all('td')
        cols = [' '.join(td.text.strip().split()) for td in tds]
    
        if '_thumb_image' not in tds[3]['class']:  # 현장확인 날짜와 이미지가 없는 행
            cols.insert(3, '')
        
            
        거래 = cols[0]
        종류 = cols[1]
        확인일자 = datetime.strptime(cols[2], '%y.%m.%d.')
        현장확인 = cols[3]
        매물명 = cols[4]
        매물명 = 매물명.split(' ')
        for val in 매물명:
            if val == '집주인':
                pass
            elif val=='네이버부동산에서':
                pass
            elif val=='보기':
                pass
            else: 매물명=val
        면적 = cols[5]
        공급면적 = re.findall('공급면적(.*?)㎡', 면적)[0].replace(',', '')
        전용면적 = re.findall('전용면적(.*?)㎡', 면적)[0].replace(',', '')
        공급면적 = float(공급면적)
        전용면적 = float(전용면적)
        층 = cols[6]
        매물가 = int(cols[7].replace(',', ''))
        연락처 = cols[8]
    
        value_list.append([종류, 거래, 매물명, 공급면적, 층, 매물가])
    cols = ['종류','거래', '매물명', '공급면적',  '층', '매물가']
    df = pd.DataFrame(value_list, columns=cols)
    return df

#조건을 넣는 함수
def input_what_you_want():
    area_nm=input("지역명: ")
    deal_type=input("거래조건: ")
    home_type=input("주택종류: ")
    home_cost=input("가격: ")
    home_extent=input("면적: ")
    area_code_list=get_area(area_nm)  
    
    real_asset = pd.DataFrame()
    for i in area_code_list:
        for j in range(1,3):
            df_tmp=get_naver_realasset(i,j)
            if len(df_tmp)<=0:
                break
            real_asset = real_asset.append(df_tmp,ignore_index=True)
    
    cond=real_asset[(real_asset['거래']==deal_type)&(real_asset['종류']==home_type)&((real_asset['매물가']>=home_cost-5000)|(real_asset['매물가']<=home_cost+5000)) & ((real_asset['공급면적']>=home_extent-30)|(real_asset['공급면적']<=home_extent+30))]     
    
    return cond
      
    
#함수의 실행
a=input_what_you_want()
pirnt(a)



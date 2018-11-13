from selenium import webdriver
import time
import requests,json
import os
from urllib.request import urlretrieve
import tkinter as tk
import pandas as pd
from bs4 import BeautifulSoup

class GUI:
    def __init__(self):
        self.tk=tk.Tk()
        tk.Label(self.tk,text='Forvo API Key',borderwidth=10).grid(row=1,column=1)
        
        tk.Label(self.tk,text='Language',borderwidth=10).grid(row=2,column=1)

        self.e1=tk.Entry(self.tk,borderwidth=5,relief="sunken")
        self.e1.grid(row=1,column=2)
        self.e3=tk.Entry(self.tk,borderwidth=5,relief="sunken")
        self.e3.grid(row=2,column=2)

        
        
        tk.Button(self.tk,text='Do IT',command=self.execute,borderwidth=5).grid(row=4,columnspan=6)
        
        self.tk.mainloop()

    def language(self):
        res=requests.get('https://forvo.com/languages-codes/').text
        df_list = pd.read_html(res)
        df = df_list[-1]
        df.columns=df.iloc[0]
        df=df[1:]
        a=df['ISO code'].tolist()
        b=df['English name'].tolist()
        c={b[x].lower():a[x]for x in range(0,len(a))}
        return c
    
    def search_audio(self,res,num):
        sp=BeautifulSoup(res,'lxml')
        part=sp.find('div',{'id':num})
        get=part.find_all('th')
        flag=False
        count=1
        for a in get:
            rw=(a.text)
            
            if 'Audio' in rw:
                flag=True
                break
            count+=1

        if flag:
            return count
        
        
        
        
    def execute(self):
        
        
        shw='''
        2 OPtions are there

        1. To start from fresh that means
            You have to go till edit page only .
            Press 1 for this

        2 . To start from login you have to only login.
            Press 0 for this

        '''
        print (shw)
        
        driver=webdriver.Chrome()
        driver.get('https://www.memrise.com/login/')
        #driver.find_element_by_xpath('//*[@id="login"]/div[4]/input').send_keys('')
        #driver.find_element_by_xpath('//*[@id="login"]/div[5]/input').send_keys('')
        #driver.find_element_by_xpath('//*[@id="login"]/input[3]').click()
        time.sleep(3)

        
        rec=input('Enter 1 to start it fresh and 0 to start it from previous position:')
        
        lang=self.language()[self.e3.get()]
        if rec=='0':
            track=open('track.txt').readlines()[0].rstrip('\n').split(',') #

            temp_id=track[0].split('#')[-1]#
            
            driver.get(track[0].split('#')[0])
            
        html=driver.page_source
        soup=BeautifulSoup(html,'lxml')
        pg=soup.find_all('div',{'class':'level collapsed'})
        all_ids=[a['id'] for a in pg]
        if rec=='0':
            pos=all_ids.index(temp_id)#
            all_ids=all_ids[pos:]#
        mn=driver.current_url
        

        
        for one in all_ids:
            cur_url=mn+'#'+one
            driver.get(cur_url)
            time.sleep(3)

            ids=cur_url.split('#')[-1]
            cl=self.search_audio(driver.page_source,one)
            if not cl:
                cl=4
            a=1
            if rec=='0':
                if one==temp_id:#
                    a=int(track[1])+1
                    
            while True:
                
                try:
                    value=driver.find_element_by_xpath('//*[@id="%s"]/div[3]/table/tbody[1]/tr[%s]/td[2]/div/div'%(ids,a)).text
                except:
                    print ('Done.. Uploading')
                    break
                
                lk='https://apifree.forvo.com/key/%s/format/json/action/word-pronunciations/word/%s/language/%s'%(self.e1.get(),value,lang)
                res=json.loads(requests.get(lk).text)
                url=res['items']
                if url:
                    
                    url=url[0]['pathmp3']
                    
                    vl=value+'.mp3'
                    print ('Downloading.. %s'%vl)
                    urlretrieve(url,vl)
                    print ('Downloaded.. %s'%vl)
                    time.sleep(3)

                    
                    x='//*[@id="%s"]/div[3]/table/tbody[1]/tr[%s]/td[%s]/div/div[1]/input'%(ids,a,cl)
                    
                    driver.find_element_by_xpath(x).send_keys(os.getcwd()+'/'+vl)
                    print ('Uploaded.. %s'%vl)
                    #############################################
                    track=open('track.txt','w')
                    to_save='%s,%s'%(cur_url,a)
                    track.write(to_save)
                    track.close()
                    #############################################
                else:
                    print('Skipped... Not found Pronounciation in forvo :: %s'%value)

                
                    
                a+=1
                

GUI()
 

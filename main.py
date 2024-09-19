import asyncio
import os
import re
import discord
from discord.ext import commands, tasks
from discord.utils import get
import random
from suno import *
from guild import *
import server
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

intents = discord.Intents.default()
client = discord.Client(intents=intents)

GUILD_ID=1122707918177960047
RESULT=None
THREADS=[]

@client.event
async def on_ready():
    global RESULT,THREADS
    try:
        req=requests.get('http://localhost:8888')
        print(req.status_code)
        await client.close() 
        print('Client closed')
        exit()
    except:
        server.b()  
        guild = client.get_guild(GUILD_ID)
        RESULT=await getBasic(guild)
        for thread in RESULT['threadsCh'].threads:
            msgs=[msg async for msg in thread.history(oldest_first=True)]
            THREADS.append({
                'username':msgs[0].content.split('@')[1],
                'lastMsg':msgs[-1]
            })
        
        if not playing.is_running():
            playing.start(guild)
        await asyncio.sleep(60)
        if not updateData.is_running():
            updateData.start(guild)
@tasks.loop(seconds=60)
async def updateData(guild):
    global RESULT,THREADS
    THREADS=[]
    print('updateData is running')
    try:
        RESULT=await getBasic(guild)
        usernames=[]
        for msg in RESULT['usernames']:
            usernames.append(msg.content)
        for user in usernames:
            email=user.split('||')[1].replace('``','')
            isset=False
            for thread in RESULT['threadsCh'].threads:
                if email==thread.name:
                    isset=True
            if not isset:
                rs=await RESULT['threadsCh'].create_thread(name=user.split('||')[1].replace('``',''),content='https://suno.com/@'+user.split('||')[0].replace('``','').lower())
                req=requests.get('https://suno.com/@'+user.split('||')[0].replace('``',''))
                soup=BeautifulSoup(req.text,'html.parser')
                els=soup.find('div',{'class':'flex flex-col lg:flex-row gap-8 px-4 pb-8 lg:p-8 pt-16 items-center -mt-32 md:mt-0 z-[20]'}).find('div',{'class':'flex flex-col lg:flex-row gap-8 w-full lg:w-auto'}).find('div',{'class':'flex flex-col'}).find('div',{'class':'flex flex-row gap-2'}).find_all('div')
                await rs.thread.send(content=f"``LIKE``== **{els[0].getText().split(' ')[0]}** | ``FANS``== **{els[1].getText().split(' ')[0]}** | ``PLAYS``== **{els[2].getText().split(' ')[0]}**")
        for thread in RESULT['threadsCh'].threads:
            try:
                msgs=[msg async for msg in thread.history(oldest_first=True)]
                THREADS.append({
                    'username':msgs[0].content.split('@')[1],
                    'lastMsg':msgs[-1]
                })
            except:
                pass
    except:
        pass
@tasks.loop(seconds=1)
async def playing(guild):
    print('playing is running')
    global RESULT,THREADS
    for thread in THREADS:
        try:
            username=thread['username']
            url='https://clerk.suno.com/v1/client/sessions/sess_2mHWu8j9M0ICNeeYSIyofy0XnLE/touch?_clerk_js_version=5.22.3'
            headers={
                'cookie':'__cf_bm=0rbeCSFyX_1QKzLm064UwuYS71pzk.OXB28I6R06JMc-1726734155-1.0.1.1-ix0rwkEKHYBy3dDAYaWT2mLHHyd_tHW0Eu8zju6H66S.FTxVzcUYy0RvtLDCQUyclqIQNvqawukvoK0rzvSnvQ; _cfuvid=vEoQsXOqn7_RWffFtnozG8vzWnITezQxO_EAoIRIyyg-1726734155372-0.0.1.1-604800000; __client_uat=1726734201; __client_uat_U9tcbTPE=1726734201; __client=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNsaWVudF8ybUhXcERxaTFJZjBESE9ySHQzQTBNcTZwanQiLCJyb3RhdGluZ190b2tlbiI6Im0yaTUwbGxpazZlZ2djdmE3ZGx3MDgxczdvbXlldmdjYzZqYTExNjkifQ.CVW3p1cWsWYryKyLgY2ScazeJrxncZmVivCQjMfRfy2rnu59Z7F_cwpU_kRtxNQ5KwJ184MG1fqhvN-muvlQATt7WtQYBFMv6ya08dYgz_Yy7eXL0OXwtVuK0y0Z95jXNJOLTdwc4_qXGSUcu60cCoZirB306BcmmD1ty_7jd0jxsDd01YVyYPJan5hkyvyh9bl2hOjquDXZXVcfblX6vVtu8hfjdv5e5wO7ByDoi4ki-SHWDx6q3dNvhwl0u7xbWwjRuQpQf7z3Ed4ExvreoX11IzgwjlDIst4o598LE8ivz8gYGdP5eQpgkYXEE49UqNLd3ANrfdfUIboy3IW21A; ajs_anonymous_id=ae0a5283-be14-470f-8d3b-e3969fdb2c42',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.9',
            }
            data={
                'active_organization_id':''
            }
            req=requests.post(url,headers=headers,data=data)
            token=req.json()['response']['last_active_token']['jwt']
            headers['RSC']='1'
            req=requests.get('https://suno.com/@'+username+'?_rsc=1l6gm',headers=headers)
            strs=re.search('.*2:\["\$","\$L10",null,(.*?)\]\n.*',req.text).group(1)
            data=json.loads(strs)
            for row in data['profile']['clips']:
                url=f'https://studio-api.suno.ai/api/gen/{row["id"]}/increment_play_count/v2'
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.9',
                    'Authorization':'Bearer '+token,'Origin':'https://suno.com'       
                }
                data={"sample_factor":1}
                req=requests.post(url,headers=headers,json=data)
                if req.status_code<400:
                    print('Increament 1 Played')
                if datetime.now().hour==12 and datetime.now().minute==0:
                    req=requests.get('https://suno.com/@'+username)
                    soup=BeautifulSoup(req.text,'html.parser')
                    els=soup.find('div',{'class':'flex flex-col lg:flex-row gap-8 px-4 pb-8 lg:p-8 pt-16 items-center -mt-32 md:mt-0 z-[20]'}).find('div',{'class':'flex flex-col lg:flex-row gap-8 w-full lg:w-auto'}).find('div',{'class':'flex flex-col'}).find('div',{'class':'flex flex-row gap-2'}).find_all('div')
                    await thread['lastMsg'].edit(content=f"``LIKE``== **{els[0].getText().split(' ')[0]}** | ``FANS``== **{els[1].getText().split(' ')[0]}** | ``PLAYS``== **{els[2].getText().split(' ')[0]}**")
        except:
            pass
client.run(os.environ.get('botToken'))

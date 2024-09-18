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

@client.event
async def on_ready():
    global RESULT
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
        result = await getBasic(guild)
        if not updateData.is_running():
            updateData.start(guild)
        if not playing.is_running():
            playing.start(guild)
@tasks.loop(seconds=30)
async def updateData(guild):
    global RESULT
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
            rs=await RESULT['threadsCh'].create_thread(name=user.split('||')[1].replace('``',''),content='https://suno.com/@'+user.split('||')[0].replace('``',''))
            req=requests.get('https://suno.com/@'+user.split('||')[0].replace('``',''))
            soup=BeautifulSoup(req.text,'html.parser')
            els=soup.find('div',{'class':'flex flex-col lg:flex-row gap-8 px-4 pb-8 lg:p-8 pt-16 items-center -mt-32 md:mt-0 z-[20]'}).find('div',{'class':'flex flex-col lg:flex-row gap-8 w-full lg:w-auto'}).find('div',{'class':'flex flex-col'}).find('div',{'class':'flex flex-row gap-2'}).find_all('div')
            await rs.thread.send(content=f"``LIKE``== **{els[0].getText().split(' ')[0]}** | ``FANS``== **{els[1].getText().split(' ')[0]}** | ``PLAYS``== **{els[2].getText().split(' ')[0]}**")
@tasks.loop(seconds=1)
async def playing(guild):
    print('playing is running')
    global RESULT
    for thread in RESULT['threadsCh'].threads:
        msgs=[msg async for msg in thread.history(oldest_first=True)]
        username=msgs[0].content.split('@')[1]
        url='https://clerk.suno.com/v1/client/sessions/sess_2mDnGfr55VzPNAqZFq6Wa4kPzq8/touch?_clerk_js_version=5.21.2'
        headers={
            'cookie':'__cf_bm=Z_sB6bARq8DGnkZm7oYfQsxiUSvZAWbSwE5_yFEhaMI-1726629712-1.0.1.1-SJ_7i_m7fDZxC17bgWnRGfgaTGpP1IIn88QvZfwnxAOhiBBCSen5X5HGUdWiPTP1.EFGREtlZFd_F6Xc4k0Kwg; _cfuvid=H8yFhqqMQd7crZp6vEgjJgy6XzcNFe12N8mez8cQ58c-1726619489684-0.0.1.1-604800000; __client_uat=1726619919; __client=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNsaWVudF8ybURuOElFY25JNk9HNFROWGYzYmJqU1M0cVAiLCJyb3RhdGluZ190b2tlbiI6InU1MzUxdTlieHBjM2QzZTFmOWhyMG1ka3R4bXp6Y3Vva2M2amp0bGQifQ.CeCJIu6Vdy7KyBsgN7oCaLCbPIYfN7pOGJ5w7qY2qil7Jrnn427cd6FkrtUK2P0fQdrcv2-UH5QlwgqyrhHfAuUOeAJEqy-7Enxwc0GgkwkTTCYvLlPbBQ9kLjivaUKQqfcGV5GSwsIYE8shdQvBPAheq8zuBEeZTOkQ1v3xcZofuNoTgrJOMERvmw71xk9v2GyY5Gw0qXL0CndVCxOWTtcHjyfc3NAgqIXSJhISw5SxOFFd5ZAynEse6m3M44iCAxu7Sr9e1vGjN67huxXFb1nQI5s0L5IY38RYDaEHNsVwL9llgdnN6ftkBqbI5RlaseWwzSRP0glj9xWHHHT_dQ',
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
                await msgs[-1].edit(content=f"``LIKE``== **{els[0].getText().split(' ')[0]}** | ``FANS``== **{els[1].getText().split(' ')[0]}** | ``PLAYS``== **{els[2].getText().split(' ')[0]}**")
client.run(os.environ.get('botToken'))

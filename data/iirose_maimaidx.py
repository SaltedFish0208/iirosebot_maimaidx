import requests
import os
import sqlite3

from loguru import logger
from API.api_message import at_user
from API.api_iirose import APIIirose  # 大部分接口都在这里
from globals.globals import GlobalVal  # 一些全局变量 now_room_id 是机器人当前所在的房间标识，websocket是ws链接，请勿更改其他参数防止出bug，也不要去监听ws，websockets库只允许一个接收流
from API.api_get_config import get_master_id  # 用于获取配置文件中主人的唯一标识
from API.decorator.command import on_command, MessageType  # 注册指令装饰器和消息类型Enmu

API = APIIirose()  # 吧class定义到变量就不会要求输入self了（虽然我都带了装饰器没有要self的 直接用APIIirose也不是不可以 习惯了

maimaidxapi = "https://maimai.lxns.net/api/v0/maimai/"
headers = {
    "Authorization":""
}
difficulty = {
    "0":"Basic 绿",
    "1":"Advanced 黄",
    "2":"Expert 红",
    "3":"Master 紫",
    "4":"Re:Master 白"
}

fullsync = {
    "None":"无",
    "fs":"Full Sync",
    "fsp":"Full Sync+",
    "fsd":"Full Sync DX",
    "fsdp":"Full Sync DX+"
}

fullcombo = {
    "None":"无",
    "fc":"Full Combo",
    "fcp":"Full Combo+",
    "ap":"All Prefect",
    "app":"All Prefect+"
}

rate = {
    "d":"D",
    "c":"C",
    "b":"B",
    "bb":"BB",
    "bbb":"BBB",
    "a":"A",
    "aa":"AA",
    "aaa":"AAA",
    "s":"S",
    "sp":"S+",
    "ss":"SS",
    "ssp":"SS+",
    "sss":"SSS",
    "sssp":"SSS+"
}

maimaitype = {
    "standard":"标准",
    "dx":"DX"
}

@on_command('>绑定好友码 ', True, command_type=[MessageType.room_chat, MessageType.private_chat])  # command_type 参数可让本指令在哪些地方生效，发送弹幕需验证手机号，每天20条。本参数需要输入列表，默认不输入的情况下只对房间消息做出反应，单个类型也需要是列表
async def maimaidx_bindfriendid(Message, text):  # 请保证同一个插件内不要有两个相同的指令函数名进行注册，否则只会保留最后一个注册的
    print(os.path.exists("./plugins/iirose_maimaidx/"))
    if os.path.exists("./plugins/iirose_maimaidx/") == True:
        connect = sqlite3.connect("./plugins/iirose_maimaidx/code.db")
        cursor = connect.cursor()
        cursor.execute(f'replace into LXNSFRIEND (User_ID, Friend_ID) values (\'{Message.user_id}\', \'{text}\')')
        connect.commit()
        cursor.close()
        connect.close()
        await API.send_msg(Message, "已完成")
    elif os.path.exists("./iirose_maimaidx/") == False:
        os.mkdir("./plugins/iirose_maimaidx/")
        connect = sqlite3.connect("./plugins/iirose_maimaidx/code.db")
        cursor = connect.cursor()
        cursor.execute("create table LXNSFRIEND (User_ID varchar(255), Friend_ID int)")
        connect.commit()
        cursor.close()
        connect.close()
@on_command('>b50', False, command_type=[MessageType.room_chat, MessageType.private_chat])  # command_type 参数可让本指令在哪些地方生效，发送弹幕需验证手机号，每天20条。本参数需要输入列表，默认不输入的情况下只对房间消息做出反应，单个类型也需要是列表
async def maimaidx(Message):  # 请保证同一个插件内不要有两个相同的指令函数名进行注册，否则只会保留最后一个注册的
    standardlist = []
    dxlist = []
    connect = sqlite3.connect("./plugins/iirose_maimaidx/code.db")
    cursor = connect.cursor()
    cursor.execute(f'select Friend_ID from LXNSFRIEND  where User_ID=\'{Message.user_id}\'')
    friendcode = cursor.fetchall()
    try:
        response = requests.get(f'{maimaidxapi}player/{friendcode[0][0]}/bests', headers=headers).json()
        for i in response["data"]["standard"]:
            standardlist.append(f'| ![图片](https://assets.lxns.net/maimai/jacket/{i["id"]}.png#e) | {i["song_name"]} | {i["level"]} | {difficulty[str(i["level_index"])]} | {i["achievements"]} | {fullcombo[str(i["fc"])]} | {fullsync[str(i["fs"])]} | {round(i["dx_rating"], 1)} | {rate[i["rate"]]} | {maimaitype[i["type"]]} |')
        for i in response["data"]["dx"]:
                dxlist.append(f'| ![图片](https://assets.lxns.net/maimai/jacket/{i["id"]}.png#e) | {i["song_name"]} | {i["level"]} | {difficulty[str(i["level_index"])]} | {i["achievements"]} | {fullcombo[str(i["fc"])]} | {fullsync[str(i["fs"])]} | {round(i["dx_rating"], 1)} | {rate[i["rate"]]} | {maimaitype[i["type"]]} |')
        msg = "\n".join(standardlist)
        msg2 = "\n".join(dxlist)
        await API.send_msg(Message, r'\\\*''\n'
        f'# 以下是您的b50信息 总分:{response["data"]["standard_total"]+response["data"]["dx_total"]}\n'
        f'# 旧曲\n'
        f'| 图片 | 歌名 | 谱面难度 | 谱面等级 | 完成度 | 是否FC | 是否FS | 加分 | 完成度 | 谱面类型 |\n'
        f'|---|---|---|---|---|---|---|---|---|---|\n'
        f'{msg}\n'
        f'# 新曲\n'
        f'| 图片 | 歌名 | 谱面难度 | 谱面等级 | 完成度 | 是否FC | 是否FS | 加分 | 完成度 | 谱面类型 |\n'
        f'|---|---|---|---|---|---|---|---|---|---|\n'    
        f'{msg2}')
    except:
         await API.send_msg(Message, "出错了！也许是您没有绑定落雪查分器的好友码？使用“>绑定好友码 <好友码>”来绑定您的查分器账户")
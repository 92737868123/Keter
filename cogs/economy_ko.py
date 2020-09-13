import discord
import time
import psutil
import os
import asyncio
import openpyxl
import random
import math

from datetime import datetime
from discord.ext import commands
from evs import default, permissions

userlib = "./lib/economy/users/"


def get_kor_amount_string(num_amount, ndigits_round=0, str_suffix='원'):
    """숫자를 자릿수 한글단위와 함께 리턴한다 """
    assert isinstance(num_amount, int) and isinstance(ndigits_round, int)
    assert num_amount >= 1, '최소 1원 이상 입력되어야 합니다'
    ## 일, 십, 백, 천, 만, 십, 백, 천, 억, ... 단위 리스트를 만든다.
    maj_units = ['만', '억', '조', '경', '해', '자', '양', '구', '간', '정', '재', '극']  # 10000 단위
    units = [' ']  # 시작은 일의자리로 공백으로하고 이후 십, 백, 천, 만...
    for mm in maj_units:
        units.extend(['십', '백', '천'])  # 중간 십,백,천 단위
        units.append(mm)

    list_amount = list(str(round(num_amount, ndigits_round)))  # 라운딩한 숫자를 리스트로 바꾼다
    list_amount.reverse()  # 일, 십 순서로 읽기 위해 순서를 뒤집는다

    str_result = ''  # 결과
    num_len_list_amount = len(list_amount)

    for i in range(num_len_list_amount):
        str_num = list_amount[i]
        # 만, 억, 조 단위에 천, 백, 십, 일이 모두 0000 일때는 생략
        if num_len_list_amount >= 9 and i >= 4 and i % 4 == 0 and ''.join(list_amount[i:i + 4]) == '0000':
            continue
        if str_num == '0':  # 0일 때
            if i % 4 == 0:  # 4번째자리일 때(만, 억, 조...)
                str_result = units[i] + str_result  # 단위만 붙인다
        elif str_num == '1':  # 1일 때
            if i % 4 == 0:  # 4번째자리일 때(만, 억, 조...)
                str_result = str_num + units[i] + str_result  # 숫자와 단위를 붙인다
            else:  # 나머지자리일 때
                str_result = units[i] + str_result  # 단위만 붙인다
        else:  # 2~9일 때
            str_result = str_num + units[i] + str_result  # 숫자와 단위를 붙인다
    str_result = str_result.strip()  # 문자열 앞뒤 공백을 제거한다
    if len(str_result) == 0:
        return None
    if not str_result[0].isnumeric():  # 앞이 숫자가 아닌 문자인 경우
        str_result = '1' + str_result  # 1을 붙인다
    return str_result + str_suffix  # 접미사를 붙인다

class economy_ko(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())
        #폴더생성
        if os.path.isdir("./lib/economy/users"):
            print("user folder exist")
        else:
            os.makedirs("./lib/economy/users")

    #참여
    @commands.command()
    async def 참여(self, ctx):

        embed = discord.Embed(title="케테르 경제", description="케테르 경제에 참여하시겠습니까?", color=0xeff0f1)
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/750540820842807396/752684853320745000/KETER_PRESTIGE.png")
        msg = await ctx.send(embed=embed)

        def reaction_check_(m):
            if m.message_id == msg.id and m.user_id == ctx.author.id and str(m.emoji) == "✅":
                return True
            return False

        try:
            await msg.add_reaction("✅")
            await self.bot.wait_for('raw_reaction_add', timeout=10.0, check=reaction_check_)
            if os.path.isfile(userlib + str(ctx.author.id) + ".xlsx"):
                embed = discord.Embed(title="케테르 경제", description="이미 참여하셨습니다.", color=0xeff0f1)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="케테르 경제", description="새로 오셨군요? " + str(ctx.author.name) + "님을 위한 파일들을 생성중이에요!",
                                      color=0xeff0f1)
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/750540820842807396/752690012369190942/DARK_KETER_1.png")
                await ctx.send(embed=embed)
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.cell(row=1, column=1).value = "Hello World" #:)
                ws.cell(row=1, column=2).value = "8600000" #money
                ws.cell(row=1, column=3).value = "0" #pres
                ws.cell(row=1, column=4).value = "-" #rank
                ws.cell(row=2, column=1).value = "None" #status
                ws.cell(row=2, column=2).value = "0" #perfect
                ws.cell(row=2, column=3).value = "0" #great
                ws.cell(row=2, column=4).value = "0" #good
                ws.cell(row=2, column=5).value = "0" #bad
                ws.cell(row=3, column=1).value = "0" #tsucc
                ws.cell(row=3, column=2).value = "0" #tfail
                ws.cell(row=3, column=3).value = "0" #fails
                ws.cell(row=4, column=1).value = "0" #home count
                ws.cell(row=4, column=2).value = "[1]" #title
                ws.cell(row=4, column=3).value = "1" #header
                ws.cell(row=4, column=4).value = "1" #tail
                ws.cell(row=5, column=1).value = "100" #HP
                ws.cell(row=5, column=2).value = "100" #STR
                ws.cell(row=5, column=3).value = "100" #DEF
                ws.cell(row=5, column=4).value = "100" #INT
                wb.save(userlib + str(ctx.author.id) + ".xlsx")
                wb.close()
                time.sleep(1)
                embed = discord.Embed(title="케테르 경제",
                                      description=str(ctx.author.name) + " 생성 완료!",
                                      color=0xeff0f1)
                await ctx.send(embed=embed)

        except asyncio.TimeoutError:
            await msg.delete()
            embed = discord.Embed(title="케테르 경제", description="서명하지 않으셨습니다. 다음 기회에..", color=0xeff0f1)
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/750540820842807396/752690012369190942/DARK_KETER_1.png")
            await ctx.send(embed=embed)

        except discord.Forbidden:
            embed = discord.Embed(title="케테르 경제", description="케테르 경제에 참여하시겠습니까?", color=0xeff0f1)
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/750540820842807396/752684853320745000/KETER_PRESTIGE.png")
            await msg.edit(content=embed)

    @commands.command(aliases=['돈내놔', '돈줘'])
    async def 돈받기(self,ctx):
        if os.path.isfile(userlib + str(ctx.author.id) + ".xlsx"):
            num = random.randrange(0,6)
            wb = openpyxl.load_workbook(userlib + str(ctx.author.id) + ".xlsx")
            ws = wb.active
            getmoney = ws.cell(row=1, column=2).value
            getmoney = int(getmoney) + int(num)
            ws.cell(row=1, column=2).value = str(getmoney)
            wb.save(userlib + str(ctx.author.id) + ".xlsx")
            wb.close()
            embed = discord.Embed(title="KET", description="<@" + str(ctx.author.id) + "> " +str(num)+"<:ket:753449741186105375>을 받았어요!", color=0xeff0f1)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="NO", description="먼저 ``.참여``를 입력해서 케테르 경제에 참여해주세요!", color=0xeff0f1)
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/750540820842807396/752684853320745000/KETER_PRESTIGE.png")
            await ctx.send(embed=embed)

    @commands.command()
    async def 돈(self, ctx):
        if (ctx.message.mentions.__len__() > 0):
            for user in ctx.message.mentions:
                if os.path.isfile(userlib + str(user.id) + ".xlsx"):
                    wb = openpyxl.load_workbook(userlib + str(user.id) + ".xlsx")
                    ws = wb.active
                    money = ws.cell(row=1, column=2).value
                    wb.close()
                    embed = discord.Embed(title="KET", description="<@" + str(user.id) + ">님은 " + str(get_kor_amount_string(money)) + "<:ket:753449741186105375>을 가지고 계십니다!", color=0xeff0f1)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="NO", description="유저가 ``케테르 경제``에 참여하지 않았어요..", color=0xeff0f1)
                    embed.set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/750540820842807396/752684853320745000/KETER_PRESTIGE.png")
                    await ctx.send(embed=embed)
        else:
            if os.path.isfile(userlib + str(ctx.author.id) + ".xlsx"):
                wb = openpyxl.load_workbook(userlib + str(ctx.author.id) + ".xlsx")
                ws = wb.active
                money = ws.cell(row=1, column=2).value
                wb.close()
                embed = discord.Embed(title="KET", description="<@" + str(ctx.author.id) + "> " + str(get_kor_amount_string(money)) + "<:ket:753449741186105375>을 가지고 계십니다!", color=0xeff0f1)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="NO", description="먼저 ``.참여``를 입력해서 케테르 경제에 참여해주세요!", color=0xeff0f1)
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/750540820842807396/752684853320745000/KETER_PRESTIGE.png")
                await ctx.send(embed=embed)


    @commands.command(aliases=['프리스티지', '프레스티지'])
    async def 호프(self, ctx):
        if os.path.isfile(userlib + str(ctx.author.id) + ".xlsx"):
            wb = openpyxl.load_workbook(userlib + str(ctx.author.id) + ".xlsx")
            ws = wb.active
            prestige = ws.cell(row=1, column=3).value
            wb.close()
            embed = discord.Embed(title="PRESTIGE", description="<@" + str(ctx.author.id) + "> " + str(
                prestige) + "<:pre:753458787465297993>을 가지고 계십니다!", color=0xeff0f1)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="NO", description="먼저 ``.참여``를 입력해서 케테르 경제에 참여해주세요!", color=0xeff0f1)
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/750540820842807396/752684853320745000/KETER_PRESTIGE.png")
            await ctx.send(embed=embed)

    @commands.command(aliases=['ㄷㅂ'])
    async def 도박(self, ctx, val:int):
        if os.path.isfile(userlib + str(ctx.author.id) + ".xlsx"):
            wb = openpyxl.load_workbook(userlib + str(ctx.author.id) + ".xlsx")
            ws = wb.active
            money = ws.cell(row=1, column=2).value
            if int(money) > val:
                discrim = random.random()
                if discrim < 0.02:
                    ws.cell(row=1, column=2).value = str(int(ws.cell(row=1, column=2).value) + 11*val)
                    ws.cell(row=3, column=3).value = "0"
                    embed = discord.Embed(title="도박", description="<@" + str(ctx.author.id) + "> " + "축하합니다! 대박이 나서 12배를 획득 하셨어요! 🎉\n획득량:" + str(12*val) + " <:ket:753449741186105375>", color=0xeff0f1)
                elif 0.02 < discrim < 0.05 + math.sqrt(int(ws.cell(row=3, column=3).value)*100)/100:
                    ws.cell(row=1, column=2).value = str(int(ws.cell(row=1, column=2).value) + 2*val)
                    ws.cell(row=3, column=3).value = "0"
                    embed = discord.Embed(title="도박", description="<@" + str(ctx.author.id) + "> " + "축하합니다! 도박에 성공하셔서 3배를 획득 하셨어요! 🎉\n획득량:" + str(3*val) + " <:ket:753449741186105375>", color=0xeff0f1)
                elif 0.05 + math.sqrt(int(ws.cell(row=3, column=3).value)*100)/100 < discrim < 0.1 + math.sqrt(int(ws.cell(row=3, column=3).value)*100)/50:
                    ws.cell(row=1, column=2).value = str(int(ws.cell(row=1, column=2).value) + val)
                    ws.cell(row=3, column=3).value = "0"
                    embed = discord.Embed(title="도박", description="<@" + str(ctx.author.id) + "> " +  "축하합니다! 도박에 성공하셔서 2배를 획득 하셨어요! 🎉\n획득량:" + str(2*val) + " <:ket:753449741186105375>", color=0xeff0f1)
                else:
                    emj = "<:dar:754345236574109716>"
                    ws.cell(row=1, column=2).value = str(int(ws.cell(row=1, column=2).value) - val)
                    ws.cell(row=3, column=3).value = str(int(ws.cell(row=3, column=3).value) + 1)
                    embed = discord.Embed(title="도박", description="도박에 실패하여 돈을 잃으셨습니다. " + emj, color=0xeff0f1)
                wb.save(userlib + str(ctx.author.id) + ".xlsx")
                wb.close()
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="NO", description="보유하신 잔액보다 큰 금액을 베팅할 수는 없어요.", color=0xeff0f1)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="NO", description="먼저 ``.참여``를 입력해서 케테르 경제에 참여해주세요!", color=0xeff0f1)
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/750540820842807396/752684853320745000/KETER_PRESTIGE.png")
            await ctx.send(embed=embed)

    @commands.command()
    async def 송금(self, ctx, mention:str, valu:int):
        if (ctx.message.mentions.__len__() > 0):
            for user in ctx.message.mentions:
                if os.path.isfile(userlib + str(user.id) + ".xlsx"):
                    wb = openpyxl.load_workbook(userlib + str(ctx.author.id) + ".xlsx")
                    ws = wb.active
                    money = int(ws.cell(row=1, column=2).value)
                    if int(money) > valu:
                        wb2 = openpyxl.load_workbook(userlib + str(user.id) + ".xlsx")
                        ws2 = wb2.active
                        money2 = int(ws2.cell(row=1, column=2).value)
                        money2 = money2+valu
                        ws2.cell(row=1, column=2).value = str(money2)
                        wb2.save(userlib + str(user.id) + ".xlsx")
                        wb2.close()
                        money = money - valu
                        ws.cell(row=1, column=2).value = str(money)
                        wb.save(userlib + str(ctx.author.id) + ".xlsx")
                        wb.close()
                        embed = discord.Embed(title="송금", description="<@" + str(ctx.author.id) + "> " + str(valu) + " <:ket:753449741186105375>" + "송금 완료", color=0xeff0f1)
                        await ctx.send(embed=embed)
                    else:
                        embed = discord.Embed(title="NO", description="보유하신 잔액보다 큰 금액을 송금할 수는 없어요.", color=0xeff0f1)
                        await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="NO", description="유저가 ``케테르 경제``에 참여하지 않았어요..", color=0xeff0f1)
                    embed.set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/750540820842807396/752684853320745000/KETER_PRESTIGE.png")
                    await ctx.send(embed=embed)

    @commands.command()
    @commands.check(permissions.is_owner)
    async def 초기화(self,ctx):
        file_list = os.listdir(userlib)
        file_list = [file for file in file_list if file.endswith(".xlsx")]
        for i in range(len(file_list)):
            wb = openpyxl.load_workbook(userlib + file_list[i])
            ws = wb.active
            if int(ws.cell(row=1, column=3).value) <= 1000:
                ws.cell(row=1, column=3).value = str(int(ws.cell(row=1, column=3).value) + math.ceil(int(ws.cell(row=1, column=2).value) / 1000000000))
            else:
                ws.cell(row=1, column=3).value = str(round(int(ws.cell(row=1, column=3).value) / 2) + math.ceil(int(ws.cell(row=1, column=2).value) / 1000000000))
            ws.cell(row=1, column=2).value = "8600000"
            wb.save(userlib + file_list[i])
            wb.close()
        embed = discord.Embed(title="Admin", description="초기화 완료", color=0xeff0f1)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.check(permissions.is_owner)
    async def 돈추가(self, ctx, mention:str, value:int):
        if (ctx.message.mentions.__len__() > 0):
            for user in ctx.message.mentions:
                if os.path.isfile(userlib + str(user.id) + ".xlsx"):
                    wb = openpyxl.load_workbook(userlib + str(user.id) + ".xlsx")
                    ws = wb.active
                    money = ws.cell(row=1, column=2).value
                    money = int(money)+value
                    ws.cell(row=1, column=2).value = money
                    wb.save(userlib + str(user.id) + ".xlsx")
                    wb.close()
                    embed = discord.Embed(title="KET", description=str(money) + "<:ket:753449741186105375> 추가 완료", color=0xeff0f1)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="NO", description="유저가 ``케테르 경제``에 참여하지 않았어요..", color=0xeff0f1)
                    embed.set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/750540820842807396/752684853320745000/KETER_PRESTIGE.png")
                    await ctx.send(embed=embed)

    @commands.command()
    @commands.check(permissions.is_owner)
    async def 전체초기화(self, ctx):
        file_list = os.listdir(userlib)
        file_list = [file for file in file_list if file.endswith(".xlsx")]
        for i in range(len(file_list)):
            os.remove(userlib + file_list[i])
            await ctx.send(file_list[i] + "deleted")

def setup(bot):
    bot.add_cog(economy_ko(bot))

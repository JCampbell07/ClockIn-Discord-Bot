import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import datetime
import dataIO
import json
import asyncio
import pickle
import os
import sys
import subsystem
import pytz
import sqlite3
import threading

intents = discord.Intents.all()
intents.members = True

allowedmentions=discord.AllowedMentions(users=True, everyone=False, roles=True, replied_user=True)

client = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True, help_command=None, allowed_mentions=allowedmentions)
client.remove_command('help')

conn = sqlite3.connect('clock.sqlite')
c = conn.cursor()

# Discord ID goes in the discords variable
discords = [496080101037965314]

# Staff role IDs go here
roleids = [753307464946024588,687581733603770368]


# checkTime() allows for twice a day automatic clock outs
async def checkTime():
    print("Watching the clock to automatically check staff out at midnight and noon.")
    # function runs every 5 minutes
    threading.Timer(300, checkTime).start()
    now = datetime.datetime.now()
    guild=client.get_guild(discords[0])
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    currentday = datetime.datetime.now().strftime('%d')
    currentmonth = datetime.datetime.now().strftime('%m')
    currentyear = datetime.datetime.now().strftime('%Y')
    currenthour = datetime.datetime.now().strftime('%H')
    currentmin = datetime.datetime.now().strftime('%M') 
    
    # Enter your chosen times here in UTC (HH:MM)
    if current_time == '12:00' or current_time == '00:00':
        print("Clocking all users out.")
        c.execute(f"update hours set outday = {currentday}")
        c.execute(f"update hours set outmonth = {currentmonth}")
        c.execute(f"update hours set outyear = {currentyear}")
        c.execute(f"update hours set outhour = {currenthour}")
        c.execute(f"update hours set outmin = {currentmin}")
        conn.commit()
        usersintable = []
        usersintable2 = []
        c.execute(f"select staffid from hours")
        users = c.fetchall()
        for user in users:
            usersintable.append(user[0])
        print(usersintable)
        for item in usersintable:
            use = client.get_user(item)
            usersintable2.append(use)
            
            # Your On Duty Role ID goes here
        ondutyrole = discord.utils.get(guild.roles,id=979210570433716224)
        for moderator in ondutyrole.members:
            if moderator.id in usersintable:
                c.execute(f'select inday from hours where staffid = {moderator.id}')
                exists=c.fetchone()
                inday = exists[0]
                if int(inday) < 10:
                    inday= f"0{inday}"
                c.execute(f'select inmonth from hours where staffid = {moderator.id}')
                exists=c.fetchone()
                inmonth = exists[0]
                if int(inmonth) < 10:
                    inmonth= f"0{inmonth}"
                c.execute(f'select inyear from hours where staffid = {moderator.id}')
                exists=c.fetchone()
                inyear = exists[0]
                c.execute(f'select inhour from hours where staffid = {moderator.id}')
                exists=c.fetchone()
                inhour = exists[0]
                if int(inhour) < 10:
                    inhour= f"0{inhour}"
                c.execute(f'select inmin from hours where staffid = {moderator.id}')
                exists=c.fetchone()
                inmin = exists[0]
                if int(inmin) < 10:
                    inmin= f"0{inmin}"

                c.execute(f'select outday from hours where staffid = {moderator.id}')
                exists=c.fetchone()
                outday = exists[0]
                if int(outday) < 10:
                    outday= f"0{outday}"
                c.execute(f'select outmonth from hours where staffid = {moderator.id}')
                exists=c.fetchone()
                outmonth = exists[0]
                if int(outmonth) < 10:
                    outmonth= f"0{outmonth}"
                c.execute(f'select outyear from hours where staffid = {moderator.id}')
                exists=c.fetchone()
                outyear = exists[0]
                c.execute(f'select outhour from hours where staffid = {moderator.id}')
                exists=c.fetchone()
                outhour = exists[0]
                if int(outhour) < 10:
                    outhour= f"0{outhour}"
                c.execute(f'select outmin from hours where staffid = {moderator.id}')
                exists=c.fetchone()
                outmin = exists[0]
                if int(outmin) < 10:
                    outmin= f"0{outmin}"

                # Calculate total time clocked in
                instring = f"{inyear}-{inmonth}-{inday} {inhour}:{inmin}:00"
                indate = datetime.datetime.fromisoformat(instring)

                outstring = f"{outyear}-{outmonth}-{outday} {outhour}:{outmin}:00"
                outdate = datetime.datetime.fromisoformat(outstring)

                totalTime = (outdate-indate).total_seconds() / 60

                print(totalTime)
                c.execute(f"select totaltime from hours where staffid = {moderator.id}")
                exists = c.fetchone()
                currentTotal = exists[0]
                totalTime = int(currentTotal) + int(totalTime)
                c.execute(f"update hours set totaltime = {totalTime} where staffid = {moderator.id}")
                conn.commit()
                await moderator.remove_roles(ondutyrole)
                await moderator.send(f"You have been clocked out in {guild.name}. Please clock back in if you are still active.")

@client.event
async def on_ready():
    print("Tracking Staff Hours...")
    guild = client.get_guild(discords[0])
    await checkTime()
    # Place your On Duty Role ID here again
    ondutyrole = discord.utils.get(guild.roles,id=979210570433716224)
    # Place the ID of your clock in channel here
    purgeChan = client.get_channel(979131454179143791)
    await purgeChan.purge(limit=2)
    

    async def incallback(interaction2):
        inday = datetime.datetime.now().strftime('%d')
        inmonth = datetime.datetime.now().strftime('%m')
        inyear = datetime.datetime.now().strftime('%Y')
        inhour = datetime.datetime.now().strftime('%H')
        inmin = datetime.datetime.now().strftime('%M')
        print(f"{inyear}-{inmonth}-{inday} {inhour}:{inmin}:00")
        c.execute(f'update hours set inday = {inday} where staffid = {interaction2.user.id}')
        c.execute(f'update hours set inmonth = {inmonth} where staffid = {interaction2.user.id}')
        c.execute(f'update hours set inyear = {inyear} where staffid = {interaction2.user.id}')
        c.execute(f'update hours set inhour = {inhour} where staffid = {interaction2.user.id}')
        c.execute(f'update hours set inmin = {inmin} where staffid = {interaction2.user.id}')
        conn.commit()
        await interaction2.user.add_roles(ondutyrole)
        await interaction2.response.send_message("You have clocked in.", ephemeral=True)

    async def outcallback(interaction2):

        # Too lazy to change variable names, just modified SQL commands to point to proper columns

        inday = datetime.datetime.now().strftime('%d')
        inmonth = datetime.datetime.now().strftime('%m')
        inyear = datetime.datetime.now().strftime('%Y')
        inhour = datetime.datetime.now().strftime('%H')
        inmin = datetime.datetime.now().strftime('%M')
        print(f"{inyear}-{inmonth}-{inday} {inhour}:{inmin}:00")
        c.execute(f'update hours set outday = {inday} where staffid = {interaction2.user.id}')
        c.execute(f'update hours set outmonth = {inmonth} where staffid = {interaction2.user.id}')
        c.execute(f'update hours set outyear = {inyear} where staffid = {interaction2.user.id}')
        c.execute(f'update hours set outhour = {inhour} where staffid = {interaction2.user.id}')
        c.execute(f'update hours set outmin = {inmin} where staffid = {interaction2.user.id}')
        conn.commit()

        # Pull clock in time from database

        c.execute(f'select inday from hours where staffid = {interaction2.user.id}')
        exists=c.fetchone()
        inday = exists[0]
        if int(inday) < 10:
            inday= f"0{inday}"
        c.execute(f'select inmonth from hours where staffid = {interaction2.user.id}')
        exists=c.fetchone()
        inmonth = exists[0]
        if int(inmonth) < 10:
            inmonth= f"0{inmonth}"
        c.execute(f'select inyear from hours where staffid = {interaction2.user.id}')
        exists=c.fetchone()
        inyear = exists[0]
        c.execute(f'select inhour from hours where staffid = {interaction2.user.id}')
        exists=c.fetchone()
        inhour = exists[0]
        if int(inhour) < 10:
            inhour= f"0{inhour}"
        c.execute(f'select inmin from hours where staffid = {interaction2.user.id}')
        exists=c.fetchone()
        inmin = exists[0]
        if int(inmin) < 10:
            inmin= f"0{inmin}"

        c.execute(f'select outday from hours where staffid = {interaction2.user.id}')
        exists=c.fetchone()
        outday = exists[0]
        if int(outday) < 10:
            outday= f"0{outday}"
        c.execute(f'select outmonth from hours where staffid = {interaction2.user.id}')
        exists=c.fetchone()
        outmonth = exists[0]
        if int(outmonth) < 10:
            outmonth= f"0{outmonth}"
        c.execute(f'select outyear from hours where staffid = {interaction2.user.id}')
        exists=c.fetchone()
        outyear = exists[0]
        c.execute(f'select outhour from hours where staffid = {interaction2.user.id}')
        exists=c.fetchone()
        outhour = exists[0]
        if int(outhour) < 10:
            outhour= f"0{outhour}"
        c.execute(f'select outmin from hours where staffid = {interaction2.user.id}')
        exists=c.fetchone()
        outmin = exists[0]
        if int(outmin) < 10:
            outmin= f"0{outmin}"

        # Calculate total time clocked in
        instring = f"{inyear}-{inmonth}-{inday} {inhour}:{inmin}:00"
        indate = datetime.datetime.fromisoformat(instring)

        outstring = f"{outyear}-{outmonth}-{outday} {outhour}:{outmin}:00"
        outdate = datetime.datetime.fromisoformat(outstring)

        totalTime = (outdate-indate).total_seconds() / 60

        print(totalTime)
        c.execute(f"select totaltime from hours where staffid = {interaction2.user.id}")
        exists = c.fetchone()
        currentTotal = exists[0]
        totalTime = int(currentTotal) + int(totalTime)
        c.execute(f"update hours set totaltime = {totalTime} where staffid = {interaction2.user.id}")
        conn.commit()
        await interaction2.user.remove_roles(ondutyrole)
        await interaction2.response.send_message("You have clocked out.", ephemeral=True)

    inButton = Button(label="Clock In", style=discord.ButtonStyle.success)
    outButton = Button(label="Clock Out", style=discord.ButtonStyle.danger)

    inButton.callback=incallback
    outButton.callback=outcallback

    clockView = View(timeout=None)
    clockView.add_item(inButton)
    clockView.add_item(outButton)

    tableEmbed = discord.Embed(title="Clock In/Out", description="Clock in/out for community hours", color=discord.Color.red())
    
    #Choose your clock in Rules and place a warning if you choose to do so.
    tableEmbed.add_field(name="Rules", value="Do not clock in and be inactive. You will be automatically clocked out if you forget to clock out on your own. Hours will be periodically verified.")
    tableEmbed.add_field(name="~WARNING~", value=f"Abuse of this system will result in loss of position within {guild.name}.")
    await purgeChan.send(embed=tableEmbed, view=clockView)

    
# This command sets clock.sqlite up for usage
@client.slash_command(guild_ids=discords, name="setuptable", description="Sets up staff time table.")
async def setuptable(ctx):
    guild = client.get_guild(discords[0])
    # Modify your role set ups here for clock.sqlite, These roles are the roles that contain your staff members.
    modrole = discord.utils.get(guild.roles, id=roleids[0])
    staffrole = discord.utils.get(guild.roles, id=roleids[1])

    for member in modrole.members:
        c.execute(f'select staffid from hours where staffid = {member.id}')
        exists = c.fetchone()
        if exists is None:
            sql = "insert into hours (staffid, name) values (?, ?)"
            val = (member.id, member.name)
            c.execute(sql, val)
            c.execute(f"update hours set totaltime = 0")
            conn.commit()
        else:
            return
            
    for member in staffrole.members:
        c.execute(f'select staffid from hours where staffid = {member.id}')
        exists = c.fetchone()
        if exists is None:
            sql = "insert into hours (staffid, name) values (?, ?)"
            val = (member.id, member.name)
            c.execute(sql, val)
            c.execute(f"update hours set totaltime = 0")
            conn.commit()
        else:
            return

    await ctx.interaction.response.send_message("Table has been set up.", ephemeral=True)

@client.slash_command(guild_ids=discords, name="staffcheck", description="Query the time database for clocked hours.")
async def staffcheck(ctx, member: discord.User):

    c.execute(f"select totaltime from hours where staffid = {member.id}")
    exists = c.fetchone()
    if exists is None:
        timeVal = f"{member.mention} is not in the database."
    else:
        if int(exists[0]) > 60:
            timeVal = f"{member.mention} has {exists[0] / 60} hours recorded on the clock."
        elif int(exists[0]) == 60:
            timeVal = f"{member.mention} has 1 hour recorded on the clock."
        elif int(exists[0]) == 0:
            timeVal = f"{member.mention} has 0 minutes recorded on the clock."
        else:
            timeVal = f"{member.mention} has {exists[0]} minute(s) recorded on the clock."
    print(timeVal)
    await ctx.interaction.response.send_message(timeVal, ephemeral=True)





client.run('{TOKEN}')

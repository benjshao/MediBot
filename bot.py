import os
from patient import Patient
import datetime
import matplotlib.pyplot as plt

import discord
from dotenv import load_dotenv
import asyncio

from discord.ext import commands, tasks

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('Bot is ready.')

patientlist = {}

@bot.command(name='new-prescription')
async def new_prescription(ctx, patient: discord.Member):
    
    await ctx.send(f"What medication is to be prescribed?")
    medication = await bot.wait_for("message", check=None)
    
    await ctx.send(f"What is the amount of {medication.content} that is to be taken?")
    amount = await bot.wait_for("message", check=None)

    await ctx.send("Enter the time to set the patient's reminder.")
    time_entry = await bot.wait_for("message", check=None)
    hour, minute = map(int, time_entry.content.split(':'))
    reminder = datetime.time(hour, minute)
    await ctx.send(f"Prescription set for {patient.name}!")

    patientlist[patient.id] = Patient(patient, medication.content, amount.content, reminder)
    

    embed=discord.Embed(title="A new prescription reminder has been set for you!", description="Prescription Number", color=0x539cea)
    embed.set_thumbnail(url="https://image.flaticon.com/icons/png/512/2397/2397639.png")
    embed.add_field(name="Medication", value=medication.content, inline=True)
    embed.add_field(name="Amount", value=amount.content, inline=True)
    embed.add_field(name="Time", value=reminder.strftime("%I:%M %p"), inline=True)
    await patient.send(embed=embed)

@bot.command(name='info')
async def prescription_info(ctx, patient: discord.Member):

    #define figure and axes
    fig, ax = plt.subplots()

    #create values for table
    table_data=[
        ["Patient Name", patient.name],
        ["Prescription Number", None],
        ["Medication", patientlist[patient.id].medication],
        ["Amount", patientlist[patient.id].amount],
        ["Time", patientlist[patient.id].reminder.strftime("%I:%M %p")]
    ]

    #create table
    table = ax.table(cellText=table_data, loc='center')

    #modify table
    table.set_fontsize(9)
    table.scale(1,4)
    ax.axis('off')

    #display table
    plt.savefig('images/patientinfo.png', bbox_inches='tight', dpi=150)
    file = discord.File("images/patientinfo.png", filename="patientinfo.png")
    embed = discord.Embed()
    embed.set_image(url="attachment://patientinfo.png")
    await ctx.send(file=file, embed=embed)

@tasks.loop(seconds=60.0)
async def remindertask():

    for key in patientlist:
        now = datetime.datetime.now()

        if now.strftime("%H:%M")==patientlist[key].reminder.strftime("%H:%M"):
            embed=discord.Embed(title="It is time to take your medication!", description="Prescription Number", color=0x539cea)
            embed.add_field(name="Medication", value=patientlist[key].medication, inline=True)
            embed.add_field(name="Amount", value=patientlist[key].amount, inline=True)
            embed.set_footer(text="Respond by typing \"Done\" confirm that you have taken your medication!")
            dm = await patientlist[key].member.send(embed=embed)

            def check(m):
                return isinstance(m.channel, discord.DMChannel) and m.content == "Done"

            try:
                confirmation = await bot.wait_for("message", timeout=15.0, check=check)
                if confirmation:
                    await patientlist[key].member.send("Confirmed!")
            except asyncio.TimeoutError:
                channel = bot.get_channel(805167613272915989)
                await channel.send(f"{patientlist[key].member.name} missed their reminder.")

        else:
            next

@bot.command(name='start-reminders')
async def start_reminder(ctx):
    remindertask.start()

bot.run(TOKEN)
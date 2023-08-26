from decouple import config
from discord.ext import commands
import discord
import pandas as pd

term_gpa = pd.read_csv("condensed-gpa-by-term.csv")
instructor_gpa = pd.read_csv("condensed-gpa-by-instructor.csv")
course_gpa = pd.read_csv("condensed-gpa-by-course.csv")


token = config('BOT_TOKEN')
intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def hello(ctx):
    await ctx.send("Hello, " + ctx.author.display_name)

@bot.command()
async def term(ctx, subject: str, number: int, instructor: str, term: str, year: int):
    subject = subject.upper()
    instructor = instructor[0:1].upper() + instructor[1:].lower()
    term = term[0:1].upper() + term[1:].lower()
    try:
        search = term_gpa.loc[term_gpa['Subject'] == subject]
        search = search.loc[search['Number'] == number]
        search = search.loc[search['Instructor Last Name'] == instructor]
        search = search.loc[search['Term'] == term]
        search = search.loc[search['Years'] == year]
    except:
        await ctx.send("Invalid input. Please enter SUBJECT NUMBER INSTRUCTOR-LAST-NAME TERM YEAR in that order (note the spaces!).")
    else:
        if search.empty:
            await ctx.send("No records found.")
            return
        if len(search.index) > 1:
            await ctx.send("Multiple instructors found. Please re-query with your desired instructor.")
            for i in range(len(search.index)):
                await ctx.send(str(i) + ") " + search.iloc[i]['Primary Instructor'])
            return
        await ctx.send(subject + " " + str(number) + " as taught by (Professor) " + instructor + " in " + term + " " + str(year) + ":")
        await ctx.send("Average GPA: " + str(float(search['Average GPA'])))
        await ctx.send("Median grade: " + str(search['Median Grade'].values[0]))
        await ctx.send("Standard deviation: " + str(float(search['Standard Deviation'])))

@bot.command()
async def instructor(ctx, subject: str, number: int, instructor: str):
    subject = subject.upper()
    instructor = instructor[0:1].upper() + instructor[1:].lower()
    try:
        search = instructor_gpa.loc[instructor_gpa['Subject'] == subject]
        search = search.loc[search['Number'] == number]
        search = search.loc[search['Instructor Last Name'] == instructor]
    except:
        await ctx.send("Invalid input. Please enter SUBJECT NUMBER INSTRUCTOR-LAST-NAME in that order (note the spaces!).")
    else:
        if search.empty:
            await ctx.send("No records found.")
            return
        if len(search.index) > 1:
            await ctx.send("Multiple instructors found. Please re-query with your desired instructor.")
            for i in range(len(search.index)):
                await ctx.send(str(i) + ") " + search.iloc[i]['Primary Instructor'])
            return
        await ctx.send(subject + " " + str(number) + " as taught by (Professor) " + instructor + ":")
        await ctx.send("Average GPA: " + str(float(search['Average GPA'])))
        await ctx.send("Median grade: " + str(search['Median Grade'].values[0]))
        await ctx.send("Standard deviation: " + str(float(search['Standard Deviation'])))
        await ctx.send("Difference from average " + subject + " " + str(number) + " GPA: " + str(float(search['Difference'])))

@bot.command()
async def course(ctx, subject: str, number: int):
    subject = subject.upper()
    try:
        search = course_gpa.loc[course_gpa['Subject'] == subject]
        search = search.loc[search['Number'] == number]
    except:
        await ctx.send("Invalid input. Please enter SUBJECT NUMBER in that order (note the spaces!)")
    else:
        if search.empty:
            await ctx.send("No records found.")
            return
        await ctx.send(subject + " " + str(number) + ":")
        await ctx.send("Average GPA: " + str(float(search['Average GPA'])))
        await ctx.send("Median grade: " + str(search['Median Grade'].values[0]))
        await ctx.send("Standard deviation: " + str(float(search['Standard Deviation'])))

@bot.command()
async def info(ctx):
    await ctx.send("Query commands:\n!term (data for an instructor in a specific term)\n!instructor (data for an instructor in general)\n!course (data for a course)")

@bot.command()
async def rank(ctx):
    sorted = course_gpa.sort_values(by=['Average GPA'])
    df = sorted.head(10)
    await ctx.send("Top 10 HARDEST classes (by aggregate GPA average):")
    for i in range(10):
        await ctx.send(str(i+1) + ') ' + str(df.iloc[i]['Subject']) + " " + str(df.iloc[i]['Number']) + ": " + str(float(df.iloc[i]['Average GPA'])))
    await ctx.send("Top 10 EASIEST classes (by aggregate GPA average):")
    df = sorted.tail(10)
    for i in range(10):
        await ctx.send(str(i+1) + ') ' + str(df.iloc[i]['Subject']) + " " + str(df.iloc[i]['Number']) + ": " + str(float(df.iloc[i]['Average GPA'])))
bot.run(token)

import pandas as pd
import numpy as np
from urllib.request import urlretrieve as retrieve
import os
from datetime import date
import matplotlib.pyplot as plt
import smtplib
import ssl
from email.message import EmailMessage
import runpy
variable = "/Users/ROBERT/Documents/python/email/variable.py" #storing my credentials
runpy.run_path(path_name=variable)

# Load the file
url = 'https://fixturedownload.com/download/epl-2022-UTC.csv'
retrieve(url,"fixtures.csv")
file = os.path.join(os.getcwd(), "fixtures.csv")
df = pd.read_csv(file, delimiter=",")

## Today's matches
df["Match Date"], df["Match Hour"] = df["Date"].str.split(' ', 1).str

today = date.today()
today = today.strftime("%d/%m/%Y") # dd/mm/YY

df_today = df[df["Match Date"] == today].reset_index()
current_round = df_today.loc[0, "Round Number"]
prev_round = current_round - 1
df_last = df[df["Round Number"] == prev_round].reset_index()

### Prepare plots with points and goals

def update_plots():
    #df1 = df.copy()
    
    # prepare columns with goals in a round
    df["Home Goals"], df["Away Goals"] = df["Result"].str.split(' - ', 1).str
    df["Home Goals"] = pd.to_numeric(df["Home Goals"])
    df["Away Goals"] = pd.to_numeric(df["Away Goals"])
    
    # prepare columns with points received in a round
    df["Home Points"] = np.where(np.isnan(df["Home Goals"]), np.nan,
                            np.where(df["Home Goals"] > df["Away Goals"], 3, 
                                     np.where(df["Home Goals"] < df["Away Goals"], 0, 1
                            )))
    df["Away Points"] = np.where(np.isnan(df["Away Goals"]), np.nan,
                            np.where(df["Away Goals"] > df["Home Goals"], 3, 
                                     np.where(df["Away Goals"] < df["Home Goals"], 0, 1
                            )))
    df["Home Points"] = pd.to_numeric(df["Home Points"])
    df["Away Points"] = pd.to_numeric(df["Away Points"])
    
    # prepare aggregated tables for clubs
    total_home = df.groupby(by="Home Team", as_index=False).sum()[["Home Team","Home Goals","Home Points"]]
    total_away = df.groupby(by="Away Team", as_index=False).sum()[["Away Team","Away Goals","Away Points"]]

    total_home.rename(columns = {"Home Team":"Team", "Home Goals":"Goals", "Home Points":"Points"}, inplace = True)
    total_away.rename(columns = {"Away Team":"Team", "Away Goals":"Goals", "Away Points":"Points"}, inplace = True)

    total = pd.concat([total_home, total_away], ignore_index=True).groupby(by="Team", as_index=False).sum()
    total["Points"] = total["Points"].astype("int64")
    total["Goals"] = total["Goals"].astype("int64")
    
    # create and save a plot for points
    plt.figure(figsize=(8,4), dpi=100)
    total = total.sort_values("Points")
    points = plt.barh(total["Team"], total["Points"])
    plt.bar_label(points, labels=total["Points"])
    chart_title = chart_title = "Total Points after " + str(prev_round) + " rounds"
    plt.title(chart_title, fontdict={'fontname': 'Arial', 'fontsize': 12})
    plt.savefig('points.jpg', dpi=100)
    #plt.show()
    
    # create and save a plot for points
    
    plt.figure(figsize=(8,4), dpi=100)
    total = total.sort_values("Goals")
    points = plt.barh(total["Team"], total["Goals"], color="red")
    plt.bar_label(points, labels=total["Goals"])
    chart_title = chart_title = "Total Goals after " + str(prev_round) + " rounds"
    plt.title(chart_title, fontdict={'fontname': 'Arial', 'fontsize': 12})
    plt.savefig('goals.jpg', dpi=100)
    #plt.show()

def provide_html_today(df_today):
    today_matches_list = []

    for index, row in df_today.iterrows():
        today_match = row["Home Team"] + " - " + row["Away Team"] + " (" + row["Location"] + "; " + row["Match Hour"] + " UK)"
        today_matches_list.append(today_match)

    today_matches_html = str()

    for i in today_matches_list:
        today_matches_html = today_matches_html + i + " <br /> "

    return today_matches_html

def provide_html_last(prev_round):
    last_matches_list = []

    for index, row in df_last.iterrows():
        last_match = row["Home Team"] + " - " + row["Away Team"] + " " + row["Result"]
        last_matches_list.append(last_match)
    
    last_matches_html = str()
    
    for i in last_matches_list:
        last_matches_html = last_matches_html + i + " <br /> "

    return last_matches_html

def send_email():
    # Define email sender and receiver
    contacts = 'apple7com@gmail.com'
    email_sender = os.environ.get('EMAIL_ADDRESS')
    email_password = os.environ.get('EMAIL_PASS')
    email_receiver = contacts

    # Set the subject and body of the email
    subject = f"Premier League Today {today}"
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(content)
    em.add_alternative(content, subtype="html")

    # Add SSL (layer of security)
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

### Prepare e-mail

def prepare_email():

    head = """\
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Document</title>
        <style>
          @import url("https://fonts.googleapis.com/css2?family=Raleway:ital,wght@1,200&display=swap");

          * {
            margin: 0;
            padding: 0;
            border: 0;
          }

          body {
            font-family: "Raleway", sans-serif;
            background-color: #d8dada;
            font-size: 19px;
            max-width: 800px;
            margin: 0 auto;
            padding: 3%;
          }

          img {
            max-width: 100%;
          }

          header {
            width: 98%;
          }

          #logo {
            max-width: 120px;
            margin: 3% 0 3% 3%;
            float: left;
          }

          #wrapper {
            background-color: #f0f6fb;
          }

          #social {
            float: right;
            margin: 3% 2% 4% 3%;
            list-style-type: none;
          }

          #social > li {
            display: inline;
          }

          #social > li > a > img {
            max-width: 35px;
          }

          h1,
          p {
            margin: 3%;
          }
          .btn {
            float: right;
            margin: 0 2% 4% 0;
            background-color: #303840;
            color: #f6faff;
            text-decoration: none;
            font-weight: 800;
            padding: 8px 12px;
            border-radius: 8px;
            letter-spacing: 2px;
          }

          hr {
            height: 1px;
            background-color: #303840;
            clear: both;
            width: 96%;
            margin: auto;
          }

          #contact {
            text-align: center;
            padding-bottom: 3%;
            line-height: 16px;
            font-size: 12px;
            color: #303840;
          }
        </style>
      </head>
    </html>"""

    ##

    body = f"""\
    <!DOCTYPE html>
    <html lang="en">
      <body>
        <div id="wrapper">
          <header>
            <div id="logo">
              <img
                src="https://download.logo.wine/logo/Premier_League/Premier_League-Logo.wine.png"
                alt=""
              />
            </div>
          </header>
          <div id="banner">
            <img
              src="https://www.massivemusic.com/data/content/uploads/images/projects/thumbnails/_size_1280_630/Premier-League-Rebranding-THUMB.jpg?mtime=20171212164459"
              alt=""
            />
          </div>
          <br />

          <div class="one-col">
            <h2> {today}  <br /> <br /> <br /> Another fascinating day in the Premier League! <br /> </h2>
            <br />
            <h3> Fixtures for today: </h3>
            <br /> 
            <p>{today_matches_html} <br /> </p>

            <h3> The results of the previous games (Round {prev_round}) <br /> </h3>
            <br />   
            <p>{last_matches_html} <br /> </p>
            <br />
            <h3>The English Premier League team ranking after {prev_round} rounds: </h3>

            <img src="points.jpg">

            <br />
            <center>
            <a href="https://www.premierleague.com/matchweek/7833/blog" class="btn">Learn more</a>
            </center>
            <hr />

            <footer>
              <p id="contact">
                Robert Lewandowski <br />
                robert.rl.lewandowski@gmail.com
              </p>
            </footer>
          </div>
        </div>
      </body>
    </html>
    """

    content = head + body
    return content

# Execute code to be provided with the e-mail address

today_matches_html = provide_html_today(df_today)
last_matches_html = provide_html_last(prev_round)
update_plots()
content = prepare_email()

if len(df_today) > 0:
  today_matches_html = provide_html_today(df_today)
  last_matches_html = provide_html_last(prev_round)
  update_plots()
  content = prepare_email()
  send_email()
else:
  pass
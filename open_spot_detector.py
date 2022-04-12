"""
made by zack sating
i used this article for the emailing: https://realpython.com/python-send-email/
& the rest of the code i know

future to-do: turn this into an extension so can be used easily in a browser 
"""

from bs4 import BeautifulSoup as bs # webscraping
import requests as rq # web requests
from webbrowser import open # opening browswer
import smtplib, ssl # for sending emails
import asyncio # for sleeping
from datetime import datetime # for debugging
from dotenv import load_dotenv
from os import getenv



##
# gets the number of seats in a specific course
##
def get_num_seats(courseID, sectionID, termID):
  url = f"https://app.testudo.umd.edu/soc/search?courseId={courseID}&sectionId={sectionID}&termId={termID}&_openSectionsOnly=on&creditCompare=&credits=&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on"
  
  try:
    page = rq.get(url)
  except Exception as e:
    print(f"error getting testudo data:\n{e}")
  
  soup = bs(page.text, features="lxml")

  numseats = soup.find_all("span","open-seats-count")[0].get_text()
  professor = soup.find_all("span","section-instructor")[0].get_text()
  numwaitlist = soup.find_all("span", "waitlist-count")[0].get_text()

  return int(numseats), url, professor, int(numwaitlist)



##
# sends email notification in case user is away from computer: 
# if you have 2factor auth then follow this and use the 
# password from here:  https://support.google.com/accounts/answer/185833?p=InvalidSecondFactor
##
async def send_notification_email(courseID, professor, numseats):
  load_dotenv()
  address = getenv('email_address')
  password = getenv('email_password')

  msg = f"Subject: {courseID} {professor}\n\nthere's {numseats} spots left now"

  with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as server:
    server.login(address, password)
    server.sendmail(address, address, msg) # from, to, message



##
# loops until condition is detected (usually when a seat in a course opens up)
# and sends an email to user and opens up Testudo in the browser of the user
#
# if invalid input, the url will be opened to what the user specified, improve this later
##
async def main():
  
  count = 1
  courseID, sectionID, termID = "STAT401", "0201", "202201"
  
  # run indefinitely until detects open spot
  while True:
    try:
      
      numseats, url, professor, numwaitlist = get_num_seats(courseID, sectionID, termID)
      print(numseats)

      if numseats == -1:
        print(f"sectionId not valid: {sectionID}\n, retrying...\n")
        open(url)
        continue

      elif numseats != 0:

        # open in browser, only do for extension
        open(url)
        await send_notification_email(courseID, professor, numseats)

        # exit loop since done
        print("found seat(s)\nbreaking loop; finishing process")
        break

      # else pause for a minute and then check again
      else:
        time = datetime.now().strftime("%H:%M:%S")
        print(f"check {count}: {time}\n\topen: {numseats}\twaitlist: {numwaitlist}")
        count += 1 ## the -2 above is hardcoded bc cringe
        await asyncio.sleep(30)

    except Exception as e:
      print(e)
      pass

          

# this structure is weird? so probably change it 
if __name__ == '__main__':
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    print("\nstopped by user")
  except Exception as e:
    print(e)

# the end!
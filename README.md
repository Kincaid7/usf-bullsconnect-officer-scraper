Officer Contact Scraper & Google Contacts Importer
This tool allows you to scrape officer contact data from BullsConnect, generate a clean HTML directory, and prepare a CSV file suitable for import into Google Contacts. Officer profile images are also downloaded and stored locally.
NOTE: This program was designed for use by The European Society at USF. Labels generated in the CSV are done with that use-case in mind. You will have to tweak both the labels generated, as well as the links to the officer pages to reflect the use case you intend. ChatGPT should be able to hold your hand through such modifications.
________________________________________
🚀 Setup Instructions (Baby-Proofed)
1. Install Python (If Not Already Installed)
•	Go to https://www.python.org/downloads/
•	Download the latest version for your OS
•	During installation, make sure to check the box that says "Add Python to PATH"
•	Open a terminal/command prompt and run:
python --version
You should see something like Python 3.12.x
________________________________________
2. Download This Project
•	Download the ZIP or clone the repository.
•	Extract the folder and open it in File Explorer or your terminal.
________________________________________
3. Set Up a Virtual Environment
•	In the folder with scrape_usf.py, run:
python -m venv venv
•	Then activate it:
venv\Scripts\activate   # Windows
You should see (venv) at the start of your terminal prompt.
________________________________________
4. Install Dependencies
Make sure you’re in the usf-scraper directory and run
pip install -r requirements.txt
If you get an error saying pip not found, make sure Python is installed correctly and added to PATH.
________________________________________
5. Download Microsoft Edge WebDriver
•	Go to: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
•	Download the driver that matches your Microsoft Edge version (check edge://settings/help)
•	Extract and place msedgedriver.exe into the same folder as scrape_usf.py
________________________________________
🧩 How to Use
Step 1: Start the Script
python scrape_usf.py
You’ll see:
🔤 Opening BullsConnect...
🕰️ After login completes, press ENTER here to continue...
Wait for the Edge window to open and log in manually. After logging in, return to the terminal and press ENTER.
________________________________________
Step 2: Let It Run
The script will:
•	Visit each club’s officer page
•	Collect their info
•	Sort and organize contacts
•	Create:
o	officers.html directory
o	club_contacts.csv file
o	officer_photos/ folder with image files named by email
________________________________________
Step 3: Import to Google Contacts
1.	Go to contacts.google.com
2.	Click Import on the left side
3.	Upload the generated club_contacts.csv
4.	Contacts will be added with emails, roles, and labels like:
o	European Society E-Boards ::: European Society RoleNames ::: ClubName Officers
________________________________________
🖼️ Optional: Add Profile Photos (Manual Method)
Step A: Upload Photos
1.	Go to drive.google.com
2.	Create a folder called: Officer Profile Photos
3.	Upload everything inside the officer_photos/ folder
Step B: Assign Them to Contacts
•	Open each contact in Google Contacts manually
•	Click the profile image circle
•	Select "Upload Photo"
•	Choose the image with their email address as filename
You can also bulk add using Google Workspace tools or 3rd-party APIs.
________________________________________
🔧 Tweaking the Script
✅ To Add New Clubs
•	Open scrape_usf.py
•	Scroll to club_urls = [ ... ]
•	Paste in new BullsConnect officer tabs
✅ To Sort Officers Differently
•	Edit the ROLE_ORDER list:
ROLE_ORDER = ["President", "Vice President", "Treasurer", "Secretary"]
✅ To Change Contact CSV Format
•	Modify the csv_writer.writerow([...]) section
•	This includes what data goes in each column and the column headers
✅ To Skip Default Placeholder Photos
•	Already built in: skips any image containing:
/images/ico/female_user_large.png
/images/ico/male_user_large.png
•	This avoids saving default blank images
________________________________________
📁 Output Summary
File/Folder	Purpose
scrape_usf.py	The main scraping script
officers.html	Clean, styled visual directory
club_contacts.csv	Ready to import to Google Contacts
/officer_photos/	Officer profile photos, named by email
________________________________________
👥 Made With Love
Created by Abraham Smitz & ChatGPT 🤝
________________________________________
📌 For Future You
If Google changes the Contacts CSV format:
•	Visit: Google’s guide
•	Double check the column headers and order
If WebDriver or the BullsConnect layout changes:
•	You might need to re-check element selectors (use F12 DevTools)
•	Update scraping logic accordingly
Stay fly 🦅


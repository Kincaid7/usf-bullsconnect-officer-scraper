from selenium import webdriver                                # Main Selenium driver
from selenium.webdriver.edge.service import Service as EdgeService  # For Edge browser
from selenium.webdriver.edge.options import Options as EdgeOptions  # Edge options
from selenium.webdriver.common.by import By                  # Needed for clicking tabs by XPath
from bs4 import BeautifulSoup                                # For parsing HTML
import time                                                  # For pauses
from collections import defaultdict                          # For grouping officers


# Officer role sorting priority
ROLE_ORDER = [
    "President",
    "Vice-President",
    "Vice President",
    "Treasurer",
    "Secretary",
    "Advisor"
]

def sort_officers(officers):
    def get_priority(position):
        if position in ROLE_ORDER:
            return ROLE_ORDER.index(position)
        elif position.lower() == "officer":
            return len(ROLE_ORDER) + 1  # Officer goes dead last
        else:
            return len(ROLE_ORDER)      # Custom titles come just before Officer

    return sorted(officers, key=lambda o: get_priority(o["position"]))

# === SETUP EDGE ===
options = EdgeOptions()
options.add_argument("--log-level=3")  # Suppresses most logging
options.add_argument("--disable-logging")
options.add_argument("--disable-gpu")  # You already had this
options.add_experimental_option("excludeSwitches", ["enable-logging"])


service = EdgeService(executable_path="msedgedriver.exe")
driver = webdriver.Edge(service=service, options=options)

# === LOGIN FIRST ===
print("🔤 Opening BullsConnect...\n")
driver.get("https://bullsconnect.usf.edu/")
input("🕰️ After login completes, press ENTER here to continue...\n")
print("⏳ Scraping officer info from club pages. Please hold...\n")

# === CLUB URLS TO SCRAPE ===
club_urls = [
    "https://bullsconnect.usf.edu/feeds?type=club&type_id=71725&tab=officers",
    "https://bullsconnect.usf.edu/feeds?type=club&type_id=58067&tab=officers",
    "https://bullsconnect.usf.edu/feeds?type=club&type_id=71500&tab=officers",
    "https://bullsconnect.usf.edu/feeds?type=club&type_id=58047&tab=officers",
    "https://bullsconnect.usf.edu/feeds?type=club&type_id=58175&tab=officers",
    "https://bullsconnect.usf.edu/feeds?type=club&type_id=58631&tab=officers",
    "https://bullsconnect.usf.edu/feeds?type=club&type_id=71550&tab=officers",
    "https://bullsconnect.usf.edu/feeds?type=club&type_id=71437&tab=officers",
    #"https://bullsconnect.usf.edu/feeds?type=club&type_id=NEW ID&tab=officers",
    #"https://bullsconnect.usf.edu/feeds?type=club&type_id=NEW ID&tab=officers",
]

all_officers = []
club_links = {}  # maps club name to their page URL

# === SCRAPE EACH CLUB ===
for url in club_urls:
    driver.get(url)
    time.sleep(3)

    # === Ensure we're on the Officers tab ===
    soup = BeautifulSoup(driver.page_source, "html.parser")
    if not soup.select("li.list-group-item"):
        try:
            print("🔄 Attempting to manually switch to Officers tab using JS...")
            type_id = url.split("type_id=")[-1].split("&")[0]
            driver.execute_script(f"clickFeedTopTab({type_id}, 'officers')")
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
        except Exception as e:
            print(f"⚠️ Could not switch to Officers tab for {url}: {e}")
            continue  # skip this club


    # Get club name
    club_name_tag = soup.select_one("div.feed__top-title__name span")
    club_url = driver.current_url.replace("&tab=officers", "&tab=about")  # grab the about page URL
    club_name = club_name_tag.get_text(strip=True) if club_name_tag else "Unknown Club"

    club_links[club_name] = club_url  # NEW dictionary you'll define earlier

    # Get club logo
    club_logo_tag = soup.select_one("div.feed__top-title__img img")
    logo_src = club_logo_tag['src'] if club_logo_tag and 'src' in club_logo_tag.attrs else ""
    if logo_src.startswith("/"):
        logo_src = "https://bullsconnect.usf.edu" + logo_src

    for li in soup.select("li.list-group-item"):
        name_tag = li.select_one("h2.media-heading")
        email_tag = li.select_one("a[href^=mailto]")
        position_tag = li.select_one("strong")
        image_tag = li.select_one("img.img-user")

        name = name_tag.get_text(strip=True) if name_tag else None
        email = email_tag['href'].replace('mailto:', '') if email_tag and 'href' in email_tag.attrs else None
        position = position_tag.get_text(strip=True) if position_tag else None
        img_src = image_tag['src'] if image_tag else None

        if name and email and position and "[firstName]" not in name:
            if img_src and img_src.startswith("/"):
                img_src = "https://bullsconnect.usf.edu" + img_src

            all_officers.append({
                "club": club_name,
                "logo": logo_src,
                "name": name,
                "email": email,
                "position": position,
                "default_img": not img_src,
                "img": img_src or "https://bullsconnect.usf.edu/images/listing-default.png"

            })

driver.quit()

# === DOWNLOAD AND STORE OFFICER CONTACT PHOTOS FOR OPTIONAL IMPORT LATER ===
import requests
import os
import shutil

photos_dir = "officer_photos"

# Ensure the folder is clean on each run
if os.path.exists(photos_dir):
    shutil.rmtree(photos_dir)
os.makedirs(photos_dir, exist_ok=True)

# These fragments identify default placeholder profile images and should be skipped
default_img_fragments = [
    "male_user_large.png",
    "female_user_large.png"
]

for officer in all_officers:
    img_url = officer["img"]
    email = officer["email"]

    # Skip default placeholder images and officers without email or image
    if (
        img_url
        and email
        and not any(fragment in img_url for fragment in default_img_fragments)
    ):
        try:
            response = requests.get(img_url)
            if response.status_code == 200:
                # Extract extension from image URL, safely truncated
                ext = img_url.split(".")[-1].split("?")[0][:4]
                filename = os.path.join(photos_dir, f"{email}.{ext}")
                with open(filename, "wb") as img_file:
                    img_file.write(response.content)
        except Exception as e:
            # Log download errors (e.g., network issues or 404s)
            print(f"Error downloading {img_url}: {e}")

# === GROUP OFFICERS BY CLUB ===
temp_grouped = defaultdict(list)
club_logos = {}

for officer in all_officers:
    temp_grouped[officer["club"]].append(officer)
    club_logos[officer["club"]] = officer.get("logo", "")

# Sort the officers per club
grouped = {club: sort_officers(officers) for club, officers in temp_grouped.items()}

# === Prepare CSV for Google Contacts ===
import csv
import io

csv_buffer = io.StringIO()
csv_writer = csv.writer(csv_buffer)

# Google Contacts format
csv_writer.writerow([
    "First Name", "Middle Name", "Last Name", "Phonetic First Name", "Phonetic Middle Name",
    "Phonetic Last Name", "Name Prefix", "Name Suffix", "Nickname", "File As",
    "Organization Name", "Organization Title", "Organization Department", "Birthday",
    "Notes", "Photo", "Labels", "E-mail 1 - Label", "E-mail 1 - Value", 
    "E-mail 2 - Label", "E-mail 2 - Value"
])

def pluralize_position(position):
    """Basic pluralization for common roles."""
    # Handle special cases or just add 's'
    position = position.strip()
    if position.lower().endswith("y"):
        return position[:-1] + "ies"
    elif position.lower().endswith("s"):
        return position + "es"
    else:
        return position + "s"

standard_roles = {"President", "Vice-President", "Treasurer", "Secretary", "Advisor"}

for officer in all_officers:
    full_name = officer["name"]
    first, last = (full_name.split(" ", 1) + [""])[:2]

    # Construct labels
    club_officer_label = f"{officer['club']} Officers"
    base_board_label = "ES Officers"

    position = officer["position"].strip()
    if position in standard_roles:
        role_plural_label = f"ES {pluralize_position(position)}"
    else:
        role_plural_label = "ES Other Officers"

    labels = f"{club_officer_label} ::: {base_board_label} ::: {role_plural_label}"


    csv_writer.writerow([
        first,                     # First Name
        "",                        # Middle Name
        last,                      # Last Name
        "", "", "", "", "", "",    # Phonetic names, prefixes, etc.
        "",                        # File As
        officer["club"],           # Organization Name
        officer["position"],       # Organization Title
        "",                        # Organization Department
        "",                        # Birthday
        f"Photo: {officer['img']}",# Notes (include photo URL here)
        "",                        # Photo (not supported by Google)
        labels,                    # Labels (now properly formatted)
        "*",                       # E-mail 1 - Label
        officer["email"],          # E-mail 1 - Value
        "",                        # E-mail 2 - Label
        ""                         # E-mail 2 - Value
    ])

html_csv_data = csv_buffer.getvalue().strip().replace('\r\n', '\\n').replace('"', '\\"')
#csv_data = csv_buffer.getvalue().replace('\n', '\\n').replace('"', '\\"')  #  for HTML embed

# === SAVE CSV LOCALLY===
try:
    with open("club_contacts.csv", "w", encoding="utf-8", newline='') as f:
        f.write(csv_buffer.getvalue())
except PermissionError:
    print("❌ ERROR: Please close 'club_contacts.csv' before running the script again.")


# === BUILD HTML ===
html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset=\"UTF-8\">
    <title>Officer Contacts</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f9f9f9; padding: 20px; }
        h1 { text-align: center; }
        h2 { color: #00703C; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 40px; display: flex; align-items: center; gap: 10px; }
        .logo { height: 2rem; width: 2rem; border-radius: 5px; background: white; }
        .grid { display: flex; flex-wrap: wrap; gap: 20px; justify-content: flex-start; }
        .card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            width: 250px;
            padding: 15px;
            text-align: center;
        }
        img.profile {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;d
            margin-bottom: 10px;
        }
        .name { font-weight: bold; font-size: 18px; }
        .position { color: #00703C; font-weight: 600; }
        .email { color: #444; font-size: 14px; }
        .email-link {
            color: #444;
            text-decoration: none;
        }

        .email-link:hover {
            text-decoration: underline;
        }

	.club-link {
            text-decoration: none;
            color: inherit;
        }
        .club-link:hover {
            text-decoration: underline;
        }

    </style>
</head>
<body>
    <h1>Officer Contacts</h1>
"""

html_content += f"""
    <button onclick="downloadCSV()" style='margin-bottom: 20px; padding: 10px 15px; background: #00703C; color: white; border: none; border-radius: 5px; cursor: pointer;'>
        Download CSV
    </button>
<p style="margin-top: 0; color: #444; font-size: 14px;">
    This CSV is formatted for importing into Google Contacts
</p>
    <script>
        function downloadCSV() {{
            // const csvData = `{{csv_data}}`; //
            const csvData = `{html_csv_data}`;
            const blob = new Blob([csvData], {{ type: 'text/csv;charset=utf-8;' }});
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.setAttribute('href', url);
            link.setAttribute('download', 'club_contacts.csv');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // Prompt to open Google Contacts
            if (confirm("Would you like to open Google Contacts to import this CSV?")) {{
                window.open("https://contacts.google.com/", "_blank")
            }} else {{
                // Optional: you can log or leave this empty
                console.log("User chose not to open Google Contacts.");
            }}
        }}
    </script>
"""

for club, officers in grouped.items():
    if officers:
        logo = club_logos.get(club, "")
        logo_html = f'<img src="{logo}" class="logo" alt="{club} logo">' if logo else ""
        club_url = club_links.get(club, "#")
        html_content += f"<h2><a href=\"{club_url}\" target=\"_blank\" class=\"club-link\">{logo_html} {club}</a></h2>\n<div class='grid'>\n"

        for officer in officers:
            html_content += f"""
            <div class=\"card\">
                <img src=\"{officer['img']}\" alt=\"{officer['name']}\" class=\"profile\">
                <div class=\"name\">{officer['name']}</div>
                <div class=\"position\">{officer['position']}</div>
                <div class=\"email\">
                    <a href=\"mailto:{officer['email']}\" class=\"email-link\">{officer['email']}</a>
                </div>

            </div>
            """
        html_content += "</div>\n"

html_content += """
</body>
</html>
"""

# === SAVE TO FILE ===
with open("officers.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ officers.html created\n✅ club_contacts.csv created\n✅ officers_photos folder created\n\n      You can see contact info for each clubs eboard.\n      You can easily import the contact list into Google Contacts using the download CSV button!")

#OPENS FILE
import webbrowser
import os

file_path = os.path.abspath("officers.html")
webbrowser.open(f"file://{file_path}")
import instaloader
import mysql.connector
import time
import random
import re
from instaloader.exceptions import PrivateProfileNotFollowedException
import urllib3
import http.client
import urllib.request

def run_instaleads(target_username, db_config):
    # Set Instaloader
    L = instaloader.Instaloader()

    # Set custom User-Agent string
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36,gzip(gfe)',
        'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 13; SM-S901U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 13; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 12; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
    ]

    def get_random_user_agent():
        return random.choice(user_agents)

    # Set custom opener with User-Agent header
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', get_random_user_agent())]
    urllib.request.install_opener(opener)

    # Create a MySQL connection
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    # Create a table name based on the target username
    table_name = f"instagram_followers_{target_username}"

    # Create the table if it doesn't exist
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255),
            full_name VARCHAR(255),
            phone_number TEXT,
            website VARCHAR(255)
        )
    """)

    # Login to Instagram
    username = "usuario"
    password = "senha"
    L.login(user=username, passwd=password)

    # Find the target account
    while True:
        try:
            profile = instaloader.Profile.from_username(L.context, target_username)
            break
        except instaloader.exceptions.QueryReturnedBadRequestException:
            print("Error: 400 Bad Request. Retrying in 10 seconds...")
            time.sleep(10)

    # Get the followers
    followers = profile.get_followers()

    # Set a random delay between 60-70 seconds for each request
    delay_range = (60, 70)

    # Retrieve follower information
    for follower in followers:
        try:
            # Get the follower's profile
            follower_profile = instaloader.Profile.from_username(L.context, follower.username)

            phone_number_match = re.search(r'\+?\d{1,2}\s?\(?\d{2,3}\)?[\s.-]?\d{3,4}[\s.-]?\d{4}', follower_profile.biography)

            if phone_number_match:
                phone_number = phone_number_match.group()  # Get the matched phone number as a string
            else:
                phone_number = None  # Set phone number to None if not found
            
            # Insert the data into the MySQL database
            cursor.execute(f"""
                INSERT INTO `{table_name}` (username, full_name, phone_number, website)
                VALUES (%s, %s, %s, %s)
            """, (
                follower.username,
                follower_profile.full_name,
                phone_number,
                follower_profile.external_url
            ))

            # Commit the changes
            cnx.commit()

            # Random delay between requests
            time.sleep(random.uniform(*delay_range))

        except PrivateProfileNotFollowedException:
            print(f"Skipping private account: {follower.username}")
            continue
        except Exception as e:
            print(f"Error processing {follower.username}: {str(e)}")
            continue

    # Close the cursor and connection
    cursor.close()
    cnx.close()

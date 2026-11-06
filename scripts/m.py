from requests import get
from os import getenv
import random
from dotenv import load_dotenv
load_dotenv()
strings = "Thank you Mistress Lina"
new_string = ""
for stri in strings:
    choice = random.choice([True, False])
    if choice == True:
        new_string += stri
    else:
        new_string += ""
print (new_string)
token = getenv("TOKEN")
req = get("https://discord.com/api/v10/users/523964745792094254", headers={"Authorization": f"Bot {token}"})
print (req.json())
from whtfuncs import *
from config import *
from selenium import webdriver

# Open session to avoid QR code scanning every time
browser = open_chrome(chrome_profile_path)

# Iterate unread messages with a infinite loop
iterate_messages_loop(browser)

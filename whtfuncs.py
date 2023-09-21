import pywhatkit as whatkit
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import re
from webdriver_manager.chrome import ChromeDriverManager
from config import chrome_profile_path #Importar perfil autorizado Chrome

#-----------------PyWhatKit FUNCTIONS---------------
def message_new_client_loop(clients, processedClients):
    while True:
        for client in clients:
            if (client['phone'], client['course']) not in processedClients:
                message = f"Hello {client['name']}. \nThank you for purchasing the course: {client['course']}!"
                localTime = time.localtime()
                hour, minute = localTime.tm_hour, localTime.tm_min
                
                # minute overflow correction
                if minute > 59:
                    hour += 1
                    
                # Try to send message 2 minutes after loop execution
                try:
                    whatkit.sendwhatmsg(client['phone'], message, hour, minute + 2, 8, tab_close=True, close_time=2)
                    time.sleep(60)  # interval to avoid bugs
                    processedClients.append((client['phone'], client['course']))  # Mark client + course as processed
                except Exception as e:
                    print(f"Failed to send to {client['name'], client['phone']}. Error: {e}")
        time.sleep(1800)


def msg_with_image_loop(clients, processedClients, imagePath, professor):
    while True:
        for client in clients:
            if (client['phone'], client['course']) not in processedClients:
                message = f"Hello {client['name']} Congratulations on purchasing the course: {client['course']}\n Check out more courses from {professor}."

                try:
                    whatkit.sendwhats_image(client['phone'], imagePath, message, wait_time=18, tab_close=True, close_time=2)
                    time.sleep(120)  # interval to avoid bugs
                    processedClients.append((client['phone'], client['course']))  # Mark client + course as processed
                except Exception as e:
                    print(f"Failed to send to {client['name'], client['phone']}. Error: {e}")
        time.sleep(1800)


#------------SELENIUM FUNCTIONS----------

def open_chrome(chrome_profile_path):
    options = webdriver.ChromeOptions()
    options.add_argument(chrome_profile_path)
    options.add_experimental_option("detach", True)
    browser = webdriver.Chrome(options=options)
    browser.maximize_window()
    browser.get("https://web.whatsapp.com")
    wait = WebDriverWait(browser, 20)  # wait for up to 20 seconds
    wait.until(expected_conditions.presence_of_all_elements_located((By.XPATH, '/html/body/div[1]/div/div/div[4]/div/div[2]')))
    return browser


def xpath_unread(index):
    return f'/html/body/div[1]/div/div/div[4]/div/div[2]/div/div/div/div[{index}]/div/div/div/div[2]/div[2]/div[2]/span[1]/div/span'

def unread_message_content(index):
    return f'/html/body/div[1]/div/div/div[4]/div/div[2]/div/div/div/div[{index}]/div/div/div/div[2]/div[2]/div[1]/span/span'

def sender_number(index):
    return f'/html/body/div[1]/div/div/div[4]/div/div[2]/div/div/div/div[{index}]/div/div/div/div[2]/div[1]/div[1]/span'


def format_num_dic(number):
    return re.sub(r"[^0-9+]", "", number)

def format_num_reply(number):
    return f'"{number}"'

def iterate_messages(browser):
    returnDict = {}

    for i in range(1, 11):
        xpath = xpath_unread(i)
        unread = browser.find_elements(By.XPATH, xpath)
        
        if unread:  
            content_xpath = unread_message_content(i)
            unread_message_content = browser.find_element(By.XPATH, content_xpath).text
            xpath_string = sender_number(i)
            sender_number = browser.find_element(By.XPATH, xpath_string).text
                
            if unread_message_content == "-test":
                target = format_num_reply(sender_number)
                text = 'Whatsapp system test'
                
                # Click on the chat/group using the target (phone number)
                x_arg = '//span[contains(@title,' + target +')]'
                group_title = WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.XPATH, x_arg)))
                group_title.click()
                
                # Send the message
                input_xpath = '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p'
                input_box = WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.XPATH, input_xpath)))
                input_box.send_keys(text + Keys.ENTER)
                time.sleep(5)
        
            # Store the values in the dictionary as a simple string, to send users on route depending on choice
            returnDict[i] = {
                "phone_number": format_num_dic(sender_number),
                "new_msg": unread_message_content
            }
            
    return returnDict


def iterate_messages_loop(browser):
    while True:
        try:
            iterate_messages(browser)
            time.sleep(15)  # Sleep for 15 seconds before checking again
        except Exception as e:
            print(f"Erro: {e}")
            break

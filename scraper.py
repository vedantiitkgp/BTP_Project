from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import sys
import time
import calendar
import utils
import urllib.request
import requests
import shutil
from settings import BROWSER_EXE, FIREFOX_BINARY, GECKODRIVER, PROFILE
import os


class CollectPosts(object):
    """Collector of recent FaceBook posts.
           Note: We bypass the FaceBook-Graph-API by using a 
           selenium FireFox instance! 
           This is against the FB guide lines and thus not allowed.
    """

    def __init__(self, ids=["oxfess"], file="posts.csv", depth=5, delay=5,number_posts=10):
        self.ids = ids
        self.out_file = file
        self.depth = depth + 1
        self.delay = delay
        self.number_posts = number_posts 
        # browser instance
        self.browser = webdriver.Firefox(executable_path=GECKODRIVER,
                                         firefox_binary=FIREFOX_BINARY,
                                         firefox_profile=PROFILE,)
        utils.create_csv(self.out_file)

    def scroller(self):
        # Scroll down depth-times and wait delay seconds to load
        # between scrolls
        time.sleep(self.delay)
        for scroll in range(self.depth):
            # Scroll down to bottom
            old_height = self.browser.execute_script("return document.body.scrollHeight;")
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #Wait to load the page
            time.sleep(self.delay)
            new_height = self.browser.execute_script("return document.body.scrollHeight;")
            if(new_height==old_height):
                return False
        return True
    
    def infinite_scroller(self):
        # Scroll down to infinte depth and wait delay seconds to load
        # between scrolls
        time.sleep(self.delay)
        while(1):
            # Scroll down to bottom
            old_height = self.browser.execute_script("return document.body.scrollHeight;")
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #Wait to load the page
            time.sleep(self.delay)
            new_height = self.browser.execute_script("return document.body.scrollHeight;")
            if(new_height==old_height):
                break

    def image_and_video_downloader(self,image_url,media_dir,counter):
        self.browser.get(image_url)
        time.sleep(3)
        try:
            image_element = self.browser.find_element_by_xpath("//*[@data-visualcompletion='media-vc-image']")
            image_url_new = image_element.get_attribute('src')
            urllib.request.urlretrieve(image_url_new,media_dir+"/photo"+str(counter)+".jpg")
        except:
            pass

    def collect_page(self, page):
        
        # navigate to page
        print(page)
        self.browser.get('https://www.facebook.com/' + page + '/')
        time.sleep(5)

        parent_dir = os.getcwd()
        main_dir = os.path.join(parent_dir,"Profiles")
        profile_dir = os.path.join(main_dir,page)
        if not os.path.exists(profile_dir):
            os.mkdir(profile_dir)
    
        ##### Photos and Videos #######
        self.browser.get("https://www.facebook.com/"+page+"/photos_of/")
        time.sleep(5)
        self.infinite_scroller()
        media_elements = self.browser.find_elements_by_xpath ("//*[@class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 a8c37x1j p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 datstx6m l9j0dhe7 k4urcfbm']")
        
        media_dir = os.path.join(profile_dir,"Media")
        if not os.path.exists(media_dir):
            os.mkdir(media_dir)
          
        media_links =[]
        for media_element in media_elements:
            media_links.append(media_element.get_attribute('href'))
        
        self.browser.get("https://www.facebook.com/"+page+"/photos_all/")
        time.sleep(5)
        self.infinite_scroller()
        media_elements = self.browser.find_elements_by_xpath ("//*[@class='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 a8c37x1j p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 datstx6m l9j0dhe7 k4urcfbm']")
        
        for media_element in media_elements:
            media_links.append(media_element.get_attribute('href'))
        
        count=0
        for media_link in media_links:
            self.image_and_video_downloader(media_link,media_dir,count)
            count = count + 1
        print("Media done")
      
        ###### Friends ###########

        self.browser.get('https://www.facebook.com/'+page+'/friends/')
        number_friends = 200
        count =0
        counter =0
        file1 = open(profile_dir+"/friends.txt","w+")
        friends_list = []
        self.infinite_scroller()
        friend_elements = self.browser.find_elements_by_xpath("//*[@class='buofh1pr hv4rvrfc']//*[@role='link']")
        while(1):
            if "mutual" not in friend_elements[counter].text:
                friends_list.append(f"{friend_elements[counter].text} | {friend_elements[counter].get_attribute('href')} \n")
                count = count + 1
                if(count==number_friends):
                    break
            counter = counter +1
            if(counter==len(friend_elements)):
                break
        file1.writelines(friends_list)
        file1.close()
        print("Friends done")
        
        ##### About #####
        file2 = open(profile_dir+"/about.txt","w")

        file2.write("\n1. Overview\n\n\n")
        self.browser.get('https://www.facebook.com/'+page+'/about/')
        time.sleep(3)
        overview_element = self.browser.find_element_by_xpath("//*[@class='buofh1pr']")
        file2.write(overview_element.text)

        file2.write("\n\n\n2. Work and Educations\n\n\n")
        self.browser.get('https://www.facebook.com/'+page+'/about_work_and_education/')
        time.sleep(3)
        work_and_education_element = self.browser.find_element_by_xpath("//*[@class='buofh1pr']")
        file2.write(work_and_education_element.text)

        file2.write("\n\n\n3. Places Lived\n\n\n")
        self.browser.get('https://www.facebook.com/'+page+'/about_places/')
        time.sleep(3)
        places_element = self.browser.find_element_by_xpath("//*[@class='buofh1pr']")
        file2.write(places_element.text)

        file2.write("\n\n\n4. Contacts and Basic info\n\n\n")
        self.browser.get('https://www.facebook.com/'+page+'/about_contact_and_basic_info/')
        time.sleep(3)
        contacts_element = self.browser.find_element_by_xpath("//*[@class='buofh1pr']")
        file2.write(contacts_element.text)

        file2.write("\n\n\n5. Family and relationships\n\n\n")
        self.browser.get('https://www.facebook.com/'+page+'/about_family_and_relationships/')
        time.sleep(3)
        family_element = self.browser.find_element_by_xpath("//*[@class='buofh1pr']")
        file2.write(family_element.text)

        file2.write("\n\n\n6. Details\n\n\n")
        self.browser.get('https://www.facebook.com/'+page+'/about_details/')
        time.sleep(3)
        details_element = self.browser.find_element_by_xpath("//*[@class='buofh1pr']")
        file2.write(details_element.text)

        file2.write("\n\n\n7. Life Events\n\n\n")
        self.browser.get('https://www.facebook.com/'+page+'/about_life_events/')
        time.sleep(3)
        life_element = self.browser.find_element_by_xpath("//*[@class='buofh1pr']")
        file2.write(life_element.text)
        file2.close()
        print("About element done")

        #### Intro element ###
        self.browser.get('https://www.facebook.com/' + page + '/')
        time.sleep(5)
        file3 = open(profile_dir+"/intro.txt","w")
        intro_element = self.browser.find_element_by_xpath("//*[@data-pagelet='ProfileTilesFeed_0']")
        file3.write(intro_element.text)
        file3.close()
        print("Intro element done")

        #### Posts #####
        file4_name = profile_dir+"/posts.csv"
        # Loading the first post and start scrolling
        element = self.browser.find_element_by_xpath(f"//*[@aria-posinset='1']")
        self.browser.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(5)
        counter = 1
        for count in range(1,self.number_posts):
            analysis = []
            try:
                element = self.browser.find_element_by_xpath(f"//*[@aria-posinset='{count}']")
                self.browser.execute_script("arguments[0].scrollIntoView();", element)
            except:
                time.sleep(5)
                try:
                    element = self.browser.find_element_by_xpath(f"//*[@aria-posinset='{count}']")
                    self.browser.execute_script("arguments[0].scrollIntoView();", element)
                except:
                    break

            #Checking for see more in the post
            xpath = "//div[text()='See more']"
            try:
                link = self.browser.find_element_by_xpath(xpath)
                link.click()
            except:
                pass

            #Checking for text and media sub element in the post
            try:
                new_element = element.find_element_by_xpath(".//*[@data-ad-preview]")
                time_xpath = ".//*[@class='buofh1pr']//*[@aria-label and @role='link' and @tabindex]"
                media_xpath = ".//*[contains(@class, 'i09qtzwb n7fi1qx3 datstx6m')]"
                photo_links = []
                video_links = []
                #Checking for media (if not photo then video)
                try:
                    photo_elements = element.find_elements_by_xpath(media_xpath)
                    for i in range(len(photo_elements)):
                        photo_links.append(photo_elements[i].get_attribute('src'))
                except:
                    pass
                try:
                    video_xpath = media_xpath+"//*[video]//*[@style]"
                    video_elements = element.find_elements_by_xpath(video_xpath)
                    for i in range(len(video_elements)):
                        video_links.append(video_elements[i].get_attribute('src'))
                except:
                    pass
                time_element = element.find_element_by_xpath(time_xpath)
                analysis.append(f"Post {counter}  ")
                analysis.append(time_element.get_attribute('aria-label'))
                analysis.append(new_element.text)
                analysis.append(photo_links)
                analysis.append(video_links)
                counter = counter+1
                utils.write_to_csv(file4_name, analysis)
            except:
                pass
            
            time.sleep(self.delay)
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("Posts done")
        

    def collect(self, type):
        if type == "groups":
            for iden in self.ids:
                self.collect_groups(iden)
        elif type == "pages":
            for iden in self.ids:
                self.collect_page(iden)
        self.browser.close()

    def safe_find_element_by_id(self, elem_id):
        try:
            return self.browser.find_element_by_id(elem_id)
        except NoSuchElementException:
            return None

    def login(self, email, password):
        try:

            self.browser.get("https://www.facebook.com")
            self.browser.maximize_window()

            # filling the form
            self.browser.find_element_by_name('email').send_keys(email)
            self.browser.find_element_by_name('pass').send_keys(password)

            # clicking on login button
            try:
                # clicking on login button
                self.browser.find_element_by_id("loginbutton").click()
            except NoSuchElementException:
                # Facebook new design
                self.browser.find_element_by_name("login").click()
            # if your account uses multi factor authentication
            mfa_code_input = self.safe_find_element_by_id('approvals_code')

            if mfa_code_input is None:
                return

            mfa_code_input.send_keys(input("Enter MFA code: "))
            self.browser.find_element_by_id('checkpointSubmitButton').click()

            # there are so many screens asking you to verify things. Just skip them all
            while self.safe_find_element_by_id('checkpointSubmitButton') is not None:
                dont_save_browser_radio = self.safe_find_element_by_id('u_0_3')
                if dont_save_browser_radio is not None:
                    dont_save_browser_radio.click()

                self.browser.find_element_by_id(
                    'checkpointSubmitButton').click()

        except Exception as e:
            print("There was some error while logging in.")
            print(sys.exc_info()[0])
            exit()

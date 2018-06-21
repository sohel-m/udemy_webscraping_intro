from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from xlsxwriter import Workbook
import os
import requests
import shutil

################################################################################

class App:
    def __init__(self, username='', password='', target_username='',
                 path='/Users/Momin/Desktop/udemy_python/insta_pics_captions'): #Change this to your Instagram details and desired images path
        self.username = username
        self.password = password
        self.target_username = target_username
        self.all_images={}
        self.main_url = 'https://www.instagram.com'
        self.error = False
        if not os.path.exists(path): # make parent folder for different targets
            os.mkdir(path)
        self.path = os.path.join(path,target_username) # Different folders for different targets
        self.driver = webdriver.Chrome() #ChromeDriver path.
        self.driver.get(self.main_url)
        sleep(5)
        self.log_in()

        if self.error is False:
            self.close_dialog_box()
            self.open_target_profile()

        if self.error is False:
            self.scroll_down()

        self.driver.close()

        if self.error is False:
            if not os.path.exists(self.path):
                os.mkdir(self.path)
            self.downloading_images()
            self.write_captions_to_excel_file()

################################################################################

    def log_in(self, ):
        try:
            log_in_button = self.driver.find_element_by_link_text('Log in')
            log_in_button.click()
            sleep(5)
        except Exception:
            self.error = True
            print('Unable to find login button')
        else:
            try:
                user_name_input = self.driver.find_element_by_xpath('//input[@aria-label="Phone number, username, or email"]')
                user_name_input.send_keys(self.username)
                password_input = self.driver.find_element_by_xpath('//input[@aria-label="Password"]')
                password_input.send_keys(self.password)
                user_name_input.submit()
                self.close_settings_window_if_there()
            except Exception:
                print('Some exception occurred while trying to find username or password field')
                self.error = True
################################################################################

    def close_settings_window_if_there(self):
        try:
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
        except Exception as e:
            pass

    def close_dialog_box(self):
        try:
            sleep(10)
            close_btn = self.driver.find_element_by_xpath('//div[text()="Not Now"]')
            sleep(3)
            close_btn.click()
            sleep(1)
        except Exception:
            pass
################################################################################

    def open_target_profile(self):
        try:
            target_profile_url = self.main_url + '/' + self.target_username + '/'
            self.driver.get(target_profile_url)
            sleep(5)
        except Exception:
            self.error = True
            print('Could not find open target profile, Check if profile is correct')

    def scroll_down(self):
        try:
            no_of_posts = self.driver.find_element_by_xpath('//span[text()=" posts"]').text
            no_of_posts = no_of_posts.replace(' posts', '')
            no_of_posts = str(no_of_posts).replace(',', '')  # 15,483 --> 15483
            self.no_of_posts = int(no_of_posts)
            if self.no_of_posts > 12:
                no_of_scrolls = int(self.no_of_posts/12) + 3
                try:
                    for value in range(no_of_scrolls):
                        soup = BeautifulSoup(self.driver.page_source, 'lxml')
                        for image in soup.find_all('img'):
                            try:
                                caption = image['alt']
                            except KeyError:
                                caption = 'No caption exists for this image'
                            self.all_images[image['src']]=caption

                        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                        sleep(5)
                except Exception as e:
                    self.error = True
                    print(e)
                    print('Some error occurred while trying to scroll down')
            sleep(5)
        except Exception:
            print('Could not find no of posts while trying to scroll down')
            self.error = True

################################################################################

    def downloading_images(self):
        print('Length of all images', len(self.all_images))
        for index, image in enumerate(self.all_images):
            filename = 'image_' + str(index) + '.jpg'
            image_path = os.path.join(self.path, filename)
            print('Downloading image', index)
            response = requests.get(image, stream=True)
            try:
                with open(image_path, 'wb') as file:
                    shutil.copyfileobj(response.raw, file)  # source -  destination
            except Exception as e:
                print(e)
                print('Could not download image number ', index)
                print('Image link -->', image)


    def write_captions_to_excel_file(self):
        print('writing to excel')
        workbook = Workbook(os.path.join(self.path, 'captions.xlsx'))
        worksheet = workbook.add_worksheet()
        row = 0
        worksheet.write(row, 0, 'Image name')       # 3 --> row number, column number, value
        worksheet.write(row, 1, 'Caption')
        row += 1
        for index, image in enumerate(self.all_images):
            filename = 'image_' + str(index) + '.jpg'
            caption = self.all_images[image]
            worksheet.write(row, 0, filename)
            worksheet.write(row, 1, caption)
            row += 1
        workbook.close()

################################################################################

if __name__ == '__main__':
    app = App()

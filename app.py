from flask import Flask, request, jsonify
from playwright.sync_api import Playwright, sync_playwright, TimeoutError
from urllib.parse import urlparse
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

app = Flask(__name__)


class CodeInit:
    def __init__(self, result):
        self.result = result
    def code_type(self):
        if self.result == 'phishing':
            return 1
        elif self.result == 'legitimate':
            return 0
        elif self.result == 'random error':
            return 2


class UrlDetection:
    def __init__(self, url):
        self.url = url
        self.input_tag_xpath = "//input"
        self.text_type_xpath = "//input[@type='text']"
        self.email_type_xpath = "//input[@type='email']"
        self.email_id_xpath = "//input[@id='email']"
        self.email_name_xpath = "//input[@name='email']"
        self.userId_xpath = "//input[@id='user']"
        self.user_name_xpath = "//input[@name='user']"
        self.username_name_xpath = "//input[@name='username']"
        self.passwd_xpath = "//input[@type='password']"

    def CheckExistsXpath(self, driver, xpath):
        try:
            driver.wait_for_selector(xpath, state="attached", timeout=100)
            return True
        except TimeoutError:
            return False

    def EmailPasswordCheck(self, driver):
        input_tag = self.CheckExistsXpath(driver, self.input_tag_xpath)
        text_type = self.CheckExistsXpath(driver, self.text_type_xpath)
        email_type = self.CheckExistsXpath(driver, self.email_type_xpath)
        email_id = self.CheckExistsXpath(driver, self.email_id_xpath)
        email_name = self.CheckExistsXpath(driver, self.email_name_xpath)
        user_id = self.CheckExistsXpath(driver, self.userId_xpath)
        user_name = self.CheckExistsXpath(driver, self.user_name_xpath)
        username_name = self.CheckExistsXpath(driver, self.username_name_xpath)
        passwd = self.CheckExistsXpath(driver, self.passwd_xpath)

        return input_tag, text_type, email_type, email_id, email_name, \
               user_id, user_name, username_name, passwd

    def FakeCredentials(self, driver, test_mail, xpath, count):
        try:
            user = driver.query_selector(xpath)
            if count > 0:
                try:
                    user.fill("")
                except:
                    pass
            user.fill(test_mail)
        except:
            pass

    def FakePassword(self, driver, count):
        passwd = driver.query_selector(self.passwd_xpath)
        if count > 0:
            try:
                passwd.fill("")
            except:
                pass
        passwd.fill("fuckyou123456")
        passwd.press("Enter")

    def EmailList(self):
        emails = ['fuck@gmail.com', 'fuck@huawei.com', 'fuck@foxmail.com', 'fuck@163.com']
        return emails

    def GetDomainUri(self, uri):
        domain_name = urlparse(uri).hostname
        return domain_name

    def Checker(self, driver, domain_name):
        url = self.url
        input_tag, text_type, email_type, email_id, email_name, \
        user_id, user_name, username_name, \
        password = self.EmailPasswordCheck(driver)
        count = 0
        email_list = self.EmailList()
        try:
            while input_tag and count < 3:
                if password:
                    domain = self.GetDomainUri(url)
                    if email_type:
                        self.FakeCredentials(driver, email_list[count], self.email_type_xpath, count)

                    elif email_id:
                        self.FakeCredentials(driver, email_list[count], self.email_id_xpath, count)

                    elif email_name:
                        self.FakeCredentials(driver, email_list[count], self.email_name_xpath, count)

                    elif user_id:
                        self.FakeCredentials(driver, email_list[count], self.userId_xpath, count)

                    elif user_name:
                        self.FakeCredentials(driver, email_list[count], self.user_name_xpath, count)

                    elif username_name:
                        self.FakeCredentials(driver, email_list[count], self.username_name_xpath, count)

                    elif text_type:
                        self.FakeCredentials(driver, email_list[count], self.text_type_xpath, count)

                    self.FakePassword(driver, count)

                    newDomain = self.GetDomainUri(url)

                    if newDomain != domain:
                        return {'code':CodeInit('phishing').code_type(), 'result': 'this is a phishing website due to domain change'}
                    else:
                        count += 1
                        input_tag, text_type, email_type, email_id, email_name, \
                        user_id, user_name, username_name, \
                        password = self.EmailPasswordCheck(driver)

                else:
                    break


        except PlaywrightTimeoutError as Error:
            if password and count > 0:
                return {'code': CodeInit('legitimate').code_type(), 'result': 'this is a legitimate page'}

        if count < 1 and (not email_type or not email_id or not email_name) and not password:
            return { 'code': CodeInit('random error').code_type(), 'result': 'this page has no login'}
        elif not password and count < 2:
            if not email_type or not email_id or not email_name:
                return { 'code': CodeInit('phishing').code_type(), 'result': 'this is a phishing website due to test'}
        elif password and count >= 2:
            return { 'code': CodeInit('legitimate').code_type(), 'result': 'this is a legitimate page'}
        else:
            return {'code': CodeInit('random error').code_type(), 'result': 'random error'}

@app.route('/check', methods=['GET'])
def check():
    url = request.args.get('url')
    driver = sync_playwright().start()
    driver = driver.chromium.launch()
    driver = driver.new_context()
    page = driver.new_page()
    
    url_detection = UrlDetection(url)
    domain = url_detection.GetDomainUri(url)
    
    page.goto(url)
    result = url_detection.Checker(page, domain)
    page.close()
    driver.close()

    return jsonify(result)

if __name__ == "__main__":
    app.run()

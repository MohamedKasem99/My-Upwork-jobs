from selenium import webdriver

driver = webdriver.Chrome()

driver.set_page_load_timeout(10)

driver.get("https://provo.craigslist.org/tlg/d/alpine-model-needed-female/7061291756.html")

driver.find_element_by_xpath("/html/body/section/section/header/div[2]/div/button").click()
try:
    print(driver.find_element_by_xpath("/html/body/section/section/header/div[2]/div/div[1]/aside"))
except:
    "/html/body/section/section/header/div[2]/div/div[1]/aside/ul/li[3]/input"
    raise 
import logging
import os
import time
import yaml

from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# third party libraries
from webdriver_update_tool import update_chromedriver4mac as ucd4mac


here = os.path.abspath(os.path.dirname(__file__))
config_yml_path = os.path.join(here, "config.yml")
if not os.path.isfile(config_yml_path):
    raise Exception("Please create a config.yml")

with open(config_yml_path, 'r') as f:
    myconfig = yaml.load(f, Loader=yaml.FullLoader)

# add dirname
for key in myconfig['driver']:
    myconfig['driver'][key] = os.path.join(here, myconfig['driver'][key])

for key in myconfig['fb_group']:
    myconfig['fb_group'][key] = os.path.join(here, myconfig['fb_group'][key])


def init_driver():
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("headless")
    driver = webdriver.Chrome(
        myconfig['driver']['chrome'],
        options=options
    )
    return driver


def scroll_down_page(driver, times=1):
    logging.info("scrolling down the page...")
    for i in range(times):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)


def get_post(driver, target_post_num):
    prev_num = 0
    articles = []
    while len(articles) < target_post_num:
        prev_num = len(articles)
        scroll_down_page(driver, 2)
        articles = driver.find_elements(By.CSS_SELECTOR, "div[role='article']:not([tabindex='-1'])")
        # not work
        # articles = list(filter(lambda article: article.get_attribute('aria-posinset'), articles))
        if len(articles) == prev_num:
            break

    if len(articles) == 0:
        logging.warning('The html structure has been changed. Please correct locator.')

    return articles[:target_post_num] if len(articles) >= target_post_num else articles


def crawl(driver, target_url, target_post_num=10):
    # visit target website
    try:
        driver.get(target_url)
    except InvalidArgumentException as e:
        logging.error(e)
        return
    time.sleep(1)

    if " | Facebook" not in driver.title:
        logging.error("Facebook group title is {}. Please modify code.".format(driver.title))
        return

    title = driver.title[:len(driver.title) - len(" | Facebook")]
    logging.info("visit {}".format(driver.title))

    # close dialog
    try:
        dialog = driver.find_element(By.CSS_SELECTOR, "div[role='dialog']")
        dialog.find_element(By.CSS_SELECTOR, "div[role='button']").click()
    except NoSuchElementException:
        pass

    # create folder and file to store data
    timestamp = time.strftime('%Y%m%d')
    target_url_title_dir_path = os.path.join(myconfig['fb_group']['post_dirname'], title)
    if not os.path.isdir(target_url_title_dir_path):
        os.makedirs(target_url_title_dir_path)
    post_info_path = "{}/{}_{}_post".format(target_url_title_dir_path, timestamp, title)

    # try to crawl posts
    logging.info("try to get {} posts".format(target_post_num))
    articles = get_post(driver, target_post_num)

    logging.info("start to find post info and write data...")
    # find articles' info: 1. author 2. publish time 3. content
    with open(post_info_path, 'w') as f:
        for article in articles:
            try:
                author_action = article.find_element(By.XPATH, ".//strong[1]//ancestor::h2")
                f.write(author_action.text + '\n')

                publish_time = author_action.find_element(By.XPATH, "../../../div[2]")
                f.write(publish_time.text + '\n')

                post_content = publish_time.find_element(By.XPATH, "../../../../../div[3]")
                f.write(post_content.text + '\n')

                f.write("---------------------------------------------------------------------\n")
            except NoSuchElementException:
                logging.info("no more articles")
                break
    logging.info("crawling is done")

    # save page source
    logging.info("save page source")
    page_source_path = "{}/{}_{}_page.html".format(target_url_title_dir_path, timestamp, title)
    with open(page_source_path, 'w') as f:
        f.write(driver.page_source)


if __name__ == '__main__':
    if not os.path.isfile(myconfig['fb_group']['link_filename']):
        raise Exception("Please add %s" % (myconfig['fb_group']['link_filename']))

    with open(myconfig['fb_group']['link_filename'], 'r') as f:
        lines = f.readlines()
        logging.info("initialize driver")
        # check if the webdriver is outdated else update it
        ucd4mac.check_driver(
            myconfig['browser']['chrome']['mac'],
            myconfig['driver']['dirname'],
            myconfig['driver']['chrome']
        )
        driver = init_driver()
        for line in lines:
            line = line.strip()
            link, target_post_num = line.split()
            crawl(driver, link, int(target_post_num))
        driver.quit()

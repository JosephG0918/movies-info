from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import sqlite3
from datetime import date
import re

def main():
    '''
    Function creates a SQLite database and declares a headless Firefox browser instance using Selenium.
    Function calls the scrape_and_store(conn, cursor, browser) method.
    '''
    conn = sqlite3.connect('database\\movies.db')
    cursor = conn.cursor()

    options = Options()
    options.add_argument("-headless")
    browser = webdriver.Firefox(options=options)

    scrape_and_store(conn, cursor, browser)

def scrape_and_store(conn, cursor, browser):
    '''
    Function web scrapes movie titles, star ratings, and user reviews of movies, then populates a SQLite database with all of that data.
    '''
    movies_list = []
    cursor.execute('''CREATE TABLE IF NOT EXISTS AMC_MOVIES (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      date DATE NOT NULL,
                      movie_title TEXT(50), 
                      IMDb_rating TEXT(5),
                      tomatometer TEXT(5),
                      featured_user_review TEXT(200)
                      )''')
    
    browser.get("https://www.amctheatres.com/movies") 
    soup = BeautifulSoup(browser.page_source, 'html.parser')

    for i in range(len(soup.find_all('div', class_='flex flex-col gap-2'))):
        results = soup.find_all('div', class_='flex flex-col gap-2')[i]
        h2_tags = str(results.find_all('h2', class_='sr-only')[0].text)
        movies_list.append(h2_tags)

    for movie in movies_list:
        browser.get("https://www.imdb.com/")

        action = ActionChains(browser)
        wait = WebDriverWait(browser, 30)

        try:
            searchTextbox = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="suggestion-search"]')))
            action.move_to_element(searchTextbox).click().send_keys(movie).perform()
            searchTextbox.send_keys(Keys.ENTER)

            searchMovie = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/main/div[2]/div[3]/section/div/div[1]/section[2]/div[2]/ul/li[1]')))
            action.click(searchMovie).perform()

            time.sleep(5)
            get_url = str(browser.current_url)
            browser.get(get_url)
            soup = BeautifulSoup(browser.page_source, 'html.parser')

            rating = soup.find_all('span', class_='sc-d541859f-1 imUuxf')[0].text
            featured_user_review = str(soup.find_all('div', class_='sc-a2ac93e5-5 feMBGz')[0].text)
        except Exception as e:
            rating = None
            featured_user_review = None
            print(f"{e}: imdb")

        try:
            browser.get("https://www.rottentomatoes.com/")
            searchTextbox = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="header-main"]/search-results-nav/search-results-controls/input')))
            action.move_to_element(searchTextbox).click().send_keys(movie).perform()
            searchTextbox.send_keys(Keys.ENTER)

            searchMovie = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/main/div[1]/div/section[1]/div/search-page-result[1]/ul/search-page-media-row[1]/a[2]')))
            action.click(searchMovie).perform()

            time.sleep(5)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            rotten_tomatoes_rating = re.findall('"/m/[a-zA-Z.,!?0-9&$#@*\(\)+-=_/\<\>]+/reviews","scorePercent":"([0-9]+%)","title":"Tomatometer"', str(soup.find_all('div', class_='media-scorecard no-border')[0]))[0]
        except Exception as e:
            rotten_tomatoes_rating = None
            print(f"{e}: rottentomatoes")
        
        today_date = date.today()
        cursor.execute('''INSERT INTO AMC_MOVIES (date, movie_title, IMDb_rating, tomatometer, featured_user_review) VALUES (?, ?, ?, ?, ?)''', (today_date, movie, rating, rotten_tomatoes_rating, featured_user_review))
        conn.commit()

    conn.close()
    browser.quit()

if __name__ == "__main__":
    main()
    print("Finished!")
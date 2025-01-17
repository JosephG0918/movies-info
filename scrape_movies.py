from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time, sqlite3, re, requests
from datetime import date
from difflib import SequenceMatcher

def main():
    conn = sqlite3.connect('database/movies.db')
    cursor = conn.cursor()

    options = Options()
    options.add_argument("-headless")
    browser = webdriver.Firefox(options=options)

    scrape_and_store(conn, cursor, browser)

def scrape_and_store(conn, cursor, browser):
    headers = {"User-Agent": "Mozilla/5.0"}
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AMC_MOVIES (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            movie_title TEXT(50),
            IMDb_rating TEXT(5),
            tomatometer TEXT(5),
            featured_user_review TEXT(200)
        )
    ''')

    # Get list of movie titles from AMC website
    browser.get("https://www.amctheatres.com/movies")
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    movies_list = [
        div.find('h2', class_='sr-only').text
        for div in soup.find_all('div', class_='flex flex-col gap-2')
    ]

    wait = WebDriverWait(browser, 30)
    action = ActionChains(browser)

    for movie in movies_list:
        # IMDb Scraping
        rating, featured_user_review = None, None
        try:
            browser.get("https://www.imdb.com/")
            searchBox = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="suggestion-search"]')))
            action.move_to_element(searchBox).click().send_keys(movie).send_keys(Keys.ENTER).perform()

            searchMovie = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="__next"]/main/div[2]/div[3]/section/div/div[1]/section[2]/div[2]/ul/li[1]')
            ))
            action.click(searchMovie).perform()
            time.sleep(5)

            get_url = browser.current_url
            browser.get(get_url)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            req = requests.get(get_url, headers=headers)
            soup_bs4 = BeautifulSoup(req.content, 'html.parser')
            movieMatch = soup_bs4.find('span', class_='hero__primary-text').text

            # Check if the found movie title closely matches the expected title
            if SequenceMatcher(None, movieMatch, movie).ratio() >= 0.9:
                # Extract rating and featured review if titles match closely
                rating = soup.find('span', class_='sc-d541859f-1 imUuxf').text
                featured_user_review = soup.find('div', class_='sc-8c7aa573-5 gBEznl').text
        except Exception as e:
            print(f"{e}: IMDb scraping issue")

        # Rotten Tomatoes Scraping
        rotten_tomatoes_rating = None
        try:
            browser.get("https://www.rottentomatoes.com/")
            searchBox = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="header-main"]/search-results-nav/search-results-controls/input')
            ))
            action.move_to_element(searchBox).click().send_keys(movie).send_keys(Keys.ENTER).perform()

            searchMovie = wait.until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[3]/main/div[1]/div/section[1]/div/search-page-result[1]/ul/search-page-media-row[1]/a[2]')
            ))
            action.click(searchMovie).perform()
            time.sleep(5)

            soup = BeautifulSoup(browser.page_source, 'html.parser')
            rating_match = re.search('[0-9]+%', soup.find('rt-text', slot='criticsScore').text)
            if rating_match:
                rotten_tomatoes_rating = rating_match.group()
        except Exception as e:
            print(f"{e}: Rotten Tomatoes scraping issue")

        today_date = date.today()
        cursor.execute('''
            INSERT INTO AMC_MOVIES 
            (date, movie_title, IMDb_rating, tomatometer, featured_user_review) 
            VALUES (?, ?, ?, ?, ?)
        ''', (today_date, movie, rating, rotten_tomatoes_rating, featured_user_review))
        conn.commit()

    conn.close()
    browser.quit()

if __name__ == "__main__":
    main()
    print("Finished!")
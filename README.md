# AMC Theater Movie Scraper

This Python project scrapes movie information from AMC Theaters, including details like the title, rating, Tomatometer score, and top review, and inserts the data into a SQLite database. The data can then be displayed in a formatted, easy-to-read layout using the CLI.

## Features

- **Web Scraping**: Collects movie details such as title, rating, Tomatometer score, and top review from AMC Theater listings.
- **Data Storage**: Stores scraped data in a SQLite database for easy retrieval and organization.
- **CLI Display**: `display_movies.py` retrieves and formats data from the database, displaying it neatly in a CLI environment using the `tabulate` library.

## Project Structure

- `scrape_movies.py`: Main script that performs web scraping and saves data into the SQLite database.
- `display_movies.py`: Retrieves data from the SQLite database and formats it using `tabulate` for a neat CLI display.
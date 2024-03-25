# TrustpilotReviewScraper

`TrustpilotReviewScraper` is a Python script designed to scrape reviews from Trustpilot.com. It extracts detailed review information including the reviewer's name, review count, country, rating, review date, review title, review content, and date of experience. The tool supports scraping across multiple pages and can fetch reviews in all available languages, outputting the data into a CSV file for further analysis.

## Requirements

- Python 3.12.1 (May work with earlier versions of Python 3, but not tested)

## Setup

To use `TrustpilotReviewScraper`, follow these setup instructions:

1. **Clone the Repository**

    ```
    git clone https://github.com/YOUR_USERNAME/TrustpilotReviewScraper.git
    cd TrustpilotReviewScraper
    ```

2. **Create and Activate a Virtual Environment**

    - For Unix/macOS:

        ```
        python3 -m venv env
        source env/bin/activate
        ```

    - For Windows:

        ```
        python -m venv env
        .\env\Scripts\activate
        ```

3. **Install Required Packages**

    ```
    pip install -r requirements.txt
    ```

## Usage

To start scraping reviews from a specific domain on Trustpilot, run the script as follows:

```python 
trustpilot_scraper.py [domain]
```
Replace `[domain]` with the Trustpilot domain you wish to scrape. For example:
python trustpilot_scraper.py example.com


The script will scrape reviews and save them into a CSV file named `reviews_[domain].csv`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have suggestions or improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.







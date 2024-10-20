from flask import Flask, render_template, request
import requests
from requests.exceptions import ReadTimeout
from googlesearch import search  # Make sure to install the googlesearch-python library

app = Flask(__name__)

def fetch_with_retries(query, retries=3):
    url = f"https://www.google.com/search?q={query}"
    for attempt in range(retries):
        try:
            # Perform the search and return results
            results = search(query, num_results=10)  # Adjust num_results as needed
            return list(results)
        except ReadTimeout:
            print(f"Attempt {attempt + 1} timed out. Retrying...")
            if attempt == retries - 1:
                print("Failed after multiple retries.")
                return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

def count_bad_reviews(query):
    search_results = fetch_with_retries(query)
    # Simulating bad reviews detection
    bad_reviews = [result for result in search_results if "bad" in result.lower()]
    num_bad_reviews = len(bad_reviews)
    is_safe = num_bad_reviews < 10  # Determine if the app is safe
    return num_bad_reviews, is_safe, search_results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        num_bad_reviews, is_safe, search_results = count_bad_reviews(query)
        return render_template('results.html', query=query, is_safe=is_safe, bad_reviews=num_bad_reviews, search_results=search_results)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

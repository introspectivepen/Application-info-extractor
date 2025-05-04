from flask import Flask, render_template, request
from cachetools import TTLCache
import asyncio
import os
from serpapi.google_search import GoogleSearch
from requests.exceptions import ReadTimeout

app = Flask(__name__)

# Initialize cache (stores results for 1 hour)
cache = TTLCache(maxsize=100, ttl=3600)

# Use provided SerpAPI key (preferably set via environment variable)
SERPAPI_KEY = os.getenv('SERPAPI_KEY', '876ee57984a2d7d6ced4e3ea04aa84768a17f66afcc28530b8cacd403b211765')
if not SERPAPI_KEY:
    raise ValueError("SERPAPI_KEY is not set.")

async def fetch_with_retries_async(query, num_results=10):
    # Check cache first
    cache_key = f"{query}:{num_results}"
    if cache_key in cache:
        return cache[cache_key]

    try:
        # Perform the search using SerpAPI
        params = {
            "q": query,
            "num": num_results,
            "api_key": SERPAPI_KEY
        }
        search = GoogleSearch(params)
        results = search.get_dict().get("organic_results", [])
        # Extract URLs, titles, and snippets for sentiment analysis
        processed_results = []
        for result in results:
            url = result.get("link", "")
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            processed_results.append({
                "url": url,
                "title": title,
                "snippet": snippet
            })
        cache[cache_key] = processed_results[:num_results]  # Limit to requested number
        return cache[cache_key]
    except ReadTimeout:
        print("Search timed out.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def count_bad_reviews(query, num_results=10):
    # Run async function using asyncio.run to create a new event loop
    search_results = asyncio.run(fetch_with_retries_async(query, num_results))
    
    # Debug: Log the search results to inspect what SerpAPI returns
    print("Search Results:", search_results)
    
    # Expanded keyword lists for better sentiment detection
    bad_keywords = ["bad", "poor", "negative", "complaint", "terrible", "awful", "horrible", "disappointing", "worst", "problem", "issue"]
    good_keywords = ["good", "great", "positive", "excellent", "awesome", "amazing", "fantastic", "wonderful", "best", "love", "perfect"]
    
    num_bad_reviews = 0
    num_good_reviews = 0
    
    for result in search_results:
        # Combine URL, title, and snippet for keyword matching
        text_to_check = f"{result['url']} {result['title']} {result['snippet']}".lower()
        
        # Debug: Log the text being checked
        print(f"Text to check: {text_to_check}")
        
        # Check for bad keywords
        bad_match = any(kw in text_to_check for kw in bad_keywords)
        if bad_match:
            num_bad_reviews += 1
            print(f"Bad review detected (keywords: {', '.join(kw for kw in bad_keywords if kw in text_to_check)}): {text_to_check}")
        
        # Check for good keywords (allow overlap; a result can be both good and bad)
        good_match = any(kw in text_to_check for kw in good_keywords)
        if good_match:
            num_good_reviews += 1
            print(f"Good review detected (keywords: {', '.join(kw for kw in good_keywords if kw in text_to_check)}): {text_to_check}")
        
        # If no match, log for debugging
        if not bad_match and not good_match:
            print(f"No sentiment keywords found in: {text_to_check}")
    
    # Calculate average sentiment (percentage of good reviews)
    total_reviews = num_good_reviews + num_bad_reviews
    sentiment_percentage = (num_good_reviews / total_reviews * 100) if total_reviews > 0 else 0
    
    # Determine sentiment category
    if total_reviews == 0:
        sentiment_category = "Neutral"  # Default to Neutral if no sentiment keywords are found
        sentiment_percentage = 50.0  # Neutral midpoint
    elif sentiment_percentage > 80:
        sentiment_category = "Mostly Good"
    elif sentiment_percentage > 60:
        sentiment_category = "Good"
    elif sentiment_percentage > 40:
        sentiment_category = "Neutral"
    elif sentiment_percentage > 20:
        sentiment_category = "Bad"
    else:
        sentiment_category = "Mostly Bad"
    
    # Extract just the URLs for display in the template
    display_urls = [result["url"] for result in search_results]
    
    return num_good_reviews, num_bad_reviews, sentiment_percentage, sentiment_category, display_urls

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        num_results = int(request.form.get('num_results', 10))
        num_good_reviews, num_bad_reviews, sentiment_percentage, sentiment_category, search_results = count_bad_reviews(query, num_results)
        return render_template('results.html', query=query, 
                             num_good_reviews=num_good_reviews, 
                             num_bad_reviews=num_bad_reviews, 
                             sentiment_percentage=sentiment_percentage, 
                             sentiment_category=sentiment_category, 
                             search_results=search_results)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)

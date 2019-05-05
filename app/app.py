# Import libraries
from flask import Flask, request, render_template, url_for, redirect
from website_wordcloud import crawler, create_wordcloud
import uuid

# Initiate Flask
app = Flask(__name__)

def crawl_and_generate(start_url, page_limit=10):
    """
    Use website_wordcloud.py to crawl the site and generate a wordcloud
    """
    # Define file name
    random_string = str(uuid.uuid4().hex)
    file_store = f"./static/text_extracts/{random_string}.txt"
    # Run crawler
    crawler(start_url=start_url, page_limit=page_limit, file_store=file_store)
    # Create wordcloud
    wc_file_path = create_wordcloud(file_store, random_string)
    # Return path to image file
    return wc_file_path

@app.route("/", methods=["GET"])
def index():
    # Handle GET requests
    if request.method == "GET":
        return render_template(
            "index.html", 
            title="Website WordCloud", 
            description="Turn your website into a beautiful wordcloud."
        )

@app.route("/wordcloud", methods=["GET", "POST"])
def wordcloud_page():
    # Handle GET requests -- direct requests to this page not allowed
    if request.method == "GET":
        return redirect(url_for("index"))
    
    # Handle POST requests
    if request.method == "POST":
        # Get the URL the user submitted
        user_url = request.form.get("user_url")
        # Crawl and generate wordcloud
        wc_file_path = crawl_and_generate(user_url, page_limit=5)
        # render
        return render_template(
            "wordcloud.html",
            wc_file_path=wc_file_path,
            title="Your WordCloud",
            description="Here's your wordcloud!"
        )

if __name__ == "__main__":
    app.run(debug=True)





from flask import Flask, render_template, redirect

# Import our pymongo library, which lets us connect our Flask app to our Mongo database.
import pymongo
import mars_scraper

# Create an instance of our Flask app.
app = Flask(__name__)

# Create connection variable
conn = 'mongodb://localhost:27017'

# Pass connection to the pymongo instance.
client = pymongo.MongoClient(conn)

# Connect to a database. Will create one if not already available.
db = client.NASA_db


# Set route
@app.route('/')
def index():
    #scrape() # Uncomment if your database is not preloaded.
    # Get the data from the db

    saved = db.mars.find_one()
    # print
    print(saved)
    # Return the template with the saved data
    return render_template('index.html', data=saved)


@app.route('/scrape')
def update():
    news = mars_scraper.getHeadlines()
    print(news["Title"])
    caro = mars_scraper.getFeaturedImage()
    print(caro)
    tweepy = mars_scraper.getTweets()
    print(tweepy)
    mfact = mars_scraper.getMarsFacts()
    print(mfact)
    mHemisphere = mars_scraper.getMarsHemispheres()

    # print(mHemisphere)

    # print()
    # print()
    # print()

    # # latest = db.mars.find_one()
    # # print(latest)

    marsDict = {
        "Headline": news["Title"],
        "News": news["Para"],
        "Image": caro["featured_img_url"],
        "Weather": tweepy["Mars_Weather"],
 #       "Profile": mfact["Profile"],
        "Table": mfact["table"],
        "Hemisphere": mHemisphere["images"]
    }

    db.mars.drop()
    db.mars.insert(marsDict)
    # # Return the template with the teams list passed in
    # return render_template('index.html', data=latest)
    return redirect('/', code=302)


if __name__ == "__main__":
    app.run(debug=True)
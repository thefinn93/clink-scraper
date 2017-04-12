# Clink Scraper

Scrape data about availability of Century Link service and render it onto a map.

*This is a quick hack I did, not remotely user friendly. If someone wants to spend the time to clean it up, that would
be much appriciated.*


# Scraping

1. Install depends: `pip install -r requirements.txt`, including the [selenium driver](http://www.seleniumhq.org/projects/webdriver/) (`apt install chromedriver` on Debian)
1. Go to [openstreetmap.org/export](https://www.openstreetmap.org/export), select the area you wish to check, and hit the export button
1. Now we get to actually do the scraping! Assuming the expored file is named `map.osm` and is in the same directory as this code, run:
```bash
osmfilter map.osm --keep="addr:housenumber and addr:street" --drop-relations --drop-ways | osmconvert - --all-to-nodes --csv="addr:housenumber addr:street addr:city addr:postcode @id @lat @lon" | ./discoverservices.py
```
this will scrape everything on that map that it can. It kinda sucks and misses a lot, mostly due to me having no idea how OSM works.

# Map Rendering
1. `./mapmaker.py > mapdata.js`
1. open `map.html`
1. If uploading to a server, you'll need `map.html`, `mapdata.js` and the `icons/` folder.

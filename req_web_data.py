import requests
from bs4 import BeautifulSoup
from matplotlib import image
from matplotlib import pyplot
from io import BytesIO
from PIL import Image

import re
import time
import csv


def price_filter_thing(c): 
    if re.search("\d", c) == None:
        return False
    else:
        return True

cookieHeader = dict(SESSION_ID = "I removed my session_id for security reasons, you can get yours by logging into artsy.net")
datapoints = [] # will have arrays [img-url, price]

print()
print("TIEDONKERÄYS: Maalaukset & niiden hinnat")

print()
print("Aloita tiedonkeräys. 100 sivua.")
print(". . . ")

beginning_time = time.time()
file_path = "data_links.csv"
f = open(file_path, "w", newline="")
writer = csv.writer(f)

writer.writerow(["image_id", "image_link", "price", "currency"])

counter = 1
for page_number in range(100):
    page_number += 1

    collectionR = requests.get("https://www.artsy.net/collect?page=" + str(page_number), cookies=cookieHeader)
    soup = BeautifulSoup(collectionR.text, 'html.parser')

    three_columns = soup.find_all(attrs={"class": "Box-sc-15se88d-0 Flex-cw39ct-0 ArtworkGrid__InnerContainer-sc-1jsqquq-1 LbPWX cqZQYS fresnel-greaterThanOrEqual-lg"})
    three_columns = str(three_columns[1])

    cols_soup = BeautifulSoup(three_columns, 'html.parser')

    first_col = cols_soup.div.div
    second_col = first_col.next_sibling
    third_col = second_col.next_sibling

    cols = [first_col, second_col, third_col]
    for col in cols:
        soup = BeautifulSoup(str(col), 'html.parser')
        artworkGridItems = soup.find_all(attrs={"data-test": "artworkGridItem"})

        for gridItem in artworkGridItems:
            soup2 = BeautifulSoup(str(gridItem), 'html.parser')

            img_url = soup2.a.div.img['src']

            #<div color="black100" font-weight="bold" font-family="sans" class="Box-sc-15se88d-0 Text-sc-18gcpao-0 eXbAnU jkuGdd">US$19,995 </div>
            info = list(soup2.find("div", attrs={"class": "Box-sc-15se88d-0 Text-sc-18gcpao-0 eXbAnU jkuGdd"}).children)[0]
            price_string = str(info)

            currency = "unknown"
            if "€" in price_string:
                currency = "EUR"
            elif "£" in price_string:
                currency = "POU"
            elif "$" in price_string and "US" in price_string:
                currency = "USD"

            weird_char = "–"
            if weird_char in price_string:
                price_string = price_string.split(weird_char)[1]


            price = filter(price_filter_thing, price_string)
            price = "".join(price)
            if price == "":
                price = 0
            else:
                price = int(price)
            
            new_row = [counter, img_url, price, currency]
            writer.writerow(new_row)
            datapoints.append([img_url, price])
            
            counter += 1

#writer.writerows(datapoints) #already doing this just above
f.close()
ending_time = time.time()
running_time = (ending_time - beginning_time) / 60.0

print("\n--- DONE ---\n")
print("datapoints received:  " + str(len(datapoints)))
print("data stored to: " + file_path)
print("time consumed: " + str(running_time) + " minutes")
print()





if False:
    img_url = "https://i.pinimg.com/550x/dd/50/43/dd50435018e7b325324f3f4408774716.jpg"  #test some url
    r = requests.get(img_url)
    img = BytesIO(r.content)
    load_image = Image.open(img)
    load_image.show() #works with default image-opener-programme in my windows 10

if False:
    img_pyplot = image.imread(img)
    pyplot.imshow(img_pyplot)
    pyplot.show()  #doesnt work, i think it needs a PNG

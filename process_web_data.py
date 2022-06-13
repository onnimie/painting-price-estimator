from ctypes.wintypes import RGB
from pyparsing import line
import requests
import csv
from io import BytesIO
from PIL import Image

import csv
import time

beginning_time = time.time()

read_file_path = "data_links.csv"

write_file_path = "image_RGB_data.csv"
#write_test_path = "data_test.csv"

f = open(read_file_path)
w = open(write_file_path, "w", newline="")
reader = csv.reader(f, delimiter = ",")
writer = csv.writer(w)

print()
print("Aloitetaan tiedon prosessointi...")
print(". . .")
print()


def vector_distance(origin: tuple, destination: tuple):
    ret = 0
    for i in range(len(origin)):
        ret += abs(destination[i] - origin[i])
    return ret


line_count = 0
misshapes = 0

for row in reader:
    if line_count == 0:
        text = "columns in " + read_file_path + ": " + ", ".join(row)
        line_count += 1
        writer.writerow(["image_id", "rgb_strengths", "five_most_frequent_rgb", "color_count", "avg_use_of_same_color", "width", "height", "price", "currency"])
    else:
        image_id = row[0]
        price = row[2]
        currency = row[3]

        img_url = row[1]
        r = requests.get(img_url)

        img = BytesIO(r.content)
        load_image = Image.open(img)

        pil_img = load_image.load()


        rgb_values = dict()
        rgb_strengths = [0.0, 0.0, 0.0]
        divider = 10000.0

        width, height = load_image.size
        max_strength = 255 * width * height / divider
        for i in range(width):
            for j in range(height):
                value = pil_img[i, j]
                
                if not isinstance(value, int):
                    length = len(value)
                    for x in range(min(3, length)):
                        rgb_strengths[x] = rgb_strengths[x] + value[x]/divider
                    
                    if length == 3:
                        if value in rgb_values:
                            rgb_values[value] = rgb_values[value] + 1
                        else:
                            rgb_values[value] = 1

        line_count += 1
        if rgb_strengths[0] == 0.0 and rgb_strengths[1] == 0.0 and rgb_strengths[2] == 0.0:
            misshapes += 1
            continue
        rgb_strengths = [str(rgb_strengths[0]/max_strength), str(rgb_strengths[1]/max_strength), str(rgb_strengths[2]/max_strength)]
        #print(rgb_strengths)


        rgb_values_sorted = sorted(rgb_values, key=rgb_values.get, reverse=True)
        if len(rgb_values_sorted) == 0:
            misshapes += 1
            continue
        
        take_first: list[tuple[int]] = []
        test_len = len(rgb_values_sorted)
        bruh = True
        i = 0
        prev = (0,0,0)
        while (bruh):
            if len(take_first) == 0:
                try:
                    a = rgb_values_sorted[i]
                    take_first.append(a)
                    prev = a
                except:
                    j = 0
                    while (len(take_first < 5)):
                        if rgb_values_sorted[j] not in take_first:
                            take_first.append(rgb_values_sorted[j])
            else:
                candidate = rgb_values_sorted[i]
                if vector_distance(prev, candidate) > 15:
                    take_first.append(candidate)
                    prev = candidate
            if len(take_first) > 4:
                bruh = False
            else:
                i += 1
        assert(len(take_first) == 5)

        take_first = [str(tup) for tup in take_first]

        color_count = len(rgb_values.keys())
        avg_use_of_same_color = width * height / float(color_count)

        writer.writerow([image_id, "-".join(rgb_strengths), ">".join(take_first), color_count, avg_use_of_same_color, width, height, price, currency])

f.close()
w.close()

ending_time = time.time()
running_time = (ending_time - beginning_time) / 60.0

print("---DONE---")
print("datapoints processed: " + str(line_count))
print("misshaped datapoints: " + str(misshapes))
print("time consumed: " + str(running_time) + " minutes")
print()

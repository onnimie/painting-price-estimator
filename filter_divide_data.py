from asyncio import base_futures
from audioop import avg
from ctypes.wintypes import RGB
from pyparsing import line
import csv
import time

beginning_time = time.time()

read_file_path = "image_RGB_data.csv"

write_file_path1 = "rgbdata_freq.csv"
write_file_path2 = "rgbdata_strength_price.csv"

f = open(read_file_path)

w_rgb_freq = open(write_file_path1, "w", newline="")
w_strength_price = open(write_file_path2, "w", newline="")

reader = csv.reader(f, delimiter = ",")
writer_strength_price = csv.writer(w_strength_price)
writer_rbg_freq = csv.writer(w_rgb_freq)

print()
print("Aloitetaan tiedon filterointi ja separointi...")
print(". . .")
print()

line_count = 0
filtered_datapoints = 0

for row in reader:
    currency_unknown = False

    if line_count == 0:
        text = "columns in " + read_file_path + ": " + ", ".join(row)

        writer_strength_price.writerow(["image_id", "R_strength", "G_strength", "B_strength", "width", "height", "price_eur"])
        r = ["image_id", "color_count", "avg_use_of_same_color"]
        for i in ["1", "2", "3", "4", "5"]:
            for c in ["R", "G", "B"]:
                r.append(i + "_used_" + c)
        writer_rbg_freq.writerow(r)

    else:
        image_id = row[0]
        rgb_strengths = row[1]
        most_freq_rgb = row[2]
        color_count = int(row[3])
        avg_use_of_same_color = float(row[4])
        width = int(row[5])
        height = int(row[6])
        price = int(row[7])
        currency = row[8]

        match currency:
            case "EUR":
                price = price
            case "POU":
                price = int(price * 1.21)
            case "USD":
                price = int(price * 0.92)
            case unknown:
                currency_unknown = True

        rgb_strengths = rgb_strengths.split("-")

        r_strength = float(rgb_strengths[0])
        g_strength = float(rgb_strengths[1])
        b_strength = float(rgb_strengths[2])

        if ( r_strength == 0.0 and g_strength == 0.0 and b_strength == 0.0 ) or currency_unknown:
            filtered_datapoints += 1
            continue

        temp = most_freq_rgb.split(">")
        most_freq_rgb: list[list[int]] = []
        for a in temp:
            a = a[1:-1]
            a = a.split(", ")
            try:
                a = [int(b) for b in a]
            except:
                filtered_datapoints += 1
                continue
            most_freq_rgb.append(a)
        
        r = [image_id, color_count, avg_use_of_same_color]
        for i in range(len(most_freq_rgb)):
            for c in range(3):
                i_used_c = most_freq_rgb[i][c]
                r.append(i_used_c)
        
        writer_strength_price.writerow([image_id, r_strength, g_strength, b_strength, width, height, price])
        writer_rbg_freq.writerow(r)

        
    line_count += 1



f.close()
w_rgb_freq.close()
w_strength_price.close()

ending_time = time.time()
running_time = (ending_time - beginning_time) / 60.0

print("---DONE---")
print("datapoints accepted: " + str(line_count))
print("filtered datapoints: " + str(filtered_datapoints))
print("time consumed: " + str(running_time) + " minutes")
print()

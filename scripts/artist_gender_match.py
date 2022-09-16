import os
import csv
from tqdm import tqdm


dataloc = r'C:\Users\Milan\OneDrive\Desktop\Said\GenderClassification\export'
files = ['Artimage_data.csv', 'ArtUK-Artists-2021-03-12.csv']
artistdataloc = r'C:\Users\Milan\OneDrive\Desktop\Said\Art\ArtistData\raw\artfacts_data.csv'


artistData = []
for f in files:
    fileData = []
    path = os.path.join(dataloc, f)
    with open(path, 'r', errors='ignore', encoding='utf-8') as r:
        csvR = csv.reader(r, delimiter=',')
        for line in csvR:
            fileData.append(line)
    artistData.append(fileData)


artFactsData = [[], []]
with open(artistdataloc, 'r', errors='ignore', encoding='utf-8') as r:
        csvR = csv.reader(r, delimiter=';', quotechar='|')
        for line in csvR:
            name = line[1]
            gender = line[12]
            artFactsData[0].append(name)
            artFactsData[1].append(gender)

'''
artImageExport = []
artImagePath = os.path.join(dataloc, files[0].split('.')[0] + '-v1.csv')
for x, line in tqdm(enumerate(artistData[0]), total=len(artistData[0])):
    if x == 0:
        line.append('artistDBmatch')
    elif x > 0:
        artist = line[2]
        if artist in artFactsData[0]:
            index = artFactsData[0].index(artist)
            gender = artFactsData[1][index]
            line.append(gender)
        else:
            line.append('')
    artImageExport.append(line)
with open(artImagePath, 'w', encoding='utf-8', newline='') as w:
    csvW = csv.writer(w)
    for line in artImageExport:
        csvW.writerow(line)
'''

artUKExport = []
artUKPath = os.path.join(dataloc, files[1].split('.')[0] + '-v1.csv')
for x, line in tqdm(enumerate(artistData[1]), total=len(artistData[1])):
    if x == 0:
        line.append('artistDBmatch')
    elif x > 0:
        artist = line[2]
        if artist in artFactsData[0]:
            index = artFactsData[0].index(artist)
            gender = artFactsData[1][index]
            line.append(gender)
        else:
            line.append('')
    artUKExport.append(line)
with open(artUKPath, 'w', encoding='utf-8', newline='') as w:
    csvW = csv.writer(w)
    for line in artUKExport:
        csvW.writerow(line)
import pandas as pd
import csv

DATALOC = 'D:/SBS/Data/04-08-2021/data.csv'
EXPORTLOC = 'D:/SBS/Data/04-08-2021/frequency/'

def importData():
    df = pd.read_csv(DATALOC, usecols=['category', 'materials'])
    return df


def countOccurances(df):
    categories = {}
    df = df.dropna()
    df = df.groupby(['category'])
    for category, material in df:
        frequency = {}
        try:
            mats = material['materials']
            for artmat in mats:
                artmat = artmat.split(' ')
                
                for mat in artmat:
                    mat = mat.lower().strip().replace(',', '')
                    if mat in frequency.keys():
                        frequency[mat] += 1
                    else:
                        frequency[mat] = 1
        except AttributeError as e:
            print(e)
            mats = []
        categories[category] = frequency 
                
    return categories


def exportData(frequency):
    for category in frequency:
        cat = category.replace('/', '-').replace(' ', '-')
        with open(EXPORTLOC + cat + '.csv', 'w', encoding='utf8', newline='') as fs:
            csvw = csv.writer(fs, delimiter=',', quotechar='\"')
            csvw.writerow(['material', 'frequency'])
            for val in frequency[category]:
                csvw.writerow([val, frequency[category][val]])


if __name__ == "__main__":
    materials = importData()
    frequency = countOccurances(materials)
    exportData(frequency)
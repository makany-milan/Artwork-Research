import csv
import os
from typing import final
import time


IMPORTLOCATIONS = {
    'artsyFairsProcessed': r'C:\Users\makan\OneDrive\Desktop\Said\Art\PriceDataExtraction\Artsy\fairs\processedData',
    'artsyFairs': r'C:\Users\makan\OneDrive\Desktop\Said\Art\PriceDataExtraction\Artsy\fairs\data',
    'artsyPastFairs': r'C:\Users\makan\OneDrive\Desktop\Said\Art\PriceDataExtraction\Artsy\pastFairs\data\v2',
    'artsyCollections': r'D:\oxford\csv_backup\collections',
    'nonArtsy': r'D:\oxford\csv_backup\nonArtsy'
}

EXPORTLOCATIONS = {
    'artsyFairs': r'D:\oxford\rawdata\artsyFairs',
    'artsyFairsProcessed': r'D:\oxford\rawdata\artsyFairs',
    'artsyPastFairs': r'D:\oxford\rawdata\artsyPastFairs',
    'artsyCollections': r'D:\oxford\rawdata\artsyCollections',
    'nonArtsy': r'D:\oxford\rawdata\nonArtsy'
}


IMPORTLOCATIONS = {
    'newArt': r'D:\oxford\art-data'
}

EXPORTLOCATIONS = {
    'newArt': r'D:\oxford\art-data\cleaned'
}


MONTHS = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}

ERRORS = {
    'medium': 'materials',
    'image': 'image_url',
    'material': 'materials',
    'priceUSD': 'price'
}


NEWQUOTE = '"'

def cleanString(string):
    string = string.strip().replace(';', ',').replace('\"', '')
    return string


def convertCSVNewFiles(fileName, importLocation, exportLocation):
    importFile = os.path.join(importLocation, fileName)
    exportFile = os.path.join(exportLocation, fileName)
    creation = os.path.getmtime(importFile)
    modification = os.path.getctime(importFile)

    if creation > modification:
        collectionDateUnformatted = time.ctime(modification)
    else:
        collectionDateUnformatted = time.ctime(creation)
    
    collectionDateList = collectionDateUnformatted.split(' ')
    lenghtOfDate = len(collectionDateList)
    if lenghtOfDate == 5:
        collectionDate = f'{collectionDateList[4]}/{MONTHS[collectionDateList[1]]}/{collectionDateList[2]}'
    if lenghtOfDate == 6:
        collectionDate = f'{collectionDateList[5]}/{MONTHS[collectionDateList[1]]}/{collectionDateList[3]}'
    
    fiac = 'FIAC' in fileName

    data = []
    with open(importFile, 'r', encoding='utf-8') as r:
        csvR = csv.reader(r, delimiter=';', quotechar=NEWQUOTE)
        for indx, line in enumerate(csvR):
            if indx == 0:
                for inx, item in enumerate(line):
                    if item in ERRORS.keys():
                        line[inx] = ERRORS[item]
                finalLine = line
                finalLine.append('collectionDate')
                if fiac:
                    finalLine.pop(4)
                    finalLine.append('currency')

                headerLength = len(finalLine)
                data.append(finalLine)
                
            else:
                finalLine = line
                finalLine.append(collectionDate)
                if fiac:
                    finalLine.pop(4)
                    finalLine.append('USD')
                
                if len(finalLine) != headerLength:
                    print(f'lenght error @ {fileName} @ {indx}')
                else:
                    data.append(finalLine)

    numberOfFirstObs = len(data) - 1

    dataConverted = []
    for line in data:
        lineConverted = []
        for item in line:
            itemConverted = cleanString(item)
            lineConverted.append(itemConverted)
        dataConverted.append(lineConverted)
    
    numberOfConvertedObs = len(dataConverted) -1
    
    if numberOfFirstObs != numberOfConvertedObs:
        #print(f'Import error: {importFile}: {numberOfFirstObs} - {numberOfConvertedObs}')
        pass

    with open(exportFile, 'w', encoding='utf-8', newline='') as w:
        csvW = csv.writer(w, delimiter=';')
        for line in dataConverted:
            csvW.writerow(line)


def convertCSV(fileName, importLocation, exportLocation):
    importFile = os.path.join(importLocation, fileName)
    exportFile = os.path.join(exportLocation, fileName)
    creation = os.path.getmtime(importFile)
    modification = os.path.getctime(importFile)

    if creation > modification:
        collectionDateUnformatted = time.ctime(modification)
    else:
        collectionDateUnformatted = time.ctime(creation)
    
    collectionDateList = collectionDateUnformatted.split(' ')
    lenghtOfDate = len(collectionDateList)
    if lenghtOfDate == 5:
        collectionDate = f'{collectionDateList[4]}/{MONTHS[collectionDateList[1]]}/{collectionDateList[2]}'
    if lenghtOfDate == 6:
        collectionDate = f'{collectionDateList[5]}/{MONTHS[collectionDateList[1]]}/{collectionDateList[3]}'
    
    fiac = 'FIAC' in fileName

    data = []
    with open(importFile, 'r', encoding='utf-8') as r:
        csvR = csv.reader(r, delimiter=';', quotechar='|')
        for indx, line in enumerate(csvR):
            if indx == 0:
                for inx, item in enumerate(line):
                    if item in ERRORS.keys():
                        line[inx] = ERRORS[item]
                finalLine = line
                finalLine.append('collectionDate')
                if fiac:
                    finalLine.pop(4)
                    finalLine.append('currency')
                headerLenght = len(finalLine)
                
            else:
                finalLine = line
                finalLine.append(collectionDate)
                if fiac:
                    finalLine.pop(4)
                    finalLine.append('USD')
                if len(finalLine) != headerLenght:
                    print(f'lenght error @ {fileName} @ {indx}')

            for inx, item in enumerate(finalLine):
                finalLine[inx] = item.replace(';', ',')
                
            data.append(finalLine)

    numberOfFirstObs = len(data) - 1

    dataConverted = []
    for line in data:
        lineConverted = []
        for item in line:
            itemConverted = cleanString(item)
            lineConverted.append(itemConverted)
        dataConverted.append(lineConverted)
    
    numberOfConvertedObs = len(dataConverted) -1
    
    if numberOfFirstObs != numberOfConvertedObs:
        print(f'Import error: {importFile}: {numberOfFirstObs} - {numberOfConvertedObs}')
    
    with open(exportFile, 'w', encoding='utf-8', newline='') as w:
        csvW = csv.writer(w, delimiter=';')
        for line in dataConverted:
            csvW.writerow(line)


def checkVariableNames(f, importLocation, listOfVariables):
    importFile = os.path.join(importLocation, f)
    with open(importFile, 'r', encoding='utf-8') as r:
        csvR = csv.reader(r, delimiter=';', quotechar='|')
        headers = next(csvR)
        lenght = len(headers)
        for item in headers:
            if item not in listOfVariables:
                listOfVariables.append(item)
        for indx, row in enumerate(csvR):
            if len(row) != lenght:
                print(f'row {indx} wrong lenght in {f}')
    return listOfVariables


if __name__ == '__main__':
    listOfVariables = []
    for key in IMPORTLOCATIONS:
        allFiles = os.listdir(IMPORTLOCATIONS[key])
        files = [file for file in allFiles if file.endswith('.csv')]
        
        if key == 'artsyFairs':
            #allFiles = os.listdir(IMPORTLOCATIONS[key])
            #files = [file for file in allFiles if file.endswith('.csv')]

            for f in files:
                convertCSVNewFiles(f, IMPORTLOCATIONS[key], EXPORTLOCATIONS[key])
        
        elif key == 'artsyPastFairs':
            for f in files:
                convertCSVNewFiles(f, IMPORTLOCATIONS[key], EXPORTLOCATIONS[key])
        elif key == 'newArt':
            for f in files:
                convertCSVNewFiles(f, IMPORTLOCATIONS[key], EXPORTLOCATIONS[key])
        else:
            for f in files:
                convertCSV(f, IMPORTLOCATIONS[key], EXPORTLOCATIONS[key])
       
        # print(listOfVariables)
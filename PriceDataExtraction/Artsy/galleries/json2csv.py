import json
import csv
import os
from tqdm import tqdm


CD = r'D:\Said Business School\ArtsyAPI\Galleries'









    



if __name__ == '__main__':
    exportData = []
    files = os.listdir(CD)
    pbar = tqdm(desc='Fetching JSON Data', total=len(files))
    for file in files:
        with open(os.path.join(CD, file), 'r', encoding='utf-8') as r:
            jsonData = json.load(r)
            gallery = extractJSONData(jsonData)
            exportData.append(gallery)

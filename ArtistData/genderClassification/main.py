import wiki_classification
import pandas as pd
from multiprocessing.pool import ThreadPool


DATALOC = r'C:\Users\Milan\OneDrive\Desktop\SBS\Gender Classification\data\sampleClassifiedArtistData.xlsx'
EXPORTLOC = r'C:\Users\Milan\OneDrive\Desktop\SBS\Gender Classification\data\testClassificationData.xlsx'


def importData():
    df = pd.read_excel(DATALOC, sheet_name='Sheet1', header=0, index_col=0)
    return df


def exportData(df: pd.DataFrame):
    with pd.ExcelWriter(EXPORTLOC) as w:
        df.to_excel(w, sheet_name='Data', index=False)


if __name__ == '__main__':
    df = importData()

    # Fetch wikipedia data
    pool = ThreadPool(40)
    wikiresults = pool.map(wiki_classification.getWikiData, df.iterrows())
    wikidf = pd.DataFrame(wikiresults)
    exportData(wikidf)

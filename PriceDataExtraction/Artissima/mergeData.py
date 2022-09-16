# Description: This code is used to merge multiple saves from Artissima into a final export file
# that can be used for analitical purposes.
#
# Author: Milan Makany
# Organisation: Said Business School


import os
import csv


folderloc = r'C:\Users\Milán\OneDrive\Desktop\SBS\Artworks\Artissima\data'
files = []


def imFolder():
    for item in os.listdir(folderloc):
        if item.endswith('.csv'):
            files.append(folderloc + '\\' + item)




if __name__ == '__main__':
    imFolder()
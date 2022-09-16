import json
import csv

from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

import os
from time import perf_counter


CD = r'D:\Said Business School\json\spotlight'
EXPORTLOC = r'C:\Users\Milan\OneDrive\Desktop\Said\Art\ArtistData\artFacts\data\genderData.csv'
SAMPLE = r'C:\Users\Milan\OneDrive\Desktop\Said\Art\ArtistData\artFacts\data\sample.json'
LOCK = Lock()


def fetchFiles():
    files = []
    for item in os.listdir(CD):
        files.append(item)
    return files


def JSONextractor(jsonLoc):
    path = os.path.join(CD, jsonLoc)
    with open(path, 'r', encoding='utf-8') as f:
        jO = json.loads(f.read())
    try:
        idnum = jO['id']
    except:
        idnum = ''
    try:
        name = jO['name'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        name = ''
    try:
        first_name = jO['first_name'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        first_name = ''
    try:
        last_name = jO['last_name'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        last_name = ''
    try:
        aliases = ', '.join(jO['aliases']).replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        aliases = ''
    try:
        birth_date = jO['birth_date']
    except:
        birth_date = ''
    try:
        birth_year = jO['birth_year']
    except:
        birth_year = ''
    try:
        birth_location = jO['birth_location'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        birth_location = ''
    try:
        death_date = jO['death_date']
    except:
        death_date = ''
    try:
        death_year = jO['death_year']
    except:
        death_year = ''
    try:
        death_location = jO['death_location'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        death_location = ''
    try:
        sector = jO['sector'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        sector = ''
    try:
        gender = jO['gender']
    except:
        gender = ''
    try:
        nationalityP = jO['nationality']
        if type(nationalityP) is str:
            nationality = nationalityP
        if type(nationalityP) is list:
            nationality = ', '.join(nationalityP).replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
        else:
            nationality = nationalityP
    except:
        nationality = ''
    try:
        movements = ', '.join(jO['movements']).replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        movements = ''
    try:
        media = ', '.join(jO['media']).replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        media = ''
    try:
        link_artFacts = jO['links']['profile'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        link_artFacts = ''
    try:
        link_personal = jO['links']['www'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        link_personal = ''
    try:
        links_wiki = jO['links']['wikipedia'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        links_wiki = ''
    try:
        ranking = jO['ranking']
    except:
        ranking = ''
    try:
        ranking_trend = jO['ranking_trend']
    except:
        ranking_trend = ''
    try:
        citiesList = [city['name'] for city in jO['cities']]
        cities = ', '.join(citiesList).replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '').replace(';', ',')
    except:
        cities = ''
    try:
        countriesList = [country['name'] for country in jO['countries']]
        countries = ', '.join(countriesList).replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '').replace(';', ',')
    except:
        countries = ''
    try:
        artistsList = [artist['name'] for artist in jO['artists']]
        artists = ', '.join(artistsList).replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '').replace(';', ',')
    except:
        artists = ''
    try:
        groupsList = [group['name'] for group in jO['groups']]
        groups = ', '.join(groupsList).replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '').replace(';', ',')
    except:
        groups = ''
    try:
        most_exhibitions_in_countries_1 = jO['most_exhibitions_in'][0]['country']['name'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
        most_exhibitions_in_counts_1 = jO['most_exhibitions_in'][0]['count']
    except:
        most_exhibitions_in_countries_1 = ''
        most_exhibitions_in_counts_1 = ''
    try:
        most_exhibitions_in_countries_2 = jO['most_exhibitions_in'][1]['country']['name'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
        most_exhibitions_in_counts_2 = jO['most_exhibitions_in'][1]['count']
    except:
        most_exhibitions_in_countries_2 = ''
        most_exhibitions_in_counts_2 = ''
    try:
        most_exhibitions_in_countries_3 = jO['most_exhibitions_in'][2]['country']['name'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
        most_exhibitions_in_counts_3 = jO['most_exhibitions_in'][2]['count']
    except:
        most_exhibitions_in_countries_3 = ''
        most_exhibitions_in_counts_3 = ''
    try:
        most_important_exhibitions_at_institution_1 = jO['most_important_exhibitions_at'][0]['name'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_institution_1 = ''
    try:
        most_important_exhibitions_at_id_1 = jO['most_important_exhibitions_at'][0]['id']
    except:
        most_important_exhibitions_at_id_1 = ''
    try:
        most_important_exhibitions_at_link_artFacts_1 = jO['most_important_exhibitions_at'][0]['links']['profile'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_artFacts_1 = ''
    try:
        most_important_exhibitions_at_link_institutional_1 = jO['most_important_exhibitions_at'][0]['links']['www'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_institutional_1 = ''
    try:
        most_important_exhibitions_at_link_facebook_1 = jO['most_important_exhibitions_at'][0]['links']['facebook'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_facebook_1 = ''
    try:
        most_important_exhibitions_at_link_twitter_1 = jO['most_important_exhibitions_at'][0]['links']['twitter'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_twitter_1 = ''
    try:
        most_important_exhibitions_at_link_wiki_1 = jO['most_important_exhibitions_at'][0]['links']['wikipedia'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_wiki_1 = ''

    try:
        most_important_exhibitions_at_institution_2 = jO['most_important_exhibitions_at'][1]['name'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_institution_2 = ''
    try:
        most_important_exhibitions_at_id_2 = jO['most_important_exhibitions_at'][1]['id']
    except:
        most_important_exhibitions_at_id_2 = ''
    try:
        most_important_exhibitions_at_link_artFacts_2 = jO['most_important_exhibitions_at'][1]['links']['profile'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_artFacts_2 = ''
    try:
        most_important_exhibitions_at_link_institutional_2 = jO['most_important_exhibitions_at'][1]['links']['www'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_institutional_2 = ''
    try:
        most_important_exhibitions_at_link_facebook_2 = jO['most_important_exhibitions_at'][1]['links']['facebook'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_facebook_2 = ''
    try:
        most_important_exhibitions_at_link_twitter_2 = jO['most_important_exhibitions_at'][1]['links']['twitter'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_twitter_2 = ''
    try:
        most_important_exhibitions_at_link_wiki_2 = jO['most_important_exhibitions_at'][1]['links']['wikipedia'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_wiki_2 = ''

    try:
        most_important_exhibitions_at_institution_3 = jO['most_important_exhibitions_at'][2]['name'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_institution_3 = ''
    try:
        most_important_exhibitions_at_id_3 = jO['most_important_exhibitions_at'][2]['id']
    except:
        most_important_exhibitions_at_id_3 = ''
    try:
        most_important_exhibitions_at_link_artFacts_3 = jO['most_important_exhibitions_at'][2]['links']['profile'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_artFacts_3 = ''
    try:
        most_important_exhibitions_at_link_institutional_3 = jO['most_important_exhibitions_at'][2]['links']['www'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_institutional_3 = ''
    try:
        most_important_exhibitions_at_link_facebook_3 = jO['most_important_exhibitions_at'][2]['links']['facebook'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_facebook_3 = ''
    try:
        most_important_exhibitions_at_link_twitter_3 = jO['most_important_exhibitions_at'][2]['links']['twitter'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_twitter_3 = ''
    try:
        most_important_exhibitions_at_link_wiki_3 = jO['most_important_exhibitions_at'][2]['links']['wikipedia'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        most_important_exhibitions_at_link_wiki_3 = ''

    try:
        national_ranking = jO['national_ranking'][0]['rank'] + ' ' + jO['national_ranking'][0]['iso2'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        national_ranking = ''
    try:
        description = jO['description'].replace(';', ',').strip().replace('\n', ' ').replace('\r', '').replace('\'', '').replace('\"', '')
    except:
        description = ''
    try:
        exhibitions_total = jO['counts']['exhibition']['total']
    except:
        exhibitions_total = ''
    try:
        exhibitions_solo = jO['counts']['exhibition']['solo']
    except:
        exhibitions_solo = ''
    try:
        exhibitions_group = jO['counts']['exhibition']['group']
    except:
        exhibitions_group = ''
    try:
        exhibitions_artfair = jO['counts']['exhibition']['artfair']
    except:
        exhibitions_artfair = ''
    try:
        exhibitions_collective = jO['counts']['exhibition']['collective']
    except:
        exhibitions_collective = ''
    try:
        exhibitions_current = jO['counts']['exhibition']['current']
    except:
        exhibitions_current = ''
    try:
        exhibitions_biennial = jO['counts']['exhibition']['biennial']
    except:
        exhibitions_biennial = ''

    try:
        exhibitions_region_EasternAfrica = jO['counts']['exhibition_per_region'][0]['count']
    except:
        exhibitions_region_EasternAfrica = ''
    try:
        exhibitions_region_MiddleAfrica = jO['counts']['exhibition_per_region'][1]['count']
    except:
        exhibitions_region_MiddleAfrica = ''
    try:
        exhibitions_region_NorthernAfrica = jO['counts']['exhibition_per_region'][2]['count']
    except:
        exhibitions_region_NorthernAfrica = ''
    try:
        exhibitions_region_SouthernAfrica = jO['counts']['exhibition_per_region'][3]['count']
    except:
        exhibitions_region_SouthernAfrica = ''
    try:
        exhibitions_region_WesternAfrica = jO['counts']['exhibition_per_region'][4]['count']
    except:
        exhibitions_region_WesternAfrica = ''
    try:
        exhibitions_region_Caribbean = jO['counts']['exhibition_per_region'][5]['count']
    except:
        exhibitions_region_Caribbean = ''
    try:
        exhibitions_region_CentralAmerica = jO['counts']['exhibition_per_region'][6]['count']
    except:
        exhibitions_region_CentralAmerica = ''
    try:
        exhibitions_region_SouthAmerica = jO['counts']['exhibition_per_region'][7]['count']
    except:
        exhibitions_region_SouthAmerica = ''
    try:
        exhibitions_region_NorthernAmerica = jO['counts']['exhibition_per_region'][8]['count']
    except:
        exhibitions_region_NorthernAmerica = ''
    try:
        exhibitions_region_CentralAsia = jO['counts']['exhibition_per_region'][9]['count']
    except:
        exhibitions_region_CentralAsia = ''
    try:
        exhibitions_region_EasternAsia = jO['counts']['exhibition_per_region'][10]['count']
    except:
        exhibitions_region_EasternAsia = ''
    try:
        exhibitions_region_SouthernAsia = jO['counts']['exhibition_per_region'][11]['count']
    except:
        exhibitions_region_SouthernAsia = ''
    try:
        exhibitions_region_SouthEasternAsia = jO['counts']['exhibition_per_region'][12]['count']
    except:
        exhibitions_region_SouthEasternAsia = ''
    try:
        exhibitions_region_WesternAsia = jO['counts']['exhibition_per_region'][13]['count']
    except:
        exhibitions_region_WesternAsia = ''
    try:
        exhibitions_region_EasternEurope = jO['counts']['exhibition_per_region'][14]['count']
    except:
        exhibitions_region_EasternEurope = ''
    try:
        exhibitions_region_NorthernEurope = jO['counts']['exhibition_per_region'][15]['count']
    except:
        exhibitions_region_NorthernEurope = ''
    try:
        exhibitions_region_SouthernEurope = jO['counts']['exhibition_per_region'][16]['count']
    except:
        exhibitions_region_SouthernEurope = ''
    try:
        exhibitions_region_WesternEurope = jO['counts']['exhibition_per_region'][17]['count']
    except:
        exhibitions_region_WesternEurope = ''
    try:
        exhibitions_region_Australia_NewZealand = jO['counts']['exhibition_per_region'][18]['count']
    except:
        exhibitions_region_Australia_NewZealand = ''
    try:
        exhibitions_region_Melanesia = jO['counts']['exhibition_per_region'][19]['count']
    except:
        exhibitions_region_Melanesia = ''
    try:
        exhibitions_region_Polynesia = jO['counts']['exhibition_per_region'][20]['count']
    except:
        exhibitions_region_Polynesia = ''
    try:
        exhibitions_region_Micronesia = jO['counts']['exhibition_per_region'][21]['count']
    except:
        exhibitions_region_Micronesia = ''

    try:
        exhebitions_institution_museum = jO['counts']['exhibition_by_institution_type'][0][1]
    except:
        exhebitions_institution_museum = ''
    try:
        exhebitions_institution_gallery = jO['counts']['exhibition_by_institution_type'][1][1]
    except:
        exhebitions_institution_gallery = ''
    try:
        exhebitions_institution_artfair = jO['counts']['exhibition_by_institution_type'][2][1]
    except:
        exhebitions_institution_artfair = ''
    try:
        exhebitions_institution_biennial = jO['counts']['exhibition_by_institution_type'][3][1]
    except:
        exhebitions_institution_biennial = ''
    try:
        exhebitions_institution_other = jO['counts']['exhibition_by_institution_type'][4][1]
    except:
        exhebitions_institution_other = ''

    try:
        catalog = jO['counts']['catalog']
    except:
        catalog = ''
    try:
        dealer = jO['counts']['dealer']
    except:
        dealer = ''
    try:
        collection = jO['counts']['collection']
    except:
        collection = ''

    return [
        idnum, name, first_name, last_name, aliases,
        birth_date, birth_year, birth_location, death_date,
        death_year, death_location, sector, gender,
        nationality, movements, media, link_artFacts,
        link_personal, links_wiki, ranking, ranking_trend,
        cities, countries, artists, groups,
        most_exhibitions_in_countries_1,
        most_exhibitions_in_counts_1,
        most_exhibitions_in_countries_2,
        most_exhibitions_in_counts_2,
        most_exhibitions_in_countries_3,
        most_exhibitions_in_counts_3,

        most_important_exhibitions_at_institution_1,
        most_important_exhibitions_at_id_1,
        most_important_exhibitions_at_link_artFacts_1,
        most_important_exhibitions_at_link_institutional_1,
        most_important_exhibitions_at_link_facebook_1,
        most_important_exhibitions_at_link_twitter_1,
        most_important_exhibitions_at_link_wiki_1,

        most_important_exhibitions_at_institution_2,
        most_important_exhibitions_at_id_2,
        most_important_exhibitions_at_link_artFacts_2,
        most_important_exhibitions_at_link_institutional_2,
        most_important_exhibitions_at_link_facebook_2,
        most_important_exhibitions_at_link_twitter_2,
        most_important_exhibitions_at_link_wiki_2,


        most_important_exhibitions_at_institution_3,
        most_important_exhibitions_at_id_3,
        most_important_exhibitions_at_link_artFacts_3,
        most_important_exhibitions_at_link_institutional_3,
        most_important_exhibitions_at_link_facebook_3,
        most_important_exhibitions_at_link_twitter_3,
        most_important_exhibitions_at_link_wiki_3,

        national_ranking, description, exhibitions_total,
        exhibitions_solo, exhibitions_group, exhibitions_artfair,
        exhibitions_collective, exhibitions_current,
        exhibitions_biennial,
        exhibitions_region_EasternAfrica,
        exhibitions_region_MiddleAfrica,
        exhibitions_region_NorthernAfrica,
        exhibitions_region_SouthernAfrica,
        exhibitions_region_WesternAfrica,
        exhibitions_region_Caribbean,
        exhibitions_region_CentralAmerica,
        exhibitions_region_SouthAmerica,
        exhibitions_region_NorthernAmerica,
        exhibitions_region_CentralAsia,
        exhibitions_region_EasternAsia,
        exhibitions_region_SouthernAsia,
        exhibitions_region_SouthEasternAsia,
        exhibitions_region_WesternAsia,
        exhibitions_region_EasternEurope,
        exhibitions_region_NorthernEurope,
        exhibitions_region_SouthernEurope,
        exhibitions_region_WesternEurope,
        exhibitions_region_Australia_NewZealand,
        exhibitions_region_Melanesia,
        exhibitions_region_Polynesia,
        exhibitions_region_Micronesia,
        exhebitions_institution_museum,
        exhebitions_institution_gallery,
        exhebitions_institution_artfair,
        exhebitions_institution_biennial,
        exhebitions_institution_other,
        catalog, dealer, collection
    ]


def setupCSV():
    keys = [
        'id', 'name', 'first_name', 'last_name', 'aliases', 'birth_date',
        'birth_year', 'birth_location', 'death_date', 'death_year',
        'death_location', 'sector', 'gender', 'nationality', 'movements',
        'media', 'link_artFacts', 'link_personal', 'links_wiki',
        'ranking', 'ranking_trend', 'cities', 'countries', 'artists',
        'groups',

        'exhibitions_in_country_1', 'exhibitions_in_count_1',
        'exhibitions_in_country_2', 'exhibitions_in_count_2',
        'exhibitions_in_country_3', 'exhibitions_in_count_3',

        'exhibitions_at_institution_1',
        'institution_id_1',
        'institution_1_link_artFacts',
        'institution_1_link',
        'institution_1_link_facebook',
        'institution_1_link_twitter',
        'institution_1_link_wiki',

        'exhibitions_at_institution_2',
        'institution_id_2',
        'institution_2_link_artFacts',
        'institution_2_link',
        'institution_2_link_facebook',
        'institution_2_link_twitter',
        'institution_2_link_wiki',

        'exhibitions_at_institution_3',
        'institution_id_3',
        'institution_3_link_artFacts',
        'institution_3_link',
        'institution_3_link_facebook',
        'institution_3_link_twitter',
        'institution_3_link_wiki',

        'national_ranking', 'description',

        'exhibitions_total', 'exhibitions_solo', 'exhibitions_group',
        'exhibitions_artfair', 'exhibitions_collective',
        'exhibitions_current', 'exhibitions_biennial',

        'exhibitions_region_EastAfrica',
        'exhibitions_region_MiddleAfrica',
        'exhibitions_region_NorthAfrica',
        'exhibitions_region_SouthAfrica',
        'exhibitions_region_WestAfrica',
        'exhibitions_region_Caribbean',
        'exhibitions_region_CentralAmerica',
        'exhibitions_region_SouthAmerica',
        'exhibitions_region_NorthAmerica',
        'exhibitions_region_CentralAsia',
        'exhibitions_region_EastAsia',
        'exhibitions_region_SouthAsia',
        'exhibitions_region_SouthEastAsia',
        'exhibitions_region_WestAsia',
        'exhibitions_region_EastEurope',
        'exhibitions_region_NorthEurope',
        'exhibitions_region_SouthEurope',
        'exhibitions_region_WestEurope',
        'exhibitions_region_Australia-NewZealand',
        'exhibitions_region_Melanesia',
        'exhibitions_region_Polynesia',
        'exhibitions_region_Micronesia',

        'exhebitions_museum',
        'exhebitions_gallery',
        'exhebitions_artfair',
        'exhebitions_biennial',
        'exhebitions_other',

        'catalog', 'dealer', 'collection'
    ]

    with open(EXPORTLOC, 'w', encoding='utf-8', newline='') as w:
        csvW = csv.writer(w, delimiter=';')
        csvW.writerow(keys)


if __name__ == '__main__':
    timerStart = perf_counter()
    files = fetchFiles()
    timerEnd = perf_counter()
    print(f'{len(files)} files located in {timerEnd - timerStart} seconds.')

    setupCSV()
    print('CSV Setup Complete.')

    fileStream = open(EXPORTLOC, 'a', encoding='utf-8', newline='')
    writer = csv.writer(fileStream, delimiter=';', quotechar='|')

    pbar = tqdm(desc='Extracting Artist Data', total=len(files))

    with ThreadPoolExecutor(max_workers=20, thread_name_prefix='jsonExtractor') as ex:
        lock = Lock()
        futures = {ex.submit(JSONextractor, jL): jL for jL in files}
        for future in as_completed(futures):
            pbar.update(1)
            try:
                data = future.result()
                lock.acquire()
                writer.writerow(data)
                lock.release()
            except Exception as e:
                print(e)

    fileStream.close()
    pbar.close()

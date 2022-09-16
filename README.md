# Artwork-Research
Extract, clean and store artwork price data for research purposes

## Uses
- Extract artwork price data
- Extract artist characteristics data
- Extract artwork images
- Merge price data

## Scripts
| Filename | Purpose | Description |
| --- | --- | --- |
| panel_transform.do | Data Manipulation | Transforms data for panel year-country analysis. |
| panel_transform_raw_alg.do | Algorithm | Raw algorithm of panel_tranform.do |
| master_price_merge.do | Data Manipulation | Merge all artwork price, artist, and fair data |
| panel_transform_raw_alg.do | Algorithm | Raw algorithm of panel_tranform.do |
| adams_et_al_2021_analysis_replication.do | Analysis | Preliminary replication of regressions ran in Adams et al. (2021)|
| materials_frequency.py | Analysis | Extract the frequency of materials used in artworks |
| csv_format_converter.py | Data Manipulation | Format CSV files for Stata compatibility |
| artist_gender_match.py | Data Merging | Merge artists to our artist database - Specific use case|
| artist_gender_match.do | Data Merging | Merge artists to our artist database - Specific use case|


## Scripts > Side-Projects
| Filename | Purpose | Description |
| mailbox_extraction | Data Extraction | Contains scripts to automate data extraction and email sending |
| --- | --- | --- |
| automated_gallery_messages > send_emails.py | Data Collection | Automatically compose and send out pre-formatted emails |
| automated_gallery_messages > login.py | Settings | Store the login information for the mailbox |
| --- | --- | --- |
| extraction > send_emails.py | Data Collection | Extract email data including sender, date, title, contents, attachments |
| extraction > login.py | Settings | Store the login information for the mailbox |

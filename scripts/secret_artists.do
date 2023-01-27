global masterDataFile = "C:\Users\Milan\Dropbox\ArtFairs\Data\priceMaster-02-11-2021.dta"
global secretArtistsFile = "C:\Users\Milan\Dropbox\ArtFairs\Data\SecretArtists\secretartists20230109.xls"
global secretArtistsPostcardFile = "C:\Users\Milan\Dropbox\ArtFairs\Data\SecretArtists\secretartonapostcard20230109.xls"

global exportDir = "C:\Users\Milan\Dropbox\ArtFairs\Data\SecretArtists\"

* merge secret artists
clear
import excel using "$secretArtistsFile", firstrow
cd "$exportDir"
replace artist_forename = upper(artist_forename)
save secret_artists.dta, replace

clear
import excel using "$secretArtistsPostcardFile", firstrow
cd "$exportDir"
replace artist_forename = upper(artist_forename)
save secret_artists_postcard.dta, replace


use "$masterDataFile"
replace artist = upper(artist)
save "$masterDataFile", replace


cd "$exportDir"
clear
use secret_artists
gen artist = artist_forename + " " + artist_surname
joinby artist using "$masterDataFile", unm(master)
keep (artist_surname artist_forename minyear maxyear artist fair_name fair_year gender title low_price_usd high_price_usd year_completed gallery category materials length_in width_in depth_in sold_inferred)

drop artist
gen artist = artist_surname + " " + artist_forename
joinby artist using "$masterDataFile", unm(master)
keep (artist_surname artist_forename minyear maxyear artist fair_name fair_year gender title low_price_usd high_price_usd year_completed gallery category materials length_in width_in depth_in sold_inferred)

save secret_artists, replace


clear
use secret_artists_postcard
gen artist = artist_forename + " " + artist_surname
joinby artist using "$masterDataFile", unm(master)
keep (artist_surname artist_forename minyear maxyear artist fair_name fair_year gender title low_price_usd high_price_usd year_completed gallery category materials length_in width_in depth_in sold_inferred)

drop artist
gen artist = artist_surname + " " + artist_forename
joinby artist using "$masterDataFile", unm(master)
keep (artist_surname artist_forename minyear maxyear artist fair_name fair_year gender title low_price_usd high_price_usd year_completed gallery category materials length_in width_in depth_in sold_inferred)

save secret_artists_postcard, replace


*keepsuing(artist fair_name fair_year gender title price year_completed gallery category materials length_in width_in depth_in sold_inferred)
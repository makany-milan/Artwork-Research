/*
Create master files for all the art data available.


Author: Milan Makany
Version: v1.1 (14/04/2021)


1) Price Data [DONE]
	a) Artsy fairs since October 2020
	b) Artsy fairs before October 2020
	c) Artsy collections (many saves on different dates) (not fair data)
	d) Non-Artsy Data
		dA) ArtBasel:OVR
		dB) Artissima (many saves on different dates)
		dC) FIAC (many saves on different dates)
		dD) Frieze Masters and London (many saves on different dates)
		dE) Vienna Contemporary (many saves on different dates)
		dF) Sotheby's (many saves on different dates) (not fair data)
		dG) GalleryPlatformLA (many saves on different dates) (not fair data)
		dH) Frieze
		dI) Merge all non-artsy fair files
		
2) Fair Data
	Merge for fairID & fair location

3) Artist/Gender Data
	_a) WE CAN USE THE MASTER MERGED DATABASE!
	(
	a) Artsy JSON & Dataset
	b) ArtFacts JSON
	c) Auction dataset from Renée
	d) Blouin
	e) Decision Tree & Neural Network models for unmatched artists
	)
	
4) Reformat variables and correct issues with the data


IDEAS:
	- Some part artsy fairs have corrupt gallery and artist data. Re-run codes
		with improved JSON extractor method.
		
	- Create a FairID variable for easier filtering
		merge 1:1 fairName year -> unique image_ID and fair_ID match
		
	- Since there are fairs for which we have price data on multiple days, create
		a date saved variable. Use metadata from file / extract from filename.
		Extracting metadata might only be possible in python.
		!!! Look into it further !!!
	
	- Reformat csv files (DONE)
	
	- Create dummy variable for fairs for easier filtering (DONE: isFair)
	
	- Some duplicates exist intra-fair. (DONE)
		Drop duplicates when reading in data or at the end
		CODE:
			bys url fair: gen _dupe = cond(_N==1, 0, _n)
		see: "intra_fair_dupes.png" for list
*/


/*
CHANGELOG:
	- 14/04/2021	improved documentation and comments.
	
	- 06/04/2021	reformated csv files to use " as quotechar. quoted lines
					that were necessary due to this error.
					marked: "FIXED: REFORMATED CSV FILES"
*/



*******************************************************************************

*					0) Setup Export Directory
global masterDir = "C:\Users\Milan\OneDrive\Desktop\Oxford-Art"
global scriptsDir = "$masterDir\scripts"


global exportDir = "D:\oxford\07-10-2022\"
global rawDataDir = "D:\oxford\rawdata\"
capture mkdir $exportDir
global priceDataDir = "$exportDir\PriceData"
capture mkdir $priceDataDir


*						1) Price Data
* Setting the export location for the different price datasets

* 				1a) Price Data: Artsy Fairs since October 2020
local exportDir = "$priceDataDir\artsyFairs"
capture mkdir `exportDir'
local importDir = "$rawDataDir\artsyFairs"
local files: dir "`importDir'" files "*.csv"
* Convert .csv files to .dta
foreach file of local files {
    * Clear memory
    clear
	cd `importDir'
	* With the reformatted csv files bindquotes(strict) is the best setting
	import delimited using "`file'", varnames(1) delimiter(";") encoding(utf-8) bindquotes(strict)
	* Check if the csv file already has id-s assigned to the artworks. If not assign them.
	* Inconsistencies might arise for fairs that were saved on multiple occasions.
	capture confirm variable id
	* If the variable id does not exist, generate the id numbers.
	if !!_rc {
	    qui: gen int id = _n, before(artist)
	}
	* Create fair variable to store the name of the fair.
	local fairName = subinstr("`file'", ".csv", "", .)
	qui: gen str fair = "`fairName'", before(id)
	qui: gen str filename = "`file'", before(id)
	* Generate dummy variable indicating the data is from a fair.
	qui: gen isFair = 1
	* Create a .dta file with the same name as the .csv file
	cd `exportDir'
	save "`fairName'.dta", replace
}
* Create a master file from the individual .dta files.
clear
* Generate the different variables and their default empty values.
* Every string variable is stored as strL to avoid issues when appending.
* When the merge is complete use compress to save disk space.
gen strL fair = ""
gen byte isFair = .
gen strL filename = ""
gen int id = .
gen strL artist = ""
gen strL artist_slug = ""
gen strL title = ""
gen strL year = ""
gen strL gallery = ""
gen strL gallery_slug = ""
gen strL price = ""
gen str3 currency = ""
gen strL category = ""
gen strL materials = ""
gen strL dimensions = ""
gen strL url = ""
gen strL image_url = ""
gen strL collectiondate = ""

* Save the empty file and append the data.
cd $priceDataDir
save "fairs.dta", replace
local stataFiles: dir "`exportDir'" files "*.dta"
foreach file of local stataFiles {
    cd `exportDir'
	append using "`file'", force // keep(fair isFair id artist title year gallery price currency category materials dimensions url image_url)
	
}

/*
					FIXED: REFORMATED CSV FILES
					IGNORE COMMENTED LINES
* Some records in the csv are imported incorrectly due to stata not being able
* to handle custom quotechars. 
* Untill a solution is found drop where the image_id and url is invalid
* 86 observations in total.
drop if strpos(image_url, "cloudfront") == 0
drop if strpos(url, "artsy") == 0
*/

* Recast and compress string variables to save space
recast str2045 artist artist_slug title year gallery gallery_slug price currency category materials dimensions url image_url collectiondate filename
compress
cd $priceDataDir
* Save the submaster file for fairs.
save "fairs.dta", replace


*					1b) Artsy fairs before October 2020 (Past Fairs)
* Some data is corrupt due to issues in Artsy's system.
* Fix in progress: 	Re-download data from past artsy fairs with improved
* 					algorithm
clear
local exportDir = "$priceDataDir\pastFairs"
capture mkdir `exportDir'
local importDir = "$rawDataDir\artsyPastFairs"
local files: dir "`importDir'" files "*.csv"
* Convert .csv files to .dta
foreach file of local files {
    * Clear memory
    clear
	cd `importDir'
	* With the reformatted csv files bindquotes(strict) is the best setting
	import delimited using "`file'", varnames(1) delimiter(";") encoding(utf-8) bindquotes(strict)
	* Check if the csv file already has id-s assigned to the artworks. If not assign them.
	* Inconsistencies might arise for fairs that were saved on multiple occasions.
	capture confirm variable id
	* If the variable id does not exist, generate the id numbers.
	if !!_rc {
	    qui: gen int id = _n, before(artist)
	}
	* Create fair variable to store the name of the fair.
	local fairName = subinstr("`file'", ".csv", "", .)
	qui: gen str fair = "`fairName'", before(id)
	qui: gen str filename = "`file'", before(id)
	qui: gen byte isFair = 1
	* Create a .dta file with the same name as the .csv file
	cd `exportDir'
	save "`fairName'.dta", replace
}
* Create a master file from the individual .dta files.
clear
* Generate the different variables and their default empty values.
* Every string variable is stored as strL to avoid issues when appending.
* When the merge is complete use compress to save disk space.
gen strL fair = ""
gen byte isFair = .
gen strL filename = ""
gen int id = .
gen strL artist = ""
gen strL artist_slug = ""
gen strL title = ""
gen strL year = ""
gen strL gallery = ""
gen strL gallery_slug = ""
gen strL price = ""
gen str3 currency = ""
gen strL category = ""
gen strL materials = ""
gen strL dimensions = ""
gen strL url = ""
gen strL image_url = ""
gen strL collectiondate = ""


cd $priceDataDir
save "pastFairs.dta", replace

local stataFiles: dir "`exportDir'" files "*.dta"
foreach file of local stataFiles {
    cd `exportDir'
	append using "`file'", force // keep(fair isFair id artist title year gallery price currency category materials dimensions url image_url)
	
}

/*
					FIXED: REFORMATED CSV FILES
					IGNORE COMMENTED LINES
* Some records in the csv are imported incorrectly due to stata not being able
* to handle custom quotechars. 
* Untill a solution is found drop where the image_id and url is invalid
drop if strpos(image_url, "cloudfront") == 0
drop if strpos(url, "artsy") == 0
*/

* Recast and compress string variables to save space
recast str2045 artist artist_slug title year gallery gallery_slug price currency category materials dimensions url image_url collectiondate filename
compress
cd $priceDataDir
save "pastFairs.dta", replace


*		1c) Artsy collections (many saves on different dates) (not fair data)
clear
local exportDir = "$priceDataDir\collections"
capture mkdir `exportDir'
local importDir = "$rawDataDir\artsyCollections"
local files: dir "`importDir'" files "*.csv"
* Convert .csv files to .dta
foreach file of local files {
    * Clear memory
    clear
	cd `importDir'
	import delimited using "`file'", varnames(1) delimiter(";") encoding(utf-8) bindquotes(strict)
	* Check if the csv file already has id-s assigned to the artworks. If not assign them.
	* Inconsistencies might arise for fairs that were saved on multiple occasions.
	capture confirm variable id
	* If the variable id does not exist, generate the id numbers.
	if !!_rc {
	    qui: gen long id = _n, before(artist)
	}
	* Create fair variable to store the name of the fair.
	local fairName = subinstr("`file'", ".csv", "", .)
	qui: gen str fair = "`fairName'", before(id)
	qui: gen str filename = "`file'", before(id)
	qui: gen byte isFair = 0
	* Create a .dta file with the same name as the .csv file
	cd `exportDir'
	save "`fairName'.dta", replace
}
* Create a master file from the individual .dta files.
clear
* Generate the different variables and their default empty values.
* Every string variable is stored as strL to avoid issues when appending.
* When the merge is complete use compress to save disk space.
gen strL fair = ""
gen byte isFair = .
gen strL filename = ""
gen long id = .
gen strL artist = ""
gen strL title = ""
gen strL year = ""
gen strL gallery = ""
gen strL price = ""
gen str3 currency = ""
gen strL category = ""
gen strL materials = ""
gen strL dimensions = ""
gen strL url = ""
gen strL image_url = ""
gen strL collection_url = ""

cd $priceDataDir
save "collections.dta", replace

local stataFiles: dir "`exportDir'" files "*.dta"
foreach file of local stataFiles {
    cd `exportDir'
	append using "`file'", force // keep(fair isFair id artist title year gallery price currency category materials dimensions url image_url collection_url)
}

/*
					FIXED: REFORMATED CSV FILES
					IGNORE COMMENTED LINES
* Some records in the csv are imported incorrectly due to stata not being able
* to handle custom quotechars. 
* Untill a solution is found drop where the image_id and url is invalid
drop if strpos(image_url, "cloudfront") == 0
drop if strpos(url, "artsy") == 0
*/

* Recast and compress string variables to save space
recast str2045 artist title year gallery price currency category materials dimensions url image_url filename collection_url
compress
cd $priceDataDir
save "collections.dta", replace



*					1dA) ArtBasel:OVR
clear
local exportDir = "$priceDataDir\nonArtsy"
capture mkdir `exportDir'
local importDir = "$rawDataDir\nonArtsy\ArtBaselOVR"
local files: dir "`importDir'" files "*.csv"
* Convert .csv files to .dta
foreach file of local files {
    * Clear memory
    clear
	cd `importDir'
	import delimited using "`file'", varnames(1) delimiter(";") encoding(utf-8) bindquotes(strict)
	
	* Few observations have incorrect formatting..
	drop if currency != "USD"
	keep artist title year gallery price materials dimensions url image_url collectiondate currency
	
	* Check if the csv file already has id-s assigned to the artworks. If not assign them.
	* Inconsistencies might arise for fairs that were saved on multiple occasions.
	* (The same artwork might have a different ID on a different date)
	capture confirm variable id

	* If the variable id does not exist, generate the id numbers.
	if !!_rc {
	    qui: gen long id = _n, before(artist)
	}
	
	* Create fair variable to store the name of the fair.
	local fairName = subinstr("`file'", ".csv", "", .)
	qui: gen str fair = "`fairName'", before(id)
	qui: gen str filename = "`file'", before(id)
	qui: gen byte isFair = 1
	* Create a .dta file with the same name as the .csv file
	cd `exportDir'
	save "`fairName'.dta", replace
}


*					1dB) Artissima
* The csv filenames do not include the year.
* Change the fairName variable to include 2020!
clear
local exportDir = "$priceDataDir\nonArtsy"
local importDir = "$rawDataDir\nonArtsy\Artissima"
local files: dir "`importDir'" files "*.csv"
* Convert .csv files to .dta
foreach file of local files {
    * Clear memory
    clear
	cd `importDir'
	import delimited using "`file'", varnames(1) delimiter(";") encoding(utf-8) bindquotes(strict)
	* Check if the csv file already has id-s assigned to the artworks. If not assign them.
	* Inconsistencies might arise for fairs that were saved on multiple occasions.
	capture confirm variable id
	* If the variable id does not exist, generate the id numbers.
	if !!_rc {
	    qui: gen long id = _n, before(artist)
	}
	* Create fair variable to store the name of the fair.
	local fairName = subinstr("`file'", "-data.csv", "", .)
	qui: gen str fair = "`fairName'-2020", before(id)
	qui: gen str filename = "`file'", before(id)
	qui: gen byte isFair = 1
	
	* drop if strpos(url, "artissima") == 0
	
	* Create a .dta file with the same name as the .csv file
	cd `exportDir'
	save "`fairName'-2020.dta", replace
}


*						1dC) FIAC
clear
local exportDir = "$priceDataDir\nonArtsy"
local importDir = "$rawDataDir\nonArtsy\FIAC"
local files: dir "`importDir'" files "*.csv"
* Convert .csv files to .dta
foreach file of local files {
    * Clear memory
    clear
	cd `importDir'
	import delimited using "`file'", varnames(1) delimiter(";") encoding(utf-8) bindquotes(strict)
	* Some entries are were inconsistently extracted from the website.
	* Drop all entries without the name of the artist
	drop if artist == ""
	* Few observations have incorrect formatting..
	drop if currency != "USD"
	keep artist title year gallery price materials dimensions url image_url collectiondate currency
	* Prices are recorded both in USD and EUR. Keep only one and add a currency variable.
	* This has been solved during preprocessing in python.
	
	/*
	drop priceeur
	rename priceusd price
	gen currency = "USD", after(price)
	*/
	
	* Check if the csv file already has id-s assigned to the artworks. If not assign them.
	* Inconsistencies might arise for fairs that were saved on multiple occasions.
	capture confirm variable id
	* If the variable id does not exist, generate the id numbers.
	if !!_rc {
	    qui: gen long id = _n, before(artist)
	}
	* Create fair variable to store the name of the fair.
	local fairName = subinstr("`file'", ".csv", "", .)
	qui: gen str fair = "`fairName'", before(id)
	qui: gen str filename = "`file'", before(id)
	qui: gen byte isFair = 1
	* rename medium materials  // solved during preprocessing
	* Create a .dta file with the same name as the .csv file
	cd `exportDir'
	save "`fairName'.dta", replace
}


*					1dD) Frieze
/*
* The data is not cleaned yet.

clear
local exportDir "D:\oxford\02-11-2021\30-09-2021\PriceData\nonArtsy"
local importDir "C:\Users\Milan\OneDrive\Desktop\Said\Art\PriceDataExtraction\Frieze\data"
local files: dir "`importDir'" files "*.csv"
* Convert .csv files to .dta
foreach file of local files {
    * Clear memory
    clear
	cd "`importDir'"
	import delimited using "`file'", varnames(1) delimiter(";") encoding(utf-8) bindquotes(nobind)
	* Check if the csv file already has id-s assigned to the artworks. If not assign them.
	* Inconsistencies might arise for fairs that were saved on multiple occasions.
	capture confirm variable id
	* If the variable id does not exist, generate the id numbers.
	if !!_rc {
	    qui: gen long id = _n, before(artist)
	}
	* Create fair variable to store the name of the fair.
	local fairName = subinstr("`file'", ".csv", "", .)
	qui: gen str fair = "`fairName'-2020", before(id)
	* Some records in the csv are imported incorrectly due to stata not being able
	* to handle custom quotechars. 
	* Untill a solution is found drop where the url is invalid
	drop if strpos(url, "frieze") == 0
	* Create a .dta file with the same name as the .csv file
	cd "`exportDir'"
	save "`fairName'-2020.dta", replace
}
*/



*					1dE) Vienna Contemporary
* The filenames do not contain the fair name. Add viennaContemporary to the
* fairName variable.
clear
local exportDir = "$priceDataDir\nonArtsy"
local importDir = "$rawDataDir\nonArtsy\ViennaContemporary"
local files: dir "`importDir'" files "*.csv"
* Convert .csv files to .dta
foreach file of local files {
    * Clear memory
    clear
	cd `importDir'
	import delimited using "`file'", varnames(1) delimiter(";") encoding(utf-8) bindquotes(strict)
	drop if artist == ""
	* Check if the csv file already has id-s assigned to the artworks. If not assign them.
	* Inconsistencies might arise for fairs that were saved on multiple occasions.
	capture confirm variable id
	* If the variable id does not exist, generate the id numbers.
	if !!_rc {
	    qui: gen long id = _n, before(artist)
	}
	* Create fair variable to store the name of the fair.
	local fairName = subinstr("`file'", "-data.csv", "", .)
	qui: gen str fair = "`fairName'-2020", before(id)
	qui: gen str filename = "`file'", before(id)
	qui: gen byte isFair = 1
	/*
						FIXED: REFORMATED CSV FILES
						IGNORE COMMENTED LINES
	* Some records in the csv are imported incorrectly due to stata not being able
	* to handle custom quotechars.
	* Untill a solution is found drop where the url is invalid
	drop if strpos(url, "viennacontemporary") == 0
	replace sold = subinstr(sold, ",", "", .)
	capture drop v12
	*/
	* Create a .dta file with the same name as the .csv file
	cd `exportDir'
	save "`fairName'-2020.dta", replace
}


*					1dF) Sotheby's
clear
local exportDir = "$priceDataDir\nonArtsy"
local importDir = "$rawDataDir\nonArtsy\Sothebys"
local files: dir "`importDir'" files "*.csv"
* Convert .csv files to .dta
foreach file of local files {
    * Clear memory
    clear
	cd `importDir'
	import delimited using "`file'", varnames(1) delimiter(";") encoding(utf-8) bindquotes(strict)
	* Check if the csv file already has id-s assigned to the artworks. If not assign them.
	* Inconsistencies might arise for fairs that were saved on multiple occasions.
	capture confirm variable id
	* If the variable id does not exist, generate the id numbers.
	if !!_rc {
	    qui: gen long id = _n, before(artist)
	}
	* Create fair variable to store the name of the fair.
	local holder = subinstr("`file'", "export_", "sothebys-", .)
	local fairName = subinstr("`holder'", ".csv", "", .)
	qui: gen str fair = "`fairName'", before(id)
	qui: gen str filename = "`file'", before(id)
	qui: gen byte isFair = 0
	* rename material materials // solved during preprocessing
	
	* drop if strpos(url, "sothebys") == 0
	
	* Create a .dta file with the same name as the .csv file
	cd `exportDir'
	save "`fairName'.dta", replace
}


*					1dG) Gallery Platform LA
clear
local exportDir = "$priceDataDir\nonArtsy"
local importDir = "$rawDataDir\nonArtsy\GPLA"
local files: dir "`importDir'" files "*.csv"
* Convert .csv files to .dta
foreach file of local files {
    * Clear memory
    clear
	cd `importDir'
	import delimited using "`file'", varnames(1) delimiter(";") encoding(utf-8) bindquotes(strict)
	* Check if the csv file already has id-s assigned to the artworks. If not assign them.
	* Inconsistencies might arise for fairs that were saved on multiple occasions.
	capture confirm variable id
	* If the variable id does not exist, generate the id numbers.
	if !!_rc {
	    qui: gen long id = _n, before(artist)
	}
	* Create fair variable to store the name of the fair.
	local holder = subinstr("`file'", "price", "galleryPlatformLA", .)
	local fairName = subinstr("`holder'", ".csv", "", .)
	replace price = subinstr(price, "$", "", .)
	gen currency = "USD", after(price)
	qui: gen str fair = "`fairName'", before(id)
	qui: gen str filename = "`file'", before(id)
	qui: gen byte isFair = 0
	* rename image image_url // solved during preprocessing
	* Create a .dta file with the same name as the .csv file
	cd `exportDir'
	save "`fairName'.dta", replace
}


*					1dH) Frieze
clear
local exportDir = "$priceDataDir\nonArtsy"
local importDir = "$rawDataDir\nonArtsy\Frieze"
local files: dir "`importDir'" files "*.csv"
* Convert .csv files to .dta
foreach file of local files {
    * Clear memory
    clear
	cd `importDir'
	import delimited using "`file'", varnames(1) delimiter(";") encoding(utf-8) bindquotes(strict)
	* Some entries are were inconsistently extracted from the website.
	* Drop all entries without the name of the artist
	drop if artist == ""
	* Prices are recorded both in USD and EUR. Keep only one and add a currency variable.
	* This has been solved during preprocessing in python.
	/*
	drop priceeur
	rename priceusd price
	gen currency = "USD", after(price
	*/
	* Check if the csv file already has id-s assigned to the artworks. If not assign them.
	* Inconsistencies might arise for fairs that were saved on multiple occasions.
	capture confirm variable id
	* If the variable id does not exist, generate the id numbers.
	if !!_rc {
	    qui: gen long id = _n, before(artist)
	}
	* Create fair variable to store the name of the fair.
	local fairName = subinstr("`file'", ".csv", "", .)
	qui: gen str fair = "`fairName'", before(id)
	qui: gen str filename = "`file'", before(id)
	qui: gen byte isFair = 1
	* rename medium materials  // solved during preprocessing
	* Create a .dta file with the same name as the .csv file
	cd `exportDir'
	save "`fairName'.dta", replace
}


*					1dI) Merge Non Artsy Files

* Create a master file from the individual .dta files.
clear
local exportDir = "$priceDataDir\nonArtsy"
* Generate the different variables and their default empty values.
* Every string variable is stored as strL to avoid issues when appending.
* When the merge is complete use compress to save disk space.
gen strL fair = ""
gen byte isFair = .
gen strL filename = ""
gen int id = .
gen strL artist = ""
gen strL title = ""
gen strL year = ""
gen strL gallery = ""
gen strL price = ""
gen str3 currency = ""
gen strL category = ""
gen strL materials = ""
gen strL dimensions = ""
gen strL url = ""
gen strL image_url = ""


cd $priceDataDir
save "nonArtsy.dta", replace
local stataFiles: dir "`exportDir'" files "*.dta"

* Create variables in case they do not exist to avoid errors during append.
cd `exportDir'
foreach file of local stataFiles {
	clear
	use "`file'"
	capture confirm variable sold
	* If the variable sold does not exist, generate empty variable
	if !!_rc {
	    qui: gen str sold = ""
	}
	
	capture confirm variable category
	* If the variable category does not exist, generate empty variable
	if !!_rc {
	    qui: gen str category = ""
	}
	
	capture confirm variable materials
	* If the variable materials does not exist, generate empty variable
	if !!_rc {
	    qui: gen str materials = ""
	}
	
	capture confirm variable dimensions
	* If the variable dimensions does not exist, generate empty variable
	if !!_rc {
	    qui: gen str dimensions = ""
	}
	
	capture confirm variable url
	* If the variable url does not exist, generate empty variable
	if !!_rc {
	    qui: gen str url = ""
	}
	
	save "`file'", replace
}

cd $priceDataDir
use "nonArtsy.dta"

cd `exportDir'
foreach file of local stataFiles {
	append using "`file'", force // keep(fair isFair id artist title year gallery price currency category materials dimensions url image_url sold)
	
}

* Recast and compress string variables to save space
recast str2045 artist title year gallery price currency category materials dimensions url image_url filename
compress

cd $priceDataDir
save "nonArtsy.dta", replace


*					1e) Master Price File


* Merge collections, fairs, nonArtsy and pastFairs data
clear

* Generate the different variables and their default empty values.
* Every string variable is stored as strL to avoid issues when appending.
* When the merge is complete use compress to save disk space.
gen strL fair = ""
gen byte isFair = .
gen strL filename = ""
gen int id = .
gen strL artist = ""
gen strL title = ""
gen strL year = ""
gen strL gallery = ""
gen strL price = ""
gen str3 currency = ""
gen strL category = ""
gen strL materials = ""
gen strL dimensions = ""
gen strL url = ""
gen strL image_url = ""
gen strL collection_url = ""
gen strL sold = ""

cd $exportDir
save "priceMaster.dta", replace

cd $priceDataDir
local stataFiles: dir "$priceDataDir" files "*.dta"
cd $priceDataDir

foreach file of local stataFiles {
	cd $priceDataDir
	append using "`file'", force
}

* Drop duplicates and generate other variables.
bys url fair: gen _dupe = cond(_N==1, 0, 1) if url != ""
replace _dupe = 0 if _dupe == .
// drop if _dupe > 0 // Drops all duplicates for a single fair
bys fair: egen numberOfArtworks = max(id)

* Compress variables to save space
recast str2045 fair artist title year gallery price currency category materials dimensions url image_url collection_url sold filename details description
compress

* Drop corrupt entries
* These issues arise for past artsy fairs due to errors in the Artsy API.
* Fix in progress: re-downloading data with improved algorithm
* Number of observations dropped as of 14/04/2021:
drop if title == "Available for Sale"
drop if artist == ""
drop if title == ""
drop if gallery == "Have a question? Visit our help center."
drop if gallery == "Conditions of Sale"
drop if title == "Artsy"

cd $exportDir
save "priceMaster.dta", replace




*******************************************************************************


*						2) Fair Data

clear

* Set up folders and files
local rawFairData "$rawDataDir\fairData\fairID_multiple.xlsx"
local stataFairDataLocation "$exportDir\FairData"
capture mkdir `stataFairDataLocation'

* Import FairID and drop unnecessary variables
import excel using `rawFairData', firstrow case(lower)
drop note more category priceavailability numberofartworks imagesdownloaded
rename fairname fair_name
rename year fair_year
rename artsyurl fair_artsy_url

* Save to a dta file to prepare for merge
cd `stataFairDataLocation'
save "fairID.dta", replace

* Use price data file to preform a m:1 merge
clear
cd $exportDir
use "priceMaster.dta"

* Cannot merge along srtL variables: recast to str#
capture recast str2045 filename
capture compress filename

* Merge fairID into price data
cd `stataFairDataLocation'
merge m:1 filename using "FairID.dta", gen(fairMerge)

drop if fairMerge == 2

* Save the results
cd $exportDir
save "priceMaster.dta", replace


clear
local fairLocationData "$rawDataDir\FairData\fair_locations.xlsx"
import excel using `fairLocationData', firstrow case(lower)
capture tostring fair_id, replace
cd `stataFairDataLocation'
save "fair_location.dta", replace
clear
cd $exportDir
use "priceMaster.dta"
cd `stataFairDataLocation'
merge m:1 fair_id using "fair_location.dta", keepusing(fair_location) gen(fairLocMerge)
drop if fairLocMerge == 2
drop fairLocMerge

cd $exportDir
save "priceMaster.dta", replace
*******************************************************************************


*						3) Gender Data
clear

local stataGenderLocation "$rawDataDir\artistData"

* Use price data file to preform a m:1 merge
cd $exportDir
use "priceMaster.dta"

cd `stataGenderLocation'
merge m:1 artist using "masterArtist.dta", gen(genderMerge)
drop if genderMerge == 2

cd $exportDir
save "priceMaster.dta", replace



*******************************************************************************


*		4) NN GENDER CLASSIFICATION & Reformat variables and correct issues
clear
cd $exportDir
use priceMaster
* Add gender match and NN prediction
* The following process can only be done in Python
local genderClassificationDir = "$exportDir\\GenderClassification"
local classifiedFileLocation = "`genderClassificationDir'\priceMaster-done.csv"

confirm new file `classifiedFileLocation'
if _rc == 0 {
    capture mkdir `genderClassificationDir'
	cd `genderClassificationDir'
	export delimited priceMaster.csv, replace

	clear

	*** PYTHON BLOCK HERE
	* Environment has to have numpy, pandas, keras, tensorflow
	* set python_exec "C:\Users\Milan\Anaconda\anaconda3\envs\oxford\python.exe"
	cd $scriptsDir
	shell conda activate oxford & python name_gender_classification.py --folder `genderClassificationDir' --file priceMaster.csv
	* python name_gender_classification.py --folder `genderClassificationDir' --file priceMaster.csv
	* After the code has ran, import the updated version
}



cd `genderClassificationDir'
import delimited using priceMaster-done.csv, encoding(utf8) delimiter(";") bindquote(strict) varnames(1) case(preserve)

cd $exportDir
save priceMaster, replace

* Some entries are corrupted due to the csv import
gen corrupt = 1 if isFair == ""
replace corrupt = 1 if isFair != "0" & isFair != "1"
tab corrupt
drop if corrupt == 1
drop corrupt
destring isFair, replace

/*
* This block is required to delete already generated variables in case the gender match was done on a later dataset.
capture drop cent* bc* startYear endYear length width depth measurement fair_endDate fair_startDate lowPrice* highPrice* *_in *_cm collectiondate datecur exchange_rate aF_birth_date aF_death_date
capture rename aF_birth_date_unformatted aF_birth_date
capture rename aF_death_date_unformatted aF_death_date
capture rename collectiondate_unformatted collectiondate
*/

* Generate gender variable
replace gender = "1" if gender == "Female"
replace gender = "0" if gender == "Male"
destring gender, replace
la de genderlabel 0 "Male" 1 "Female"
la val gender genderlabel

gen genderSource = 1 if gender != .
replace gender = 1 if exactMatchGender == "Female" & gender == .
replace gender = 0 if exactMatchGender == "Male" & gender == .
replace genderSource = 2 if genderSource == . & gender != .
replace gender = 1 if NNgender == "Female" & gender == .
replace gender = 0 if NNgender == "Male" & gender == .
replace genderSource = 3 if genderSource == . & gender != .

la de genderSourceLabel 1 "Artist Database" 2 "First Name Match" 3 "Neural Network Prediction"
la val genderSource genderSourceLabel

* Only keep NN prediction where uncertainity is low.
gen NNaccuracy = abs(NNvalue - 0.5)
* NNaccuracy cutoff specified at .4
replace gender = . if genderSource == 3 & NNaccuracy < .3
replace genderSource = . if gender == .


* Convert year to startYear, endYear, type: int
* For vienna contemporary the date variable is corrupt..
* Potentially the best solution is to drop all year variables for these fairs.
* For some artworks the Year is specified only by the century.
* This will cause issues when destringing the variable.
* Mark these artworks and correct later!
gen century_dummy = 1 if strpos(year, "century")
replace century_dummy = 1 if strpos(year, "Century")
replace century_dummy = 1 if strpos(year, "cent")
replace century_dummy = 1 if strpos(year, "cent.")
replace century_dummy = 1 if strpos(year, "CENTURY")
replace century_dummy = 1 if strpos(year, "c.")
* Generate variable and mark artworks BC
gen bc_dummy = 1 if strpos(year, "BC")
replace bc_dummy = 1 if strpos(year, "bc")
replace bc_dummy = 1 if strpos(year, "B.C")
* Keep track of late and early periods of a century.
gen centLate = 1 if century_dummy == 1 & strpos(year, "Late")
replace centLate = 1 if century_dummy == 1 & strpos(year, "late")
gen centEarly = 1 if century_dummy == 1 & strpos(year, "Early")
replace centEarly = 1 if century_dummy == 1 & strpos(year, "early")
* Split year variable into startYear and endYear
split year, gen(yeargen) p("-" "|" "\" "/" "&" "—") l(2)
* From the split extract numbers with regex
gen startYear = real(regexs(0)) if regexm(yeargen1, "[0-9]+")
gen endYear = real(regexs(0)) if regexm(yeargen2, "[0-9]+")
* Correct date for artworks where date is recorded in centuries.
replace startYear = (startYear - 1) * 100 if century_dummy == 1
replace endYear = startYear + 100 if century_dummy == 1
* Get rid of temporary variables
drop yeargen*
* Make sure there is no endYear variable without startYear and that the two are not identical
replace startYear = endYear if startYear == . & endYear != .
replace endYear = . if startYear == endYear

order startYear endYear, after(year)

* Dimensions for artworks collected from artissima are corrupted
replace dimensions = "" if strpos(filename, "artissima")
* Convert dimensions to length, width, and height type: float
* Generate variable for the unit of lenght.
la de measurement 0 "cm" 1 "in"
gen measurement = 0 if strpos(dimensions, "cm")
replace measurement = 1 if strpos(dimensions, "in")
la val measurement measurement
* Split dimension variables
split dimensions, gen(dimgen) p("x" "X" "×" "x") l(3)

replace dimgen1 = subinstr(dimgen1, " in ", "",.)
replace dimgen1 = subinstr(dimgen1, " cm ", "",.)
replace dimgen1 = subinstr(dimgen1, " in", "",.)
replace dimgen1 = subinstr(dimgen1, " cm", "",.)
replace dimgen1 = subinstr(dimgen1, "in", "",.)
replace dimgen1 = subinstr(dimgen1, "cm", "",.)

replace dimgen2 = subinstr(dimgen2, " in ", "",.)
replace dimgen2 = subinstr(dimgen2, " cm ", "",.)
replace dimgen2 = subinstr(dimgen2, " in", "",.)
replace dimgen2 = subinstr(dimgen2, " cm", "",.)
replace dimgen2 = subinstr(dimgen2, "in", "",.)
replace dimgen2 = subinstr(dimgen2, "cm", "",.)

replace dimgen3 = subinstr(dimgen3, " in ", "",.)
replace dimgen3 = subinstr(dimgen3, " cm ", "",.)
replace dimgen3 = subinstr(dimgen3, " in", "",.)
replace dimgen3 = subinstr(dimgen3, " cm", "",.)
replace dimgen3 = subinstr(dimgen3, "in", "",.)
replace dimgen3 = subinstr(dimgen3, "cm", "",.)

* The following code is based on the answer of Stack Overflow user @Romalpa Akzo
* https://stackoverflow.com/questions/53429401/destring-variables-with-fractions
* Allows stata to convert fractions to floating point numbers

* Length
split dimgen1, generate(xgen) destring force p(" ") l(2)
egen ygen = ends(dimgen1) if strmatch(dimgen1,"*/*"), last
split ygen, destring force p("/")
gen length = cond(xgen1<0, xgen1-ygen1/ygen2, cond(xgen1!=.,xgen1+ygen1/ygen2, ygen1/ygen2)) if ygen1!=.
replace length = xgen1 if ygen1 == .
drop xgen* ygen*
* Width
split dimgen2, generate(xgen) destring force p(" ") l(2)
egen ygen = ends(dimgen2) if strmatch(dimgen2,"*/*"), last
split ygen, destring force p("/")
gen width = cond(xgen1<0, xgen1-ygen1/ygen2, cond(xgen1!=.,xgen1+ygen1/ygen2, ygen1/ygen2)) if ygen1!=.
replace width = xgen1 if ygen1 == .
drop xgen* ygen*
* Depth
split dimgen3, generate(xgen) destring force p(" ") l(2)
egen ygen = ends(dimgen3) if strmatch(dimgen3,"*/*"), last
split ygen, destring force p("/")
gen depth = cond(xgen1<0, xgen1-ygen1/ygen2, cond(xgen1!=.,xgen1+ygen1/ygen2, ygen1/ygen2)) if ygen1!=.
replace depth = xgen1 if ygen1 == .
drop xgen* ygen*
* Drop all temporary variables
drop dimgen*
* For Frieze NY the measurements are specified in both in and cm. Use inches.
replace measurement = 1 if strpos(fair, "frieze-ny-")


* Format price and currency
* Generate lowPrice and highPrice and convert to intiger
replace currency = "USD" if currency == "" & strpos(price, "$")
replace currency = "GBP" if currency == "" & strpos(price, "£")
replace currency = "EUR" if currency == "" & strpos(price, "€")

* < Under
gen pr_under = 1 if strpos(price, "<") | strpos(price, "Under") | strpos(price, "under")
* > Above
gen pr_above = 1 if strpos(price, ">") | strpos(price, "Above") | strpos(price, "above")
* k thousand, m million
gen pr_thousand = 1 if strpos(price, "k")
gen pr_million = 1 if strpos(price, "m")
* Split lowPrice and highPrice
split price, gen(pricegen) p("-" "—") l(2) destring force i("," "$" "€" "£" "k" "<" "Under" "m" "")

replace pricegen1 = pricegen1 * 1000 if pr_thousand == 1 & pr_million == .
replace pricegen2 = pricegen2 * 1000 if pr_thousand == 1 & pr_million == .
replace pricegen1 = pricegen1 * 1000000 if pr_million == 1
replace pricegen2 = pricegen2 * 1000000 if pr_million == 1

replace pricegen2 = pricegen1 if pr_under == 1
replace pricegen1 = . if pr_under == 1

rename pricegen1 lowPrice
rename pricegen2 highPrice
replace currency = "" if lowPrice == . & highPrice == .

drop pr_*

* Format date variables
gen collectiondate1 = date(collectiondate, "YMD")
format collectiondate1 %td
rename collectiondate collectiondate_unformatted
rename collectiondate1 collectiondate

gen af_birth_date1 = date(aF_birth_date, "YMD")
rename aF_birth_date aF_birth_date_unformatted
rename af_birth_date1 aF_birth_date

gen af_death_date1 = date(aF_death_date, "YMD")
rename aF_death_date aF_death_date_unformatted
rename af_death_date1 aF_death_date

capture destring aF_birth_year aF_death_year, replace
format aF_birth_date %td
format aF_death_date %td
format aF_death_year %ty
format aF_birth_year %ty
format bl_yobirth %ty
format bl_yodeath %ty

* Format fair date variable
rename date fair_date
split fair_date, p("-" "–") generate(dategen)
* Start date
gen dategen1_month = "1" if strpos(dategen1, "Jan")
replace dategen1_month = "1" if strpos(dategen1, "January")
replace dategen1_month = "2" if strpos(dategen1, "Feb")
replace dategen1_month = "2" if strpos(dategen1, "February")
replace dategen1_month = "3" if strpos(dategen1, "Mar")
replace dategen1_month = "3" if strpos(dategen1, "March")
replace dategen1_month = "4" if strpos(dategen1, "Apr")
replace dategen1_month = "4" if strpos(dategen1, "April")
replace dategen1_month = "5" if strpos(dategen1, "May")
replace dategen1_month = "6" if strpos(dategen1, "Jun")
replace dategen1_month = "6" if strpos(dategen1, "June")
replace dategen1_month = "7" if strpos(dategen1, "Jul")
replace dategen1_month = "7" if strpos(dategen1, "July")
replace dategen1_month = "8" if strpos(dategen1, "Aug")
replace dategen1_month = "8" if strpos(dategen1, "August")
replace dategen1_month = "9" if strpos(dategen1, "Sep")
replace dategen1_month = "9" if strpos(dategen1, "Sept")
replace dategen1_month = "9" if strpos(dategen1, "September")
replace dategen1_month = "10" if strpos(dategen1, "Oct")
replace dategen1_month = "10" if strpos(dategen1, "October")
replace dategen1_month = "11" if strpos(dategen1, "Nov")
replace dategen1_month = "11" if strpos(dategen1, "November")
replace dategen1_month = "12" if strpos(dategen1, "Dec")
replace dategen1_month = "12" if strpos(dategen1, "December")
gen dategen1_day = regexs(0) if regexm(dategen1, "[0-9]+")

* End date
gen dategen2_month = "1" if strpos(dategen2, "Jan")
replace dategen2_month = "1" if strpos(dategen2, "January")
replace dategen2_month = "2" if strpos(dategen2, "Feb")
replace dategen2_month = "2" if strpos(dategen2, "February")
replace dategen2_month = "3" if strpos(dategen2, "Mar")
replace dategen2_month = "3" if strpos(dategen2, "March")
replace dategen2_month = "4" if strpos(dategen2, "Apr")
replace dategen2_month = "4" if strpos(dategen2, "April")
replace dategen2_month = "5" if strpos(dategen2, "May")
replace dategen2_month = "6" if strpos(dategen2, "Jun")
replace dategen2_month = "6" if strpos(dategen2, "June")
replace dategen2_month = "7" if strpos(dategen2, "Jul")
replace dategen2_month = "7" if strpos(dategen2, "July")
replace dategen2_month = "8" if strpos(dategen2, "Aug")
replace dategen2_month = "8" if strpos(dategen2, "August")
replace dategen2_month = "9" if strpos(dategen2, "Sep")
replace dategen2_month = "9" if strpos(dategen2, "Sept")
replace dategen2_month = "9" if strpos(dategen2, "September")
replace dategen2_month = "10" if strpos(dategen2, "Oct")
replace dategen2_month = "10" if strpos(dategen2, "October")
replace dategen2_month = "11" if strpos(dategen2, "Nov")
replace dategen2_month = "11" if strpos(dategen2, "November")
replace dategen2_month = "12" if strpos(dategen2, "Dec")
replace dategen2_month = "12" if strpos(dategen2, "December")
gen dategen2_day = regexs(0) if regexm(dategen2, "[0-9]+")

* Merge and convert variables into date format
replace dategen2_month = dategen1_month if dategen2_month == "" & dategen2_day != ""
gen dategen_fair_year = string(fair_year)
gen dategen_startDate = dategen_fair_year + "/" + dategen1_month + "/" + dategen1_day if dategen1_day != ""
replace dategen_startDate =  dategen_fair_year + "/" + dategen1_month + "/" + "1" if dategen1_day == "" & dategen1_month != ""
gen dategen_endDate = dategen_fair_year + "/" + dategen2_month + "/" + dategen2_day if dategen2_day != ""
replace dategen_endDate = dategen_fair_year + "/" + dategen1_month + "/" + "31" if dategen1_day == "" & dategen1_month != ""

gen fair_startDate = date(dategen_startDate, "YMD")
format fair_startDate %td
gen fair_endDate = date(dategen_endDate, "YMD")
format fair_endDate %td
order fair_startDate fair_endDate, after(fair_date)
drop dategen*

order bc_dummy century_dummy centEarly centLate, after(endYear)
order lowPrice highPrice, after(price)
order length width depth measurement, after(dimensions)
order collectiondate, after(collectiondate_unformatted)
order aF_birth_date, after(aF_birth_date_unformatted )
order aF_death_date, after(aF_death_date_unformatted)

* Delete corrupt observations
replace startYear = . if bc_dummy != 1 & startYear > 2021
replace endYear = . if startYear == .
replace endYear = 2021 if endYear == 2100
replace endYear = . if bc_dummy != 1 & endYear > 2021
replace endYear = . if bc_dummy != 1 & endYear < startYear

* Format variables to conserve as much space as possible.
recast byte bc_dummy century_dummy centEarly centLate measurement
recast long numberOfArtworks

* Convert dimension variables to both inches and cenitmetres
* The constant used to convert in to cm = 2.54
* Logically converting cm to in = 1 / 2.54
gen length_in = length if measurement == 1, after(measurement)
gen width_in = width if measurement == 1, after(length_in)
gen depth_in = depth if measurement == 1, after(width_in)
replace length_in = length * 1/2.54 if measurement == 0
replace width_in = width * 1/2.54 if measurement == 0
replace depth_in = depth * 1/2.54 if measurement == 0

gen length_cm = length if measurement == 0, after(depth_in)
gen width_cm = width if measurement == 0, after(length_cm)
gen depth_cm = depth if measurement == 0, after(width_cm)
replace length_cm = length * 2.54 if measurement == 1
replace width_cm = width * 2.54 if measurement == 1
replace depth_cm = depth * 2.54 if measurement == 1

* Generate variable to merge FX data
* This variable is a combination of the date the data was collected and the currency
* specified by the seller.
gen datecur = string(collectiondate) + lower(currency) if currency != "", after(currency)

* Save changes
cd $exportDir
save "priceMaster.dta", replace


* Convert all currencies to USD at the appropriate exchange rate.
* FX data from https://www.investing.com/
local currencyDir "$rawDataDir\CurrencyData"

local exportDir "$exportDir\CurrencyData\FX"
local mergeCurDir "$exportDir\CurrencyData"

mkdir `mergeCurDir'
mkdir `exportDir'

local projectFolder "$masterDir"
local curfiles: dir "`currencyDir'" files "*.csv"
* Install package to fill in gaps in FX data
capture ssc install carryforward

foreach file of local curfiles {
	clear
	cd `currencyDir'
	local currency = subinstr("`file'", ".csv", "", .)
	import delimited using `file', varnames(1) encoding(utf8)
	
	capture drop open high low change
	
	gen datef = date(date, "DMY"), before(price)
	
	* Fill the weekend gaps using Friday's data
	tsset datef
	tsfill
	carryforward price, gen(pricegen)
	rename price price_gaps
	rename pricegen price
	
	gen datecur = string(datef) + "`currency'"
	
	cd `exportDir'
	save "`currency'.dta", replace
}

clear
cd `exportDir'
local stataFiles: dir "`exportDir'" files "*.dta"
foreach file of local stataFiles {
	append using "`file'", force
}
rename price exchange_rate
cd `mergeCurDir'
save "masterCurrency.dta", replace
* Merge FX data

local exportDir "$exportDir\CurrencyData\FX"
local mergeCurDir "$exportDir\CurrencyData"


cd $exportDir
use "priceMaster.dta"
cd `mergeCurDir'
merge m:1 datecur using masterCurrency.dta, keepusing(exchange_rate) gen(currencyMerge)
drop if currencyMerge == 2
drop currencyMerge

replace exchange_rate = 1 if currency == "USD"
order exchange_rate, after(datecur)

* Generate USD price variables
gen lowPriceUSD = lowPrice * exchange_rate, after(price)
gen highPriceUSD = highPrice * exchange_rate, after(lowPriceUSD)

* Create numerical variable from category
* Create uniform categories
replace category = "" if category == "(blank)"
replace category = "" if category == "--"
replace category = "Other" if category == "Other Materials"
replace category = "Design/Decorative Art" if category == "Design Decorative Art"
replace category = "Print" if category == "Prints & Multiples"
replace category = "Video/Film/Animation" if category == "Video/Film"
replace category = "Drawing, Collage or other Work on Paper" if category == "Work on Paper"

rename category category_unformatted
encode category_unformatted, gen(category) label(cats)
order category, before(category_unformatted)
drop category_unformatted

drop if collectiondate == .

order gender, after(artist)
order genderSource, after(gender)


* Eliminate extreme values in price
replace price = "Corrupt Data" if lowPriceUSD < 20
replace lowPriceUSD = . if price == "Corrupt Data"
replace highPriceUSD = . if price == "Corrupt Data"
replace lowPrice = . if price == "Corrupt Data"
replace highPrice = . if price == "Corrupt Data"
replace currency = "" if price == "Corrupt Data"

replace lowPrice = 500000 if price == "$500k-1m"
replace highPrice = 1000000 if price == "$500k-1m"
replace lowPriceUSD = lowPrice * exchange_rate if price == "$500k-1m"
replace highPriceUSD = highPrice * exchange_rate if price == "$500k-1m"

* Eliminate extreme values in dimensions
replace dimensions = "Corrupt Data" if dimensions == "65cm85cmcm"
replace dimensions = "Corrupt Data" if dimensions == "80cm60cmcm"
replace length_in = . if length_in == 0
replace width_in = . if width_in == 0
replace depth_in = . if depth_in == 0
replace length_cm = . if length_cm == 0
replace width_cm = . if width_cm == 0
replace depth_cm = . if depth_cm == 0


************
* The following code was written by Jiaqi Zheng
*generate a variable of year when an artwork was completed, and a variable of length of composing period
gen yearCompleted= endYear
replace yearCompleted= startYear if endYear>=.
*some works have only an approximate period. In that case, use the middle of that period as the yearCompleted
replace yearCompleted= endYear-50 if century_dummy==1 & centEarly>=. & centLate>=.
replace yearCompleted= endYear-25 if century_dummy==1 & centEarly>=. & centLate==1
replace yearCompleted= endYear-75 if century_dummy==1 & centEarly==1 & centLate>=.
*there are some issues with BC dates (endYear and startYear are reversed). Replace them by 0.
replace yearCompleted= 0 if bc_dummy==1
gen years= endYear-startYear if bc_dummy>1 & century_dummy>1
*Extremely large values of years is often due to mistake. Replace those above 50 years. Milán: would you mind checking large gap between endYear and startYear? It worth checking because it sometimes relates to wrong startYear or endYear.
replace years=. if years>=50
replace years=0 if startYear<. & endYear>=.
* Clear sold status
rename sold sold_unformatted
gen sold = ., after(sold_unformatted)
replace sold = 1 if strpos(sold_unformatted, "sold") | strpos(sold_unformatted, "Sold") | strpos(sold_unformatted, "True") | strpos(sold_unformatted, "true") | strpos(sold_unformatted, "Reserved") | strpos(sold_unformatted, "reserved")
replace sold = 0 if strpos(sold_unformatted, "FALSE") | strpos(sold_unformatted, "False") | strpos(sold_unformatted, "For sale") | strpos(sold_unformatted, "false")
* Generate Unique ID
gen image_download_id = image_id + "-" + id
drop id
capture destring artwork_id, replace
destring fair_id, replace
*generate times of collections for each artwork
bysort fair_id fair_year artwork_id (collectiondate): egen collectiondTimes=count(artwork_id)
* Generate avarage price
rename price price_unformatted
gen price = (lowPriceUSD+highPriceUSD)/2 if lowPriceUSD<. & highPriceUSD<., after(price_unformatted)
replace price = lowPriceUSD if lowPriceUSD<. & highPriceUSD>=.
*some "id"s are identical for different artworks. I will generate a new one, one-to-one corresponding to each url.
egen artwork_id = group(url)
*generate first and last appear dates
bysort fair_id fair_year artwork_id (collectiondate): gen collectiondate1=collectiondate[1]
bysort fair_id fair_year artwork_id (collectiondate): gen collectiondate2=collectiondate[_N]
bysort fair_id fair_year (collectiondate): gen collectiondate1fair=collectiondate[1]
bysort fair_id fair_year (collectiondate): gen collectiondate2fair=collectiondate[_N]
sort fair_id fair_year artwork_id collectiondate
format collectiondate1 collectiondate2 collectiondate1fair collectiondate2fair %td
*generate the date when a piece appeared as sold for the first time
gen soldDate= collectiondate if sold==1
bysort fair_id fair_year artwork_id (collectiondate): egen soldDate1= min(soldDate)
drop soldDate
rename soldDate1 soldDate
*the variable "sold" is missing for many observations. Generate an alternative variable showing when an artwork disappears
gen exitDate= collectiondate2 if collectiondate2<collectiondate2fair
format soldDate exitDate %td
sort fair_id fair_year artwork_id collectiondate
egen gallery_id = group(gallery)
egen artist_id = group(artist)
gen acclaim= length(aF_ranking) - length(subinstr(aF_ranking, "0", "", .))
replace acclaim=. if acclaim==0
************


drop image_id

gen artsyData = 1 if strpos(url, "artsy")
replace artsyData = 0 if artsyData == .
gen artfactsDataAvailable = 1 if aF_gender != "", after(artsyData)
replace artfactsDataAvailable = 0 if artfactsDataAvailable  == .

gen lnLowPriceUSD = log(lowPriceUSD)
gen lnHighPriceUSD = log(highPriceUSD)

* Make all names uniform: convert camelcase to snake_case
rename artsyData artsy_data
rename artfactsDataAvailable artfacts_data_available
rename yearCompleted year_completed
rename lowPriceUSD low_price_USD
rename highPriceUSD high_price_USD
rename lowPrice low_price
rename highPrice high_price
rename collectiondate collection_date
rename collectiondTimes collection_times
rename collectiondate1 collection_date1
rename collectiondate2 collection_date2
rename collectiondate1fair collection_date1_fair
rename collectiondate2fair collection_date2_fair
rename soldDate sold_date
rename exitDate exit_date
rename numberOfArtworks number_of_artworks
rename fair_startDate fair_start_date
rename fair_endDate fair_end_date
rename genderSource gender_source
rename manualCorrection manual_correction
rename isAvailable artist_data_available
rename au_artist_BirthPlace au_artist_birth_place
rename au_artist_YearBirth au_artist_year_birth
rename isFair is_fair
rename startYear start_year
rename endYear end_year
rename centEarly cent_early
rename centLate cent_late
rename lnLowPriceUSD ln_low_price_usd
rename lnHighPriceUSD ln_high_price_usd
rename exactMatch exact_match
rename ar_artsyPrediction ar_artsy_prediction
rename ar_artsyFemaleCounter ar_artsy_female_counter
rename ar_artsyPredictionDummy ar_artsy_prediction_dummy
rename ar_Description ar_description
rename ar_artsyMaleCounter ar_artsy_male_counter
rename au_artist_Surname au_artist_surname
rename au_artist_Forename au_artist_forename
rename au_exampleartwork_Title au_example_artwork_title
rename exactMatchGender exact_match_gender
rename NNvalidInput nn_valid_input
rename NNvalue nn_value
rename NNgender nn_gender
rename NNaccuracy nn_accuracy
rename ar_URL ar_url


* Generate birth_year
gen birth_year = aF_birth_year
replace birth_year = au_artist_year_birth if au_artist_year_birth != .
replace birth_year = bl_yobirth	if bl_yobirth != .
gen birth_error = 1 if birth_year != aF_birth_year & aF_birth_year != .
replace birth_error = 1 if birth_year != au_artist_year_birth & au_artist_year_birth != .
* ArtFacts seems to be the most reliable source. Replace results with artfacts data if inconsistent
replace birth_year = aF_birth_year if birth_error == 1 & aF_birth_year != .
* Generate death_year
gen death_year = aF_death_year
replace death_year = bl_yodeath	if bl_yodeath != .
gen death_error = 1 if death_year != aF_death_year & aF_death_year != .
* ArtFacts seems to be the most reliable source. Replace results with artfacts data if inconsistent
replace death_year = aF_death_year if death_error == 1 & aF_death_year != .

egen sector = group(aF_sector), l
* Generate log price
gen ln_price = log(price)

* Generate geographical data
split aF_birth_location, p("(") gen(locgen)
replace locgen4 = subinstr(locgen4, ")", "", .)
gen country_code = locgen4
replace locgen3 = subinstr(locgen3, "))", "", .)
replace locgen3 = subinstr(locgen3, ")", "", .)
replace country_code = locgen3 if country_code == ""
replace locgen2 = subinstr(locgen2, "))", "", .)
replace locgen2 = subinstr(locgen2, ")", "", .)
replace country_code = locgen2 if country_code == ""
replace country_code = "" if country_code == "unknown identity"
replace country_code = "RU" if country_code == "sU"
replace country_code = "US" if country_code == "us"
replace country_code = "DE" if country_code == "Germany"
replace country_code = "DE" if country_code == "DE ♀"
replace country_code = "PS" if country_code == "Palästina/ Palestine"

split country_code, p("/*") gen(countrygen)
drop country_code
drop locgen*
rename countrygen1 artist_first_nationality
rename countrygen2 artist_secondary_nationality

gen artist_dual_nationality = .
replace artist_dual_nationality = 0 if artist_first_nationality != "" & artist_secondary_nationality == ""
replace artist_dual_nationality = 1 if artist_first_nationality != "" & artist_secondary_nationality != ""

* Use additional available variables to determine nationality
split aF_national_ranking, p(" ") g(nat_gen)
drop nat_gen1 nat_gen2
replace artist_first_nationality = nat_gen3 if artist_first_nationality == ""
drop nat_gen3

replace artist_first_nationality = "US" if artist_first_nationality == "" & au_derived_nationality == "American"
replace artist_first_nationality = "GB" if artist_first_nationality == "" & au_derived_nationality == "British"
replace artist_first_nationality = "IT" if artist_first_nationality == "" & au_derived_nationality == "Italian"
replace artist_first_nationality = "FR" if artist_first_nationality == "" & au_derived_nationality == "French"
replace artist_first_nationality = "DE" if artist_first_nationality == "" & au_derived_nationality == "German"
replace artist_first_nationality = "NL" if artist_first_nationality == "" & au_derived_nationality == "Dutch"
replace artist_first_nationality = "RU" if artist_first_nationality == "" & au_derived_nationality == "Russian"
replace artist_first_nationality = "ES" if artist_first_nationality == "" & au_derived_nationality == "Spanish"
replace artist_first_nationality = "HU" if artist_first_nationality == "" & au_derived_nationality == "Hungarian"
replace artist_first_nationality = "BR" if artist_first_nationality == "" & au_derived_nationality == "Brazilian"
replace artist_first_nationality = "AT" if artist_first_nationality == "" & au_derived_nationality == "Austrian"
replace artist_first_nationality = "AU" if artist_first_nationality == "" & au_derived_nationality == "Australian"
replace artist_first_nationality = "CA" if artist_first_nationality == "" & au_derived_nationality == "Canadian"
replace artist_first_nationality = "IL" if artist_first_nationality == "" & au_derived_nationality == "Israeli"
replace artist_first_nationality = "MX" if artist_first_nationality == "" & au_derived_nationality == "Mexican"
replace artist_first_nationality = "JP" if artist_first_nationality == "" & au_derived_nationality == "Japanese"
replace artist_first_nationality = "ZA" if artist_first_nationality == "" & au_derived_nationality == "South African"
replace artist_first_nationality = "CH" if artist_first_nationality == "" & au_derived_nationality == "Swiss"
replace artist_first_nationality = "VE" if artist_first_nationality == "" & au_derived_nationality == "Venezuelan"

replace artist_first_nationality = "AR" if artist_first_nationality == "" & au_nationality_code == "ARG"
replace artist_first_nationality = "BE" if artist_first_nationality == "" & au_nationality_code == "BEL"
replace artist_first_nationality = "IN" if artist_first_nationality == "" & au_nationality_code == "IND"


replace artist_first_nationality = "US" if artist_first_nationality == "" & bl_nationality == "American"
replace artist_first_nationality = "BR" if artist_first_nationality == "" & bl_nationality == "Brazilian"
replace artist_first_nationality = "GB" if artist_first_nationality == "" & bl_nationality == "British"
replace artist_first_nationality = "CA" if artist_first_nationality == "" & bl_nationality == "Canadian"
replace artist_first_nationality = "CN" if artist_first_nationality == "" & bl_nationality == "Chinese"
replace artist_first_nationality = "CU" if artist_first_nationality == "" & bl_nationality == "Cuban"
replace artist_first_nationality = "DK" if artist_first_nationality == "" & bl_nationality == "Danish"
replace artist_first_nationality = "NL" if artist_first_nationality == "" & bl_nationality == "Dutch"
replace artist_first_nationality = "FR" if artist_first_nationality == "" & bl_nationality == "French"
replace artist_first_nationality = "DE" if artist_first_nationality == "" & bl_nationality == "German"
replace artist_first_nationality = "IL" if artist_first_nationality == "" & bl_nationality == "Israeli"
replace artist_first_nationality = "IT" if artist_first_nationality == "" & bl_nationality == "Italian"
replace artist_first_nationality = "JP" if artist_first_nationality == "" & bl_nationality == "Japanese"
replace artist_first_nationality = "MX" if artist_first_nationality == "" & bl_nationality == "Mexican"
replace artist_first_nationality = "KR" if artist_first_nationality == "" & bl_nationality == "Korean"
replace artist_first_nationality = "NG" if artist_first_nationality == "" & bl_nationality == "Nigerian"
replace artist_first_nationality = "PE" if artist_first_nationality == "" & bl_nationality == "Peruvian"
replace artist_first_nationality = "PL" if artist_first_nationality == "" & bl_nationality == "Polish"
replace artist_first_nationality = "ZA" if artist_first_nationality == "" & bl_nationality == "South African"

* Generate dummy variable for artists from G7 countries
gen artist_g7 = 1 if artist_first_nationality == "US" | artist_secondary_nationality == "US"
replace artist_g7 = 1 if artist_first_nationality == "UK" | artist_secondary_nationality == "UK"
replace artist_g7 = 1 if artist_first_nationality == "CA" | artist_secondary_nationality == "CA"
replace artist_g7 = 1 if artist_first_nationality == "FR" | artist_secondary_nationality == "FR"
replace artist_g7 = 1 if artist_first_nationality == "DE" | artist_secondary_nationality == "DE"
replace artist_g7 = 1 if artist_first_nationality == "IT" | artist_secondary_nationality == "IT"
replace artist_g7 = 1 if artist_first_nationality == "JP" | artist_secondary_nationality == "JP"
* EU Countries
gen artist_eu = 1 if artist_first_nationality == "AT" | artist_secondary_nationality == "AT"
replace artist_eu = 1 if artist_first_nationality == "BE" | artist_secondary_nationality == "BE"
replace artist_eu = 1 if artist_first_nationality == "BG" | artist_secondary_nationality == "BG"
replace artist_eu = 1 if artist_first_nationality == "HR" | artist_secondary_nationality == "HR"
replace artist_eu = 1 if artist_first_nationality == "CY" | artist_secondary_nationality == "CY"
replace artist_eu = 1 if artist_first_nationality == "CZ" | artist_secondary_nationality == "CZ"
replace artist_eu = 1 if artist_first_nationality == "DK" | artist_secondary_nationality == "DK"
replace artist_eu = 1 if artist_first_nationality == "EE" | artist_secondary_nationality == "EE"
replace artist_eu = 1 if artist_first_nationality == "FI" | artist_secondary_nationality == "FI"
replace artist_eu = 1 if artist_first_nationality == "FR" | artist_secondary_nationality == "FR"
replace artist_eu = 1 if artist_first_nationality == "DE" | artist_secondary_nationality == "DE"
replace artist_eu = 1 if artist_first_nationality == "GR" | artist_secondary_nationality == "GR"
replace artist_eu = 1 if artist_first_nationality == "HU" | artist_secondary_nationality == "HU"
replace artist_eu = 1 if artist_first_nationality == "IE" | artist_secondary_nationality == "IE"
replace artist_eu = 1 if artist_first_nationality == "IT" | artist_secondary_nationality == "IT"
replace artist_eu = 1 if artist_first_nationality == "LV" | artist_secondary_nationality == "LV"
replace artist_eu = 1 if artist_first_nationality == "LT" | artist_secondary_nationality == "LT"
replace artist_eu = 1 if artist_first_nationality == "LU" | artist_secondary_nationality == "LU"
replace artist_eu = 1 if artist_first_nationality == "MT" | artist_secondary_nationality == "MT"
replace artist_eu = 1 if artist_first_nationality == "NL" | artist_secondary_nationality == "NL"
replace artist_eu = 1 if artist_first_nationality == "PL" | artist_secondary_nationality == "PL"
replace artist_eu = 1 if artist_first_nationality == "PT" | artist_secondary_nationality == "PT"
replace artist_eu = 1 if artist_first_nationality == "RO" | artist_secondary_nationality == "RO"
replace artist_eu = 1 if artist_first_nationality == "SK" | artist_secondary_nationality == "SK"
replace artist_eu = 1 if artist_first_nationality == "SI" | artist_secondary_nationality == "SI"
replace artist_eu = 1 if artist_first_nationality == "ES" | artist_secondary_nationality == "ES"
replace artist_eu = 1 if artist_first_nationality == "SE" | artist_secondary_nationality == "SE"
replace artist_eu = 0 if artist_eu == . & artist_first_nationality != ""
replace artist_g7 = 1 if artist_eu == 1
* Replace anything remaining
replace artist_g7 = 0 if artist_g7 == . & artist_first_nationality  != ""

* Generate dummy variable for countries regarded as advanced economies by the IMF
gen artist_advanced_econ = 1 if artist_first_nationality == "AU" | artist_secondary_nationality == "AU"
replace artist_advanced_econ = 1 if artist_first_nationality == "AT" | artist_secondary_nationality == "AT"
replace artist_advanced_econ = 1 if artist_first_nationality == "BE" | artist_secondary_nationality == "BE"
replace artist_advanced_econ = 1 if artist_first_nationality == "CA" | artist_secondary_nationality == "CA"
replace artist_advanced_econ = 1 if artist_first_nationality == "CY" | artist_secondary_nationality == "CY"
replace artist_advanced_econ = 1 if artist_first_nationality == "CZ" | artist_secondary_nationality == "CZ"
replace artist_advanced_econ = 1 if artist_first_nationality == "DK" | artist_secondary_nationality == "DK"
replace artist_advanced_econ = 1 if artist_first_nationality == "EE" | artist_secondary_nationality == "EE"
replace artist_advanced_econ = 1 if artist_first_nationality == "FI" | artist_secondary_nationality == "FI"
replace artist_advanced_econ = 1 if artist_first_nationality == "FR" | artist_secondary_nationality == "FR"
replace artist_advanced_econ = 1 if artist_first_nationality == "DE" | artist_secondary_nationality == "DE"
replace artist_advanced_econ = 1 if artist_first_nationality == "GR" | artist_secondary_nationality == "GR"
replace artist_advanced_econ = 1 if artist_first_nationality == "HK" | artist_secondary_nationality == "HK"
replace artist_advanced_econ = 1 if artist_first_nationality == "IS" | artist_secondary_nationality == "IS"
replace artist_advanced_econ = 1 if artist_first_nationality == "IE" | artist_secondary_nationality == "IE"
replace artist_advanced_econ = 1 if artist_first_nationality == "IL" | artist_secondary_nationality == "IL"
replace artist_advanced_econ = 1 if artist_first_nationality == "IT" | artist_secondary_nationality == "IT"
replace artist_advanced_econ = 1 if artist_first_nationality == "JP" | artist_secondary_nationality == "JP"
replace artist_advanced_econ = 1 if artist_first_nationality == "KR" | artist_secondary_nationality == "KR"
replace artist_advanced_econ = 1 if artist_first_nationality == "LV" | artist_secondary_nationality == "LV"
replace artist_advanced_econ = 1 if artist_first_nationality == "LT" | artist_secondary_nationality == "LT"
replace artist_advanced_econ = 1 if artist_first_nationality == "LU" | artist_secondary_nationality == "LU"
replace artist_advanced_econ = 1 if artist_first_nationality == "MO" | artist_secondary_nationality == "MO"
replace artist_advanced_econ = 1 if artist_first_nationality == "MT" | artist_secondary_nationality == "MT"
replace artist_advanced_econ = 1 if artist_first_nationality == "NL" | artist_secondary_nationality == "NL"
replace artist_advanced_econ = 1 if artist_first_nationality == "NZ" | artist_secondary_nationality == "NZ"
replace artist_advanced_econ = 1 if artist_first_nationality == "NO" | artist_secondary_nationality == "NO"
replace artist_advanced_econ = 1 if artist_first_nationality == "PT" | artist_secondary_nationality == "PT"
replace artist_advanced_econ = 1 if artist_first_nationality == "PR" | artist_secondary_nationality == "PR"
replace artist_advanced_econ = 1 if artist_first_nationality == "SM" | artist_secondary_nationality == "SM"
replace artist_advanced_econ = 1 if artist_first_nationality == "SG" | artist_secondary_nationality == "SG"
replace artist_advanced_econ = 1 if artist_first_nationality == "SK" | artist_secondary_nationality == "SK"
replace artist_advanced_econ = 1 if artist_first_nationality == "SI" | artist_secondary_nationality == "SI"
replace artist_advanced_econ = 1 if artist_first_nationality == "ES" | artist_secondary_nationality == "ES"
replace artist_advanced_econ = 1 if artist_first_nationality == "SE" | artist_secondary_nationality == "SE"
replace artist_advanced_econ = 1 if artist_first_nationality == "CH" | artist_secondary_nationality == "CH"
replace artist_advanced_econ = 1 if artist_first_nationality == "TW" | artist_secondary_nationality == "TW"
replace artist_advanced_econ = 1 if artist_first_nationality == "UK" | artist_secondary_nationality == "UK"
replace artist_advanced_econ = 1 if artist_first_nationality == "US" | artist_secondary_nationality == "US"
* Replace anything remaining
replace artist_advanced_econ = 0 if artist_advanced_econ == . & artist_first_nationality  != ""

rename artwork_id artwork_url_id

* Infer category from materials
gen category_missing = 1 if category == .
* 1 Architecture
replace category = 1 if strpos(lower(materials), "homes") & category_missing == 1
replace category = 1 if strpos(lower(materials), "sectors") & category_missing == 1


* 2 Books and Portfolios
replace category = 2 if strpos(lower(materials), "hardcover") & category_missing == 1

 
* 3 Design/Decorative Art
replace category = 3 if strpos(lower(materials), "stoneware") & category_missing == 1
replace category = 3 if strpos(lower(materials), "mahogany") & category_missing == 1
replace category = 3 if strpos(lower(materials), "wool") & category_missing == 1
replace category = 3 if strpos(lower(materials), "bamboo") & category_missing == 1
replace category = 3 if strpos(lower(materials), "brass") & category_missing == 1


* 4 Drawing, Collage or other Work on Paper
replace category = 4 if strpos(lower(materials), "paper") & category_missing == 1
replace category = 4 if strpos(lower(materials), "ink") & category_missing == 1
replace category = 4 if strpos(lower(materials), "pencil") & category_missing == 1
replace category = 4 if strpos(lower(materials), "watercolor") & category_missing == 1
replace category = 4 if strpos(lower(materials), "graphite") & category_missing == 1
replace category = 4 if strpos(lower(materials), "charcoal") & category_missing == 1
replace category = 4 if strpos(lower(materials), "gouache") & category_missing == 1
replace category = 4 if strpos(lower(materials), "drawing") & category_missing == 1
replace category = 4 if strpos(lower(materials), "crayon") & category_missing == 1
replace category = 4 if strpos(lower(materials), "coloured") & category_missing == 1
replace category = 4 if strpos(lower(materials), "pen") & category_missing == 1


* 5 Ephemera or Merchandise


* 6 Fashion Design and Wearable Art


* 7 Installation
replace category = 7 if strpos(lower(materials), "installation") & category_missing == 1


* 8 Jewelry
replace category = 8 if strpos(lower(materials), "sterling") & category_missing == 1
replace category = 8 if strpos(lower(materials), "diamonds") & category_missing == 1
replace category = 8 if strpos(lower(materials), "18k") & category_missing == 1
replace category = 8 if strpos(lower(materials), "diamond") & category_missing == 1
replace category = 8 if strpos(lower(materials), "sapphires") & category_missing == 1


* 9 Mixed Media
replace category = 9 if strpos(lower(materials), "mixed media") & category_missing == 1
replace category = 9 if strpos(lower(materials), "mixed") & category_missing == 1


* 10 Other


* 11 Painting
replace category = 11 if strpos(lower(materials), "canvas") & category_missing == 1
replace category = 11 if strpos(lower(materials), "oil") & category_missing == 1
replace category = 11 if strpos(lower(materials), "acrylic") & category_missing == 1
replace category = 11 if strpos(lower(materials), "panel") & category_missing == 1
replace category = 11 if strpos(lower(materials), "linen") & category_missing == 1
replace category = 11 if strpos(lower(materials), "tempera") & category_missing == 1


* 12 Performance Art


* 13 Photography
replace category = 13 if strpos(lower(materials), "print") & category_missing == 1
replace category = 13 if strpos(lower(materials), "archival") & category_missing == 1
replace category = 13 if strpos(lower(materials), "gelatin") & category_missing == 1
replace category = 13 if strpos(lower(materials), "pigment") & category_missing == 1
replace category = 13 if strpos(lower(materials), "digital") & category_missing == 1
replace category = 13 if strpos(lower(materials), "inkjet") & category_missing == 1
replace category = 13 if strpos(lower(materials), "photograph") & category_missing == 1
replace category = 13 if strpos(lower(materials), "vintage") & category_missing == 1
replace category = 13 if strpos(lower(materials), "polaroid") & category_missing == 1
replace category = 13 if strpos(lower(materials), "chromogenic") & category_missing == 1
replace category = 13 if strpos(lower(materials), "silver") & category_missing == 1
replace category = 13 if strpos(lower(materials), "platinum") & category_missing == 1


* 14 Posters


* 15 Print
replace category = 15 if strpos(lower(materials), "lithograph") & category_missing == 1
replace category = 15 if strpos(lower(materials), "offset") & category_missing == 1
replace category = 15 if strpos(lower(materials), "etching") & category_missing == 1
replace category = 15 if strpos(lower(materials), "screenprint") & category_missing == 1
replace category = 15 if strpos(lower(materials), "aquatint") & category_missing == 1
replace category = 15 if strpos(lower(materials), "woodcut") & category_missing == 1
replace category = 15 if strpos(lower(materials), "drypoint") & category_missing == 1
replace category = 15 if strpos(lower(materials), "engraving") & category_missing == 1
replace category = 15 if strpos(lower(materials), "pochoir") & category_missing == 1


* 16 Reproduction


* 17 Sculpture
replace category = 17 if strpos(lower(materials), "mobile") & category_missing == 1
replace category = 17 if strpos(lower(materials), "ceramic") & category_missing == 1
replace category = 17 if strpos(lower(materials), "bronze") & category_missing == 1
replace category = 17 if strpos(lower(materials), "ceramic") & category_missing == 1
replace category = 17 if strpos(lower(materials), "cast") & category_missing == 1


* 18 Textile Arts


* 19 Video/Film/Animation

* Mark observations where category was inferred
gen category_inferred = 1 if category_missing == 1 & category != .
replace category_inferred = 0 if category_missing != 1 & category != .
order category_inferred, after(category)


* Infer sold status by looping through each fair
egen fair_group = group(filename)
gen sold_inferred = sold, after(sold)
qui: su fair_group
foreach i of num 1/`r(max)' {
	* Reset the value of variables
	qui: local sold_false = 0
	qui: local sold_true = 0
	* Count the amount of artworks labeled as not sold
	qui: count if fair_group == `i' & sold == 0
	qui: local sold_false = r(N)
	* Count the amount of artworks labeled as sold
	qui: count if fair_group == `i' & sold == 1
	qui: local sold_true = r(N)
	
	* Replace inferred values
	replace sold_inferred = 0 if sold_inferred == . & `sold_false' == 0 & `sold_true' != 0 & fair_group == `i'
	replace sold_inferred = 1 if sold_inferred == . & `sold_true' == 0 & `sold_false' != 0 & fair_group == `i'
}

replace bc_dummy = 0 if years != . & bc_dummy == .


* Label variables
la var image_download_id "ID to match artwork 1:1 to it's image"
la var artwork_url_id "group(url) Consistent throughout fairs and saves."
la var is_fair "0: non-fair data 1: fair data"
la var artsy_data "0: non-artsy data 1: artsy data"
la var artfacts_data_available "0: no match 1: match"
la var title "The title of the artwork"
la var year_completed "The year the artwork was completed"
la var years "The number of years taken to create the artwork"
la var bc_dummy "Marks whether the years are BC. 0: AD 1: BC"
la var price "(low_price_USD + high_price_USD) / 2"
la var ln_price "log(price)"
la var low_price_usd "low_price * exchange_rate"
la var high_price_usd "high_price * exchange_rate"
la var low_price "Lower end of the price range in the original currency"
la var high_price "Higher end of the price range in the original currency"
la var currency "The original currency"
la var category_inferred "category with additional classifications based on materials"
la var materials "The materials used in the creation of the artwork"
la var category "The category of the artwork"
la var length_in "The length of the artwork in inches"
la var length_cm "The length of the artwork in centimetres"
la var width_in "The width of the artwork in inches"
la var depth_in "The depth of the artwork in inches"
la var width_cm "The width of the artwork in centimetres"
la var depth_cm "The depth of the artwork in centimetres"
la var sold "0: not sold 1: sold"
la var sold_inferred "0: not sold 1: sold with additional classifications"
la var collection_date "The date of observation"
la var collection_times "The number of times the artwork appears in the database"
la var sold_date "The date the artwork was sold"
la var gallery "The name of the gallery"
la var gallery_slug "The artsy URL of the gallery"
la var fair_id "The ID of fair."
la var fair_name "The name of the fair"
la var fair_year "The year of the fair"
la var number_of_artworks "The number of artworks that appeared on the fair"
la var fair_start_date "Start date of fair"
la var fair_end_date "End date of fair"
la var artist "The name of the artist"
la var birth_year "The year of birth of the artist"
la var death_year "The death year of the artist"
la var artist_slug "The artsy url of the artist"
la var acclaim "gen acclaim= length(aF_ranking) - length(subinstr(aF_ranking, '0', '', .))"
la var gender "The gender of the artist, based on multiple sources"
la var gender_source "The source of the artist's gender"
la var artist_g7 "Marks whether the artist is a national of a G7 country"
la var artist_advanced_econ "Marks whether the artist is a national of an IMF advanced economy"
la var artist_eu "Marks whether the artist is an EU national"
la var artist_first_nationality "The two letter code of the artist's primary nationality"
la var artist_secondary_nationality "The two letter code of the artist's secondary nationality"
la var artist_dual_nationality "Dummy marking whether the artist is a dual national"
la var inconsistency "Marks discrepancies between the gender of artist databases"
la var manual_correction "Marks whether the discrepancy was corrected manually"
la var artist_data_available "Marks whether the artist's gender is available in the artist database"
la var aF_gender "The artist's gender in the ArtFacts database"
la var au_gender_MANUAL "The artist's gender in the auction database, manually checked"
la var au_gender "The artist's gender in the auction database"
la var bl_gender "The artist's gender in the Blouin database"
la var ar_gender "The artist's gender in the Artsy database"
la var nn_gender "The artist's gender predicted by the neural network"
la var exact_match_gender "The artist's gender based on an exact first name match"
la var aF_birth_date "The artist' date of birth in the ArtFacts database"
la var aF_birth_year "The artist's year of birth in the ArtFacts database"
la var aF_death_date "The artist's date of death in the ArtFacts database"
la var aF_death_year "The artist's year of death in the ArtFacts database"
la var aF_birth_location "The birthplace of the artist in the ArtFacts database"
la var aF_countries "The countries where the artist was active"
la var aF_sector "The movement in which the artist was active"
la var aF_ranking "The global ranking of the artist in the ArtFacts database"
la var aF_exhibitions_in_count_1 "The number of exhibitions in country_1"
la var aF_exhibitions_in_country_2 "The country where the artist had the second most exhibitions"
la var aF_exhibitions_in_country_1 "The country where the artist had the most exhibitions"
la var aF_exhibitions_in_count_2 "The number of exhibitions in country_2"
la var aF_exhibitions_in_country_3 "The country where the artist had the third most exhibitions"
la var aF_exhibitions_in_count_3 "The number of exhibitions in country_3"
la var aF_exhibitions_at_institution_1 "The institution where the artist had the most exhibitions"
la var aF_exhibitions_at_institution_2 "The institution where the artist had the second most exhibitions"
la var aF_institution_id_1 "The ID corresponding to institution_1 in the ArtFacts database"
la var aF_institution_id_2 "The ID corresponding to institution_2 in the ArtFacts database"
la var aF_institution_id_3 "The ID corresponding to institution_3 in the ArtFacts database"
la var aF_national_ranking "The national ranking of the artist in the ArtFacts database"
la var aF_exhibitions_total "The total number of exhibitions tracked by ArtFacts"
la var bl_nationality "The artist's nationality in the Blouin database"
la var bl_yobirth "The birth year of the artist in the Blouin database"
la var bl_yodeath "THe artist's year of death in the Blouin database"
la var death_error "Marks whether the death year differs across sources"
la var price_unformatted "The original price variable as collected"
la var filename "The name of the file where the price data was saved"
la var year "The original year of the artwork's creation as collected"
la var start_year "The start of the artwork's creation"
la var end_year "The end of the artwork's creation"
la var century_dummy "Support variable: marks whether the original date was specified in centuries"
la var cent_early "Support variable: marks whether the original date specified the artwork as early .. century"
la var cent_late "Support variable: marks whether the original date specified the artwork as late .. century"
la var ln_low_price_usd "log(low_price_USD)"
la var ln_high_price_usd "log(high_price_USD)"
la var datecur "Support variable used to merge with currency data"
la var exchange_rate "The relevant daily average exchange rate"
la var dimensions "The original dimensions variable as collected"
la var length "The length of the artwork in the original unit of measurement"
la var width "The width of the artwork in the original unit of measurement"
la var depth "The depth of the artwork in the original unit of measurement"
la var measurement "0: cm 1: in, Dummy variable marking the original unit of measurement"
la var url "The URL of the artwork where the data was collected"
la var image_url "The URL of an image of the artwork"
la var sold_unformatted "The original sold variable as collected"
la var collectiondate_unformatted "The date of collection in string format"
la var details "Relevant only for FRIEZE fairs. The detials of the artwork"
la var description "Relevant only for FRIEZE fairs. The additional details of the artwork"
la var _dupe "MARKS COLLECTION DUPES bys url fair: gen _dupe = cond(_N==1, 0, 1) if url != ''"
la var fair_date "The original fair date variable in string format"
la var fair_artsy_url "The Artsy URL of the fair"
la var aF_id "The ID of the artist in the ArtFacts database"
la var aF_first_name "The first name of the artist in the ArtFacts database"
la var aF_last_name "The last name of the artist in the ArtFacts databse"
la var aF_aliases "The aliases of the artist in the ArtFacts database"
la var aF_birth_date_unformatted "The unformatted birth date of the artist in the ArtFacts database"
la var aF_death_date_unformatted "The unformatted death date of the artist in the ArtFacts database"
la var aF_death_location "The death location of the artist in the ArtFacts database"
la var aF_movements "The artist's prominent movements in the ArtFacts database"
la var aF_media "The artist's most common art category"
la var aF_link_artfacts "The link to the artist's ArtFacts website"
la var aF_link_personal "The link to the artist's personal website"
la var aF_links_wiki "The link to the artist's wikipedia page"
la var aF_ranking_trend "The recent popularity of the artist in the ArtFacts database."
la var aF_cities "Cities where the artist created most of his artworks"
la var aF_groups "Groups in which the artist is a member"
la var aF_description "Small description of the artist as in the ArtFacts database"
la var aF_exhibitions_solo "The number of solo exhibitions by the artist"
la var aF_exhibitions_group "The number of group exhibtions by the artist"
la var aF_exhibitions_artfair "The number of fair exhibitions by the artist"
la var aF_exhibitions_collective "The number of collective exhibitions by the artist"
la var aF_exhibitions_current "The number of current exhibitions by the artist (as of the collection date)"
la var aF_exhibitions_biennial "The number of bienial exhibitions by the artist"
la var aF_exhebitions_gallery "The number of shows held in a gallery featuring the artist's artworks"
la var aF_exhebitions_museum "The number of shows held in museums featuring the artist's artworks"
la var aF_exhebitions_other "The number of shows held in other institutions featuring the artist"
la var ar_url "The artist's artsy URL"
la var ar_artsy_prediction_dummy "Marks whether there is an available gender prediction from artsy"
la var ar_description "The description of the artist in the artsy database"
la var ar_artsy_female_counter "The number of female pronouns in the artsy description"
la var ar_artsy_male_counter "The number of male pronouns in the artsy description"
la var ar_artsy_prediction "The gender prediction based on the pronouns in the artsy description"
la var au_artist_surname "The artist's surname in the auction database"
la var au_artist_forename "The artist's forename in the auction database"
la var au_example_artwork_title "An example artwork's title in the auction database"
la var au_medium "The artist's most common medium in the auction database"
la var au_nationality_code "The artist's nationality in the auction database"
la var au_artist_id "ID of the artist in the auction database"
la var au_style "The artist's most common style in the auction database"
la var bl_malepronouns "The number of male pronouns in the Blouin description"
la var bl_femalepronouns "The number of female pronouns in the Blouin description"
la var bl_predictionaccuracy "The accuracy of the prediction based on Blouin the pronouns"
la var bl_url "The artist's Blouin link"
la var exact_match "The gender based on the first name match in the first name database"
la var nn_valid_input "Marks whether the neural network could evaluate the name"
la var nn_value "The neural networks output"
la var nn_accuracy "abs(NNvalue - 0.5)"
la var sector "group(aF_sector)"
la var category_missing "Marks whether the category was not originally specified"



rename fair_date fair_date_unformatted
rename bl_yodeath bl_death_year
rename bl_yobirth bl_birth_year
rename year year_unformatted
rename dimensions dimensions_unformatted

replace artist_data_available = 0 if artist_data_available == .
* Drop redundant and unnecessary variables
drop aF_nationality fair collection_url aF_artists  aF_exhebitions_artfair aF_exhebitions_biennial aF_catalog  aF_dealer aF_collection

* Jiaqi's ordering of variables
*order artwork_id artwork_fair_id image_id is_fair artsy_data artfacts_data_available title year_completed years bc_dummy price ln_price low_price_USD high_price_USD low_price high_price currency category materials length_in width_in depth_in sold collection_date collection_times collection_date1 collection_date2 collection_date1_fair collection_date2_fair sold_date exit_date gallery_id gallery gallery_slug fair_id fair_name fair_image_id fair_year number_of_artworks fair_start_date fair_end_date artist_id artist birth_year death_year artist_slug acclaim gender gender_source sector artist_g7 artist_advanced_econ artist_eu artist_first_nationality artist_secondary_nationality artist_dual_nationality inconsistency manual_correction artist_data_available aF_gender au_gender_MANUAL au_gender bl_gender ar_gender nn_gender exact_match_gender aF_birth_date aF_birth_year aF_death_date aF_death_year aF_birth_location aF_nationality aF_countries aF_sector aF_ranking aF_exhibitions_in_country_1 aF_exhibitions_in_count_1 aF_exhibitions_in_country_2 aF_exhibitions_in_count_2 aF_exhibitions_in_country_3 aF_exhibitions_in_count_3 aF_exhibitions_at_institution_1 aF_institution_id_1 aF_exhibitions_at_institution_2 aF_institution_id_2 aF_exhibitions_at_institution_3 aF_institution_id_3 aF_national_ranking aF_exhibitions_total au_derived_nationality au_artist_birth_place au_artist_year_birth au_deceased bl_nationality bl_yobirth bl_yodeath birth_error death_error
*sort fair_id fair_year artwork_id collectiondate

capture destring aF_id aF_exhibitions_in_count_1 aF_exhibitions_in_count_3 aF_institution_id_1 aF_institution_id_2 aF_exhebitions_other ar_artsy_prediction_dummy au_artist_id au_artwork_id, replace

drop acclaim
egen acclaim = group(aF_ranking), l
egen acclaim_trend = group(aF_ranking_trend), l


order artwork_url_id is_fair fair_name fair_year fair_start_date fair_end_date artsy_data artfacts_data_available artist_id artist gender gender_source birth_year death_year sector title start_year end_year year_completed years category price ln_price low_price_usd high_price_usd ln_low_price_usd ln_high_price_usd gallery_id gallery materials length_in width_in depth_in sold_inferred collection_date collection_times acclaim acclaim_trend artist_g7 artist_advanced_econ artist_eu aF_* ar_* au_* bl_* *_unformatted category_inferred
sort fair_end_date fair_id collection_date artist_id

replace gallery = "" if gallery == "Want to sell a work by this artist? Consign with Artsy."
replace gallery_id = . if gallery == ""


* Create dummy variable for major fairs.
gen major_fair = .
replace major_fair = 1 if fair_id == "45" | fair_id == "44" | fair_id == "63" | fair_id == "22" | fair_id == "40" | fair_id == "104" | fair_id == "8" | fair_id == "1" | fair_id == "87" | fair_id == "133" | fair_id == "3" | fair_id == "34" | fair_id == "47" | fair_id == "50" | fair_id == "82" | fair_id == "23" | fair_id == "42" | fair_id == "4" | fair_id == "32"
replace major_fair = 0 if major_fair == .
la var major_fair "Marks whether a fair is part of the 20 largest fairs worldwide"


* Generate numeric fair id to control for fair level variations.
rename fair_id fair_image_id
gen fair_id = fair_image_id
order fair_id, after(fair_name)
replace fair_id = "0" if fair_id == "C"
replace fair_id = "999" if fair_id == "G"
replace fair_id = "998" if fair_id == "S"
destring fair_id, replace

* Replicate Adams et al. (2021)

* Generate additional variables
gen surface_sqin = width_in * length_in
gen ln_surface = log(surface_sqin)

gen artist_deceased = 1 if death_year != .
order artist_deceased, after(death_year)
replace artist_deceased = 1 if birth_year < 1920
replace artist_deceased = 0 if artist_deceased == . & birth_year != .

gen mega_price = 1 if price >= 1000000 & price != .
replace mega_price = 0 if mega_price ==. & price != .


gen artist_age = 2021 - birth_year
order artist_age, after(artist_deceased)

cd $exportDir
save "priceMaster.dta", replace
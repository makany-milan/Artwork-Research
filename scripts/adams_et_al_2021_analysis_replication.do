clear
cd "D:\oxford\02-11-2021"
use "priceMaster-02-11-2021.dta"

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

* Replicate regressions
reg ln_price gender
* Omit category "paintings"
reg ln_price gender b12.category, vce(robust)
reg ln_price gender b12.category##c.ln_surface, vce(robust)
reg ln_price gender b12.category##c.ln_surface artist_deceased, vce(robust)
reg ln_price gender b12.category##c.ln_surface artist_deceased sector, vce(robust)


* Use only fair data
reg ln_price gender if is_fair == 1
reg ln_price gender b12.category if is_fair == 1, vce(robust)
reg ln_price gender b12.category##c.ln_surface if is_fair == 1, vce(robust)

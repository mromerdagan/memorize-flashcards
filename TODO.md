
## Wish list
* In policy and console client: Add trian-multiple mode. For example, suppose I want to
  train myself with two courses that are now most relevant for me. I want cards from both
  courses to appear with equal probability. 
  So usage should change form this:

	Usage:
	    nsg-run-compose-branch <coursename> <num-cards>

  To:

	Usage:
	    nsg-run-compose-branch <coursename>[,<coursename>,..] <num-cards>

* In list courses, add --sort-by-freq to show courses so most frquently used are at the
  top

* Add backup/restore/show-diff \<location\> actions to admin. 

* Implement REST API for admin (which can be used later for console app, web app etc)
  

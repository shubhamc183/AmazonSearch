"""
To understand this program, one must understand the basics of HTML http://www.w3schools.com/html/
Learn how Regular Expressions work, https://docs.python.org/2/library/re.html
Basic Sql and database commands , and how they are implemented in python, google them.
Databases are out of scope for this project
Learn how requests are sent and experiment with different possibilities
Learn what a url is and how it is padded
Finally Have a basic understanding of beautiful soup the main package for scraping web data.
Instruction on installation of all these packages can be found in the Readme
All Rights Reserved Shubham C, Gitam University
"""

import re  #Package for Regular Expressions

import requests #Package to send and receive requests for the website

import MySQLdb #Database package to store the results in a database on the Local Machine

from bs4 import BeautifulSoup #The Package used for webscraping https://www.crummy.com/software/BeautifulSoup/bs4/doc/ <---Docs

from urllib.request import urlretrieve #used to retrieve url info


def scrape(q,n): #The Actual Scraping function, Go below to see the Call.

	types=['','popularity-rank','price-asc-rank','price-desc-rank','review-rank','date-desc-rank'] #Based on the value of n, one will be selected
	#Headers are used to make Amazon.in think that the requests are received from browser and not a python program.
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'} #To spoof Python
	
	Q=''
	
	for i in q.split(): #Padding the Product word search entered so that it can fit into the url
		Q+=i+'%20'
		
	Q=Q[:len(Q)-3] # Removing the last %20 which ends up being added in the above loop
	#The actual query url you see in a web browser, try entering the url in the web browser
	query=requests.get('http://www.amazon.in/s/url=search-alias%3Daps&field-keywords='+Q+"&sort="+types[n-1],headers=headers)
	# request package sends a request to the url in the form of a browser.
	#The status code is returned by the server, Here is a list of status codes ---> https://www.w3.org/Protocols/HTTP/HTRESP.html
	if query.status_code!=200: #if the request is not accepted try again
		
		query.close()	
		
		query=requests.get('http://www.amazon.in/s/url=search-alias%3Daps&field-keywords='+Q+'&sort='+types[n-1],headers=headers)
	
	if query.status_code!=200: #if the request is not accepted a second time, print error and exit
		
		print("Error")
		
		exit()
	
	s=BeautifulSoup(query.text,"html.parser") #use beautiful soup to the beautify the html page to manipulate it
	
	db=MySQLdb.connect(host="localhost",user="shubham",passwd="Flyhigh123$",db="mysql") #connect to a local database
	# the user can be changed to your own user and passwd can be changed to ur new passwd
	
	cursor=db.cursor() #set control in the database
	
	cursor.execute("create table amazon(link varchar(150), name varchar(100),price integer,rating integer)")
	#create a table named amazon, column, link for the image, name of the product and price and rating
	
	print("The query link is",query.url)
	
	R=-1
	#The actual extraction from the soup starts here
	while(1):
		
		R+=1
		
		i=s.find("li",{"id":"result_"+str(R)})# find the first result with the help of the id tag.
		
		if i==None:
			#if no results are available the program breaks
			print("Sorry No results match your search, Surender Please try another search :/")
			
			break
		
		else:
			
			link=i.find('img')['src'] #get the link to the image of the product
			
			name=i.find('h2').text[:100]# get the product name
			
			price=i.find("span",{"class":"a-size-base a-color-price s-price a-text-bold"}) # get the price based on the class tag
			
			try:
				
				price=str(re.findall('[0-9].*',price.text))# use re to find only numbers as the price, if none are found try a different method
				
			except:
				
				price=i.findAll("span",{"class":"a-color-price"}) # use a different class to find the price
				
				try:
					
					price=str(re.findall('[0-9].*',price[1].text)) # now try to the find only numbers as the price using re
				except:
					
					print(name)
					#if price not available, leave it and go to next result
					continue
			pri=''
			for I in price:
				
				if I=="-":
					#if price is empty break and continue with next result
					break
				
				if I!='[' and I!=']' and I!='"' and I!="'" and I!=" " and I!=",":
					#if the price is only numbers and not anything else then take it in
					pri+=I
					
			price=float(pri) # get the floating price
			
			price=int(price) #round it off using int
			
			rating=0
			
			k=i.findAll("a",{"class":"a-size-small a-link-normal a-text-normal"}) #now find its rating using the class tag
			
			for t in k:
				
				if len(t)>0:
					#if there is some content in the scraped data
					e=(t.text).replace(',','') # remove , in the rating. Study the html of the beautified url.
					
					if str.isnumeric(e):
						#if it is a number then assign it to the rating
						rating=int(e)
						#break out of the INNER loop
						break
			#print all the three properties
			print(name,price,rating)
			
			sql='insert into amazon values("%s", "%s",%d,%d )' % (link,name,price,rating)#insert these values into the database.
			#link:Image link, Product name, Its price and rating
			
			try:
				
				cursor.execute(sql)
				#If possible add them to the database using above command
				db.commit()
				#save changes in the db
			except:
				
				db.rollback()
				#undo the previous changes in the database and try again.
				
if __name__ == "__main__":
	#The Actual program execution starts from here. This program cannot be used as a package therefore.
	a=input("Name the product: ")

	print("Set Sort by","1.Relevance","2.New & Popular","3.Price:Low to High","4.Price:High to Low","5.Avg. Customer Review","6.Newest Arrivals",sep="\n")
	
	while(1):
		
		n=input() #enter any of the above numbers to sort the results according to your need.
	
		if n=='1' or n=='2' or n=='3' or n=='4' or n=='5' or n=='6':
		
			scrape(a,int(n)) # The Actual scraping function call
		
			break
	
		if  n=='e' or n=='E': #condition for exiting
	
			print("thank you...!")
		
			exit()
		
		else: #Any other input gives a message to enter again
	
			print("try again	or press e/E for exiting..!")

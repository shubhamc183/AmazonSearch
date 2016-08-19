import re
import requests
import MySQLdb
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
def scrape(q,n):
	types=['','popularity-rank','price-asc-rank','price-desc-rank','review-rank','date-desc-rank']
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'} #To spoof Python
	Q=''
	for i in q.split():
		Q+=i+'%20'
	Q=Q[:len(Q)-3]
	query=requests.get('http://www.amazon.in/s/url=search-alias%3Daps&field-keywords='+Q+"&sort="+types[n-1],headers=headers)
	if query.status_code!=200:
		query.close()	
		query=requests.get('http://www.amazon.in/s/url=search-alias%3Daps&field-keywords='+Q+'&sort='+types[n-1],headers=headers)
	if query.status_code!=200:
		print("Error")
		exit()
	s=BeautifulSoup(query.text,"html.parser")
	db=MySQLdb.connect(host="localhost",user="shubham",passwd="Flyhigh123$",db="mysql")
	cursor=db.cursor()
	cursor.execute("create table amazon(link varchar(150), name varchar(100),price integer,rating integer)")
	print("The query link is",query.url)
	R=-1
	while(1):
		R+=1
		i=s.find("li",{"id":"result_"+str(R)})
		if i==None:
			break
		else:
			link=i.find('img')['src']
			name=i.find('h2').text[:100]
			price=i.find("span",{"class":"a-size-base a-color-price s-price a-text-bold"})
			try:
				price=str(re.findall('[0-9].*',price.text))
			except:
				price=i.findAll("span",{"class":"a-color-price"})
				try:
					price=str(re.findall('[0-9].*',price[1].text))
				except:
					print(name)
					continue
			pri=''
			for I in price:
				if I=="-":
					break
				if I!='[' and I!=']' and I!='"' and I!="'" and I!=" " and I!=",":
					pri+=I
			price=float(pri)
			price=int(price)
			rating=0
			k=i.findAll("a",{"class":"a-size-small a-link-normal a-text-normal"})
			for t in k:
				if len(t)>0:
					e=(t.text).replace(',','')
					if str.isnumeric(e):
						rating=int(e)
						break
			print(name,price,rating)
			sql='insert into amazon values("%s", "%s",%d,%d )' % (link,name,price,rating)
			try:
				cursor.execute(sql)
				db.commit()
			except:
				db.rollback()
a=input("Name the product: ")
print("Set Sort by","1.Relevance","2.New & Popular","3.Price:Low to High","4.Price:High to Low","5.Avg. Customer Review","6.Newest Arrivals",sep="\n")
while(1):
	n=input()
	if n=='1' or n=='2' or n=='3' or n=='4' or n=='5' or n=='6':
		scrape(a,int(n))
		break
	if  n=='e' or n=='E':
		print("thank you...!")
		exit()
	else:
		print("try again	or press e/E for exiting..!")

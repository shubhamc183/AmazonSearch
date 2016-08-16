import re
import requests
import MySQLdb
from bs4 import BeautifulSoup
db=MySQLdb.connect(host="localhost",user="user_name",passwd="password",db="select_database")
cursor=db.cursor()
def scrape(q,n):
	types=['','popularity-rank','price-asc-rank','price-desc-rank','review-rank','date-desc-rank']
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}			#To spoof Python
	Q=''
	for i in q.split():
		Q+=i+'%20'
	Q=Q[:len(Q)-3]
	query=requests.get('http://www.amazon.in/s/url=search-alias%3Daps&field-keywords={s}&sort={t}'.format(s=Q,t=types[n-1]),headers=headers)
	s=BeautifulSoup(query.text,"html.parser")
	cursor.execute("create table amazon(name varchar(100),price integer,rating integer)")
	for J in range(15):
		res="result_"+str(J)
		for i in s.findAll("li",{"id":res}):
			k=i.find("div",{"class":"a-row a-spacing-none"})
			name=k.text
			price=i.find("span",{"class":"a-size-base a-color-price s-price a-text-bold"})
			try:
				price=str(re.findall('[0-9].*',price.text))
			except:
				price=i.findAll("span",{"class":"a-color-price"})
				price=str(re.findall('[0-9].*',price[1].text))
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
			if len(k)>1:
				t=(k[1].text).replace(',','')
				if str.isnumeric(t):
					rating=int(t)
			print(name,price,rating)
			sql='insert into amazon values("%s",%d,%d )' % (name,price,rating)
			cursor.execute(sql)
			db.commit()
a=input("Name the product: ")
print("Set Sort by","1.Relevance","2.New & Popular","3.Price:Low to High","4.Price:High to Low","5.Newest Arrivals",sep="\n")
n=int(input())
scrape(a,n)

from bs4 import BeautifulSoup
import re
import os.path
def parse(path_to_file):
    with open(path_to_file,encoding='utf-8') as file:
        html=file.read()
        soup=BeautifulSoup(html,'xml')
        imgs=0
        headers=0
        lists=0
        div=soup.find(name='div',id="bodyContent")
        for i in div.find_all(name="img"):
            if(i.has_attr("width")):
                if int(i["width"])>=200:
                    imgs+=1
        for i in div.find_all(name=re.compile(r"^h")):
            if(i.text!=""):
                if i.text[0]in['E','T','C']:
                    headers+=1
        for i in div.find_all(name="ul"):
            temp1=i.find_parent(name="ul")
            temp2=i.find_parent(name="ol")
            if  temp1 == None and temp2 == None:
                lists+=1
        for i in div.find_all(name="ol"):
            temp1 = i.find_parent(name="ul")
            temp2 = i.find_parent(name="ol")
            if temp1 == None and temp2 == None:
                lists += 1
        set=div.find_all(name="a")
        linkslen=0
        maxlink=0
        for i in range(1,len(set)):
            if set[i-1].find_next_sibling()==set[i]:
                linkslen+=1
            else:
                if(linkslen>maxlink):
                    maxlink=linkslen
                linkslen=0
        if(linkslen>maxlink):
            maxlink=linkslen
        return [imgs, headers, maxlink+1, lists]

def find_all_links(path,page):
    with open(path+page, encoding='utf-8') as file:
        links = set()
        for i in re.findall(r"(?<=/wiki/)[\w()]+", file.read()):
            if os.path.exists(path + i):
                links.add(i)
        links=list(links)
        for i in range(0,len(links)):
            if links[i].upper()==page.upper():
                links[i]=""
        links = set(links)
        links.discard("")
        links=list(links)
        return links



class Link:
    len_of_path=1
    def __init__(self,parent,childrens,value):
        self.parent=parent
        self.childrens=childrens
        self.value=value

def build_bridge(path, start_page, end_page):
    """возвращает список страниц, по которым можно перейти по ссылкам со start_page на
    end_page, начальная и конечная страницы включаются в результирующий список"""
    a=Link(None,find_all_links(path,start_page),start_page)
    visited_links={a.value:0}
    que_dict={a.value:a}
    que_list_of_value=[a.value]
    def bfc(dict):
        temp={}
        while end_page not in que_list_of_value:
            for i in dict.keys():
                for j in find_all_links(path,i):
                    if j not in que_list_of_value:
                        que_dict.setdefault(j,Link(que_dict[i],None,j))
                        que_list_of_value.append(j)
                        temp.setdefault(j,dict[i]+1)
            bfc(temp)



    bfc(visited_links)
    result=[]
    end = que_dict.get(end_page)
    while end.value!=start_page:
        result.append(end.parent.value)
        end=end.parent
    result.reverse()
    result.append(end_page)
    return result



def get_statistics(path, start_page, end_page):
    """собирает статистику со страниц, возвращает словарь, где ключ - название страницы,
    значение - список со статистикой страницы"""

    pages = build_bridge(path, start_page, end_page)
    result={}
    for i in pages:
        result.setdefault(i,parse(path+i))
    return result
from bs4 import BeautifulSoup
import requests as r
import re
from time import sleep

    
def get_unis(url, tipo):
    response = r.get(url).text.split("\n")
    unis = [x for x in response if "Universidade" in x][0]
    
    unis = unis.replace("\t","")
    unis = unis.replace("\r","")

    unis = [x for x in re.split("<option value='\d+' ?(?:selected)?>",unis) if x]

    universidades = []

    for x in unis:
        s = x.split(" - ")
        universidades.append({"code":s[0],"name": ": ".join(s[1:]),'type':tipo})
        
    return universidades

def get_courses(uni):
    url = "https://www.dges.gov.pt/coloc/2021/col1listaredir.asp"
    sleep(0.1)
    response = r.get(url, data={"CodEstab":uni['code'],"CodR":11,"listagem":"Lista+Ordenada+de+Candidatos"})
    
    
    courses = [x for x in response.text.split("\n") if "option value" in x]
    t = 1
    while not courses:
        print("Demasiados pedidos" if "pedidos" in response.text else response.text)
        sleep(t)
        t += 0.5
        response = r.get(url, data={"CodEstab":uni['code'],"CodR":11,"listagem":"Lista+Ordenada+de+Candidatos"})
        courses = [x for x in response.text.split("\n") if "option value" in x]
        
    courses = courses[0]
    courses = courses.replace("\t","")
    courses = courses.replace("\r","")
    
    courses = [x for x in re.split("<option value='\w+' ?(?:selected)?>",courses) if x]
    courses_dict = []
    for course in courses:
        s = course.split(" - ")
        courses_dict.append({'code': s[0], 'name': " ".join(s[1:]), "faculty":uni})
        
    return courses_dict


def get_candidates(faculty_code,course_code):
    url = "https://www.dges.gov.pt/coloc/2021/col1listaser.asp"
    data = {"CodEstab":f"{faculty_code}","CodCurso":course_code,
            # "search":"Continuar","CodR":11,"listagem":"Lista+Ordenada+de+Candidatos",
            "ids":0,"ide":9999,"Mx":9999}
    
    response = r.get(url,params=data)
    soup = BeautifulSoup(response.content, "html5lib")
    
    try:
        table = soup.findAll("table",attrs={"class":"caixa"})[-1].findAll("td")
        table = [x.text.strip() for x in table]
    except:
        try:
            print("Demasiados pedidos" if "pedidos" in response.text else response.text)
            sleep(1)
            response = r.get(url,data=data)
            soup = BeautifulSoup(response.content, "html5lib")
            table = soup.findAll("table",attrs={"class":"caixa"})[-1].findAll("td")
            table = [x.text.strip() for x in table]
        except:
            print("Failed",course_code)
            return []
        

    candidates = []
    for i in range(len(table)):
        if '(...)' in table[i]:
            candidates.append(table[i]+table[i+1])
    
    return candidates

if __name__ == "__main__":
    get_candidates("0906","L188")
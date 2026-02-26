from dataclasses import dataclass

@dataclass
class Nedvizhimost:
    vladeleс: str
    data:str
    stoimost:str
    
def create_object(str):
    start = str.find('"')
    end = str.find('"', start + 1)
    
    vladeleс = str[start + 1:end]
    
    ostatok = str[end + 1:].split()
    
    data = ostatok[0]
    
    stoimost = int(ostatok[1])
    
    return Nedvizhimost(vladeleс, data, stoimost)

def counter(s, ind1, ind2):
    c = 0
    if (s[ind1] == s[ind2]):
        for k in range(ind1+1, ind2):
            if s[k] == s[ind1+1]: 
                c+=1
        return c

def summ(str1):
    s = 0
    for i in range (len(str1)):
            if str1[i] != "-":
                 continue
            for j in range (i+1, len(str1)):
                if str1[j] 
    return s

str1 = input()
print(summ(str1))

str = input("Введите: ")
obj = create_object(str)
print("Владелец:", obj.vladeleс)
print("Дата:", obj.data)
print("Стоимость:", obj.stoimost)
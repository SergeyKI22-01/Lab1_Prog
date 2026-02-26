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
        for i in range(ind1+1, ind2):
            if s[ind1+1] == s[ind1+2]: 
                c+=1
        if c == ind2 - (ind1+1):
            return c
s = input()
print(counter(s,0, 4))

str = input("Введите: ")
obj = create_object(str)
print("Владелец:", obj.vladeleс)
print("Дата:", obj.data)
print("Стоимость:", obj.stoimost)
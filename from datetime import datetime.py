from datetime import datetime
import re

class RealEstate:
    
    def __init__(self, owner, registration_date, estimated_cost):
        
        self.owner = owner
        self.registration_date = registration_date
        self.estimated_cost = estimated_cost

    def __str__(self):
        return (f"Недвижимость:\n"  
                f"  Владелец: {self.owner}\n"  
                f"  Дата постановки на учет: {self.registration_date.strftime('%Y.%m.%d')}\n"  
                f"  Ориентировочная стоимость: {self.estimated_cost} руб.") 
    
    def __repr__(self):
        return (f"RealEstate(owner='{self.owner}', "
                f"registration_date={self.registration_date}, "  
                f"estimated_cost={self.estimated_cost})")  

def parse_real_estate(input_string):
   
    pattern = r'"([^"]+)"\s+(\d{4}\.\d{2}\.\d{2})\s+(\d+)'
    
    match = re.match(pattern, input_string.strip())
    
    
    if not match:
        raise ValueError("Неверный формат входной строки")
    
    owner = match.group(1)
    
    date_str = match.group(2) 
    
    cost_str = match.group(3) 
    
    registration_date = datetime.strptime(date_str, '%Y.%m.%d')
    
    estimated_cost = int(cost_str)
    
    return RealEstate(owner, registration_date, estimated_cost)

def main():
    
    print("Введите данные в формате: \"Владелец\" гггг.мм.дд стоимость")
    print("Или нажмите Enter для выхода\n")
    
    while True:
       
        user_input = input("Введите данные: ").strip()
        
        if not user_input:  
            print("Программа завершена.")
            break

        try:
            real_estate = parse_real_estate(user_input)
            print()
            print(real_estate)
            print()
            
      
        except ValueError as e:
            print("Проверьте формат ввода!\n")
            
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}\n")

if __name__ == "__main__":
    main()
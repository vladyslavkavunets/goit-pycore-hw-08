from collections import UserDict
from datetime import datetime, timedelta
import pickle 

class Field:
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return str(self.value)
    
class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)
        
class Phone(Field):
    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must contain 10 digits")
        super().__init__(value)
        
class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format: Use DD.MM.YYYY")
        
    def __str__(self):
        return self.value
    
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        
    def add_phone(self, phone):
        self.phones.append(Phone(phone))
        return f"Phone {phone} added to contact {self.name}"
    
    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return f"Phone {phone} removed from contact {self.name}"
        raise ValueError(f"Phone {phone} not found for contact {self.name}")
    
    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return f"Phone {old_phone} changed to {new_phone} for contact {self.name}"
        raise ValueError(f"Phone {old_phone} not found for contact {self.name}")
    
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
        return f"Birthday added to contact {self.name}"
    
    def show_birthday(self):
        if self.birthday:
            return f"Birthday of contact {self.name}: {self.birthday}"
        return f"Birthday for contact {self.name} is not set"
    
    def __str__(self):
        birthday_info = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact: {self.name.value}, phones: {': '.join(p.value for p in self.phones)}{birthday_info}"
        
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
        return f"Contact {record.name.value} added to address book"
    
    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return f"Contact {name} deleted from address book"
        raise KeyError(f"Contact {name} not found")
    
    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []
        
        for name, record in self.data.items():
            if record.birthday:
                birthday_date = record.birthday.date
                birthday_this_year = birthday_date.replace(year=today.year).date()
                
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                delta_days = (birthday_this_year - today).days
                
                if 0 <= delta_days < 7:
                    celebrate_date = birthday_this_year
                    if celebrate_date.weekday() >= 5:
                        days_to_add = 7 - celebrate_date.weekday()
                        celebrate_date = celebrate_date + timedelta(days=days_to_add)
                        
                    upcoming_birthdays.append({
                        "name": name,
                        "birthday": record.birthday.value,
                        "celebrate_date": celebrate_date.strftime("%d.%m.%Y"),
                    })

        return upcoming_birthdays
   
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)
        
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()   
 
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Input error: {e}"
        except KeyError as e:
            return f"Contact not found: {e}"
        except IndexError:
            return "Incomplete command. Type 'help' to see all available commands"
        except Exception as e:
            return f"Error: {e}"
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise ValueError("Please provide name and phone number")
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated"
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added"
        
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    if len(args) != 3:
        raise ValueError("Please provide name, ald phone and new phone")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        raise KeyError(f"Contact {name} not found")
    record.edit_phone(old_phone, new_phone)
    return "Phone updated"

@input_error
def show_phone(args, book):
    if len(args) != 1:
        raise ValueError("Please provide contact name")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError(f"Contact {name} not found")
    if not record.phones:
        return f"Contact {name} has no phones"
    return ", ".join(p.value for p in record.phones)

@input_error
def show_all(book):
    if not book.data:
        return "Address book is empty"
    result = []
    for record in book.data.values():
        result.append(str(record))
    return "\n".join(result)

@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise ValueError("Please provide name and birthday (DD.MM.YYYY)")
    name, birthday = args
    record = book.find(name)
    if record is None:
        raise KeyError(f"Contact {name} not found")
    return record.add_birthday(birthday)

@input_error
def show_birthday(args, book):
    if len(args) != 1:
        raise ValueError("Please provide contact name")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError(f"Contact {name} not found")
    return record.show_birthday()

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No birthday next week"
    
    result = ["Upcoming birthday next week:"]
    for birthday in upcoming_birthdays:
        result.append(f"{birthday['name']}: {birthday['birthday']} (celebrate on: {birthday['celebrate_date']})")
        
    return "\n".join(result)

def show_help():
    return (
        "Bot Commands:\n"
        "- add [name] [phone]: Add new contact or phone to existing contact\n"
        "- change [name] [old phone] [new phone]: Change contact's phone\n"
        "- phone [name]: Show contact's phone(s)\n"
        "- all: Show all contacts\n"
        "- add-birthday [name] [birthday]: Add birthday for contact (DD.MM.YYYY)\n"
        "- show-birthday [name]: Show contact's birthday\n"
        "- birthdays: Show upcoming birthdays for next week\n"
        "- hello: Get greeting from bot\n"
        "- help: Show this help\n"
        "- exit/close: Close the program"
    )
    
def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    print("Type 'hello' to start or 'help' to see all commands.")

    while True:
        user_input = input("Enter a command: ")

        if not user_input:
            continue

        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "help":
            print(show_help())
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command. Type 'help' to see all commands.")

if __name__ == "__main__":
    main()
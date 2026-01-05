from collections import UserDict
from functools import wraps
from datetime import datetime, date, timedelta

# created custom exceptions to not catch same ValueError for different classes
class InvalidPhoneError(Exception):
    pass

class InvalidBirthdayError(Exception):
    pass

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        # check if number is only digits and 10 length
        if len(value) == 10 and value.isdigit():
            self.value = value
        else: 
            raise InvalidPhoneError()
        
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise InvalidBirthdayError()

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    # method for adding Phone Objects
    def add_phone(self, phone):
          self.phones.append(Phone(phone))

    # method for removing Phone Objects
    def remove_phone(self, phone):
        p = self.find_phone(phone)
        if p:
            self.phones.remove(p)
    
    # method for changing Phone Objects
    def edit_phone(self, old, new):
        if self.find_phone(old):
            self.add_phone(new)
            self.remove_phone(old)
        else:
            raise ValueError("Phone not found")

    # method for finding Phone Objects
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
                
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday.value}"

class AddressBook(UserDict):

    # method for adding entries to a dictionary by key (name), whose value becomes a Record Object
    def add_record(self, record):
        self.data[record.name.value] = record

    # method for searching for a Record Object by name 
    def find(self, name):
        if name in self.data:
            return self.get(name)
        else:
            return None

    # method for finding all upcoming birthdays for next 7 days
    def get_upcoming_birthdays(self, days=7):
        self.upcoming_birthdays = []
        today = date.today()

        for record in self.data.values():
            birthday_this_year = record.birthday.value.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                

            if 0 <= (birthday_this_year - today).days <= days:
                if birthday_this_year.weekday() >= 5:
                    days_ahead = 0 - birthday_this_year.weekday()
                    if days_ahead <= 0:
                        days_ahead += 7
                        birthday_this_year = birthday_this_year + timedelta(days=days_ahead)


                congratulation_date_str = birthday_this_year.strftime("%d.%m.%Y")
                self.upcoming_birthdays.append({"name": record.name.value, "upcoming_birthday": congratulation_date_str})
        return self.upcoming_birthdays

        
    # method for removing records by its name     
    def delete(self, name):
        if name in self.data:
            self.data.pop(name)

    # magic method for returning a string with all dictionary entries
    def __str__(self):
        result = ""
        for record in self.data.values():
            phones_str = "; ".join(p.value for p in record.phones)
            result += f"Contact name: {record.name.value}, phones: {phones_str}\n"
        return result.strip()
    


banner = '''
  /$$$$$$   /$$$$$$   /$$$$$$  /$$$$$$  /$$$$$$  /$$$$$$$$ /$$$$$$  /$$   /$$ /$$$$$$$$       /$$$$$$$   /$$$$$$  /$$$$$$$$
 /$$__  $$ /$$__  $$ /$$__  $$|_  $$_/ /$$__  $$|__  $$__//$$__  $$| $$$ | $$|__  $$__/      | $$__  $$ /$$__  $$|__  $$__/
| $$  \ $$| $$  \__/| $$  \__/  | $$  | $$  \__/   | $$  | $$  \ $$| $$$$| $$   | $$         | $$  \ $$| $$  \ $$   | $$   
| $$$$$$$$|  $$$$$$ |  $$$$$$   | $$  |  $$$$$$    | $$  | $$$$$$$$| $$ $$ $$   | $$         | $$$$$$$ | $$  | $$   | $$   
| $$__  $$ \____  $$ \____  $$  | $$   \____  $$   | $$  | $$__  $$| $$  $$$$   | $$         | $$__  $$| $$  | $$   | $$   
| $$  | $$ /$$  \ $$ /$$  \ $$  | $$   /$$  \ $$   | $$  | $$  | $$| $$\  $$$   | $$         | $$  \ $$| $$  | $$   | $$   
| $$  | $$|  $$$$$$/|  $$$$$$/ /$$$$$$|  $$$$$$/   | $$  | $$  | $$| $$ \  $$   | $$         | $$$$$$$/|  $$$$$$/   | $$   
|__/  |__/ \______/  \______/ |______/ \______/    |__/  |__/  |__/|__/  \__/   |__/         |_______/  \______/    |__/                                                                                                                        
'''


def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone, please."
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Enter the argument for the command."
        except InvalidPhoneError:
            return "Phone must be 10 digits only."
        except InvalidBirthdayError:
            return "Invalid date format. Use DD.MM.YYYY"

    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

# func for adding/removing contacts
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

# func for showing phones by the name of the record
@input_error
def show_phone(args, book: AddressBook):
    record = book.find(args[0])
    return '; '.join([p.value for p in record.phones])

#func for showing all contacts with their phones    
@input_error
def show_all(args, book: AddressBook):
    output = []
    if not book:
        return "No contacts found."
    return str(book)

# func for adding birthdays to contacts
@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    if birthday:
        record.add_birthday(birthday)
    return "Birthday added."

# func for showing birthday for the contact
@input_error
def show_birthday(args, book):
    record = book.find(args[0])
    return record.birthday

# func for showing all birthdays upcoming in 7 days
@input_error
def birthdays(args, book):
    return book.get_upcoming_birthdays()




def main():
    book = AddressBook()

    print(banner)
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "change":
            print(add_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
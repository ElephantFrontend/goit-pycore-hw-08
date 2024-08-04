import copy
import pickle
from datetime import datetime, timedelta


class Field:
    """Базовий клас для полів запису."""
    def __init__(self, value):
        self.value = value


class Name(Field):
    """Клас для зберігання імені контакту. Обов'язкове поле."""
    def __init__(self, value):
        super().__init__(value)


class Phone(Field):
    """Клас для зберігання номера телефону. Має валідацію формату (10 цифр)."""
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Invalid phone number. Must be 10 digits.")
        super().__init__(value)

    @staticmethod
    def validate(value):
        return value.isdigit() and len(value) == 10


class Birthday(Field):
    """Клас для зберігання дня народження. Має валідацію формату (DD.MM.YYYY)."""
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    """Клас для зберігання інформації про контакт, включаючи ім'я, список телефонів і день народження."""
    def __init__(self, name, phones=None, birthday=None):
        self.name = Name(name)
        self.phones = [Phone(phone) for phone in phones] if phones else []
        self.birthday = Birthday(birthday) if birthday else None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                break

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)


class AddressBook:
    """Клас для зберігання та управління записами."""
    def __init__(self):
        self.records = {}

    def add_record(self, record):
        self.records[record.name.value] = record

    def remove_record(self, name):
        if name in self.records:
            del self.records[name]

    def find_record(self, name):
        return self.records.get(name)

    def list_records(self):
        return [record for record in self.records.values()]

    def get_upcoming_birthdays(self, days=7):
        today = datetime.now()
        upcoming_birthdays = []
        for record in self.records.values():
            if record.birthday:
                next_birthday = record.birthday.value.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)
                if 0 <= (next_birthday - today).days < days:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays


# Декоратор для обробки помилок
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, KeyError) as e:
            return f"Error: {str(e)}"
    return wrapper


# Функції-обробники команд
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find_record(name)
    if record:
        record.add_phone(phone)
        return f"Phone {phone} added to contact {name}."
    else:
        new_record = Record(name, phones=[phone])
        book.add_record(new_record)
        return f"Contact {name} with phone {phone} added."


@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find_record(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Phone {old_phone} changed to {new_phone} for contact {name}."
    return f"Contact {name} not found."


@input_error
def show_phones(args, book: AddressBook):
    name, *_ = args
    record = book.find_record(name)
    if record:
        phones = ", ".join([phone.value for phone in record.phones])
        return f"Contact {name}: Phones: {phones}"
    return f"Contact {name} not found."


@input_error
def show_all_contacts(args, book: AddressBook):
    all_records = book.list_records()
    result = []
    for rec in all_records:
        phones = ", ".join([phone.value for phone in rec.phones])
        birthday = rec.birthday.value.strftime('%d.%m.%Y') if rec.birthday else 'No birthday'
        result.append(f"Name: {rec.name.value}, Phones: {phones}, Birthday: {birthday}")
    return "\n".join(result)


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find_record(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday {birthday} added to contact {name}."
    return f"Contact {name} not found."


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find_record(name)
    if record and record.birthday:
        return f"Contact {name}: Birthday: {record.birthday.value.strftime('%d.%m.%Y')}"
    return f"Contact {name} not found or no birthday set."


@input_error
def birthdays(args, book: AddressBook):
    days = int(args[0]) if args else 7
    upcoming = book.get_upcoming_birthdays(days)
    if upcoming:
        result = []
        for rec in upcoming:
            result.append(f"{rec.name.value} - {rec.birthday.value.strftime('%d.%m.%Y')}")
        return "\n".join(result)
    return "No upcoming birthdays."


# Функції для серіалізації та десеріалізації
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено


# Основна функція main
def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = user_input.split()
        command = command.lower()

        if command in ["close", "exit"]:
            save_data(book)  # Зберегти дані перед виходом
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phones(args, book))

        elif command == "all":
            print(show_all_contacts(args, book))

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

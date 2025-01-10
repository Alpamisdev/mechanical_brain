# Kitapxana - class
# argument - kitaptin ati
# kitaplardi kore aliw kerek, kitap qosa aliw kerek, kitapti oshire aliw kerek

class Library():
    books = ['Vavilondagi eng boy odam', 'Rich dad and Poor dad']

    def __init__(self, book=None):
        self.book = book
    
    def add_book(self, title):
        self.books.append(title)
        print(f"{title} kitabi qosildi")

    def book_list(self):
        print(self.books)

    def remove_book(self, title):
        pass

kitapxana = Library('book')
kitapxana.add_book('Ajiniyaz')
kitapxana.book_list()
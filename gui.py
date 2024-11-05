
from PyQt5 import QtCore, QtGui, QtWidgets
from ir_backend import InformationRetrieval
import speech_recognition as sr

class IRSystemGUI(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setStyleSheet("background-color: #ffffff;")  # Light background

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Title Label
        self.title_label = QtWidgets.QLabel(self.centralwidget)
        self.title_label.setGeometry(QtCore.QRect(200, 20, 400, 60))
        font = QtGui.QFont()
        font.setFamily("Helvetica Neue")
        font.setPointSize(28)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setText("Mini IR")
        self.title_label.setStyleSheet("color: #333;")

        # Search Box
        self.search_input = QtWidgets.QLineEdit(self.centralwidget)
        self.search_input.setGeometry(QtCore.QRect(200, 100, 400, 50))
        self.search_input.setPlaceholderText("Enter search word here...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #007bff;
                border-radius: 25px;
                padding: 10px;
                font-size: 18px;
            }
        """)
        self.search_input.textChanged.connect(self.show_suggestions)  # Trigger auto-suggest
        
        # Suggestions List
        self.suggestions_list = QtWidgets.QListWidget(self.centralwidget)
        self.suggestions_list.setGeometry(QtCore.QRect(200, 150, 400, 120))
        self.suggestions_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #007bff;
                border-radius: 10px;
                font-size: 16px;
                background-color: white;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        self.suggestions_list.hide()
        self.suggestions_list.itemClicked.connect(self.select_suggestion)

        # Search Button
        self.search_button = QtWidgets.QPushButton(self.centralwidget)
        self.search_button.setGeometry(QtCore.QRect(620, 100, 120, 50))
        self.search_button.setText("Search")
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 25px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.search_button.clicked.connect(self.search_word)

        # Voice Search Button (Separate and smaller)
        self.voice_button = QtWidgets.QPushButton(self.centralwidget)
        self.voice_button.setGeometry(QtCore.QRect(470, 100, 50, 50))
        self.voice_button.setText("🎤")
        self.voice_button.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-radius: 25px;
            }
        """)
        self.voice_button.clicked.connect(self.voice_search)

        # Results Area
        self.results_area = QtWidgets.QTextEdit(self.centralwidget)
        self.results_area.setGeometry(QtCore.QRect(150, 220, 500, 300))
        self.results_area.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
                background-color: #f9f9f9;
            }
        """)
        self.results_area.setReadOnly(True)

        MainWindow.setCentralWidget(self.centralwidget)

        # Initialize Information Retrieval Backend
        self.ir_system = InformationRetrieval('./documents/')
        self.ir_system.index_documents()

    def show_suggestions(self):
        """Show auto-suggestions based on the current text in the search input."""
        query = self.search_input.text()
        if query:
            suggestions = self.ir_system.auto_suggest(query)
            self.suggestions_list.clear()
            self.suggestions_list.addItems(suggestions)
            self.suggestions_list.show()
        else:
            self.suggestions_list.hide()

    def select_suggestion(self, item):
        """Handle selection of a suggestion from the list."""
        self.search_input.setText(item.text())  # Set the selected suggestion in the search input
        self.suggestions_list.hide()  # Hide suggestions after selection
        self.search_word()  # Trigger search

    def search_word(self):
        """Perform the search based on the input and display the results."""
        query = self.search_input.text()
        results = self.ir_system.search(query)

        self.results_area.clear()  # Clear previous results
        if results:
            for doc, count, snippet in results:
                self.results_area.append(f"Document: {doc}\nOccurrences: {count}\nSnippet: {snippet}\n")
        else:
            self.results_area.setPlainText("No results found.")

    def voice_search(self):
        """Perform voice search."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
            try:
                query = recognizer.recognize_google(audio)
                print(f"You said: {query}")
                self.search_input.setText(query)  # Set the recognized text in the search input
                self.search_word()  # Trigger search with the recognized text
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")

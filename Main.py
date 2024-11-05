import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from gui import IRSystemGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    
    # Create instance of the GUI and set it up
    ui = IRSystemGUI()
    ui.setupUi(main_window)
    
    main_window.show()
    sys.exit(app.exec_())
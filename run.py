try:
    from PyQt4.QtGui import QApplication
except ImportError:
    from PyQt5.QtWidgets import QApplication

import sys

import todomvc


def main():
    app = QApplication(sys.argv)

    model = todomvc.TodoListModel()
    view = todomvc.MainView()
    view.show()

    presenter = todomvc.MainPresenter(view, model)  # noqa

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

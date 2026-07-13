from __future__ import annotations

from database.initializer import initialize_database
from views.login_view import LoginView


def main() -> None:
    initialize_database(seed=True)
    LoginView().run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye.")

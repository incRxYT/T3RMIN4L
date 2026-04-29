"""main.py — T3RMIN4L entry point."""

import sys

def main():
    try:
        import customtkinter  # noqa: F401
    except ImportError:
        print("customtkinter is not installed.\nRun:  pip install -r requirements.txt")
        sys.exit(1)

    from ui import T3RMINAL
    app = T3RMINAL()
    app.mainloop()


if __name__ == "__main__":
    main()

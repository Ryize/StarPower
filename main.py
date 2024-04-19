from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    from controller import app
    from errors import app

    app.run(debug=False)

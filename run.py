from app import app
import random


#run.py
if __name__ == '__main__':
    app.secret_key = str(random.randint(100000,999999))
    app.run(host="0.0.0.0",port=5000)
    app.run(debug=True,use_reloader=False)

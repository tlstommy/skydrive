from app import app
import random


#run.py
if __name__ == '__main__':
    app.secret_key = str(random.randint(100000,999999))
    app.run(host="0.0.0.0",port=80)
    app.run(debug=False,use_reloader=False)

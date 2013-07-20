flask-example
=============

Example Flask application.

# You need
    
    Mongodb running.
    E-mail server running.

# Running email server using python

    sudo python -m smtpd -n -c DebuggingServer localhost:25

# Install and run project
    
    git clone https://github.com/allisson/flask-example.git
    cd flask-example
    pip install -r requirements.txt
    python run.py # run on 127.0.0.1:5000

# How run the tests?
    
    nosetests

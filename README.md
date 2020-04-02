# CSC394
### Software Projects

### To Run This

#### For Mac/Linux
1. Check if you have Python 3
```
python3
```
If the shell opens, you have it. Make sure the version is 3.6+

If you don't have it,

#### For Mac
visit: https://docs.python-guide.org/starting/install3/osx/ and install

#### For Linux (Debian or Ubuntu)
```
sudo apt-get update
sudo apt-get install python3.8
```

2. Install and Activate Virtual Environment
* Install
```
python3 -m venv venv
```
* Activate
```
source venv/bin/activate
```
* Install the Dependencies into the Virtual Environment
```
pip3 install -r requirements.txt
```

3. Run Main Program
```
python main.py
```

* HTML is in the templates folder
* CSS/JS is in static folder
* main.py contains endpoints (views) for the website



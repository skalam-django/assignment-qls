# assignment-qls
#Instruction to run this application

# Download and extract the project

# Create virtual environment outside of 'qls' project folder
vitualenv -p python3 env

# Activate the environment
source env/bin/activate

# Install packages
pip install -r requirements.txt

# To run the application in developement sever, export the following keys into environment (Skip if running the application in Local):

export qls_DEV=True
export qls_PRINT=False
export qls_SECRET_KEY='g%5c%3_wib%m&g2k+muja#1907l)(ko051r^r4^vbvqb6qmnem'
export qls_SSL=False
export qls_NAME=<db-name>
export qls_USER=<db-user>
export qls_PASSWORD=<db-password>
export qls_HOST=<db-host>
export qls_PORT=<db-port>

# To run the application in production sever, export the following keys into environment (Skip if running the application in Local):

export qls_PROD=True
export qls_TRACEBACK_OFF=False
export qls_SECRET_KEY='g%5c%3_wib%m&g2k+muja#1907l)(ko051r^r4^vbvqb6qmnem'
export qls_SSL=True
export qls_NAME=<db-name>
export qls_USER=<db-user>
export qls_PASSWORD=<db-password>
export qls_HOST=<db-host>
export qls_PORT=<db-port>


# Change directory into 'qls'
cd qls

# Run the server
python manage.py runserver



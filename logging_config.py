import logging

# Create and configure logger
logging.basicConfig(
    filename="logfile.log",
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Creating an object
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)
#print(logger)

###############################################################################
#Basic config file for Fossilizer
###############################################################################

#where can we find the fossilizer binary
FOSSIL_BIN = '/usr/local/bin/fossil'

#Where are the fossil files to be created on the local file system
FOSSIL_PATH = '/usr/local/fossils'

FOSSIL_TMP = '/tmp'

#FOSSIL_CGI = """#!%s
#directory: %s
#notfound: %s""" % (FOSSIL_BIN, FOSSIL_PATH, URL('index'))

FOSSIL_INDEX = 'index.cgi'



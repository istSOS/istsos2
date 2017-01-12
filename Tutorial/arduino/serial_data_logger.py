# -*- coding: utf-8 -*-
import serial
import datetime
from tzlocal import get_localzone
import csv
import os

import json
from collections import OrderedDict

import argparse


def loop(config, s_port, baud):
    """
        Loop read data and write csv file in csv2istsos format
    """

	# enable serial comunication
    s = serial.Serial(s_port, baud)
    header = [
		'urn:ogc:def:parameter:x-istsos:1.0:time:iso8601'
	]

    agg = __read_prop_agg(config['propertiesAggregation'], header)

    local = get_localzone()

	# tmpVal
    last_file = datetime.datetime.now(local)#.replace(tzinfo=timezone(time.tzname[0]))

    buffer_tmp = []
    buffer_result = []

    print "start loop"
	# clear buffer (avoid bad read)
    s.flushInput()
    while True:
		# read message
		message = s.readline()
		data = message.split(',')

		tmp_row = []
		now = datetime.datetime.now(local)#.replace(tzinfo=timezone(time.tzname[0]))
		tmp_row.append(now.strftime("%Y-%m-%dT%H:%M:%S%z"))


		try:
			for elem in data:
				tmp_row.append(float(elem))
		except Exception as e:
			print " Exception: ", e 
			continue
		print tmp_row


		buffer_tmp.append(tmp_row)

		if (now - last_file) > datetime.timedelta(seconds=config['dataResolution']):

			tmp = __aggregate_data(buffer_tmp, agg)

			buffer_result.append(tmp)
			buffer_tmp = []

			if len(buffer_result) >= config['measuresPerFile']:
				print "create new observation file"
				# filename with
				file_name = "result/" + config['procedure'] + "_" + now.utcnow().strftime("%Y%m%d%H%M%S%f")[:-4] + ".dat"

				f = open(file_name,"w")

				c = csv.writer(f)
				c.writerow(header)
				for row in buffer_result:
					c.writerow(row)
				f.close()
				buffer_result = []

			last_file = now

def __read_prop_agg(propagg, header):
    """
        get aggregate function and observed properties
    """
    agg = []
    for key in propagg.keys():
        header.append(key)
        agg.append(propagg[key])

    return agg

def __read_config(path):
    """
        read config file
    """

    string = file(path, 'r').read().decode('UTF-8')
    # read json mantaining keys order
    config = json.loads(string, object_pairs_hook=OrderedDict)

    return config


def __aggregate_data(temp, agg):
    """
        aggregate data according to aggregate function
    """
    length = len(temp)

    result = []
    result.append(temp[-1][0])

    mean = []
    for i in range(1,len(temp[0])):
    	op = agg[i - 1]
    	if op == "MIN":
    		mean.append(10000)
    	elif op == "MAX":
    		mean.append(-100000)
    	else:
    		mean.append(0)

    for elem in temp:
		for i in range(1, len(elem)):
			op = agg[i -1]
			if op == "AVG":
				mean[i - 1] +=  elem[i]
			elif op == "MAX":
				if elem[i] > mean[i -1]:
					mean[i - 1] = elem[i]
			else:
				if elem[i] < mean[i -1]:
					mean[i - 1] = elem[i]

    for i in range(0, len(mean)):
		elem = mean[i]
		op = agg[i]

		if op == "AVG":
			result.append("%.2f" % (elem/ length))
		else:
			result.append("%.2f" % (elem))

    return result


def execute(args):
	"""
		read args params
	"""
	try:
		s_port = args['s']
		baud = int(args['b'])
		path = args['c']

		config = __read_config(path)

		# start loop
		loop(config, s_port, baud)

	except Exception as e:
		print "Error: ", e
		return


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Load data read from a serial port inside csv file.")

	parser.add_argument('-s','--serial',
				action='store',
				required=True,
				dest='s',
				default='/dev/ttyACM0',
				help='Serial port to listen'
			)

	parser.add_argument('-b','--baudrate',
				action='store',
				dest='b',
				default=9600,
				help='serial port baudrate'
			)

	parser.add_argument('-c','--config',
				action='store',
				required=True,
				dest='c',
				default='config.json',
				help='path to configuration file'
			)

	args = parser.parse_args()

	execute(args.__dict__)

from contextlib import suppress
from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException,StaleElementReferenceException,NoSuchElementException,WebDriverException,TimeoutException,NoAlertPresentException
import sys
import time
import os
import ast

global sys,ast,os,suppress
global drivers,tabs,curr_driver,curr_tab,output_fields_list,input_fields_list,input_vals,path_to_button,curr_vals,output_xpaths


path_to_button = "/html/body/center/table/tbody/tr[2]/td[1]/form/table/tbody/tr[5]/td[17]/input"

def get_inputs(json_file_name):
	with open(json_file_name) as file:
		json_inputs = ast.literal_eval(file.read())
	result = {}
	for p,vals in json_inputs.items():
		import numpy
		if "vals" in vals and "vals" != None:
			if isinstance(vals["vals"],list):
				result[p] = [str(v) for v in vals["vals"]]
			else:
				result[p] = [str(vals["vals"])]
		else:
		#"max" in vals and (isinstance(vals["max"],int) or isinstance(vals["max"],float)):
			val_is_int = True
			if "step" in vals and (isinstance(vals["step"],int) or isinstance(vals["step"],float)):
				num_points = int((vals["max"]-vals["min"])/vals["step"])
				if isinstance(vals["step"],float):
					val_is_int = False
			elif "num vals" in vals and isinstance(vals["num vals"], int):
				num_points = vals["num vals"]
			else:
				num_points = 1
			if "max" not in vals or vals["max"] == None:
				if "min" not in vals or vals["min"] == None:
					continue
				else:
					vals["max"] = vals["min"]
			if "min" not in vals or vals["min"] == None:
				vals["min"] = vals["max"]
			if isinstance(vals["min"],float) or isinstance(vals["max"],float):
				val_is_int = False
			temp = numpy.linspace(vals["min"],vals["max"],num_points)
			if val_is_int:
				result[p] = (str(int(item)) for item in temp)
			else:
				result[p] = (str(item) for item in temp)
	global input_fields_list
	input_fields_list = list(result.keys())
	inefficient = tuple(list(result[field_name]) for field_name in input_fields_list)
	from itertools import product
	actual_result = product(*inefficient)
	return actual_result



input_vals = get_inputs("inputs.txt")
#input_fields_list = list(input_vals.keys())
with open("wanted outputs.txt") as f:
	output_fields_list = f.read().split("\n")
with open("all_output_xpaths.txt","r") as f:
	output_xpaths = [v for k,v in ast.literal_eval(f.read()).items()
							if k in output_fields_list]
for i in output_fields_list:
	print("\t"+i)

drivers = []
tabs = []

curr_driver = 0
curr_tab = 0
curr_vals = {}


def set_up_drivers(n):
	for _ in range(n):
		driver = webdriver.Chrome(os.path.abspath(os.path.dirname(sys.argv[0])) + "/chromedriver")
		driver.implicitly_wait(10)
		drivers.append(driver)

def log_in():
	driver = drivers[curr_driver]
	driver.get("https://www.ecalc.ch/calcmember/login.php?https://www.ecalc.ch/")
	if driver.current_url == "https://www.ecalc.ch/":
		return
	log_in_fields = driver.find_element_by_id("innerbox").find_elements_by_tag_name("input")[0:2]
	log_in_fields[0].send_keys("designbuildfly@cornell.edu")
	log_in_fields[1].send_keys("TakeFlight")
	driver.find_element_by_id("myButton").click()
	for _ in range(10):
		with suppress(Exception):
			driver.switch_to_alert().accept()
			break
		time.sleep(0.1)

def set_up_csv(filename):
	with open(filename,"r+") as file:
		file.write(",".join(input_fields_list) + ",")
		file.write(",".join(output_fields_list))
		file.write("\n")

def increment_driver_and_tab():
	global curr_tab
	curr_tab = (curr_tab+1) % len(drivers[curr_driver].window_handles)
	if curr_tab == 0:
		driver = (curr_driver+1) % len(drivers)

def get_and_save_eCalc_output(url,input_vals_str):
	increment_driver_and_tab()
	driver = drivers[curr_driver]
	driver.switch_to.window(driver.window_handles[curr_tab])
	driver.get(url)
	try:
		with suppress(Exception):
			driver.switch_to_alert().accept()
		driver.find_element_by_xpath(path_to_button).click()
	except Exception:
		log_in()
		driver.get(url)
		with suppress(Exception):
			driver.switch_to_alert().accept()
		driver.find_element_by_xpath(path_to_button).click()
	outputs = get_output_vals()
	output_file.write(input_vals_str + "," + ",".join(outputs) +"\n")

def get_output_vals():
	output_vals = []
	driver = drivers[curr_driver]
	for xpath in output_xpaths:
		e = driver.find_element_by_xpath(xpath)
		for i in range(100):
			if e.text != '-':
				output_vals.append(e.text)
				break
			time.sleep(0.01)
	return output_vals

def combinatorically_iterate_over_dct():
	url_extension = ""
	for vals in input_vals:
		url_extension = "&".join(input_fields_list[i] + "=" + v for i,v in enumerate(vals))
		input_vals_str = ",".join(vals)
		get_and_save_eCalc_output("https://www.ecalc.ch/motorcalc.php?lang=en&" + url_extension,input_vals_str)

"""
def combinatorically_iterate_over_dct(fields_list_index=0,url_extension="",input_vals_str=""):
	url_extension = url_extension+input_fields_list[fields_list_index]+"="
	for val in input_vals[input_fields_list[fields_list_index]]:
		if fields_list_index == len(input_fields_list)-1:
			get_and_save_eCalc_output("https://www.ecalc.ch/motorcalc.php?lang=en&"
						+ url_extension+val+"&",input_vals_str+val)
		else:
			combinatorically_iterate_over_dct(fields_list_index+1,
						url_extension+val+"&",input_vals_str+val+",")
"""

def get_axis_input(query):
	def show():
		print("inputs:")
		str = ""
		for i,d in enumerate(input_fields_list):
			str += "\t\t" + d
			if i % 3 == 0:
				print(str)
				str = ""
		if str != "":
			print(str)
		print("outputs:")
		str = ""
		for i,d in enumerate(output_fields_list):
			str += "\t" + d
			if i % 3 == 0:
				print(str)
				str = ""
		if str != "":
			print(str)

	total = ""
	keep_accepting = False
	while True:
		curr_query = query + (" (\"done\" to finish): " if keep_accepting else ": ")
		x = input(curr_query).split(",")
		if x[0] == "show":
			show()
		elif x[0] in ["done","exit"]:
			break
		elif x[0] in ["list","multiple"]:
			keep_accepting = True
		else:
			temp = []
			for i in x:
				if i not in input_fields_list and i not in output_fields_list:
					print("\n\[\033[1m\]" + i + "\[\033[m\] is not a valid field.\n")
				else:
					temp.append(i)
			if len(temp) > 1:
				keep_accepting = True
			if len(temp) > 0:
				if isinstance(total,list):
					total.extend(temp)
				else:
					total = temp
				if len(x) == 1 and not keep_accepting:
					break
	if isinstance(total,list):
		return total
	else:
		return [total]

def method():
	global output_file
	output_file = open("out.csv","a+",buffering=15000)
	output_file.truncate(0)
	set_up_csv("out.csv")
	#driver = webdriver.Chrome(os.path.abspath(os.path.dirname(sys.argv[0])) + "/chromedriver")
	#driver.implicitly_wait(10)
	set_up_drivers(1)
	combinatorically_iterate_over_dct()
	output_file.close()
	for d in drivers:
		d.close()
	from matplotlib import pyplot as plt
	import pandas as pd
	data = pd.read_csv("out.csv")
	while True:
		x = get_axis_input(query="x-axis, comma-separated if multiple")
		if x == "":
			break
		y = get_axis_input(query="y-axis, comma-separated if multiple")
		if y == "":
			break
		plt.scatter(data[x],data[y])
		plt.show()
method()

import queue
import logging
import threading
import csv
import os
import time
from scrape_url_employee_count import scrape_company_info
file_process= queue.Queue()
ip_data = []
op_data = []
op_header = ["company_name",]

def getCompanyInfo():
    try:
        while True:
            if not file_process.empty():
                file_name = file_process.get()
                if not os.path.exists("output"):
                    os.makedirs("output")
                try:
                    output_file_name = "output/out_"+file_name.split("/")[1]
                    with open(file_name,'r')as file:
                        filecontent=csv.reader(file)
                        for i,row in enumerate(filecontent):
                            if i == 0:
                                op_header = row
                            else:
                                ip_data.append(row)
                    print(op_header, ip_data)
                    op_header.append("company_url")
                    op_header.append("employee_count")
                    for data in ip_data:
                        print(data,data[0])
                        company_url, email_count = scrape_company_info(data[0]) # assuming company_name is the first one
                        data.append(company_url)
                        data.append(email_count)
                        op_data.append(data)
                    with open(output_file_name,"w") as opfile:
                        writer = csv.writer(opfile)
                        writer.writerow(op_header)
                        for data in op_data:
                            writer.writerow(data)

                                # print(row)
                                # if i == 0:
                                # else:
                    os.remove(file_name)

                except Exception as e:
                    logging.exception(f"error occured while processing file error {e}")

            time.sleep(10)

    except Exception as e:
        logging.exception(f"error occured while processing file error {e}")
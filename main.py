import os
import csv
import time
from datetime import datetime, timedelta
import argparse

import comics #https://github.com/irahorecka/comics
from comics.exceptions import InvalidDateError
from comics.exceptions import InvalidEndpointError

#adds/updates record of comic in database            
def addDownloadDBRecord(comic_Obj): 
    with open("db.csv","r") as f:
        reader=csv.reader(f)
        shitList=[]
        flag=False
        for i in reader:
            if i == []:
                continue
            elif i[0]==comic_Obj.endpoint:
                shitList.append([i[0],datetime.strftime(datetime.now(),"%m/%d/%Y")])
                flag=True
            else:
                shitList.append(i)
    if flag==False:
        shitList.append([str(comic_Obj.endpoint),str(datetime.strftime(datetime.now(),"%m/%d/%Y"))])             
    with open("db.csv","w") as f:
        writer=csv.writer(f)
        writer.writerows(shitList)

#actually downloads all of the comics
def dlComicSeries(comic_Obj,dl_Start_date,path):
    dl_Start_date=dl_Start_date.split("-")
    dl_Start_date=dl_Start_date[1]+"/"+dl_Start_date[2]+"/"+dl_Start_date[0]
    while True:
        #check and make sure we're not going past the current date
        curdate=datetime.now()
        curdate=datetime.strftime(curdate,"%m/%d/%Y")
        temp=str(dl_Start_date).split(" ")
        if curdate==temp[0]:
            break

        try:
            date=dl_Start_date.split("/")
            fileName=f"{path}\\{comic_Obj.endpoint} {date[2]}-{date[0]}-{date[1]}.gif"
            ch=comics.search(comic_Obj.endpoint).date(dl_Start_date)
            ch.download(fileName)
            print("DOWNLOADED:  "+fileName)
        except InvalidDateError:
            print("NO COMIC FOR THIS DATE: "+dl_Start_date)
        
        #update the date to the next day
        datetime_object=datetime.strptime(str(dl_Start_date),"%m/%d/%Y")
        datetime_object=datetime_object+timedelta(days=1)
        dl_Start_date=datetime.strftime(datetime_object,"%m/%d/%Y")
        
        time.sleep(int(args.timer)) 

    print("DOWNLOAD HAS FINISHED WOO!")

#makes the folder for the comic being downloaded
def makeDirectory(comic_Obj):
    newpath=".\\"+str(comic_Obj.endpoint)
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    return newpath

#checks DB file to see if the comic already exists in the db. If it doesn't we'll add it after downloading everything so far
def checkDownloadStatus(comic_Obj):
    with open("db.csv","r") as f:
        reader=csv.reader(f)
        for row in reader:
            if row[0]==comic_Obj.endpoint:
                return row[1]
    return comic_Obj.start_date

#gets the comic object for the comic series being downloaded
def getComicObj(comic_name):
    try:
        comicObj=comics.search(comic_name)
        return comicObj
    
    except InvalidEndpointError:
        return "Error"

#Lists all of the comics available (called from LS)
def listComics():
    x=comics.directory.listall()
    for i in x:
        print(i)

args=None #global arg variable for passing in delta between downloads

#main UI. Calls everything else
def main():

    #terminal argument parser
    parser=argparse.ArgumentParser(description="I heard you like to read comic books")
    parser.add_argument('timer',type=int, help='set the amount of time to sleep between file downloads.')
    global args
    args=parser.parse_args()
    
    #UI Code for main menu
    while True: 
        print("____________________________")
        print("Welcome to ComicScraper V0.2")
        print("____________________________")
        print("Select from the following options:")
        print("LS - lists all available web comics")
        print("DL + _ + name of the comic you want - Downloads the comic you selected")
        print("     for example DL_garfield will download garfield")
        print("Exit - exits the programme")
        print("____________________________")

        #main logic from menu selection
        value=input("Selection: ")
        if(value=="LS"):
            listComics()
        temp=value.split("_")
        if(temp[0]=="DL"):
            comicObj=getComicObj(temp[1])
            if(comicObj=="Error"):
                print("The comic you tried to download does not exist or an error occurred.")
            else:
                dlStartDate=checkDownloadStatus(comicObj)
                path=makeDirectory(comicObj)
                dlComicSeries(comicObj,dlStartDate,path)
                addDownloadDBRecord(comicObj)
        if(value=="Exit"):
            print("Bye bye")
            break


if __name__=="__main__":
    main()
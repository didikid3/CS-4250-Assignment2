#-------------------------------------------------------------------------
# AUTHOR: your name
# FILENAME: title of the source file
# SPECIFICATION: description of the program
# FOR: CS 4250- Assignment #2
# TIME SPENT: how long it took you to complete the assignment
#-----------------------------------------------------------*/

#IMPORTANT NOTE: DO NOT USE ANY ADVANCED PYTHON LIBRARY TO COMPLETE THIS CODE SUCH AS numpy OR pandas. You have to work here only with
# standard arrays

#importing some Python libraries
from pymongo import MongoClient
import datetime

def connectDataBase():

    # Create a database connection object using pymongo
    DB_NAME= "a2"
    DB_HOST= "localhost"
    DB_PORT= 27017

    try:
        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]
        return db
    
    except:
        print("Database not connected succesfully.")
def createDocument(col, docId, docText, docTitle, docDate, docCat):
    # create a dictionary to count how many times each term appears in the document.
    # Use space " " as the delimiter character for terms and remember to lowercase them.
    def removePunc(text):
        res_string = ""
        for letter in text:
            if letter not in __import__('string').punctuation:
                res_string += letter
        return res_string
    text_noPunc = removePunc(docText)
    
    def identify_terms(text):
        return text.split()
    text_terms = identify_terms(text_noPunc)

    # create a list of dictionaries to include term objects.
    terms = []
    for term in text_terms:
        term_dict = {}
        term_dict["Term"] = term
        term_dict["count"] = text_noPunc.count(term)

        terms.append(term_dict)

    #Producing a final document as a dictionary including all the required document fields
    charSize = len(text_noPunc) - text_noPunc.count(' ')
    document = {
        "_id" : docId,
        "Title" : docTitle,
        "Text" : docText,
        "Category" : docCat,
        "num_chars" : charSize,
        "Date" : datetime.datetime.strptime(docDate, "%m/%d/%Y %H:%M:%S"),
        "Terms" : terms
    }

    # Insert the document
    col.insert_one(document)

def deleteDocument(col, docId):
    # Delete the document from the database
    col.delete_one({"_id": id})

def updateDocument(col, docId, docText, docTitle, docDate, docCat):
    pass

    # Delete the document
    # --> add your Python code here

    # Create the document with the same id
    # --> add your Python code here

def getIndex(col):
    pass

    # Query the database to return the documents where each term occurs with their corresponding count. Output example:
    # {'baseball':'Exercise:1','summer':'Exercise:1,California:1,Arizona:1','months':'Exercise:1,Discovery:3'}
    # ...
    # --> add your Python code here


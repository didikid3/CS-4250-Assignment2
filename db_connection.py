#-------------------------------------------------------------------------
# AUTHOR: Brandon Chao
# FILENAME: db_connection
# SPECIFICATION: Reverse Index Database
# FOR: CS 4250- Assignment #2
# TIME SPENT: 3 hrs
#-----------------------------------------------------------*/

#IMPORTANT NOTE: DO NOT USE ANY ADVANCED PYTHON LIBRARY TO COMPLETE THIS CODE SUCH AS numpy OR pandas. You have to work here only with
# standard arrays

import psycopg2
from psycopg2.extras import RealDictCursor

def connectDataBase():

    # Create a database connection object using psycopg2
    # --> add your Python code here

    DB_NAME = "websearch"
    DB_USER = "postgres"
    DB_PASS = "123"
    DB_HOST = "localhost"
    DB_PORT = "5432"

    try:
        conn = psycopg2.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST,
                                port=DB_PORT,
                                cursor_factory=RealDictCursor)
        return conn
    except:
        print("Database not connected successfully")
        
def createCategory(cur, catId, catName):

    sql = "INSERT INTO category (id, name) VALUES (%s, %s)"

    recset = [catId, catName]
    cur.execute(sql, recset)


def createDocument(cur, docId, docText, docTitle, docDate, docCat):

    # 1 Get the category id based on the informed category name
    category_sql = "SELECT id FROM category WHERE name=%(idcat)s"
    cur.execute(category_sql, {'idcat': docCat})
    recset = cur.fetchall()

    id = recset[0]['id']
    

    # 2 Insert the document in the database. For num_chars, discard the spaces and punctuation marks.
    def removePunc(text):
        res_string = ""
        for letter in text:
            if letter not in __import__('string').punctuation:
                res_string += letter
        return res_string
    
    text_noPunc = removePunc(docText)
    charSize = len(text_noPunc) - text_noPunc.count(' ')

    document_sql = "INSERT INTO document(docid, id, title, text, numchar, date) VALUES(%s,%s,%s,%s,%s,%s)"

    recset = [docId, id, docTitle, docText, charSize, docDate]
    cur.execute(document_sql, recset)

    # 3 Update the potential new terms.
    # 3.1 Find all terms that belong to the document. Use space " " as the delimiter character for terms and Remember to lowercase terms and remove punctuation marks.
    # 3.2 For each term identified, check if the term already exists in the database
    # 3.3 In case the term does not exist, insert it into the database
    def identify_terms(text):
        return text.split()
    text_terms = identify_terms(text_noPunc)

    search_term_sql = "SELECT * FROM terms WHERE term=%(term)s"
    insert_term_sql = "INSERT INTO terms(term, numchar) VALUES(%s,%s)"
    for term in text_terms:
        cur.execute(search_term_sql, {'term': term})
        recset = cur.fetchall()

        #If term is new, generate new row in Terms Table
        if len(recset) < 1:
            vals = [term, len(term)]
            cur.execute(insert_term_sql, vals)

    # 4 Update the index
    # 4.1 Find all terms that belong to the document
    # 4.2 Create a data structure the stores how many times (count) each term appears in the document
    # 4.3 Insert the term and its corresponding count into the database
    # --> add your Python code here
    termDoc = {}
    for term in text_terms:
        termDoc[term] = text_noPunc.count(term)

    insert_termdoc_sql = "INSERT INTO termdoc(term, docid, count) VALUES(%s,%s,%s)"
    for term, count in termDoc.items():
        vals = [term, docId, count]
        cur.execute(insert_termdoc_sql, vals)

def deleteDocument(cur, docId):

    # 1 Query the index based on the document to identify terms
    # 1.1 For each term identified, delete its occurrences in the index for that document
    # 1.2 Check if there are no more occurrences of the term in another document. If this happens, delete the term from the database.
    select_docterm_sql = "SELECT term FROM termdoc WHERE docid=%(docId)s"
    cur.execute(select_docterm_sql, {'docId': docId})
    recset = cur.fetchall()

    terms = []
    for term in recset:
        terms.append(term['term'])
    print(terms)

    # Remove Document From TermDoc Tables
    delete_docterm_sql = "DELETE FROM termdoc WHERE docid=%(docId)s"
    vals = {'docId':docId}
    cur.execute(delete_docterm_sql, vals)
    
    # Check if Term Exists in TermDoc
    select_term_docterm_sql = "SELECT * FROM termdoc WHERE term=%(term)s"
    delete_term_sql = "DELETE FROM terms WHERE term=%(term)s"
    for term in terms:
        cur.execute(select_term_docterm_sql, {'term':term})
        res = cur.fetchall()

        # If term no longer in use, remove term
        if len(res) < 1:
            cur.execute(delete_term_sql, {'term':term})


    # 2 Delete the document from the database
    delete_document_sql = "DELETE FROM document WHERE docid=%(docId)s"
    vals = {'docId':docId}
    cur.execute(delete_document_sql, vals)

def updateDocument(cur, docId, docText, docTitle, docDate, docCat):

    # 1 Delete the document
    deleteDocument(cur, docId)

    # 2 Create the document with the same id
    createDocument(cur, docId, docText, docTitle, docDate, docCat)

def getIndex(cur):

    # Query the database to return the documents where each term occurs with their corresponding count. Output example:
    # {'baseball':'Exercise:1','summer':'Exercise:1,California:1,Arizona:1','months':'Exercise:1,Discovery:3'}
    # ...
    select_termdoc_sql = "SELECT * FROM termdoc"
    select_document_Sql = "SELECT title FROM document WHERE docid=%(docid)s"
    cur.execute(select_termdoc_sql)
    res = cur.fetchall()

    terms = {}
    for row in res:
        term = row['term']
        docId = row['docid']
        count = row['count']

        cur.execute(select_document_Sql, {'docid':docId})
        documentData = cur.fetchall()
        title = documentData[0]['title']
            


        entry = title + ":" + str(count)

        curList = terms[term] if term in terms else []
        terms[term] = curList + [entry]
    
    for term, lstDocs in terms.items():
        terms[term] = ",".join(lstDocs)

    return terms
        
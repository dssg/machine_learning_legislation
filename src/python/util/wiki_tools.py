import MySQLdb

db = MySQLdb.connect(host="sunlight.c5faqozfo86k.us-west-2.rds.amazonaws.com",user="sunlight", passwd="govtrack", db="wikipedia")

def get_page_category(page_name):
    """
    given a Wikipedia page name, return a list of its categories
    """
    cur = db.cursor()
    cur.execute("""SELECT cl_to FROM categorylinks cl
                JOIN (SELECT * FROM page where page_title='%s') p
                ON cl.cl_from = p.page_id""" % page_name)
    categories = [result[0] for result in cur.fetchall()]
    return categories


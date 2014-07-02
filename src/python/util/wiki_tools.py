import MySQLdb

db = MySQLdb.connect(host="sunlight.c5faqozfo86k.us-west-2.rds.amazonaws.com",user="sunlight", passwd="govtrack", db="wikipedia")

def get_category_hierarchy(page_name, depth=1):
    """
    given a Wikipedia page name, return a list of its categories
    at the given depth
    """
    results = []
    results.append(get_categories(page_name))
    for i in range(1,depth):
        categories = []
        for category in results[i-1]:
            parent_categories = get_categories(category, True)
            categories = categories + parent_categories
        results.append(categories)

    return results


def get_categories(page_name, is_category=False):
    """
    given a Wikipedia page name, return a list of its categories
    """
    cur = db.cursor()
    namespace = 0
    if is_category:
        namespace = 14
    cur.execute("""SELECT cl_to FROM categorylinks cl
                JOIN page p ON cl.cl_from = p.page_id
                WHERE p.page_title="%s" AND page_namespace=%s;
            """ % (page_name, namespace))
    categories = [result[0] for result in cur.fetchall()]
    return categories

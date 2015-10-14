__author__ = 'Kaiyuan_Wang'

def generate_suggestions(keywords):
    return ' '.join(reduce(lambda x,y: x + y, [get_all_substring(keyword) for keyword in keywords.split()]))

def get_all_substring(keyword):
    return reduce(lambda x,y: x + y, [[keyword[i:j] for j in range(i + 1,len(keyword) + 1)] for i in range(0,len(keyword))])
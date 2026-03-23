import json 

def get_data_fromtxt(path : str):
    """ 
        getting data from txt file \n
        path : đường dẫn của file source. 
    """

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


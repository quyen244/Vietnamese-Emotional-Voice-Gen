import json 

def get_data_fromtxt(path : str):
    """ 
        getting data from txt file
    
    """

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


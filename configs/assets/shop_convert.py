import sys
import os

PATH = os.path.realpath(__file__)
DIR = os.path.dirname(PATH)

project_path = os.path.join(DIR,'../../')
sys.path.append(project_path)


from configs import item_price,item_common

def generate_shop_items():
    shop_item_dict = {}
    config_item_price = item_price.find()
    for item in config_item_price:
        store_ids = item.store_id
        item_id = item.item_id
        config_item_common = item_common.get(pk=item.item_iid)
        quality = config_item_common.item_quality
        for store_id in str(store_ids).split(','):
            store_id = int(store_id)
            if store_id not in shop_item_dict:
                shop_item_dict[store_id] = []
            else:
                shop_item_dict[store_id].append((item_id,quality))
        
    return shop_item_dict

def convert_shop_item():
    shop_item = generate_shop_items()
    
    file_path = os.path.join(DIR,'../')
    file_name = os.path.join(file_path,'shop_item.py')
    with open(file_name,'w') as f:
        data = "items = %s" % str(shop_item)
        f.write(data)
        f.close()
    return True
    

if __name__ == "__main__":
    if convert_shop_item():
        print "convert shop item success"

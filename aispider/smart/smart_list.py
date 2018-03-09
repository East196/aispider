# -*- coding: utf-8 -*-


import json

from lxml import etree

file_name = u"anjuke.index.html"
parser = etree.HTMLParser()
root = etree.parse(file_name, parser)


def fixed_path(path):
    if path.endswith("]"):
        return path[:-3]
    return path


one_item_paths = []
metas = []

for e in root.iter():
    path = root.getpath(e)
    if path.find("div[19]") > 0:
        one_item_paths.append((path, len(path)))
        field_class = e.get("class")
        if field_class is not None and e.text is not None and e.text.strip() != "":
            field_class = field_class.split(" ")[-1:][0]
            field_path = fixed_path(path)
            attr_num = len(root.xpath(field_path))
            field_is_list = attr_num > 1
            item_string = root.xpath(field_path)[0].xpath("string()")
            meta = {"name": field_class, "xpath": field_path, "is_list": field_is_list, "data": item_string}
            try:
                if [y["name"] for y in metas].index(field_class) is -1:
                    metas.append(meta)
                    print(meta, item_string)
            except ValueError:
                metas.append(meta)
                print(meta, item_string)

                # text=root.xpath(path)[0].text
                # if text is not None:
                #     if text.find("华润城润府")!=-1:
                #         print path
                #     if text.find("70000")!=-1:
                #         print path

class_ = root.xpath(one_item_paths[0][0])[0].get("class")
items_path = one_item_paths[0][0].replace("div[19]", "div") + "[@class='" + class_ + "']"
one_page_item_size = len(root.xpath(items_path))
print(items_path)
print(root.getpath(root.xpath(items_path)[0]))
print(root.getpath(root.xpath(items_path)[-1]))
print(one_page_item_size)
for meta in metas:
    print(str(meta))

json_object = {"type": "list", "xpath": items_path, "field_metas": metas}
print(json_object)
json_string = json.dumps(json_object, ensure_ascii=False)
print(json_string)
json_file_name = "d:/anjuke.index.meta.json"

f = open(json_file_name, 'w')
f.write(json_string)

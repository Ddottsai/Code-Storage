from resource_database import resource_database
import sys
import textwrap
import re
from prompt_toolkit import PromptSession

def get_input(query,return_lowercase=True):
    while True:
        init_user_input = ps.prompt(query)
        user_input = init_user_input.lower()
        lst_input = re.split("[, ]+",user_input)
        if lst_input[0] == "show":
            print()
            attr = lst_input[1] if len(lst_input) > 1 else re.split("[, ]+",ps.prompt("Attribute to show: "))[0]
            if attr in ["tag","tags"]:
                cats = ""
                while True:
                    cats = lst_input[2] if len(lst_input) > 2 else ps.prompt("Categories to search for tags (type 'all' to include all tags): ")
                    if cats == "show":
                        resource_database.show(["cats"])
                    else:
                        break
                resource_database.show(["tags",re.split("[, ]+", cats)])
            elif attr in ["alias","aliases"]:
                resource_database.show(["aliases"])
            elif attr in ["cat","cats"]:
                resource_database.show(["cats"])
            elif attr in ["fam","fams","family","families"]:
                resource_database.show(["families"])
            elif attr in ["option","options","help"]:
                print("Options are: tag, alias, cat, fam")
            else:
                print("'"+attr+"' is not a valid field. choose from tag, alias, cat, and fam.")
            """
            if lst_input[1] == "key":
                query = ["keys",re.split("[, ]+",input(
                        "Categories to search for keys (type 'all' to include all keys): "))]
                resource_database.show(query)
            """
            print()
        else:
            if return_lowercase:
                return user_input
            else:
                return init_user_input

wrapper = textwrap.TextWrapper(initial_indent="     ")
temp_input = ""
dct = {"categories":[],"tags":[],"keys":[],"family":None,"summary":None}
fields = [i for i in dct.keys()]
index = 0
ps = PromptSession()
try:
    while True:
        print("\n\n")
        for f in fields:
            if dct[f] is not None:
                if isinstance(dct[f],list):
                    print(f + ": " + resource_database.get_contents(dct[f]))
                else:
                    if f == "ref" and len(dct[f]) > 100:
                        print(f + ": " + dct[f][:100])
                    else:
                        print(f + ": " + dct[f])
            else:
                print(f + ":")
        if index >= len(dct):
            if len(dct["categories"]) == 0:
                print("\n\nPlease specify at least one valid category.")
            else:
                confirmation = get_input("\nAre these specs okay? ")
                if confirmation == "yes":
                    break
            index = 0
            continue
        if fields[index] != "summary":
            temp = get_input("\nInput for "+fields[index].upper()+": ",return_lowercase = True)
        else:
            temp = get_input("\nInput for "+fields[index].upper()+": ",return_lowercase = False)
        if fields[index] in ["keys","tags"]:
            temp = re.split("[,]+",temp)
        elif fields[index] == "categories":#isinstance(dct[fields[index]],list):
            temp = re.split("[, ]+",temp)
        if isinstance(dct[fields[index]],list):
            if len(temp) == 0:
                first = []
            else:
                for i,d in enumerate(temp):
                    if len(d) > 0 and d[0] == " ":
                        temp[i] = d[1:]
                i = temp[0].find(" ")
                if i != -1 and temp[0][:i] in ["replace","set","add","append"]:
                    print("asdf")
                    first = temp[0][:i]
                    a = [temp[0][:i],temp[0][i+1:]]
                    a.extend(temp[1:])
                    temp = a
                else:
                    first = temp[0]
        else:
            if len(temp) > 0 and temp[0] == " ":
                temp = temp[1:]
            if temp.find(" ") != -1:
                first = temp[:temp.find(" ")]
            else:
                first = temp
        if len(temp) == 0 or first in ["skip","pass",""]:
            pass
        elif first in ["back"]:
            index -= 1
            continue
        elif first in ["delete","clear"]:
            if isinstance(dct[fields[index]],list):
                dct[fields[index]] = []
            else:
                dct[fields[index]] = None
            continue
        elif first in ["replace","set"]:
            if len(temp) > 1:
                dct[fields[index]] = temp[1:]
            else:
                print(temp)
        elif first in ["add","append"]:
            del temp[0]
            if not isinstance(dct[fields[index]], list):
                print("Cannot add more than one value to this field.")
                continue
        else:
            if len(temp) != 0:
                if isinstance(dct[fields[index]], list):
                    dct[fields[index]].extend(temp)
                else:
                    dct[fields[index]] = temp
        wrong_cats = []
        i = 0
        while i < len(dct["categories"]):
            if not resource_database.open_cat(dct["categories"][i]):
                wrong_cats.append(dct["categories"][i])
                del dct["categories"][i]
            else:
                i += 1
        index+=1
    metadata = {"ref":(sys.argv[-1] if sys.argv[-1] != "url" else get_input("\nurl:")),"cats":dct["categories"],"tags":dct["tags"],
            "family":dct["family"],"keys":dct["keys"],"ref_type":"url",
            "summary":dct["summary"]}
    for k,v in metadata.items():
        if v == []:
            metadata[k] = None
    resource_database.add_ref(ref=metadata["ref"],keys=metadata["keys"],
                cats=metadata["cats"],tags=metadata["tags"],family=metadata["family"],
                summary=metadata["summary"],ref_type=metadata["ref_type"])
except Exception as e:
    print(e)
finally:
    print("Exiting program.")
    resource_database.end()

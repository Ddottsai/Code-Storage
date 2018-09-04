import textwrap
from resource_database import resource_database
import re
import os
import glob
import sys
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

def put(lst_input):
    if len(lst_input) == 0:
        temp_input = ""
        dct = {"ref":None,"categories":[],"tags":[],"keys":[],"family":None,"ref type":None,"summary":None}
        fields = [i for i in dct.keys()]
        index = 0
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
                    print("Please specify at least one valid category.")
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
            elif fields[index] == "categories":
                temp = re.split("[, ]+",temp)
            if isinstance(dct[fields[index]],list):
                if len(temp) == 0:
                    first = []
                else:
                    for i,d in enumerate(temp):
                        if len(d) > 0 and d[0] == " ":
                            temp[i] = d[1:]
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
        metadata = {"ref":dct["ref"],"cats":dct["categories"],"tags":dct["tags"],
                "family":dct["family"],"keys":dct["keys"],"ref_type":dct["ref type"],
                "summary":dct["summary"]}
    else:
        metadata = {"ref":None,"categories":[],"tags":[],"keys":[],"family":None,"ref type":None}
        choice = None
        for i in lst_input:
            if i  == "summary":
                choice = "summary"
                continue
            if i in ["tag","tags"]:
                choice = "tag"
                continue
            elif i in ["cats","cat","categories","category"]:
                choice = "cat"
                continue
            elif i in ["fams","fam","family","families"]:
                choice = "fam"
                continue
            elif i in ["key","keys"]:
                choice = "key"
                continue
            elif i in ["type","types","ref_types","ref_type","ref type","ref types"]:
                choice = "type"
                continue
            if choice == "summary":
                metadata["summary"] = i
            elif choice == "ref":
                metadata["ref"] = i
            elif choice == "tag":
                metadata["tags"].append(i)
            elif choice == "cat":
                metadata["cats"].append(i)
            elif choice == "fam":
                metadata["family"] = i
            elif choice == "keys":
                metadata["keys"].append(i)
            elif choice == "type":
                metadata["ref_types"] = i
    for k,v in metadata.items():
        if v == []:
            metadata[k] = None
    resource_database.add_ref(ref=metadata["ref"],keys=metadata["keys"],
                cats=metadata["cats"],tags=metadata["tags"],family=metadata["family"],
                summary=metadata["summary"],ref_type=metadata["ref_type"])
    return metadata

def find(lst_input):
    if len(lst_input) == 0:
        temp_input = ""
        dct = {"categories":[],"tags":[],"families":[],"ref types":[],
        "page size":[],"features to include":[]}
        fields = [i for i in dct.keys()]
        index = 0
        while index < len(dct):
            print("\n\n")
            for f in fields:
                print(f + ": " + resource_database.get_contents(dct[f]))
            if fields[index] in ["keys","tags"]:
                temp = re.split("[,]+",get_input("\nInput for "+fields[index].upper()+": "))
            else:
                temp = re.split("[, ]+",get_input("\nInput for "+fields[index].upper()+": "))
            if len(temp) == 0 or temp[0] in ["skip","pass",""]:
                pass
            elif temp[0] in ["back"]:
                index -= 1
                continue
            elif temp[0] in ["delete","clear"]:
                dct[fields[index]] = []
            elif temp[0] in ["replace","set"]:
                if len(temp) > 1:
                    if dct[fields[index]] == "page size":
                        for i in temp[1:]:
                            try:
                                int(i)
                            except ValueError:
                                print("\nError: page size must be an integer.")
                                continue
                    dct[fields[index]] = temp[1:]
            else:
                if temp[0] in ["add","append"]:
                    del temp[0]
                if len(temp) != 0:
                    dct[fields[index]].extend(temp)
            index+=1
        if len(dct["page size"]) == 0:
            dct["page size"] = 10
        else:
            if dct["page size"][0] == "all":
                dct["page size"] = "all"
            elif isinstance(dct["page size"][0],int):
                dct["page size"] = int(dct["page size"][0])
            else:
                dct["page size"] = 10
        query = {"page_size": dct["page size"],
                "features":dct["features to include"],
                "cats":dct["categories"],"tags":dct["tags"],
                "families":dct["families"],"ref_types":dct["ref types"]}
        """
        while temp_input != ["done"]:
            print("-------"*10)
            temp_input = re.split("[, ]+",get_input("query terms (type 'done' to end): ")) # cat data_science,history
            lst_input.extend(temp_input)
        """
    else:
        query = {"page_size":10,"features":[],"cats":[],"tags":[],"families":[],
                "ref_types":[]}
        choice = None
        for i in lst_input:
            if i in ["tag","tags"]:
                choice = "tag"
                continue
            elif i in ["cats","cat","categories","category"]:
                choice = "cat"
                continue
            elif i in ["fams","fam","family","families"]:
                choice = "fam"
                continue
            elif i in ["page","page_size","scroll_size","page size","scroll size","size"]:
                choice = "size"
                continue
            elif i in ["features","include"]:
                choice = "features"
                continue
            elif i in ["type","types","ref_types","ref_type","ref type","ref types"]:
                choice = "type"
                continue

            if choice == "tag":
                query["tags"].append(i)
            elif choice == "cat":
                query["cats"].append(i)
            elif choice == "fam":
                query["families"].append(i)
            elif choice == "size":
                query["page_size"] = int(i)
            elif choice == "features":
                query["features"].append(i)
            elif choice == "type":
                query["ref_types"].append(i)
    for k,v in query.items():
        if v == []:
            query[k] = None
    resource_database.scroll(page_size=query["page_size"],features=query["features"],
                cats=query["cats"],tags=query["tags"],families=query["families"],
                ref_types=query["ref_types"])

##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################

wrapper = textwrap.TextWrapper(initial_indent="     ")
all_put = []
print("\nStarting...")
choice = ""
last_enter = False
reset_last_enter = False
import sys
ps = PromptSession()
from contextlib import suppress
if sys.argv[-1] in ["textbook","textbooks","txtbk","txtbks","book","books"]:
    with suppress(KeyboardInterrupt):
        find(["fams","fa18"])
    user_input = ""
try:
    while True:
        if reset_last_enter:
            last_enter = False
        reset_last_enter = last_enter
        user_input = re.split("[, ]+",get_input("\n\nWhat would you like to do?\nUser Input: ")) if (
                    len(sys.argv) == 1 or "user_input" in locals()) else sys.argv[1:]
        method = user_input.pop(0)
        if method in ["option","options","help"]:
            print("put")
            print(wrapper.fill("""
            """))
            print("put [params]")
            print(wrapper.fill("""
            """))
            print("find ")
            print(wrapper.fill("""
            """))
            print("find [params]")
            print(wrapper.fill("""
            """))
            print("show [param]")
            print(wrapper.fill("""
            """))
        elif method in ["open","load"]:
            for i in user_input:
                resource_database.open_cat(i)
        elif method == "close":
            for i in user_input:
                resource_database.close_cat(i)
        elif method in ["find","search","scroll","query"]:
            find(user_input)
        elif method in ["refresh"]:
            resource_database.refresh_cats("all")
        elif method in ["put","add","make"]:
            organizer = get_input("\n\n\nMake ref, cat, tag (alias), or family?\n\nUser Input: ") if len(user_input) == 0 else user_input.pop(0)
            if organizer == "ref":
                if len(user_input) > 2:
                    params = put(user_input[2:])
                else:
                    params = put([])
                all_put.append(params)
            elif organizer == "cat":
                name = get_input("cat name: ") if len(user_input) == 0 else user_input.pop(0)
                """
                if len(user_input) == 0:
                    attr = ""
                    attributes = []
                    while attr is not "done":
                        attr = re.split("[, ]+",get_input("attribute (type 'done' to end): "))
                        attributes.append(attr)
                else:
                    attributes = user_input
                """
                resource_database.add_cat(name,[])
            if organizer in ["tag","alias"]:
                if len(user_input) > 0 and len([i for i in user_input if i is not " " and i is not ""]) > 0:
                    tags = user_input
                else:
                    tags = [i for i in re.split("[,]+",get_input("tags: ")) if i is not " "]
                resource_database.add_alias(tags)
            if organizer == "family":
                name = get_input("family name: ") if len(user_input) == 0 else user_input.pop(0)
                if len(user_input) == 0:
                    cat = ""
                    cats = []
                    while cat is not "done":
                        attr = re.split("[,]+",get_input("category (type 'done' to end): "))
                        cats.append(cat)
                else:
                    cats = user_input
                resource_database.make_cat(name,cats)
        elif method == "edit":
            organizer = get_input("Edit tag (alias) or edit family?\nUser Input: ") if len(user_input) == 0 else user_input.pop(0)
            if organizer in ["tag","alias"]:
                resource_database.save()
                os.system('open "/Users/dylantsai/resources/tag_aliases.csv"')
                input("Press enter when done editing tag aliases.")
                resource_database.load_tags()
            if organizer == "family":
                resource_database.save()
                os.system('open "families.txt"')
                input("Press enter when done editing families.")
                resource_database.load_families()
        elif method == "save":
            resource_database.save()
        elif method == "":
            if last_enter == True:
                break
            else:
                last_enter = True
        elif method in ["exit","end","done","break"]:
            break
        else:
            print("Sorry, I didn't understand the input. Try again.")
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
finally:
    print("Exiting program.")
    resource_database.end()

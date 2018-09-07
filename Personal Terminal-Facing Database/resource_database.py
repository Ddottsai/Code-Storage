class resource_database():
    import pandas as pd
    import ujson as json
    from io import StringIO
    from multiprocessing import Pool
    from functools import partial
    import ast
    import os
    import re
    import glob
    import textwrap
    from contextlib import suppress
    from pandas.errors import EmptyDataError
    from selenium.common.exceptions import WebDriverException
    import gnureadline
    from prompt_toolkit import PromptSession

    global tag_aliases,db,families,cat_files,wrapper,suppress,directory,id_to_cat,ps
    global pd,json,StringIO,Pool,partial,ast,os,re,textwrap,WebDriverException,glob,EmptyDataError,suppress
    #global open_cat,close_cat,close_all_cats,add_cat,add_cat_attributes
    #global get_tag_aliases,add_alias,find,add_family,add_ref,save,end,show
    ps = PromptSession()
    wrapper = textwrap.TextWrapper(initial_indent="     ")
    directory = os.path.dirname(os.path.realpath(__file__)) + '/'
    with open(directory+'ID_to_cat.txt') as file:
        id_to_cat = ast.literal_eval(file.read())
    #print(var)
    with open(directory+'tag_aliases.csv', 'r') as file:
        tag_aliases = [set(line[:-1].split(',')) for line in file.readlines()]
    with open(directory+'families.txt', 'r') as file:
        families = json.loads(file.read())
    #for key,lst in families.items():
    #    families[key] = set(lst)
    cat_files = {}
    import os
    for file_name in os.listdir(directory+"categories"):
        if not file_name.startswith('.'):
            cat_name = file_name[:-4]
            cat_files[cat_name] = None

    @classmethod
    def get_ID_to_cat(self,ID):
        global id_to_cat
        if id_to_cat is None:
            with open(directory+"ID_to_cat.txt","r") as file:
                id_to_cat = ast.literal_eval(file.read())
        try:
            return id_to_cat[str(ID)]
        except KeyError:
            print("No ref with specified ID was found!")
            return []

    @classmethod
    def add_ref_to_id_to_cat(self,ID,cats):
        global id_to_cat
        if id_to_cat is None:
            with open(directory+"ID_to_cat.txt","r") as file:
                id_to_cat = ast.literal_eval(file.read())
        id_to_cat[str(ID)] = cats

    def is_a_cat(cat):
        return cat in cat_files

    def get_input(query):
        while True:
            user_input = ps.prompt(query).lower()
            lst_input = re.split("[, ]+",user_input)
            if lst_input[0] == "show":
                print()
                attr = lst_input[1] if len(lst_input) > 1 else re.split("[, ]+",ps.prompt("Attribute to show: "))[0]
                if attr == "tag":
                    cats = ""
                    while True:
                        cats = ps.prompt("Categories to search for tags (type 'all' to include all tags): ")
                        if cats == "show":
                            resource_database.show(["cats"])
                        else:
                            break
                    resource_database.show(["tags",re.split("[, ]+", cats)])
                elif attr == "alias":
                    resource_database.show(["aliases"])
                elif attr == "cat":
                    resource_database.show(["cats"])
                elif attr == "fam":
                    resource_database.show(["families"])
                else:
                    print("Field '"+attr+"' does not exist.")
                """
                if lst_input[1] == "key":
                    query = ["keys",re.split("[, ]+",input(
                            "Categories to search for keys (type 'all' to include all keys): "))]
                    resource_database.show(query)
                """

                print()
            else:
                return user_input.lower()

    @classmethod
    def SetParser(self,data):
        return ast.literal_eval(data)

    @classmethod
    def load_tags(self):
        with open(directory+'tag_aliases.csv', 'r') as file:
            tag_aliases = [set(line.split(',')) for line in file.readlines()]

    @classmethod
    def load_families(self):
        with open(directory+'families.txt', 'r') as file:
            families = json.loads(file.read())

    @classmethod
    def open_cat(self,cat_name):
        if cat_name in cat_files and cat_files[cat_name] is not None:
            return True
        try:
            converters = {s: (lambda data : None if data=="" else ast.literal_eval(data)) for s in
                                ['keys','tags']}
            cat_files[cat_name] = pd.read_csv(directory + "categories/"+cat_name+".csv",
                                                    converters=converters,index_col=0)
            return True
        except (FileNotFoundError,EmptyDataError):
            temp = self.get_input("Category does not exist. Create a new category? ")
            if temp.lower() == "yes":
                open(directory+"categories/"+cat_name+".csv","w+").close()
                cat_files[cat_name] = pd.DataFrame()#columns=["tags","keys","summary",
                                                    #"family","ref type","date","ref"])
                return True
            else:
                print("Okay, category not created.")
                return False

    @classmethod
    def close_cat(self,cat_name):
        cat_files[cat_name].to_csv(directory+"categories/"+cat_name+".csv")
        cat_files[cat_name] = None

    @classmethod
    def close_all_cats(self):
        for cat_name in cat_files.keys():
            close_cat(cat_name)

    @classmethod
    def add_cat(self,cat_name,cat_attr=None):
        if cat_name in cat_files:
            return False
        f = open(cat_name +".txt","w+")
        f.write("{}")
        cat_files[cat_name] = None

    @classmethod
    def edit_cat_attributes(self,cat_name,cat_attr):
        self.open_cat(cat_name)
        if isinstance(cat_attr, list):
            cat_files[cat_name].extend(cat_attr)
        else:
            cat_files[cat_name].append(cat_attr)

    @classmethod
    def get_tag_aliases(self,tag):
        tag = tag.lower()
        for equiv in tag_aliases:
            if tag in equiv:
                return equiv

    @classmethod
    def add_alias(self,lst):
        final ={i.lower() for i in lst}
        for equiv in tag_aliases:
            for l in lst:
                if l in equiv:
                    final.update(equiv)
                    tag_aliases.remove(equiv)
                    break
        tag_aliases.append(final)

    @classmethod
    def query(self,cats=None,tags=None,families=None,ref_types=None):
        if cats == None:
            cats = cat_files.keys()
        if tags != None:
            tags = set(tags)
        if ref_types != None:
            ref_types = set(ref_types)
        hit_ID = []
        hits = []
        hit_cat_names = []
        for cat_name in cats:
            if cat_name not in cat_files:
                print("\nWarning: "+cat_name+" is not the name of a category.")
                continue
            if cat_files[cat_name] is None:
                self.open_cat(cat_name)
            for ID,ref_info in cat_files[cat_name].iterrows():
                if ID not in hit_ID:
                    if tags == None or len(tags.intersection(ref_info['tags'])) > 0:
                        if families == None or ref_info['family'] in families:
                            if ref_types == None or ref_info['ref type'] in ref_types:
                                hit_ID.append(int(ID))
                                hit_cat_names.append(cat_name)
                                hits.append(ref_info)
        return hits,hit_ID

    @classmethod
    def add_family(self,family_name,cats=[]):
        #families[family_name] = set(cats)
        families[family_name] = list(cats)

    @classmethod
    def add_ref(self,ref,cats=[],tags=None,keys=None,summary=None,family=None,ref_type=None):
        if ref in ["download","downloads"]:
            old_path = max(glob.iglob(os.path.expanduser('~/Downloads/*')), key=lambda a:os.stat(a).st_birthtime)
            new_path = os.path.expanduser("~/resources/downloads/")+ os.path.basename(old_path)
            os.rename(old_path,new_path)
            ref = new_path
        if ref_type == None:
            if len(ref) > 3 and (ref[0:4] == "http" or ref[0:4] == "www."):
                ref_type = "url"
            elif " " not in ref and "/" in ref:
                ref_type = "file"
            else:
                ref_type = "note"
        if ref_type == "url":
            if ref[0:4] != "www." and ref[0:4] != "http":
                ref = "www." + ref
        import datetime
        t = datetime.date.today().strftime("%B %d, %Y")
        if family != None:
            if family not in families:
                families[family] = list(cats)
            else:
                for c in cats:
                    if c not in families[family]:
                        families[family].append(c)
        series = pd.Series({"tags":tags,"keys":keys,"summary":summary,"family":family,
                            "ref type":ref_type,"date":t,"ref":ref})
        with open(directory+"max_ID.txt","r+") as file:
            #a = "wow"
            curr_max_ID = int(file.read().replace('\x00',''))
            curr_max_ID += 1
            file.truncate(0)
            file.write(str(curr_max_ID))
        series.name = str(curr_max_ID)

        #with open("resources/ref_ID","a") as file:
        #    file.write("\n"+ID + ":" + cats)

        for cat_name in cats:
            self.open_cat(cat_name)
            cat_files[cat_name] = cat_files[cat_name].append(series)
            #cat_files[cat_name] = pd.DataFrame(series).transpose()#pd.DataFrame(series,columns=["tags","keys","summary",
                    #            "family","type","date","ref"])
            self.close_cat(cat_name)

        self.add_ref_to_id_to_cat(curr_max_ID,cats)

    @classmethod
    def save(self):
        with open(directory+'tag_aliases.csv', 'w') as file:
            for i in tag_aliases:
                file.write(",".join(i) + "\n")
        with open(directory+'families.txt','w') as file:
            #file.truncate()
            file.write(json.dumps(families))
        for cat_name,df in cat_files.items():
            if df is not None:
                df.to_csv(directory+"categories/" + cat_name+".csv")
        if id_to_cat is not None:
            with open(directory+'ID_to_cat.txt','w') as file:
                #file.truncate()
                file.write(json.dumps(id_to_cat))
        """
        with open('resources/resources.txt', 'w') as file:
            file.truncate()
            file.write("{")
            for key,df in db.items():
                file.write("\""+key+ "\":" + df.to_csv(sep="`"))
            file.write("}")
        """

    @classmethod
    def end(self):
        self.save()
        exit()

    @classmethod
    def show(self,query):
        #query = [q.lower() for q in query]
        if query[0] in ["cats","cat","categories","category"]:
            print(self.get_contents(list(cat_files.keys())))
        elif query[0] == "alias" or query[0] == "aliases":
            for t in tag_aliases:
                print(t)
        elif query[0] == "tags":
            if query[1] == ["all"]:
                query[1] = cat_files.keys()
            tags = set()
            failed_cats = []
            for cat in query[1]:
                self.open_cat(cat)
                try:
                    tags.update({t for ref_tags in cat_files[cat].loc[:,"tags"] for t in ref_tags})
                except KeyError:
                    failed_cats.append(cat)
                self.close_cat(cat)
            print("\n" + self.get_contents(tags))
            if len(failed_cats) > 0:
                print("\n Note that the following were not valid categories, and thus were skipped:")
                print(wrapper.fill(self.get_contents(failed_cats)))
        elif query[0] == "family" or query[0] == "families":
            print(self.get_contents(families))

    @classmethod
    def get(self,num_hits="all",features=None,cats=None,tags=None,families=None,ref_types=None):
        ordered_cols = ["date","family","keys","ref type","summary","tags","ref"]
        display_columns = []
        if features is None:
            features = ["keys","tags","family","summary","ref"]
        for i in ordered_cols:
            if features == "all" or i in features:
                display_columns.append(i)
        hits,hit_IDs = self.query(cats,tags,families,ref_types)
        #df = pd.concat(hits, axis=1, keys=[hit.name for hit in hits])
        #df["cat"] = hit_cat_names
        if len(hits) == 0:
            return pd.DataFrame(),[]
        df = pd.DataFrame.from_records(hits)
        if len(df.index) > 0:
            if len(df.index) == 1:
                df = df.loc[:,display_columns].iloc[:len(display_columns)]
            else:
                df = df.loc[:,display_columns].iloc[:,:len(display_columns)]
            #df = df.reindex(columns=ordered_cols)
            pd.set_option('display.width', 200)
            pd.set_option('display.max_columns',100)
            pd.set_option('display.max_colwidth',60)
            if num_hits == "all" or num_hits > len(df.index):
                return df,hit_IDs
            return df.head(num_hits),hit_IDs[:num_hits]
        else:
            return pd.DataFrame(),[]

    @classmethod
    def scroll(self,page_size=10,features=None,cats=None,tags=None,families=None,ref_types=None):
        all_hits,all_hits_IDs = self.get(num_hits="all",features="all",cats=cats,tags=tags,families=families,ref_types=ref_types)
        if len(all_hits.index) == 0:
            print("\n\nNo matching refs.")
            return
        row_num = 0
        driver = None
        if features is None:
            features = ["keys","tags","family","ref type"]
            pd.set_option('display.width', 175)
            pd.set_option('display.max_columns',100)
            pd.set_option('display.max_colwidth',1000)
        else:
            if features == "all":
                features = all_hits.columns
            pd.set_option('display.width', 175)
            pd.set_option('display.max_columns',100)
            pd.set_option('display.max_colwidth',int(175/(len(features))))
        if page_size == "all":
            page_size = 1000000
        stop = False
        while not stop:
            print("\n")
            try:
                print(all_hits.ix[row_num:row_num+page_size-1,features])
            except IndexError:
                print(all_hits.ix[row_num:,features])
            print("\n"+"-"*70+"\n")
            last_enter = False
            reset_last_enter = False
            while True:
                if reset_last_enter:
                    last_enter = False
                reset_last_enter = last_enter
                user_input = self.get_input("\n\nScroll | User Input: ").lower()
                if user_input in ["option","options","help"]:
                    print("\nnext, back, repeat, break, open, zoom, edit, delete")
                elif user_input in ["scroll","next","n"]:
                    break
                elif user_input in ["stop","break","exit","end","done"]:
                    return
                elif user_input == "":
                    if last_enter == True:
                        stop = True
                        break
                    else:
                        last_enter = True
                elif user_input == "repeat":
                    row_num -= page_size
                    break
                elif user_input in ["back","b"]:
                    row_num -= page_size*2
                    break
                else:
                    user_input_lst = re.split("[, ]+",user_input)
                    if len(user_input_lst) < 2:
                        temp = re.split("[, ]+",self.get_input(
                            "Please specify (by index) which refs you'd like to "
                            + user_input_lst[0] + ": "))
                        if isinstance(temp,list):
                            user_input_lst.extend(temp)
                        else:
                            user_input_lst.append(temp)
                    try:
                        try:
                            selected_ref_nums = [all_hits_IDs[int(i)] for i in user_input_lst[1:]]
                            selected_refs = [all_hits.loc[int(i),:] for i in user_input_lst[1:]]
                        except ValueError:
                            print("All selected refs must be integers.")
                            #print("\n"+"-"*70)
                            continue
                        for i,selected_ref in enumerate(selected_refs):
                            if user_input_lst[0] == "open":
                                driver = self.open_ref(selected_ref.loc["ref"],selected_ref.loc["ref type"],driver)
                            elif user_input_lst[0] in ["refresh"]:
                                cat_names = self.get_ID_to_cat(selected_ref_nums[i])
                                self.refresh_cats(cat_names)
                            elif user_input_lst[0] in ["delete","remove","rm","del"]:
                                print(selected_ref)
                                if selected_ref["ref type"] not in ["note","url"]:
                                    choice = ""
                                    while choice not in ["remove","delete","cancel"]:
                                        choice = self.get_input(
                                        "\n\n\033[1mRemove\033[0m from refs, or \033[1mdelete\033[0m file altogether ('cancel' to exit)? ")
                                else:
                                    choice = "remove"
                                if choice != "cancel":
                                    confirmation = ""
                                    if choice == "remove":
                                        while confirmation not in ["yes","no"]:
                                            confirmation = self.get_input("\n\nAre you sure you want to \033[1mremove\033[0m this ref (shown above)? ")
                                        if confirmation == "yes":
                                            all_hits.drop(selected_ref.name,inplace=True)
                                            cat_names = self.get_ID_to_cat(selected_ref_nums[i])
                                            for cat_name in cat_names:
                                                if cat_files[cat_name] is None:
                                                    self.open_cat(cat_name)
                                                cat_files[cat_name].drop(selected_ref_nums[i],inplace=True)
                                                self.close_cat(cat_name)
                                            del id_to_cat[str(selected_ref_nums[i])]
                                            print("Okay, ref removed.")
                                    elif choice == "delete":
                                        while confirmation not in ["yes","no"]:
                                            confirmation = self.get_input("Are you sure you want to \033[1mdelete\033[0m this ref (shown above)? ")
                                        if confirmation == "yes":
                                            all_hits.drop(selected_ref.name,inplace=True)
                                            cat_names = self.get_ID_to_cat(selected_ref_nums[i])
                                            for cat_name in cat_names:
                                                if cat_files[cat_name] is None:
                                                    self.open_cat(cat_name)
                                                cat_files[cat_name].drop(selected_ref_nums[i],inplace=True)
                                                self.close_cat(cat_name)
                                            del id_to_cat[str(selected_ref_nums[i])]
                                            try:
                                                os.remove(selected_ref["ref"])
                                                print("Okay, file removed and deleted.")
                                            except Exception as e:
                                                print("File was removed, but there was an error ("+str(e)+", so file was not deleted.")
                            elif user_input_lst[0] == "zoom":
                                print("\n")
                                print("Hit #:",user_input_lst[i+1])
                                print("Ref Type:", selected_ref.loc["ref type"])
                                print("Keys:",self.get_contents(selected_ref.loc["keys"]))
                                print("Tags:",self.get_contents(selected_ref.loc["tags"]))
                                print("Family:",selected_ref.loc["family"])
                                if selected_ref.loc["summary"] != None:
                                    print("Summary:")
                                    end_str = ("..." if len(selected_ref.loc["summary"]) > 300 else "")
                                    print(wrapper.fill(selected_ref.loc["summary"][:1000] + end_str))
                                else:
                                    print("Ref Path:",selected_ref.loc["ref"])
                                if selected_ref.loc["ref type"] == "note":
                                    print("ref:")
                                    end_str = ("..." if len(selected_ref.loc["ref"]) > 300 else "")
                                    print(wrapper.fill(selected_ref.loc["ref"][:1000] + end_str))
                                else:
                                    end_str = ("..." if len(selected_ref.loc["ref"]) > 300 else "")
                                    print("ref: " + selected_ref.loc["ref"][:300] + end_str)
                            elif user_input_lst[0] == "edit":
                                print(selected_ref)
                                field = self.get_input("\n\nField to change ('done' to end): ")
                                while field != "done":
                                    try:
                                        ref_part = selected_ref["ref"][:50] if len(selected_ref["ref"]) > 50 else selected_ref["ref"]
                                    except KeyError:
                                        print("Not a valid field.")
                                        continue
                                    temp_file = "Field View - " + ref_part.replace(":","").replace("~","").replace("/","") + ".txt"
                                    try:
                                        with open(temp_file,"w+") as file:
                                            file.write(field + "\n" + str(selected_ref.loc[field]))
                                        os.system('open "' + temp_file + '"')
                                        print("\n\nEdit, save, and close file.")
                                        self.get_input("\n\nPress enter when done editing field.")
                                        with open(temp_file,"r") as file:
                                            next(file)
                                            updated_field = ""
                                            for line in file:
                                                updated_field += line
                                        if updated_field == "None":
                                            updated_field = None
                                        with suppress(Exception):
                                            updated_field = ast.literal_eval(s)
                                        all_hits.loc[selected_ref.name,field] = updated_field
                                        cat_names = self.get_ID_to_cat(selected_ref_nums[i])
                                        for cat_name in cat_names:
                                            self.open_cat(cat_name)
                                            cat_files[cat_name].loc[selected_ref_nums[i],field] = updated_field
                                            self.close_cat(cat_name)
                                    except Exception as e:
                                        print(e)
                                    field = self.get_input("\n\nField to change ('done' to end): ")
                            else:
                                print("\nSorry,",user_input[0]," is not a valid command.")
                                continue
                            print("\n\n"+"-"*70)
                    except Exception as e:
                        print(type(e))
                        print(e)
                        continue
            row_num += page_size
            if row_num >= len(all_hits):
                choice = self.get_input("\n\nAll items have been scrolled through. Press enter to exit, or"+
                        " anything else to continue.")
                if choice != "":
                    row_num -= page_size
                    stop = False
                else:
                    stop = True
        print("\nExited scroll.")

    @classmethod
    def open_ref(self,ref,ref_type,driver):
        if ref_type == "url":
            if driver is None:
                from selenium import webdriver
                driver = webdriver.Chrome('chromedriver')
            else:
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])
            for prefix in ["","http://","https://"]:
                with suppress(WebDriverException):
                    driver.get(prefix+ref)
                    break
            return driver
        elif ref_type == "note":
            print()
            print("-"*30)
            print()
            print(ref)
        else:
            """
            elif ref_type == "text":
                program =
            elif ref_type == "spreadsheet":
                program =
            elif ref_type == "image":
                program =
            elif ref_type == "pages":
                program =
            elif ref_type == "video":
                program =
            else:
                program =
            subprocess.Popen(program,ref)
            """
            os.system('open "' + ref + '"')

    @classmethod
    def refresh_cats(self,cat_names):
        if cat_names == "all":
            cat_names = cat_files.keys()
        for i in cat_names:
            if i in cat_files and cat_files[i] is not None:
                d = None
                self.open_cat(i)

    @classmethod
    def get_contents(self,arr):
        result = ""
        for i in arr:
            result += i + ", "
        if len(result) == 0:
            return ""
        return result[:-2]

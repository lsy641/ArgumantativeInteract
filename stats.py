import json
import itertools
statsFilePs = ["vegan_immigration_full_annotation_gpt-4.json", "abortion_transgender_full_annotation_gpt-4.json", "gun_violence_full_annotation_gpt-4.json"]

def merge():
    global statsFilePs
    res = []
    for fileP in statsFilePs:
        with open(fileP, "r") as f:
            res.extend(json.load(f))
    for example in res:
        for conv in example["Conversation"]:
            conv["Enhancing"] = list(set(conv["Annotation_eval"]["A1"]["Enhancing"] + conv["Annotation_eval"]["A2"]["Enhancing"] + conv["Annotation_eval"]["A3"]["Enhancing"]))
            conv["Undercutting"] = list(set(conv["Annotation_eval"]["A1"]["Undercutting"] + conv["Annotation_eval"]["A2"]["Undercutting"] + conv["Annotation_eval"]["A3"]["Undercutting"]))
            while "NA" in conv["Enhancing"]  and len(conv["Enhancing"]) > 1:
                conv["Enhancing"].remove("NA")                
            while "NA" in conv["Undercutting"]  and len(conv["Undercutting"]) > 1:
                conv["Undercutting"].remove("NA")          
            del conv["Annotation_eval"]
    # with open("annotated_data_union.json", "w") as f:
    #     json.dump(res, f, indent=1)
    return res

def moral_principle_print(convs):
    res = {}
    for conv in convs:
        res[conv["Topic"]+"_pos"] = res.get(conv["Topic"]+"_pos", [])
        res[conv["Topic"]+"_neg"] = res.get(conv["Topic"]+"_neg", [])
        stance = {}
        for u_id, utter in enumerate(conv["Conversation"]):
            print(utter)
            # list_moral = [utter["Annotation_eval"][person]["Enhancing"] for person in utter["Annotation_eval"] if "Enhancing" in utter["Annotation_eval"][person] ]
            list_moral = utter["Enhancing"] 
            if len(list(stance.keys())) == 0:
                stance[utter["Speaker_id"]] = "pos"
            if utter["Speaker_id"] not in stance:
                for word in utter["Enhancing"]:
                    if word in res[conv["Topic"]+"_pos"]:
                        stance[utter["Speaker_id"]] = "pos"
                        break
                    if word in res[conv["Topic"]+"_neg"]:
                        stance[utter["Speaker_id"]] = "neg"
                        break 
            if utter["Speaker_id"] not in stance:
                stance[utter["Speaker_id"]] = "neg"          
            while "NA" in list_moral:
                list_moral.remove("NA")  
                
            list_moral = [list_moral]
            res[conv["Topic"]+"_"+stance[utter["Speaker_id"]]].extend(itertools.chain(*list_moral))
    for topic in res:
        print(topic)
        print((",".join(res[topic])).replace(" ", "~").replace(",", " "))
    return res  

def check_quality(convs):
    res = {}
    annotated_num = 0
    annotated_num_yes = 0
    annotator_num = 0
    hit_num = 0
    total_num = 0
    for conv in convs:
        res[conv["Topic"]] = res.get(conv["Topic"], [])
        for u_id, utter in enumerate(conv["Conversation"]):
            annotated = set(utter["Enhancing"])
            annotated_num += len(annotated)
            list_moral = set(itertools.chain(* ([utter["Annotation_eval"][person]["Enhancing"] for person in utter["Annotation_eval"] if "Enhancing" in utter["Annotation_eval"][person] ])))
            annotator_num += len(list_moral)
            hit_num += (1 if sum([1 for item in annotated if item in list_moral]) > 0 else 0)
            annotated_num_yes += sum([1 for item in annotated if item in list_moral])

            annotated = set(utter["Undercutting"])
            annotated_num += len(annotated)
            list_moral = set(itertools.chain(*([utter["Annotation_eval"][person]["Undercutting"] for person in utter["Annotation_eval"] if "Undercutting" in utter["Annotation_eval"][person] ])))
            annotator_num += len(list_moral)
            hit_num += (1 if sum([1 for item in annotated if item in list_moral]) > 0 else 0)
            annotated_num_yes += sum([1 for item in annotated if item in list_moral])   
            total_num += 2        
    print("pre:", annotated_num_yes/annotated_num, "recall:", annotated_num_yes/annotator_num, "hit@1:", hit_num/total_num)


def convert_json(file_name):
    with open(file_name, "r") as f:
        data = json.load(f)
    topics = []
    prompt_data = []
    test_data = []
    for conv in data:
        if conv["Topic"] not in topics:
            topics.append(conv["Topic"])
            prompt_data.append(conv)
        else:
            test_data.append(conv)
        
    with open(file_name.split(".")[0]+"_prompt.json", "w") as f:   
        json.dump(prompt_data, f)
    with open(file_name.split(".")[0]+"_test.json", "w") as f:   
        json.dump(test_data, f)


if __name__ == "__main__":
    convert_json("annotated_data_union.json")
    # merge()
        
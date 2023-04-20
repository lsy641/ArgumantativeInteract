import json 


TopicName = "gun_violence_"
InputFileName = "annotation_"
OutputFileName= "add_annotation_"
YouName = "A1"
Model = "gpt-4"
with open(TopicName+OutputFileName +Model+".json", "r") as f:
    convs = json.load(f)
    
for c_id, conv in enumerate(convs):
    print(f"----------{c_id}-----------")
    text = ""
    for utter in conv["Conversation"]:
        prefix = f'Speaker {utter["Speaker_id"]}-Utterance {utter["Utterance_id"]}'
        utterance = f'{prefix}: {utter["Content"]}\n'
        text += utterance
    print(text)
    print("----------------------------")
    for u_id, utter in enumerate(conv["Conversation"]):
        if "Annotation_eval" in convs[c_id]["Conversation"][u_id] and YouName in convs[c_id]["Conversation"][u_id]["Annotation_eval"] and convs[c_id]["Conversation"][u_id]["Annotation_eval"][YouName]["Enhancing"] and convs[c_id]["Conversation"][u_id]["Annotation_eval"][YouName]["Undercutting"]:
            continue
        prefix = f'Speaker {utter["Speaker_id"]}-Utterance {utter["Utterance_id"]}'
        utterance = f'{prefix}: {utter["Content"]}\n'
        print(utterance)
        text += utterance
        print("Enhancing:", utter["Enhancing"])
        print("Undercutting: ", utter["Undercutting"])
        enhance_ids= input("The indexes of enhancing you approve: (e.g., 1,2,3)").split(",")
        enhance_ids = [int(enhance_id) for enhance_id in enhance_ids] if enhance_ids[0] else []
        undercut_ids= input("The indexes of undercutting you approve: (e.g., 1,2,3)").split(",")
        undercut_ids = [int(undercut_id) for undercut_id in undercut_ids] if undercut_ids[0] else []
        undercut = []
        enhance = []
        if enhance_ids:
            for enhance_id in enhance_ids:
                enhance.append(utter["Enhancing"][enhance_id])
        if undercut_ids:
            for undercut_id in undercut_ids:
                undercut.append(utter["Undercutting"][undercut_id])
            
        added_enhance = input("Your annotation for enhancing: (e.g, xx,yy)").split(",")
        added_undercut = input("Your annotation for undercutting:(e.g., xx,yy)").split(",")
        if added_enhance[0]:
            enhance.extend(added_enhance)
        if added_undercut[0]:
            undercut.extend(added_undercut)
        if "Annotation_eval" not in convs[c_id]["Conversation"][u_id]:
            convs[c_id]["Conversation"][u_id]["Annotation_eval"] = {}
        convs[c_id]["Conversation"][u_id]["Annotation_eval"][YouName] = {"Enhancing": enhance, "Undercutting": undercut}
        
        with open(TopicName+OutputFileName +Model+".json", "w" ) as f:
            json.dump(convs, f, indent=1)    
         
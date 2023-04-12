import os
import openai
import json
import time
openai.organization = "org-gcDzLqviJ8Ot15L4nFeIgR5L"
openai.api_key = open("api_key", "r").read()

model="gpt-3.5-turbo" #or gpt-3.5-turbo
params = {'temperature':1.0, 'max_tokens':2048, 'n':1}
initial_hint = "You are able to judge if two phrases, which can be moral principles, intrinsic values, or moral concerns, are semantically equivalent to each other related to a specific topic."

def detect_conflict(file_name):
    # Open the JSON file
    with open(file_name) as f:
        data = json.load(f)
    messages = [{"role":"system", "content":initial_hint}]  

    # Iterate over each object in the list
    i = 1
    total_conflicts = 0
    symbolic_count= 0
    semantic_count = 0
    correct_count = 0
    for conv in data:
        # Iterate over each conversation in the list
        # check the conflict in the given conversation obj
        print("=======Checking conflict in conversation_id: ", i)
        print("Topic: ", conv["Topic"])
        print("Speaker count: ", conv["Speaker_count"])
        print("----ground truth check result:")
        gt_conflicts = ground_truth(conv)
        # print("----symbolic check result:")
        # symbolic_conflicts = symbolic_check(conv)
        print("----semantic check result:")
        semantic_conflicts = semantic_check(conv, messages)
        semantic_count += len(semantic_conflicts)
        # calculate the accuracy
        total_conflicts += len(gt_conflicts)
        # symbolic_count += len([u for u in symbolic_conflicts if u in gt_conflicts])
        correct_count += len([u for u in semantic_conflicts if u in gt_conflicts])
        # print(f"----symbolic check accuracy: {float(symbolic_count) / float(total_conflicts)}")
        print(f"----semantic check accuracy: {float(semantic_count) / float(total_conflicts)}")
        i += 1
        print("total_conflicts, semantic_count, correct_count: ", total_conflicts, semantic_count, correct_count)
    return total_conflicts, semantic_count, correct_count
                   
def ground_truth(conv):
    enhancing_dict = {}
    undercutting_dict = {}
    utters = []
    rlt = []
    for utter1 in conv["Conversation"]:
        utter1_id = utter1["Utterance_id"]
        speaker1_id = utter1["Speaker_id"]
        utter1_enhancing = []  
        utter1_undercutting = []
        for person in utter1["Annotation_eval"]:
            assess1 = utter1["Annotation_eval"][person]
            if assess1 == {}:
                continue
            utter1_enhancing += [v for v in assess1["Enhancing"] if v != "NA"]
            utter1_undercutting += [v for v in assess1["Undercutting"] if v != "NA"]
        
        for utter2 in conv["Conversation"]:
            utter2_id = utter2["Utterance_id"]
            speaker2_id = utter2["Speaker_id"]
            if utter1_id == utter2_id or speaker1_id == speaker2_id:
                continue
            utter2_enhancing = []
            utter2_undercutting = []
            for person in utter2["Annotation_eval"]:
                assess2 = utter2["Annotation_eval"][person]
                if assess2 == {}:
                    continue
                utter2_enhancing += [v for v in assess2["Enhancing"] if v != "NA"]
                utter2_undercutting += [v for v in assess2["Undercutting"] if v != "NA"]
            # check if the two utterance conflict with each other
            conflict_values = [v for v in utter1_enhancing if v in utter2_undercutting]
            if conflict_values != []:
                print("Conflict found!")
                print(f"Conflict between utterance {utter1_id} and {utter2_id}, speaker {speaker1_id} and {speaker2_id}")
                print("Conflict value: ", set(conflict_values))
                print()
                rlt.append((utter1_id, utter2_id))
    return rlt

def symbolic_check(conv):
    enhancing_dict = {}
    undercutting_dict = {}
    utters = []
    rlt = []
    for utter1 in conv["Conversation"]:
        utter1_id = utter1["Utterance_id"]
        speaker1_id = utter1["Speaker_id"]
        utter1_enhancing = max(utter1["Enhancing"], key=utter1["Enhancing"].count)
        utter1_undercutting = max(utter1["Undercutting"], key=utter1["Undercutting"].count)
        
        for utter2 in conv["Conversation"]:
            utter2_id = utter2["Utterance_id"]
            speaker2_id = utter2["Speaker_id"]
            if utter1_id == utter2_id or speaker1_id == speaker2_id:
                continue
            utter2_enhancing = max(utter2["Enhancing"], key=utter2["Enhancing"].count)
            utter2_undercutting = max(utter2["Undercutting"], key=utter2["Undercutting"].count)
            # check if the two utterance conflict with each other with simple symbolic check
            conflict = utter1_enhancing == utter2_undercutting and (utter1_enhancing != "NA" or utter2_undercutting != "NA")
            if conflict:
                print("Conflict found!")
                print(f"Conflict between utterance {utter1_id} and {utter2_id}, speaker {speaker1_id} and {speaker2_id}")
                print(f"Reason: enhancing \"{utter1_enhancing}\" vs. undercutting \"{utter2_undercutting}\"")
                print("Conflict detector type: Symbolic")
                print()
                rlt.append((utter1_id, utter2_id))
    return rlt                
                
def semantic_check(conv, messages):
    enhancing_dict = {}
    undercutting_dict = {}
    utters = []
    rlt = []
    topic = conv["Topic"]
    for utter1 in conv["Conversation"]:
        utter1_id = utter1["Utterance_id"]
        speaker1_id = utter1["Speaker_id"]
        utter1_enhancing = max(utter1["Enhancing"], key=utter1["Enhancing"].count)
        utter1_undercutting = max(utter1["Undercutting"], key=utter1["Undercutting"].count)
        
        for utter2 in conv["Conversation"]:
            utter2_id = utter2["Utterance_id"]
            speaker2_id = utter2["Speaker_id"]
            if utter1_id == utter2_id or speaker1_id == speaker2_id:
                continue
            utter2_enhancing = max(utter2["Enhancing"], key=utter2["Enhancing"].count)
            utter2_undercutting = max(utter2["Undercutting"], key=utter2["Undercutting"].count)
            if utter1_enhancing == "NA" or utter2_undercutting == "NA":
                continue
            # check if the two utterance conflict with each other with semantic equivalence
            last_command = {"role":"user", "content": f"Is \"{utter1_enhancing}\" and \"{utter2_undercutting}\" semantically equivalent under the topic of \"{topic}\"? Answer me Yes or No."}
            semantic_equiv = False
            while True:
                try:
                    print("sending message...")
                    response = openai.ChatCompletion.create(model=model, 
                                                            messages=messages + [last_command], **params)
                    # print("response: ", response)
                    # print("message sent!")
                    for choice in response["choices"]:
                        # print(choice["message"]["content"])
                        if choice["message"]["content"] == "Yes":
                            semantic_equiv = True
                            break
                except Exception as e:
                    print(messages)
                    print(e)
                    time.sleep(1.0)  
                else:
                    break
                
            # time.sleep(1.0) 
                
            if semantic_equiv:
                print("Conflict found!")
                print(f"Conflict between utterance {utter1_id} and {utter2_id}, speaker {speaker1_id} and {speaker2_id}")
                print(f"Reason: enhancing \"{utter1_enhancing}\" vs. undercutting \"{utter2_undercutting}\"")
                print("Conflict detector type: Semantic")
                print()
                rlt.append((utter1_id, utter2_id))
    return rlt  
              
# def symbolic_check(conv):
#     enhancing_dict = {}
#     undercutting_dict = {}
#     for utter in conv["Conversation"]:
#         utter_id = utter["Utterance_id"]
#         enhancing = utter["Enhancing"]
#         undercutting = utter["Undercutting"]
#         # TOCHECK the most likely choice is the most common prediction
#         most_likely_enhancing = max(enhancing, key=enhancing.count)
#         most_likely_undercutting = max(undercutting, key=undercutting.count)
#         if most_likely_enhancing not in enhancing_dict:
#             enhancing_dict[most_likely_enhancing] = []
#         if most_likely_undercutting not in undercutting_dict:
#             undercutting_dict[most_likely_undercutting] = []
#         enhancing_dict[most_likely_enhancing].append(utter_id)
#         undercutting_dict[most_likely_undercutting].append(utter_id)
        
#     for utter in conv["Conversation"]:
#         utter_id = utter["Utterance_id"]
#         enhancing = utter["Enhancing"]
#         undercutting = utter["Undercutting"]
#         # TOCHECK the most likely choice is the most common prediction
#         most_likely_enhancing = max(enhancing, key=enhancing.count)
#         most_likely_undercutting = max(undercutting, key=undercutting.count)
#         if most_likely_enhancing == "NA":
#             continue
#         if most_likely_enhancing in undercutting_dict:
#             for conflict_utter_id in undercutting_dict[most_likely_enhancing]:
#                 if utter_id == conflict_utter_id:
#                     continue
#                 print("Conflict found!")
#                 print(f"Conflict between utterance {utter_id} and {conflict_utter_id}")
#                 print("Conflict value: ", most_likely_enhancing)
#                 print("Conflict detector type: Symbolic")
#                 print()
     
if __name__ == "__main__":
    # benchmark_set = ["gun_violence_annotation_gpt-4.json", "vegan_immigration_annotation_gpt-4.json"]
    benchmark_set = ["vegan_immigration_annotation_gpt-4.json"]
    input_file = "gun_violence_annotation_gpt-4.json"
    statistics = {}
    
    conflict_count = 0
    detected_count= 0
    correct_count = 0
    for benchmark in benchmark_set:
        print("====Evaluating benchmark: ", benchmark)
        conflict_cnt, detected_cnt, correct_cnt = detect_conflict(benchmark)
        conflict_count += conflict_cnt
        detected_count += detected_cnt
        correct_count += correct_cnt
        statistics[benchmark] = (conflict_cnt, detected_cnt, correct_cnt, float(correct_cnt) / float(conflict_cnt))
    
    print(f"total conflict count: {conflict_count}")
    print(f"total detected count: {detected_count}")
    print(f"total correct count: {correct_count}")
    print(f"----prediction accuracy: {float(correct_count) / float(conflict_count)}")
    print(f"statistics: {statistics}")
    
    # detect_conflict(input_file)
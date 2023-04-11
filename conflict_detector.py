import os
import openai
import json
import time
openai.organization = "org-gcDzLqviJ8Ot15L4nFeIgR5L"
openai.api_key = open("api_key", "r").read()

model="gpt-4" #or gpt-3.5
params = {'temperature':1.0, 'max_tokens':2048, 'n':5}

def detect_conflict(file_name):
    # Open the JSON file
    with open(file_name) as f:
        data = json.load(f)

    # Iterate over each object in the list
    i = 1
    for conv in data:
        # Iterate over each conversation in the list
        # check the conflict in the given conversation obj
        print("=======Checking conflict in conversation_id: ", i)
        print("Topic: ", conv["Topic"])
        print("Speaker count: ", conv["Speaker_count"])
        print("----ground truth check result:")
        ground_truth(conv)
        print("----symbolic check result:")
        symbolic_check(conv)
        i += 1
                   
def ground_truth(conv):
    enhancing_dict = {}
    undercutting_dict = {}
    utters = []
    for utter1 in conv["Conversation"]:
        utter1_id = utter1["Utterance_id"]
        speaker1_id = utter1["Speaker_id"]
        utter1_enhancing = []  
        utter1_undercutting = []
        for person in utter1["Annotation_eval"]:
            assess1 = utter1["Annotation_eval"][person]
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
                utter2_enhancing += [v for v in assess2["Enhancing"] if v != "NA"]
                utter2_undercutting += [v for v in assess2["Undercutting"] if v != "NA"]
            # check if the two utterance conflict with each other
            conflict_values = [v for v in utter1_enhancing if v in utter2_undercutting]
            if conflict_values != []:
                print("Conflict found!")
                print(f"Conflict between utterance {utter1_id} and {utter2_id}, speaker {speaker1_id} and {speaker2_id}")
                print("Conflict value: ", set(conflict_values))
                print()

def symbolic_check(conv):
    enhancing_dict = {}
    undercutting_dict = {}
    utters = []
    for utter1 in conv["Conversation"]:
        utter1_id = utter1["Utterance_id"]
        speaker1_id = utter1["Speaker_id"]
        utter1_enhancing = utter1["Enhancing"]  
        utter1_undercutting = utter1["Undercutting"]
        
        for utter2 in conv["Conversation"]:
            utter2_id = utter2["Utterance_id"]
            speaker2_id = utter2["Speaker_id"]
            if utter1_id == utter2_id or speaker1_id == speaker2_id:
                continue
            utter2_enhancing = utter2["Enhancing"]
            utter2_undercutting = utter2["Undercutting"]
            # check if the two utterance conflict with each other
            conflict_values = [v for v in utter1_enhancing if v in utter2_undercutting and v != "NA"]
            if conflict_values != []:
                print("Conflict found!")
                print(f"Conflict between utterance {utter1_id} and {utter2_id}, speaker {speaker1_id} and {speaker2_id}")
                print("Conflict value: ", set(conflict_values))
                print("Conflict detector type: Symbolic")
                print()
                
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
    benchmark_set = []
    input_file = "gun_violence_annotation_gpt-4.json"
    detect_conflict(input_file)
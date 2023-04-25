import os
import openai
import json
import time
openai.organization = "org-gcDzLqviJ8Ot15L4nFeIgR5L"
openai.api_key = open("api_key", "r").read()

model="gpt4"
params = {'temperature':1.0, 'max_tokens':2048, 'n':1}



def prepare_example(file_name="annotated_data_union_prompt.json"):
    with open(file_name, "r") as f:
        data = json.load(f)
    prompts = {}
    for conv in data: 
        prompts[conv["Topic"]] = conv 
    examples = {}  
    for topic in prompts:
        example = prompts[topic] 
        example_wo_label ={"Topic": example["Topic"], "Conversation": [{"Speaker_id": item["Speaker_id"], "Utterance_id": item["Utterance_id"], "Content": item["Content"] } for item in example["Conversation"]]}

        # predefine = '''   
        # class Operator:
        #     def __call__(value1, value2):
        #         raise NotImplementedError()
            
        # class Value:
        #     value = "Value"
        #     def __init__(phrase):
        #         self.value = phrase
            
        # class Undercutting(operator):
        #     def __call__(value):
        #         pass 

        # class Enhancing(operator):
        #     def __call__(value):
        #         pass 
            
        # class Utterance:
        #     def __init__(utter_id, content):
        #         self.utter_id = utter_id
        #         self.content = content
                
        #     def add_enhancing(value):
        #         self.enhancing_value = value
            
        #     def add_undercutting(value):
        #         self.undercutting_value = value
                
        # '''
        
        predefine = ""


        p = f'class Conversation:  \n\
                def __init__(example): \n\
                    print(example)     \n\
                    #{example_wo_label}  \n '
                    
                    
        conv_moral_value_reasoning = ""           
        for item in example["Conversation"]:
            conv_moral_value_reasoning +=          \
            f'  \n\
                    utter = "{item["Content"]}"    \n\
                    utter_id = "Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]}"     \n\
                    self.utter_Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]} = Utterance(utter_id, utter)   \n\
                    # Is the Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]} supporting a certain moral principle or intrinsic value? Reply me NA if it is not. Otherwise, infer the moral principle or the intrinsic value that Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]} is supporting or enhancing or praising. Answer me with a phrase within 4 words. \n\
                    self.utter_Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]}.add_enhancing({"_".join(item["Enhancing"][0].split(" "))}())   \n\
                    # Is the Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]} against a certain moral principle or intrinsic value that might be hold by other speakers? Reply me NA if it is not. Otherwise, infer the moral principle or the intrinsic value that Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]} is opposing or undercutting or attacking. Answer me with a phrase within 4 words. \n\
                    self.utter_Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]}.add_undercutting({"_".join(item["Undercutting"][0].split(" "))}())   \n'
                    
                    
                    # class {"_".join(item["Enhancing"][0].split(" "))}(Value): \n\
                    #     value = "{item["Enhancing"][0]}" \n\               
                    # class {"_".join(item["Undercutting"][0].split(" "))}(Value): \n\
                    #     value = "{item["Undercutting"][0]}" \n\
        
        
                        
            
        for pre_id, pre_item in enumerate(example["Conversation"][2:4]): 
            for lat_id, lat_item in enumerate(example["Conversation"][3:5]):
                conv_moral_conflict_reasoning = f'\
                def detect_moral_diagreement(Speaker{pre_item["Speaker_id"]}_Utter{pre_item["Utterance_id"]}, Speaker{lat_item["Speaker_id"]}_Utter{lat_item["Utterance_id"]}):   \n\
                    # detect_moral_diagreement     \n'  
                semantic_equivalent = False
                for item in pre_item["Enhancing"]:
                    if item in lat_item["Undercutting"]:
                        semantic_equivalent = True
                conv_moral_conflict_reasoning += f' \
                value1 = self.utter_Speaker{pre_item["Speaker_id"]}_Utter{pre_item["Utterance_id"]}.enhancing_value,     \n\
                # {"_".join(pre_item["Enhancing"][0].split(" "))}  \n\
                value2 = self.utter_Speaker{lat_item["Speaker_id"]}_Utter{lat_item["Utterance_id"]}.undercutting_value    \n\
                # {"_".join(lat_item["Undercutting"][0].split(" "))}   \n\
                semantic_equivalent = semantic_equivalent(value1, value2) \n\
                # {semantic_equivalent}  \n'
                
                            # print(value1.value) \n\             print(value2.value)  \n\             print(semantic_equivalent) \n\
        
        
        examples[topic] =  [predefine + p + conv_moral_value_reasoning, conv_moral_conflict_reasoning]  
    return examples        
        # return predefine + p + conv_moral_value_reasoning + conv_moral_conflict_reasoning + prepare_example(file_name="annotated_data_union_test.json", test=True)
            

def give_query(conv):
    example = conv   
    example_wo_label ={"Topic": example["Topic"], "Conversation": [{"Speaker_id": item["Speaker_id"], "Utterance_id": item["Utterance_id"], "Content": item["Content"] } for item in example["Conversation"]]}
    
    res = []
    
    p = f'class Conversation:  \n\
        def __init__(example): \n\
            print(example)     \n\
            #{example_wo_label}  \n '
            
    res.append(p)        
    # conv_moral_value_reasoning = ""           
    # for item in example["Conversation"]:
    #     conv_moral_value_reasoning +=          \
    #     f'  \n\
    #             utter = "{item["Content"]}"    \n\
    #             utter_id = "Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]}"     \n\
    #             # Is the Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]} supporting a certain moral principle or intrinsic value? Reply me NA if it is not. Otherwise, infer the moral principle or the intrinsic value that Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]} is supporting or enhancing or praising. Answer me with a phrase within 4 words. \n \
    #             enhancing_value = "{item["Enhancing"][0]}"  \n\
    #             # Is the Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]} against a certain moral principle or intrinsic value that might be hold by other speakers? Reply me NA if it is not. Otherwise, infer the moral principle or the intrinsic value that Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]} is opposing or undercutting or attacking. Answer me with a phrase within 4 words. \n \
    #             undercutting_value = "{item["Undercutting"][0]}"   \n\
    #             self.utter_Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]} = Utterance(utter_id, utter)   \n\
    #             self.utter_Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]}.add_enhancing({"_".join(item["Enhancing"][0].split(" "))}())   \n\
    #             self.utter_Speaker{item["Speaker_id"]}_Utter{item["Utterance_id"]}.add_undercutting({"_".join(item["Undercutting"][0].split(" "))}())   \n'
    
    
    for pre_id, pre_item in enumerate(example["Conversation"]): 
        for lat_id, lat_item in enumerate(example["Conversation"]):
            conv_moral_conflict_reasoning = f'\
            def detect_moral_diagreement(Speaker{pre_item["Speaker_id"]}_Utter{pre_item["Utterance_id"]}, Speaker{lat_item["Speaker_id"]}_Utter{lat_item["Utterance_id"]}):   \n\
                # detect_moral_diagreement     \n'  
            res.append(conv_moral_conflict_reasoning)    
    return res
    # p = f' conv_json = {example}  \n \
    #     class \
    
            
            
    # class conversation:
    #     def __init__(example):
    #         print(example)
    #         # conv_json = {example}
    #         utter = item["Content"]
    #         utter_id = item["Speaker_id"]_item["Utterance_id"] 
    #         # "Is the {prefix} against a certain moral principle or intrinsic value that might be hold by other speakers? Reply me NA if it is not. Otherwise, infer the moral principle or the intrinsic value that {prefix} is opposing or undercutting or attacking. Answer me with a phrase within 4 words."
    #         enhancing_value = ""
    #         # "Is the {prefix} against a certain moral principle or intrinsic value that might be hold by other speakers? Reply me NA if it is not. Otherwise, infer the moral principle or the intrinsic value that {prefix} is opposing or undercutting or attacking. Answer me with a phrase within 4 words."
    #         undercutting_value = ""
    #         self.utter_item["Speaker_id"]_item["Utterance_id"] = utterance(utter_id, utter)
    #         self.utter_item["Speaker_id"]_item["Utterance_id"].add_enhancing(enhancing_value)
    #         self.utter_item["Speaker_id"]_item["Utterance_id"].add_undercutting(undercutting_value)
            
    #     def detect_moral_diagreement():
    #         # detect_moral_diagreement
    #         value1 = self.utter_item["Speaker_id"]_item["Utterance_id"].enhancing_value, 
    #         value2 = self.utter_item["Speaker_id"]_item["Utterance_id"].undercutting_value
    
    
            
            
            
        
        
        
        # utter_item["Speaker_id"]_item["Utterance_id"] = utterance(item["Speaker_id"]_item["Utterance_id"], item["Content"])
        # # "Is the {prefix} against a certain moral principle or intrinsic value that might be hold by other speakers? Reply me NA if it is not. Otherwise, infer the moral principle or the intrinsic value that {prefix} is opposing or undercutting or attacking. Answer me with a phrase within 4 words."
        # operater, value = utter_item["Speaker_id"]_item["Utterance_id"].parse_enhancing()    
    
    


def llm_detector(file_name = None):
    initial_hint = \
    ''' 
    
    
    
    conv_json = {"Topic": "Vegan", "Data_id": 0, "Speaker_count": 2, "Conversation": [{"Speaker_id": 0, "Utterance_id": 0, "Content": "Why would chucking paint all over big ben persuade someone like me to give up meat?", "Enhancing": ["NA"], "Undercutting": ["Disruptive protest methods", "Respecting public property"]}, {"Speaker_id": 1, "Utterance_id": 1, "Content": "As you and your viewers probably know we are in a climate an ecological emergency at the moment and so what we are doing is we're asking the government to support farmers and fishing communities in a transition to a plant-based food system because we know that animal agriculture is a leading cause of the climate crisis and so if we transition to a plant-based food system we can free up vast amount of land in the UK.", "Enhancing": ["Environmental protection"], "Undercutting": ["NA"]}, {"Speaker_id": 0, "Utterance_id": 2, "Content": "Okay look that's all fine, that wasn't my question. My question is why does chucking paint over big ben? Why does desecrating Trafalgar square with red dye, chucking milk around harrods, destroying supermarket shells? How does that persuade me who already likes eating meat? Why are you going to persuade me by being a vandal? Don't get it.", "Enhancing": ["Respect for property", "Respecting public property"], "Undercutting": ["Vandalism for persuasion", "Improper way of protesting"]}, {"Speaker_id": 1, "Utterance_id": 3, "Content": "I think we're we're in an incredibly difficult position at the moment because we've been trying to talk about these things now for a very long time and so we're at a point where we need to escalate protest so we can gain more media attention on the subject.", "Enhancing": ["Escalation for attention", "Escalating protest for attention", "Media attention importance", "Escalate protest for attention"], "Undercutting": ["NA"]}, {"Speaker_id": 0, "Utterance_id": 4, "Content": "I don't know anyone you persuade. \\I haven't heard anyone go. you know what, I was a meat eater and I saw big ben being desecrated this great monument in this country and I thought I know what I'll do. I'm going to go and give up meat and start eating gruel. I haven't heard a single human being say that. Why would they?", "Enhancing": ["Personal freedom", "Preserving personal choice", "Personal choice", "Respect for monuments"], "Undercutting": ["Persuasion through vandalism"]}, {"Speaker_id": 1, "Utterance_id": 5, "Content": "I think the purpose of protests is not necessarily to win over people. It's to bring these important conversations to the table.", "Enhancing": ["Raising public awareness", "Raising awareness"], "Undercutting": ["NA"]}, {"Speaker_id": 0, "Utterance_id": 6, "Content": "But we know the conversation. You you're a vegan, right? I'm a meat eater, Why can't we just both live happily in each other's orbit? Why can't you let me just get on with eating meat and you eat your gruel and we're all go home happy.", "Enhancing": ["Live and let live", "Persoanl freedom", "Individual choice"], "Undercutting": ["NA"]}, {"Speaker_id": 1, "Utterance_id": 7, "Content": "Because we know animal farming and fishing are a leading cause of the climate.", "Enhancing": ["Climate and environment protection", "Environmental protection", "Climate change prevention", "Environmental responsibility"], "Undercutting": ["Environmental harm", "Protecting personal choice"]}, {"Speaker_id": 0, "Utterance_id": 8, "Content": "We know having a strictly vegan diet is bad for you as well.", "Enhancing": ["Human health concerns", "Vegan diet health concerns", "Personal freedom", "Health concerns", "Individual choice"], "Undercutting": ["Health concerns", "Vegan diet", "Vegan diet is healthy"]}, {"Speaker_id": 1, "Utterance_id": 9, "Content": "Well that's not true.", "Enhancing": ["Vegan diet is healthy"], "Undercutting": ["Health misinformation", "Vegan diet health concern", "Vegan diet", "Health concerns"]}, {"Speaker_id": 0, "Utterance_id": 10, "Content": "True a lot of science says it's bad for you. What do you eat? Do we eat almonds? Should you eat almond milk?", "Enhancing": ["Health value", "Vegan diet health concern", "Health concerns on vegatarian diet"], "Undercutting": ["4", "Vagan diet", "Vegan diet is healthy"]}]} \  
    '''

    print(initial_hint)
    
    return
    with open(file_name) as f:
        data = json.load(f)

    # Iterate over each object in the list
    i = 0
    total_conflicts = 0
    result_data = []
    for conv in data:
        conv_data = {}
        conv_data["topic"] = conv["Topic"]
        conv_data["id"] = i
        
        # Iterate over each conversation in the list
        # check the conflict in the given conversation obj
        print("=======Checking conflict in conversation_id: ", i)
        print("Topic: ", conv["Topic"])
        print("Speaker count: ", conv["Speaker_count"])
        gt_conflicts = ground_truth(conv)
        total_conflicts += len(gt_conflicts)
        conv_data["count"] = len(gt_conflicts)
        conv_data["conflicts"] = gt_conflicts
        i += 1
        result_data.append(conv_data)
    return result_data


def ground_truth_detector(file_name):
    with open(file_name) as f:
        data = json.load(f)
    
    # Iterate over each object in the list
    i = 0
    total_conflicts = 0
    result_data = []
    for conv in data:
        conv_data = {}
        conv_data["topic"] = conv["Topic"]
        conv_data["id"] = i
        
        # Iterate over each conversation in the list
        # check the conflict in the given conversation obj
        print("=======Checking conflict in conversation_id: ", i)
        print("Topic: ", conv["Topic"])
        print("Speaker count: ", conv["Speaker_count"])
        print("----ground truth check result:")
        gt_conflicts = ground_truth(conv)
        total_conflicts += len(gt_conflicts)
        conv_data["count"] = len(gt_conflicts)
        conv_data["conflicts"] = gt_conflicts
        i += 1
        result_data.append(conv_data)
    return result_data
                   
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
            utter1_enhancing += [v.strip().lower() for v in assess1["Enhancing"] if v != "NA"]
            utter1_undercutting += [v.strip().lower() for v in assess1["Undercutting"] if v != "NA"]
        
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
                utter2_enhancing += [v.strip().lower() for v in assess2["Enhancing"] if v != "NA"]
                utter2_undercutting += [v.strip().lower() for v in assess2["Undercutting"] if v != "NA"]
            # check if the two utterance conflict with each other
            conflict_values = [v for v in utter1_enhancing if v in utter2_undercutting]
            if conflict_values != []:
                print("Conflict found!")
                print(f"Conflict between utterance {utter1_id} and {utter2_id}, speaker {speaker1_id} and {speaker2_id}")
                print("Conflict value: ", set(conflict_values))
                print()
                rlt.append({"utter1": utter1_id, "utter2": utter2_id, "speaker1": speaker1_id, "speaker2": speaker2_id, "moral_principle": list(set(conflict_values))})
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
            # remove any prefixing spaces and to lower cases
            utter1_enhancing = utter1_enhancing.strip().lower()
            utter2_undercutting = utter2_undercutting.strip().lower()
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
            # remove any prefixing spaces and to lower cases
            utter1_enhancing = utter1_enhancing.strip().lower()
            utter2_undercutting = utter2_undercutting.strip().lower()
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
    # benchmark_set = ["gun_violence_annotation_gpt-4.json", "vegan_immigration_full_annotation_gpt-4.json", "abortion_transgender_full_annotation_gpt-4.json"]
    # for benchmark in benchmark_set:
    #     print("====Evaluating benchmark: ", benchmark)
    #     result_data = ground_truth_detector(benchmark)
    #     ground_truth_data += result_data
    # benchmark_set = ["gun_violence_annotation_gpt-4.json"]
    input_file = "annotated_data_union.json"
    res = prepare_example()
    with open("prompt_vegan", "w") as f:
        f.write(res)
    # generate ground truth data
    # ground_truth_data = ground_truth_detector(input_file)

    # with open("ground_truth_data.json", "w") as json_file:
    #     json.dump(ground_truth_data, json_file)
        
    # statistics = {}
       
    # print(f"total conflict count: {conflict_count}")
    # print(f"total detected count: {detected_count}")
    # print(f"total correct count: {correct_count}")
    # print(f"----prediction accuracy: {float(correct_count) / float(conflict_count)}")
    # print(f"statistics: {statistics}")
    
    # detect_conflict(input_file)
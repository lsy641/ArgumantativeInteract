import os
import openai
import json
import time
from conflict_detector_gpt4_pm import prepare_example, give_query
openai.organization = "org-gcDzLqviJ8Ot15L4nFeIgR5L"
openai.api_key = open("api_key", "r").read()

RawInputName = "prompt_vegan"
# AutoAnnatationOutputname = RawInputName+"annotation_wo_human_"


model="gpt-4" #or gpt-4
# AutoAnnatationOutputname+=model
params = {'temperature':1.0, 'max_tokens':2940, 'n':1}
# with open("prompt_vegan", "r") as f:
#    data = f.read()
  
# last_command = {"role":"user", "content": data}

with open("annotated_data_union_test.json") as f:  
    convs = json.load(f)
    
examples = prepare_example()   
print(examples.keys())
for conv in convs:
    temp_prompt = ""
    queries = give_query(conv)
    temp_prompt = examples[conv["Topic"]][0]
    temp_prompt += queries[0]
    
    last_command = {"role":"user", "content": temp_prompt}
    print(temp_prompt)
    while True:
        try:
            response = openai.ChatCompletion.create(model=model, 
                                                    messages=[last_command], **params)
        except Exception as e:
            print(e)               
            time.sleep(1.0)        
        else:
            break
    print(response["choices"][0]["message"]["content"])   
    
    names = []
    for pre_id, pre_item in enumerate(conv["Conversation"]): 
        for lat_id, lat_item in enumerate(conv["Conversation"]):  
            names.append((pre_item["Speaker_id"],pre_item["Utterance_id"],lat_item["Speaker_id"],lat_item["Utterance_id"]))

    for idx, query in enumerate(queries[1:]):
        temp_prompt = examples[conv["Topic"]][0] + examples[conv["Topic"]][1] + queries[0] + response["choice"][0]["message"]["content"] + query
        print(temp_prompt)
        last_command = {"role":"user", "content": temp_prompt}
                    
        while True:
            try:
                response = openai.ChatCompletion.create(model=model, 
                                                        messages=[last_command], **params)
            except Exception as e:
                print(e)               
                time.sleep(1.0)        
            else:
                break 
        
        print(response["choices"][0]["message"]["content"]) 
        
        # names[idx],response["choice"][0]["message"]["content"]
                  
# choicel = []
# for choice in response["choices"]:
#     print(choice["message"]["content"])
#     choicel.append(choice["message"]["content"])
# convs[c_id]["Conversation"][u_id]["Undercutting"] = choicel
                
# with open(AutoAnnatationOutputname+'.json',"w") as f:
#     json.dump(convs, f, indent=1)
# # break
# except:
#     print("Too long!",utter)
# # break
import os
import openai
import json
import time
openai.organization = "org-gcDzLqviJ8Ot15L4nFeIgR5L"
openai.api_key = open("api_key", "r").read()

RawInputName = "abortion_transgender_data.json"
AutoAnnatationOutputname = "abortion_transgender_annotation_wo_human_"


model="gpt-4"
AutoAnnatationOutputname+=model
# RawInputName=AutoAnnatationOutputname+'.json'
params = {'temperature':0.7, 'max_tokens':2048, 'n':5}
initial_hint = "By looking through the below conversations where people are arguing on a controversial topic, you are able to infer the moral principle or the intrinsic value of each speaker according to what they say in each turn."

with open(RawInputName, "r") as f:
   convs = json.load(f)
  
for c_id, conv in enumerate(convs):
        messages = [{"role":"system", "content":initial_hint}]  
        text = ""
        for utter in conv["Conversation"]:
            prefix = f'Speaker {utter["Speaker_id"]}-Utterance {utter["Utterance_id"]}'
            utterance = f'{prefix}: {utter["Content"]}\n'
            text += utterance
            
        for u_id, utter in enumerate(conv["Conversation"]):
            try:
                if ('Enhancing' not in utter) or ('Undercutting' not in utter):
                    prefix = f'Speaker {utter["Speaker_id"]}-Utterance {utter["Utterance_id"]}'
                    last_command = {"role":"user", "content": text + f"Is the {prefix} supporting a certain moral principle or intrinsic value? Reply me NA if it is not. Otherwise, infer the moral principle or the intrinsic value that {prefix} is supporting or enhancing or phraising. Answer me with a phrase within 4 words"}
                    
                    while True:
                        try:
                            response = openai.ChatCompletion.create(model=model, 
                                                                    messages=messages + [last_command], **params)
                        except Exception as e:
                            print(e)
                        else:
                            break
                    

                    # print(messages + [last_command])
                    choicel = []
                    for choice in response["choices"]:
                        print(choice["message"]["content"])
                        choicel.append(choice["message"]["content"])    
                    convs[c_id]["Conversation"][u_id]["Enhancing"] = choicel
                    
                    time.sleep(1.0)  
                    
                    messages.append(last_command)   
                    last_command = {"role": "assistant", "content": f'{choicel[0]}'}
                    messages.append(last_command) 

                    last_command = {"role":"user", "content": text + f"Is the {prefix} against a certain moral principle or intrinsic value that might be hold by other speakers? Reply me NA if it is not. Otherwise, infer the moral principle or the intrinsic value that {prefix} is opposing or undercutting or attacking. Answer me with a phrase within 4 words."}
                    
                    while True:
                        try:
                            response = openai.ChatCompletion.create(model=model, 
                                                                    messages=messages + [last_command], **params)
                        except Exception as e:
                            print(e)
                        else:
                            break                    
                    # print(messages + [last_command])
                    choicel = []
                    for choice in response["choices"]:
                        print(choice["message"]["content"])
                        choicel.append(choice["message"]["content"])
                    convs[c_id]["Conversation"][u_id]["Undercutting"] = choicel
                
                with open(AutoAnnatationOutputname+'.json',"w") as f:
                    json.dump(convs, f, indent=1)
                # break
            except:
                print("Too long!",utter)
        # break
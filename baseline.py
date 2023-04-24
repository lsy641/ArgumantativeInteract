import os
import openai
import json
import time
openai.organization = "org-gcDzLqviJ8Ot15L4nFeIgR5L"
openai.api_key = open("api_key", "r").read()

model = "gpt-4"  # or gpt-3.5-turbo
params = {'temperature': 1.0, 'max_tokens': 2048, 'n': 1}
disc_params = {'temperature': 1.0, 'max_tokens': 2048, 'n': 5}

initial_hints = {'symbolic': "You are able to judge if two phrases, which can be moral principles, intrinsic values, or moral concerns, are semantically equivalent to each other related to a specific topic.",
                 'semantic': "You are able to judge if two phrases, which can be moral principles, intrinsic values, or moral concerns, are semantically equivalent to each other related to a specific topic.",
                 'discourse': "You are able to find any pair of two utterances in a given conversation that conflict with each other regarding their intrinsic moral value.\n\
For example, given this conversation: \n\
Speaker 0-Utterance 1: I think women just want to sleep around and not have any consequence of it, you know, instead of taking personal accountability and being on birth control. They just want to do whatever they want.\n\
Speaker 1-Utterance 2: Do you have any care to empower women or is disempowering women part like these?\n\
Speaker 0-Utterance 3: You see, this is shame, insult and guilt that need to be right, okay? Why is it empowering to sleep around?\n\\n\
Speaker 1-Utterance 4: I do think the way you speak to women is very ... sort of like, ah, women just don't want to do this, women just don't have that... I just wonder why you have so much hatred towards women?!\n\
Utterance 2 conflicts with Utterance 3 because Speaker 1 is enhancing the empowerment of women while Speaker 0 is undercutting the empowerment of women."}


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
            utter1_enhancing += [v.strip().lower()
                                 for v in assess1["Enhancing"] if v != "NA"]
            utter1_undercutting += [v.strip().lower()
                                    for v in assess1["Undercutting"] if v != "NA"]

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
                utter2_enhancing += [v.strip().lower()
                                     for v in assess2["Enhancing"] if v != "NA"]
                utter2_undercutting += [v.strip().lower()
                                        for v in assess2["Undercutting"] if v != "NA"]
            # check if the two utterance conflict with each other
            conflict_values = [
                v for v in utter1_enhancing if v in utter2_undercutting]
            if conflict_values != []:
                print("Conflict found!")
                print(
                    f"Conflict between utterance {utter1_id} and {utter2_id}, speaker {speaker1_id} and {speaker2_id}")
                print("Conflict value: ", set(conflict_values))
                print()
                rlt.append((utter1_id, utter2_id))
    return rlt


def symbolic_check(con, messages=None):
    enhancing_dict = {}
    undercutting_dict = {}
    utters = []
    rlt = []
    for utter1 in conv["Conversation"]:
        utter1_id = utter1["Utterance_id"]
        speaker1_id = utter1["Speaker_id"]
        utter1_enhancing = max(
            utter1["Enhancing"], key=utter1["Enhancing"].count)
        utter1_undercutting = max(
            utter1["Undercutting"], key=utter1["Undercutting"].count)

        for utter2 in conv["Conversation"]:
            utter2_id = utter2["Utterance_id"]
            speaker2_id = utter2["Speaker_id"]
            if utter1_id == utter2_id or speaker1_id == speaker2_id:
                continue
            utter2_enhancing = max(
                utter2["Enhancing"], key=utter2["Enhancing"].count)
            utter2_undercutting = max(
                utter2["Undercutting"], key=utter2["Undercutting"].count)
            # check if the two utterance conflict with each other with simple symbolic check
            conflict = utter1_enhancing == utter2_undercutting and (
                utter1_enhancing != "NA" or utter2_undercutting != "NA")
            if conflict:
                print("Conflict found!")
                print(
                    f"Conflict between utterance {utter1_id} and {utter2_id}, speaker {speaker1_id} and {speaker2_id}")
                print(
                    f"Reason: enhancing \"{utter1_enhancing}\" vs. undercutting \"{utter2_undercutting}\"")
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
        utter1_enhancing = max(
            utter1["Enhancing"], key=utter1["Enhancing"].count)
        utter1_undercutting = max(
            utter1["Undercutting"], key=utter1["Undercutting"].count)

        for utter2 in conv["Conversation"]:
            utter2_id = utter2["Utterance_id"]
            speaker2_id = utter2["Speaker_id"]
            if utter1_id == utter2_id or speaker1_id == speaker2_id:
                continue
            utter2_enhancing = max(
                utter2["Enhancing"], key=utter2["Enhancing"].count)
            utter2_undercutting = max(
                utter2["Undercutting"], key=utter2["Undercutting"].count)
            if utter1_enhancing == "NA" or utter2_undercutting == "NA":
                continue
            # check if the two utterance conflict with each other with semantic equivalence
            last_command = {
                "role": "user", "content": f"Is \"{utter1_enhancing}\" and \"{utter2_undercutting}\" semantically equivalent under the topic of \"{topic}\"? Answer me Yes or No."}
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
                print(
                    f"Conflict between utterance {utter1_id} and {utter2_id}, speaker {speaker1_id} and {speaker2_id}")
                print(
                    f"Reason: enhancing \"{utter1_enhancing}\" vs. undercutting \"{utter2_undercutting}\"")
                print("Conflict detector type: Semantic")
                print()
                rlt.append((utter1_id, utter2_id))
    return rlt


def discourse_check(conv, messages):
    text = ""
    for utter in conv["Conversation"]:
        prefix = f'Speaker {utter["Speaker_id"]}-Utterance {utter["Utterance_id"]}'
        utterance = f'{prefix}: {utter["Content"]}\n'
        text += utterance

    last_command = {"role": "user", "content": f"Please find all conflict pairs of utterances in this conversation: {text}\n\
    Reply in a list of utterance id pairs (e.g. [('Utterance a','Utterance b'),('Utterance c','Utterance d')]) without explanations. If there's no conflict, reply an empty list."}
    while True:
        try:
            print("sending message...")
            response = openai.ChatCompletion.create(model=model,
                                                    messages=messages + [last_command], **disc_params)
        except Exception as e:
            print(messages)
            print(e)
            time.sleep(1.0)
        else:
            break
    responses = [response["choices"][i]["message"]["content"]
                 for i in range(disc_params["n"])]
    conflicts = eval(max(responses, key=responses.count))
    conflicts = [(int(a.split(' ')[-1]), int(b.split(' ')[-1]))
                 for a, b in conflicts]
    return conflicts


check_func = {'symbolic': symbolic_check,
              'semantic': semantic_check, 'discourse': discourse_check}


def detect_conflict(file_name, check_method):
    # Open the JSON file
    with open(file_name) as f:
        data = json.load(f)
    messages = [{"role": "system", "content": initial_hints[check_method]}]

    # Iterate over each object in the list
    i = 1
    total_conflicts = 0
    symbolic_count = 0
    semantic_count = 0
    correct_count = 0
    for conv in data:
        print("=======Checking conflict in conversation_id: ", i)
        print("Topic: ", conv["Topic"])
        print("Speaker count: ", conv["Speaker_count"])
        print("----ground truth check result:")
        gt_conflicts = ground_truth(conv)

        print("----" + check_method + " check result:")
        semantic_conflicts = check_func[check_method](conv, messages)
        print(semantic_conflicts)
        semantic_count += len(semantic_conflicts)

        # calculate the accuracy
        total_conflicts += len(gt_conflicts)
        correct_count += len([u for u in semantic_conflicts if u in gt_conflicts])
        print(
            f"----{check_method} check accuracy: {float(semantic_count) / float(total_conflicts)}")
        i += 1
        print("total_conflicts, " + check_method+"_count, correct_count: ",
              total_conflicts, semantic_count, correct_count)
    return total_conflicts, semantic_count, correct_count


if __name__ == "__main__":
    benchmark_set = ["annotated_data.json"]
    checking_method = 'discourse'
    statistics = {}

    conflict_count = 0
    detected_count = 0
    correct_count = 0
    for benchmark in benchmark_set:
        print("====Evaluating benchmark: ", benchmark)
        conflict_cnt, detected_cnt, correct_cnt = detect_conflict(
            benchmark, checking_method)
        conflict_count += conflict_cnt
        detected_count += detected_cnt
        correct_count += correct_cnt
        statistics[benchmark] = (conflict_cnt, detected_cnt, correct_cnt, float(
            correct_cnt) / float(conflict_cnt))

    print(f"total conflict count: {conflict_count}")
    print(f"total detected count: {detected_count}")
    print(f"total correct count: {correct_count}")
    print(
        f"----prediction accuracy: {float(correct_count) / float(conflict_count)}")
    print(f"statistics: {statistics}")

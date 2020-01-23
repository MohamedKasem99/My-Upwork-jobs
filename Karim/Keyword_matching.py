import utils
import re
from ner import NER
import NFile_utils
extractor = NER()
pd = utils.pd

xls = pd.ExcelFile('strings stems.xlsx')
first = pd.read_excel(xls, 'first').dropna(axis=1, how='all').dropna(axis=0, how='all')
parent_second = pd.read_excel(xls, 'parent second').dropna(axis=1, how='all').dropna(axis=0, how='all')
tutoring = pd.read_excel(xls, 'Tutoring').dropna(axis=1, how='all').dropna(axis=0, how='all')
bad_keywords= pd.read_excel(xls, 'bad keywords').dropna(axis=1, how='all').dropna(axis=0, how='all')
at_least_another= pd.read_excel(xls, 'at least another').dropna(axis=1, how='all').dropna(axis=0, how='all')
payments = pd.read_excel(xls, 'payments').dropna(axis=1, how='all').dropna(axis=0, how='all')
contract = pd.read_excel(xls, 'contract').dropna(axis=1, how='all').dropna(axis=0, how='all')


first_extract =  NFile_utils.first_extract_df
second_extract = NFile_utils.second_extract_df

utils.pre_process_df_keywords(parent_second)
utils.pre_process_df_keywords(first)
utils.pre_process_df_keywords(bad_keywords)

def extract_pay_info(second_extract, extractor):
    extracted_pay = pd.DataFrame({"field": second_extract['field3'].values, 
              "Res": list(map(extractor.extract_entities_dict,(map(utils.append_sapces,second_extract['field3'].values)))),
              "Decesion": [" "] * len(second_extract['field3'].values)
             })
    for indx, item in enumerate(extracted_pay["Res"]):
        if len(item) != '' and ("money" in item.keys() or 'cardinal' in item.keys()):
            temp = re.findall(r'\d+', str(item.values()).replace(',',""))
            try:
                extracted_pay.iloc[indx]['Decesion'] = min(list(map(int, temp)))
            except:
                extracted_pay.iloc[indx]['Decesion'] = -1
        else:
            extracted_pay.iloc[indx]['Decesion'] = -1

    return extracted_pay



raw_posts = [title + "\n\n" + body for title, body in zip(second_extract["field1"], second_extract["field2"])]
extracted_pay = extract_pay_info(second_extract,extractor)

raw_job_post = raw_posts[-1]
raw_job_post = """
My name is Jack, the designer of Bellorita handbags (bellorita.com). We are working on a 90-second video ad on facebook. We need a video editor to help us edit the video with text, image, and footage overlay to go with the script and spokewoman.

Right now the script (225 words) is ready, but the spokewoman video is not yet, and we need your suggestion on how we need her to performe to smooth your video editing.


Please note that this is an easy project, and we want the lowest rate possible. Thank you.

I will pay through cash app and I need to sign an NDA form

Sincerely
Jack
"""
indx = -1
generated_email = ""
#print(raw_job_post,"\n\n\n>>>>>\n\n",extracted_pay.iloc[indx]["Decesion"])

raw_job_post = raw_job_post.lower()

job_post = utils.pre_process(raw_job_post)
if len(raw_job_post) < 5 and len(raw_job_post.split()) <2:
    print(f"Breaking!! because is too short\n\n")
    #continue


if any(utils.step_1(raw_job_post, utils.get_two_word(job_post), bad_keywords)):
    print(f"Breaking!! because {utils.step_1(raw_job_post, utils.get_two_word(job_post), bad_keywords)} detected\n\n") 
    #continue

first_result = utils.find_workers(raw_job_post, job_post, first)[0]
highest_match = utils.find_workers(raw_job_post, job_post, first)[1]
parent_second_result = utils.find_workers(raw_job_post, job_post, parent_second)[0]
tutoring_result = utils.find_workers(raw_job_post, job_post, tutoring)[0]
pay_amount = extracted_pay.iloc[indx]["Decesion"]
pay_amount = 100
pay_method = utils.find_matching_key_word(job_post,payments)
contract_type = utils.find_matching_key_word(job_post,contract)


formatted_first = ""
formatted_second_parent = ""
formatted_pay = ""
formatted_tutoring = ""
formatted_pay_method = ""
formatted_contract_type = ""
formatted_sample = ""

is_sample = False
is_tutor = any(tutoring_result)
is_payment_method = any(pay_method)
is_contract_type = any(contract_type)

if any(first_result):

    if "someone" not in first_result:
        if len(first_result) == 1: formatted_first = first_result[0]
        elif len(first_result) == 2: formatted_first = f"{first_result[0]} and {first_result[1]}"
        elif len(first_result) == 3: formatted_first = f"{first_result[0]}, {first_result[1]} and {first_result[2]}"
        else: formatted_first = "someone"
    else: formatted_first = "someone"


    if any(parent_second_result):
        if len(parent_second_result) == 1: formatted_second_parent = parent_second_result[0]
        elif len(parent_second_result) == 2: formatted_second_parent = f"{parent_second_result[0]} and {parent_second_result[1]}"
        elif len(parent_second_result) == 3: formatted_second_parent = f"{parent_second_result[0]}, {parent_second_result[1]} and {parent_second_result[2]}"
        else: formatted_second_parent = "many things"
        is_sample = any(['x' in parent_second[i].values for i in parent_second_result])
    

else:
    print(f"Breaking because no first parent found")
    #continue



formatted_second_parent_final =f"well versed in {formatted_second_parent} and I can help you with that!" if formatted_second_parent != "" else ""
cond_1 = f"I see that you are looking for {formatted_first} {formatted_second_parent_final}"

if pay_amount > 0:
    formatted_pay = f""" Hence, I am willing to offer you this service for {pay_amount*0.8} instead of {pay_amount}"""
else:
    formatted_pay = """In this instance and rather than providing you with a quote as I assume you are on a budget, 
    I would prefer to ask you how much are you expecting to pay for this service? if it is reasonable, 
    I would gladly offer you my services. """

if is_tutor:
    formatted_tutoring = """
    As I understood, you are seeking someone to teach you how to do things instead of providing you with the services. 
    What I generally do for my clients would be that I would ask you to provide me details regarding a specific project 
    you have in mind, and I would self-record myself doing it. This will enable you to skip the learning of basics and 
    ancillary things and learn exactly what you want. You will have the video showing every movements and actions being 
    made from scratch to the result. I will also provide you, if needed, the resulting work."""

if is_sample:
    formatted_sample = """
    Feel free to have a look at my samples:
    """

if is_payment_method:
    formatted_pay_method = f"""
    I am fine to accept payments with {pay_method[0]} as you have mentioned it within your posting.
    """
else:
    formatted_pay_method = f"""I accept payments through Paypal as it is the only platform that provides a buyer’s protection for you. 
    I could send you an invoice for the service provided if needed. However, if you have other preferences, feel free to let me know.
    """

if is_contract_type:
    formatted_contract_type = f"""I am also willing, per your request to provide you/sign a {contract_type[0]} at your request.
    """

generated_email = f"""
Greetings, 

{cond_1}


My name is Karim and I am looking forward to fostering a long-term relationship with you or become your go-to service provider 
for any related future inquiries. 

{formatted_pay}
{formatted_tutoring}
{formatted_sample}
{formatted_pay_method}
{formatted_contract_type}

If interested or have any further questions, feel free to reach me at your earliest convenience and by your preferred mean of communication.
Sincerely, 
Karim
karimafilal@hotmail.com
(408) 393-4260

"""

print(generated_email)


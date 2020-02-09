import utils
import time
import re
import os
import NFile_script
from ner import NER
from email_sender import send_mail


extractor = NER()
pd = utils.pd

import run_api
xls = pd.ExcelFile('strings stems.xlsx')
first = pd.read_excel(xls, 'first').dropna(axis=1, how='all').dropna(axis=0, how='all')
parent_second = pd.read_excel(xls, 'parent second').dropna(axis=1, how='all').dropna(axis=0, how='all')
tutoring = pd.read_excel(xls, 'Tutoring').dropna(axis=1, how='all').dropna(axis=0, how='all')
bad_keywords= pd.read_excel(xls, 'bad keywords').dropna(axis=1, how='all').dropna(axis=0, how='all')
at_least_another= pd.read_excel(xls, 'at least another').dropna(axis=1, how='all').dropna(axis=0, how='all')

payments = pd.read_excel(xls, 'payments').dropna(axis=1, how='all').dropna(axis=0, how='all')
contract = pd.read_excel(xls, 'contract').dropna(axis=1, how='all').dropna(axis=0, how='all')


utils.pre_process_df_keywords(parent_second)
utils.pre_process_df_keywords(first)
utils.pre_process_df_keywords(bad_keywords)


Nfiles_df_list, first_extract, second_extract, third_extract = run_api.Nfiles_df_list, run_api.first_extract_df, run_api.second_extract_df, run_api.third_extract_df
extracted_pay = utils.extract_pay_info(second_extract,extractor)

first_extract.rename(inplace=True, columns={"field1_Text_Text": "title", "field1_Link_Link": "link"})
first_extract = run_api.cleanup_df(first_extract,"title")
second_extract = run_api.cleanup_df(second_extract,"field1")
third_extract = run_api.cleanup_df(third_extract,"email")


second_extract_pay_appended = second_extract.reset_index().merge(extracted_pay.reset_index(), on="index",how="left").drop(["index","field","Res"],axis=1)
all_info = second_extract_pay_appended.merge(third_extract, on= "field1", how="left").dropna().drop_duplicates(subset = "email")
all_info.rename(columns={"field1": "title", "field2":"body", "field3": "compensation","email": "email", "Decesion":"pay_amount"}, inplace=True)
all_info.drop_duplicates(inplace=True)

all_info = all_info.merge(first_extract, on= "title", how="left").dropna().drop_duplicates(subset = "title")

try:
    sent = pd.read_csv("sent.csv")
except:
    sent = pd.DataFrame(columns = ["gig"])
    sent.to_csv("sent.csv", index = False)
if len(all_info) != 0:

    for title, body, pay_amount, rate, cl_email, link in  zip(all_info["title"], all_info["body"], all_info["pay_amount"], all_info["amount"], all_info["email"], all_info["link"]):
        
        raw_job_post = title + "\n\n" + body

        if raw_job_post.strip() in sent.values:
            print("Breaking because already sent")
            continue
        else:
            sent = pd.DataFrame(sent["gig"].append(pd.Series(raw_job_post.strip()), ignore_index=True), columns = ["gig"])
            sent.to_csv("sent.csv", index=False)

        generated_email = ""
        
        raw_job_post = raw_job_post.replace("QR Code Link to This Post", "").lower()

        job_post = utils.pre_process(raw_job_post)
        
        if len(raw_job_post) < 5 and len(raw_job_post.split()) <2:
            print(f"Breaking!! because is too short\n\n")
            continue


        if any(utils.step_1(raw_job_post, utils.get_two_word(job_post), bad_keywords)):
            print(f"Breaking!! because {utils.step_1(raw_job_post, utils.get_two_word(job_post), bad_keywords)} detected\n\n") 
            continue

        first_result = utils.find_workers(raw_job_post, job_post, first, at_least_another)[0]
        highest_match = utils.find_workers(raw_job_post, job_post, first, at_least_another)[1]
        parent_second_result = utils.find_workers(raw_job_post, job_post, parent_second)[0]
        tutoring_result = utils.find_workers(raw_job_post, job_post, tutoring)[0]

        pay_method = utils.find_matching_key_word(job_post,payments)
        contract_type = utils.find_matching_key_word(job_post,contract)

        samples=[]
        for file_name in parent_second_result:
            path = f"samples/{file_name}.txt"
            if os.path.isfile(path):
                try:
                    with open(path,"r") as file:
                        sample = file.read().strip()
                    samples.append(sample + "\n\n")
                except:
                    print("problem with file: ", file_name)

        formatted_first = ""
        formatted_second_parent = ""
        formatted_pay = ""
        formatted_tutoring = ""
        formatted_pay_method = ""
        formatted_contract_type = ""
        formatted_sample = ""
        formatted_subject = ""
        
        is_sample = any(samples)
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
                is_sample = any(['karim' in parent_second[i].values for i in parent_second_result])


        else:
            print(f"Breaking because no first parent found")
            continue



        formatted_second_parent_final =f"well versed in {formatted_second_parent} and I can help you with that!" if formatted_second_parent != "" else ""
        cond_1 = f"I see that you are looking for {formatted_first} {formatted_second_parent_final}"

        if pay_amount > 0:
            formatted_pay = f""" Hence, I am willing to offer you this service for ${int(pay_amount*0.8)} instead of ${pay_amount}"""
            formatted_subject = f"""${int(pay_amount*0.8)} instead of ${pay_amount} {title}"""
        else:
            formatted_pay = """In this instance and rather than providing you with a quote as I assume you are on a budget, I would prefer to ask you how much are you expecting to pay for this service? if it is reasonable, I would gladly offer you my services. """
            formatted_subject = title
        if is_tutor:
            formatted_tutoring = """As I understood, you are seeking someone to teach you how to do things instead of providing you with the services. What I generally do for my clients would be that I would ask you to provide me details regarding a specific project you have in mind, and I would self-record myself doing it. This will enable you to skip the learning of basics and ancillary things and learn exactly what you want. You will have the video showing every movements and actions being made from scratch to the result. I will also provide you, if needed, the resulting work."""

        if is_sample:
            for i in samples:
                formatted_sample += i
        # else:
        #     print("Breaking because no samples are found")
        #     continue

        if is_payment_method:
            formatted_pay_method = f"""I am fine to accept payments with {pay_method[0]} as you have mentioned it within your posting.
            """
        else:
            formatted_pay_method = f"""I accept payments through Paypal as it is the only platform that provides a buyer’s protection for you. 
    I could send you an invoice for the service provided if needed. However, if you have other preferences, feel free to let me know.
            """

        if is_contract_type:
            formatted_contract_type = f"""I am also willing, per your request to provide you/sign a {contract_type[0]} at your request.
            """

        generated_email = f"""
    client_email: {cl_email}

    web_link: {link}

    Greetings,
    {cond_1}

    My name is Karim and I am looking forward to fostering a long-term relationship with you or become your go-to service provider for any related future inquiries.
    {formatted_pay}
    {formatted_tutoring}
    {formatted_sample}
    {formatted_pay_method}
    {formatted_contract_type}

    If interested or have any further questions, feel free to reach me at your earliest convenience and by your preferred mean of communication.
    Sincerely, 
    Karim
    karimafilal@hotmail.com
    (408) 393-4260 """

        send_mail(formatted_subject, generated_email, "firstenaction@gmail.com", "CastirlaCorte56", "karimafilal@hotmail.com")
        print(generated_email)

else:
    print("NO NEW INFORMATION WAS EXTRACTED")



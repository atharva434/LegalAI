from .LLM import llm
from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, validator
from typing import List

class draft(BaseModel):
    section: str = Field(description="Title of the section")
    description: str = Field(description="Description of the section")
parser = PydanticOutputParser(pydantic_object=draft)

def intro(emp_name,company_name,emp_title,company_title,date):
    introduction={"nda":f"""This Employee Confidentiality and Non-Disclosure Agreement (the "Agreement") is entered into between {company_name}, a {company_title} (hereinafter referred to as the "Company"), and {emp_name} {emp_title} (hereinafter referred to as the "Employee"), effective as of {date}.""",}
    return introduction


def nda_sections():
    sections={"Confidential Information":"The Employee agrees not to disclose or use any confidential information of the Company obtained during their engagement, except when required by law or in the ordinary course of their duties. In cases where legal disclosure is necessary, the Employee will promptly notify the Company and cooperate in protecting the confidentiality of such information.",
          "Developments":"Any developments or intellectual property created by the Employee during their engagement with the Company, related to the Company's business or resulting from their tasks, shall become the sole property of the Company. The Employee shall promptly disclose and assign all rights to these developments to the Company without any additional compensation. The Employee may be credited as an inventor in intellectual property filings by the Company.",
          "Equitable Relief":"In the event of a breach of this Agreement by the Employee, the Company reserves the right to seek equitable remedies, such as injunctions or specific performance, in addition to any legal remedies, to prevent such breaches.",
          "No Conflicting Agreements":"The Employee represents that their performance under this Agreement will not violate any prior agreements they have to keep confidential information confidential. The Employee also commits not to enter into any conflicting agreements while working for the Company.",
          "Amendments and Waivers":"Any changes or waivers to this Agreement must be made in writing and signed by the Company to be effective. A waiver of one breach of this Agreement does not waive any future breaches.",
          "Severability": "Each provision in this Agreement is separate and independent. The unenforceability of one provision does not affect the enforceability of the others. If any provision is found to be overly broad, a court may modify it to make it enforceable to the maximum extent permitted by law.",
          "Survival": "Each provision in this Agreement is separate and independent. The unenforceability of one provision does not affect the enforceability of the others. If any provision is found to be overly broad, a court may modify it to make it enforceable to the maximum extent permitted by law.",
          "Company":"The term `Company` as used in this Agreement includes the entity mentioned in the introduction paragraph, as well as its predecessors, parents, subsidiaries, subdivisions, affiliates, and successors. The Company reserves the right to assign this Agreement, and all its covenants and agreements shall benefit the Company and its successors.",
          "Governing Law and Jurisdiction":"This Agreement shall be governed by the laws of the jurisdiction where the Company is organized, without considering conflict of law’s provisions. The Employee waives claims of an inconvenient forum and consents to personal jurisdiction and venue in the jurisdiction where the Company's registered office is located for any lawsuits related to this Agreement. However, the Company can seek equitable relief in any jurisdiction to enforce the Agreement."}
    return sections

def add(doc_type,section_name, section_desc=""):
    add_sec = f"""Add another section to "{doc_type}" agreement. Title of section is "{section_name}" and the brief description about that section is "{section_desc}". Do not add any other comments, just return the section name and your generated description. Do not add a lot of jargon.
        Example for the tone of generating description is:
        {{"section":"Confidential Information" , "description":"The Employee agrees not to disclose or use any confidential information of the Company obtained during their engagement, except when required by law or in the ordinary course of their duties. In cases where legal disclosure is necessary, the Employee will promptly notify the Company and cooperate in protecting the confidentiality of such information."}} 
    """

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    _input = prompt.format_prompt(query=add_sec)
    model=llm()
    output = model(_input.to_string())
    added_sec = parser.parse(output)
    print(added_sec)
    section_name = added_sec.section
    desc = added_sec.description
    
    return section_name, desc

def amend(doc_type, section_name, add, sections):
    orignal_content=sections[section_name] #This is og para
    amend_sec = f"""Amend this section of "{doc_type}" agreement by adding a few lines based on these points "{add}". The original paragraph is "{section_name}" and description is "{orignal_content}". Do not delete any of the previous content, just add lines to it. Do not return anything in your answer except section name and its description.
        Example for the tone of generating description is:
        {{"section":"Confidential Information" , "description":"The Employee agrees not to disclose or use any confidential information of the Company obtained during their engagement, except when required by law or in the ordinary course of their duties. In cases where legal disclosure is necessary, the Employee will promptly notify the Company and cooperate in protecting the confidentiality of such information."}} 
    """

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    _input = prompt.format_prompt(query=amend_sec)
    model=llm()
    output = model(_input.to_string())
    added_sec = parser.parse(output)
    print(added_sec)
    section_name = added_sec.section
    desc = added_sec.description
    
    return desc
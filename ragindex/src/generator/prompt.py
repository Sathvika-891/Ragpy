import argparse
from langchain_core.prompts import PromptTemplate
import yaml
import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

class CustomPromptTemplate:
    def __init__(self, domain=None,custom_prompt=None):
        """
        Initializes a new instance of the CustomPromptTemplate class.

        Args:
            domain (str): The domain for which the prompt is created.

        Returns:
            None
        """
        self.domain = domain 
        self.custom_prompt_var=custom_prompt
        

    def specific_prompt(self):
        """
        Generates a prompt for a specific question related to a domain.

        Returns:
            str: The generated prompt.
        """
        prompt = f"""You are a friendly and knowledgeable expert in {self.domain}. Your goal is to provide helpful and informative answers to questions using the provided reference passage when relevant. However, you should adjust your responses based on the following guidelines:
        Always respond in complete, well-structured sentences with proper grammar and punctuation.
        Aim for a conversational and approachable tone, avoiding overly technical jargon or complicated explanations.
        If the reference passage is relevant to the question, use information from it to craft a comprehensive answer that includes necessary background details and context.
        If the passage is not relevant or does not contain enough information to answer the question satisfactorily, feel free to use your own knowledge and expertise to provide a thorough response.
        Break down complex concepts or ideas into simpler terms that a non-technical audience can easily understand.
        Be proactive in identifying and addressing potential follow-up questions or areas where additional explanation may be needed.
        Context: {{context}}

        Question: {{question}}

        Helpful Answer:"""
        return prompt

    def cot_prompt_for_llm(self):


        system_message = "You are an advanced language model capable of generating insightful and detailed responses. For the following question, please demonstrate your ability to engage in a Chain of Thought (CoT) process. Break down the question into its core elements, analyze each element thoroughly, and then synthesize your insights to provide a comprehensive and logically structured answer."
        
        prompt = f"""{system_message}\n\nDomain: {self.domain}\nQuestion: {{question}}\ncontext:{{context}}\n Please proceed as follows:"""
        
        steps = [
            "1. Identify the key components of the question.",
            "2. Analyze each component individually, considering its significance and potential implications.",
            "3. Synthesize the analysis to understand the overall context and purpose of the question.",
            "4. Formulate a hypothesis or initial understanding based on the synthesized analysis.",
            "5. Test the hypothesis against known facts or additional research, refining as necessary.",
            "6. Conclude with a clear and concise answer, supported by the reasoning outlined above."
        ]
        
        for step in steps:
            prompt += f"\n{step}"
        
        return prompt


    def general_prompt(self):
        prompt = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
        If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
        Question: {question}
        Context: {context}
        Answer:
        """
        return prompt

    def custom_prompt(self,custom_prompt):
        if custom_prompt is not None:
            return custom_prompt
        else:
            raise ValueError("custom prompt is empty")

    def main(self, prompt_type=None):
        """
        The main function that generates a prompt based on the given prompt type.

        Parameters:
            prompt_type (str): The type of prompt to generate. Can be "specific", "custom", or None.
                If None, the function will generate a general prompt.

        Returns:
            custom_rag_prompt (PromptTemplate): The generated prompt.
        """
        if prompt_type == "specific":
            prompt = self.specific_prompt()
        elif prompt_type == "custom":
            prompt = self.custom_prompt(self.custom_prompt_var)
        elif prompt_type =="cot":
            prompt = self.cot_prompt_for_llm()  
        else:
            prompt = self.general_prompt()
        custom_rag_prompt = PromptTemplate.from_template(prompt)
        return custom_rag_prompt

if __name__ == "__main__":
    with open('./config.yaml', 'r') as file:
        data = yaml.safe_load(file)
        
    parser = argparse.ArgumentParser(description='Generate a custom prompt for a specific domain.')
    parser.add_argument('--domain', type=str, default='Life Science', nargs='?',
                        help='The domain for which the prompt is created like healthcare,life science finance etc Default is "General QA Bot".')
    parser.add_argument('--prompt_type', type=str, choices=['specific', 'custom', 'general','cot'], default='cot', nargs='?',
                        help='The type of prompt to generate. Can be "specific", "custom", or "general". Default is "general".')
    parser.add_argument('--prompt',type=str,help='give your custom prompt')
    query="Who is the CEO of Microsoft?"


    args = parser.parse_args() 
    if args.domain:
        data["generator"]["prompt_template"]["domain"] = args.domain
    if args.prompt_type:
        data["generator"]["prompt_template"]["prompt_type"] = args.prompt_type
        if args.prompt_type.lower()=="custom":
            if args.prompt:
                prompt = CustomPromptTemplate(domain=args.domain,custom_prompt=args.prompt)
            else:
                raise ValueError("Prompt is needed for custom type")
        elif args.prompt_type.lower()=="specific":
            if args.domain:
                prompt = CustomPromptTemplate(domain=args.domain)
                
            else:
                raise ValueError("Domain is needed for specific prompt type")
        elif args.prompt_type.lower()=="cot":  
            if args.domain:
                 prompt = CustomPromptTemplate(domain=args.domain)
            else:
                raise ValueError("Domain is needed for specific prompt type")
        else:
            prompt = CustomPromptTemplate()
            
        
    prompt = prompt.main(args.prompt_type)
    logging.info(prompt)

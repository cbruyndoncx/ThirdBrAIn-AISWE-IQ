import argparse
import os
from dotenv import load_dotenv
from pocketgroq import GroqProvider
from typing import Optional
from prompt_canvas import PromptCanvas

load_dotenv()

DEFAULT_MODEL = os.getenv('GROMPT_DEFAULT_MODEL', 'llama-3.3-70b-versatile')
DEFAULT_TEMPERATURE = float(os.getenv('GROMPT_DEFAULT_TEMPERATURE', '0.5'))
DEFAULT_MAX_TOKENS = int(os.getenv('GROMPT_DEFAULT_MAX_TOKENS', '1024'))

def craft_system_message(canvas: Optional[PromptCanvas] = None, prompt: str = "") -> str:
    if canvas:
        return f"""You are a {canvas.persona} focused on delivering results for {canvas.audience}.

Task: {canvas.task}

Step-by-Step Approach:
{chr(10).join(f'- {step}' for step in canvas.steps)}

Context: {canvas.context}

References: {', '.join(canvas.references)}

Output Requirements:
- Format: {canvas.output_format}
- Tone: {canvas.tonality}"""
    else:
        return get_rephrased_user_prompt(prompt)

def get_rephrased_user_prompt(prompt: str) -> str:
    return f"""You are a professional prompt engineer. Optimize this prompt by making it clearer, more concise, and more effective.
    User request: "{prompt}"
    Rephrased:"""

def rephrase_prompt(prompt: str, 
                   model: str = DEFAULT_MODEL,
                   temperature: float = DEFAULT_TEMPERATURE, 
                   max_tokens: int = DEFAULT_MAX_TOKENS,
                   canvas: Optional[PromptCanvas] = None) -> str:
    try:
        groq = GroqProvider()
        system_message = craft_system_message(canvas, prompt)
        
        response = groq.generate(
            prompt=system_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.strip()
    except Exception as e:
        raise Exception(f"Prompt engineering error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Rephrase prompts using Groq LLM.")
    parser.add_argument("prompt", help="The prompt to rephrase")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--max_tokens", type=int, default=DEFAULT_MAX_TOKENS)
    
    args = parser.parse_args()
    
    try:
        rephrased = rephrase_prompt(args.prompt, args.model, args.temperature, args.max_tokens)
        print("Rephrased prompt:")
        print(rephrased)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
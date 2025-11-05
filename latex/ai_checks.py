import re
from typing import List, Dict, Any, Optional
from ai.provider import ProviderBase


def run_ai_checks(text: str, provider: ProviderBase) -> List[Dict[str, Any]]:
    """
    AI-powered checks for vague or incomplete sections.
    Analyzes the text to identify areas that might need clarification.
    Returns a list of dicts with fields: kind, message, line, context
    """
    
    suggestions = []
    lines = text.splitlines()
    
    # Split into paragraphs/sections for analysis
    # Look for sections that might be vague or incomplete
    paragraphs = []
    current_para = []
    current_start_line = 1
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Skip empty lines and comments (but track them)
        if not stripped or stripped.startswith('%'):
            if current_para:
                current_para.append(line)
            continue
        
        # Detect section breaks (LaTeX commands, blank lines with context)
        is_section_break = (
            stripped.startswith('\\') and 
            any(stripped.startswith(f'\\{cmd}') for cmd in ['section', 'subsection', 'chapter', 'part', 'begin'])
        )
        
        if is_section_break and current_para:
            # Save current paragraph
            para_text = '\n'.join(current_para).strip()
            if len(para_text) > 20:  # Only analyze substantial paragraphs
                paragraphs.append({
                    'text': para_text,
                    'start_line': current_start_line,
                    'end_line': i - 1
                })
            current_para = []
            current_start_line = i
        
        current_para.append(line)
    
    # Process last paragraph
    if current_para:
        para_text = '\n'.join(current_para).strip()
        if len(para_text) > 20:
            paragraphs.append({
                'text': para_text,
                'start_line': current_start_line,
                'end_line': len(lines)
            })
    
    # Analyze each paragraph with AI
    sys_prompt = (
        "You are analyzing LaTeX mathematical notes for clarity and completeness. "
        "Identify if a section is vague, incomplete, or lacks justification. "
        "Respond with 'VAGUE' if the section needs more detail, 'INCOMPLETE' if something is missing, "
        "'UNJUSTIFIED' if a claim lacks proof, or 'OK' if the section is clear. "
        "Be concise and specific."
    )
    
    for para in paragraphs[:10]:  # Limit to first 10 paragraphs to avoid too many API calls
        prompt = (
            f"Analyze this LaTeX note section for clarity:\n\n{para['text'][:500]}\n\n"
            "Is this section vague, incomplete, or lacks justification? "
            "Respond with only one word: VAGUE, INCOMPLETE, UNJUSTIFIED, or OK."
        )
        
        try:
            response = provider.complete(
                prompt=prompt,
                sys_prompt=sys_prompt,
                max_tokens=50,
                temperature=0.1
            ).upper()
            
            if 'VAGUE' in response:
                suggestions.append({
                    'kind': 'ai-vague',
                    'message': 'AI detected vague or unclear language. Consider adding more detail or examples.',
                    'line': para['start_line'],
                    'context': para['text'][:100] + '...' if len(para['text']) > 100 else para['text']
                })
            elif 'INCOMPLETE' in response:
                suggestions.append({
                    'kind': 'ai-incomplete',
                    'message': 'AI detected incomplete information. Consider filling in missing details.',
                    'line': para['start_line'],
                    'context': para['text'][:100] + '...' if len(para['text']) > 100 else para['text']
                })
            elif 'UNJUSTIFIED' in response:
                suggestions.append({
                    'kind': 'ai-unjustified',
                    'message': 'AI detected a claim that may need justification or proof.',
                    'line': para['start_line'],
                    'context': para['text'][:100] + '...' if len(para['text']) > 100 else para['text']
                })
        
        except Exception as e:
            # Silently continue if AI check fails
            continue
    
    return suggestions


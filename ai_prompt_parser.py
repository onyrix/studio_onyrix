"""
AI Prompt Parser - Convert natural language to music generation parameters

This module uses local LLMs (via Ollama) to parse user prompts like:
- "Create a chill lofi track in G major"
- "Generate an aggressive trap beat with heavy bass"
- "Make a cinematic orchestral piece for a movie scene"

Uses Ollama (local LLM) - zero cloud costs.
"""

import json
import os
from typing import Dict, List, Optional, Any

# Try to import ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: Ollama not installed. Prompt parsing will use fallback.")


class MusicPromptParser:
    """
    Parse natural language music requests into structured parameters
    that can be used with Studio Onyrix generation functions.
    """
    
    def __init__(self, model: str = "llama3.2:3b"):
        """
        Initialize the prompt parser.
        
        Args:
            model: Ollama model to use (llama3.2:3b recommended for speed)
        """
        self.model = model
        self.available = OLLAMA_AVAILABLE
        
        if self.available:
            try:
                # Test if model is available
                ollama.chat(model=self.model, messages=[{'role': 'user', 'content': 'test'}])
                print(f"Prompt Parser: Using {self.model}")
            except Exception as e:
                print(f"Warning: Model {self.model} not found. Run: ollama pull {self.model}")
                self.available = False
    
    def parse(self, user_prompt: str) -> Dict[str, Any]:
        """
        Parse a natural language prompt into music generation parameters.
        
        Args:
            user_prompt: Natural language description (e.g., "chill lofi in G major")
        
        Returns:
            Dictionary with keys: style, key, mood, bpm_estimate, instruments, structure
        """
        if not self.available:
            return self._fallback_parse(user_prompt)
        
        system_prompt = """You are a music theory expert and prompt engineer for Studio Onyrix,
a music generation system.

Parse the user's music request into a JSON object with these fields:
- style: MUST be one of these exact values: trap, drill, boom_bap, lofi, house, deep_house, techno, minimal_techno, dubstep, dnb, ambient, cinematic, downtempo, rock, funk, jazz, synthpop, synthwave, retrowave, outrun, darkwave, ebm, electro, idm, glitch, electronic_pop
- key: Musical key in format "Note_Type" (e.g., "C_major", "F_minor", "G_major")
- mood: Emotional quality (e.g., "chill", "aggressive", "happy", "dark", "energetic")
- bpm_estimate: Number between 60-180
- instruments: List of instruments mentioned or implied
- structure: Suggested song structure (e.g., "intro-verse-chorus-outro")
- chaos: Number between 0.0 and 1.0 (0.0 = predictable, 1.0 = very random)

Return ONLY valid JSON, no other text or explanation."""

        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ])
            
            content = response['message']['content'].strip()
            
            # Try to extract JSON from response (in case LLM adds extra text)
            # Look for JSON block
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                content = content[start:end].strip()
            elif '```' in content:
                start = content.find('```') + 3
                end = content.find('```', start)
                content = content[start:end].strip()
            
            # Parse JSON
            params = json.loads(content)
            
            # Validate and clean up
            params = self._validate_params(params)
            return params
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response as JSON: {e}")
            print(f"Response was: {content}")
            return self._fallback_parse(user_prompt)
        except Exception as e:
            print(f"LLM parsing failed: {e}")
            return self._fallback_parse(user_prompt)
    
    def _validate_params(self, params: Dict) -> Dict:
        """Validate and set defaults for parsed parameters."""
        # Validate style
        valid_styles = [
            "trap", "drill", "boom_bap", "lofi", "house", "deep_house", 
            "techno", "minimal_techno", "dubstep", "dnb", "ambient", 
            "cinematic", "downtempo", "rock", "funk", "jazz", "synthpop", 
            "synthwave", "retrowave", "outrun", "darkwave", "ebm", 
            "electro", "idm", "glitch", "electronic_pop"
        ]
        
        if 'style' not in params or params['style'] not in valid_styles:
            params['style'] = self._detect_style_from_prompt(params.get('mood', ''))
        
        # Validate key format
        if 'key' not in params:
            params['key'] = "C_minor"
        else:
            # Ensure correct format (Note_Type)
            key = params['key'].replace(' ', '_').replace('-', '_')
            if '_' not in key:
                # Assume minor if not specified
                key = key + "_minor"
            params['key'] = key
        
        # Set defaults
        if 'bpm_estimate' not in params:
            params['bpm_estimate'] = 120
        
        if 'chaos' not in params:
            params['chaos'] = 0.3
        else:
            params['chaos'] = max(0.0, min(1.0, float(params['chaos'])))
        
        if 'mood' not in params:
            params['mood'] = 'neutral'
        
        if 'instruments' not in params:
            params['instruments'] = []
        
        if 'structure' not in params:
            params['structure'] = 'intro-verse-chorus-outro'
        
        return params
    
    def _detect_style_from_prompt(self, prompt: str) -> str:
        """Simple keyword-based style detection as fallback."""
        prompt_lower = prompt.lower()
        
        # Style keywords
        style_keywords = {
            "trap": ["trap", "hip hop", "rap"],
            "lofi": ["lo-fi", "lofi", "chill", "relaxing"],
            "techno": ["techno", "electronic", "edm"],
            "house": ["house", "dance", "club"],
            "jazz": ["jazz", "swing", "improvisation"],
            "rock": ["rock", "guitar", "band"],
            "ambient": ["ambient", "atmospheric", "soundscape"],
            "cinematic": ["cinematic", "orchestral", "movie", "film"],
            "synthwave": ["synthwave", "retro", "80s", "outrun"],
            "funk": ["funk", "groove", "slap bass"],
        }
        
        for style, keywords in style_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                return style
        
        return "trap"  # Default
    
    def _fallback_parse(self, prompt: str) -> Dict[str, Any]:
        """Fallback parsing without LLM."""
        print("Using fallback prompt parsing (no LLM).")
        
        prompt_lower = prompt.lower()
        
        # Detect style
        style = self._detect_style_from_prompt(prompt_lower)
        
        # Detect key
        key = "C_minor"  # Default
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        for note in note_names:
            if note.lower() in prompt_lower:
                # Check for major/minor
                if 'major' in prompt_lower or 'maj' in prompt_lower:
                    key = f"{note}_major"
                else:
                    key = f"{note}_minor"
                break
        
        # Estimate BPM from keywords
        bpm = 120
        if any(w in prompt_lower for w in ["fast", "energetic", "upbeat"]):
            bpm = 140
        elif any(w in prompt_lower for w in ["slow", "chill", "relaxing"]):
            bpm = 90
        
        # Detect mood
        mood = "neutral"
        if any(w in prompt_lower for w in ["happy", "upbeat", "cheerful"]):
            mood = "happy"
        elif any(w in prompt_lower for w in ["sad", "melancholic", "dark"]):
            mood = "sad"
        elif any(w in prompt_lower for w in ["agressive", "intense", "heavy"]):
            mood = "agressive"
        
        return {
            "style": style,
            "key": key,
            "mood": mood,
            "bpm_estimate": bpm,
            "instruments": [],
            "structure": "intro-verse-chorus-outro",
            "chaos": 0.3
        }


def generate_from_prompt(user_prompt: str, use_ai: bool = True) -> 'pretty_midi.PrettyMIDI':
    """
    Convenience function to generate music from a natural language prompt.
    
    Args:
        user_prompt: Natural language description
        use_ai: Whether to use AI generation (if available)
    
    Returns:
        pretty_midi.PrettyMIDI object
    """
    from main import generate_track_with_style
    
    # Parse prompt
    parser = MusicPromptParser()
    params = parser.parse(user_prompt)
    
    print(f"\n=== Parsed Prompt ===")
    print(f"Style: {params['style']}")
    print(f"Key: {params['key']}")
    print(f"Mood: {params['mood']}")
    print(f"BPM Estimate: {params['bpm_estimate']}")
    print(f"Chaos: {params['chaos']}")
    
    # Generate track
    midi = generate_track_with_style(
        style_name=params['style'],
        key=params['key'],
        chaos=params['chaos'],
        use_ai=use_ai
    )
    
    return midi


if __name__ == "__main__":
    # Test the parser
    parser = MusicPromptParser()
    
    test_prompts = [
        "Create a chill lofi track in G major",
        "Generate an aggressive trap beat with heavy bass",
        "Make a cinematic orchestral piece for a movie scene",
    ]
    
    for prompt in test_prompts:
        print(f"\n{'='*50}")
        print(f"Prompt: {prompt}")
        print(f"{'='*50}")
        result = parser.parse(prompt)
        print(json.dumps(result, indent=2))
import re
from difflib import SequenceMatcher
import unicodedata

def clean_text_for_comparison(text):
    """Remove punctuation and normalize text for character counting and comparison"""
    # Remove common punctuation marks but keep the actual characters
    cleaned = re.sub(r'[？！。、？!.,\s\-―「」『』（）()[\]""''・?]', '', text)
    return cleaned

def extract_dialogue_from_original(original_text):
    """Extract just the dialogue part, removing speaker names like 'Riku：' or 'Kai：'"""
    # Remove speaker patterns like "Riku：" or "Kai："
    dialogue_only = re.sub(r'^[A-Za-z]+：\s*', '', original_text.strip())
    return dialogue_only

def similarity_ratio(text1, text2):
    """Calculate similarity ratio between two texts"""
    return SequenceMatcher(None, text1, text2).ratio()

def find_last_character_match_advanced(srt_clean, original_segment, base_length):
    """
    Advanced character boundary matching with better search algorithm
    """
    srt_last_char = srt_clean[-1] if srt_clean else ""
    best_match = None
    best_similarity = 0
    best_end_pos = base_length
    
    # Try different boundary positions with extended search range
    for offset in range(-10, 25):  # Extended search range
        test_end = base_length + offset
        if test_end <= 0 or test_end > len(original_segment):
            continue
            
        segment_slice = original_segment[:test_end]
        segment_clean = clean_text_for_comparison(segment_slice)
        
        if not segment_clean:
            continue
            
        # Calculate similarity
        similarity = similarity_ratio(srt_clean, segment_clean)
        
        # Bonus points for character length match
        length_ratio = min(len(segment_clean), len(srt_clean)) / max(len(segment_clean), len(srt_clean)) if max(len(segment_clean), len(srt_clean)) > 0 else 0
        
        # Bonus points for last character match
        last_char_bonus = 0.2 if segment_clean and segment_clean[-1] == srt_last_char else 0
        
        # Combined score
        combined_score = similarity + (length_ratio * 0.1) + last_char_bonus
        
        if combined_score > best_similarity:
            best_similarity = combined_score
            best_match = segment_slice
            best_end_pos = test_end
    
    # If we found a good match, extend to include punctuation
    if best_match:
        extended_end = best_end_pos
        while extended_end < len(original_segment):
            next_char = original_segment[extended_end]
            if re.match(r'[？！。、？!.,\s\-―「」『』（）()[\]""''・?…]', next_char):
                extended_end += 1
            else:
                break
        
        final_segment = original_segment[:extended_end]
        final_clean = clean_text_for_comparison(final_segment)
        
        print(f"  ✓ Advanced match found (score: {best_similarity:.2f}), extended to include punctuation")
        return extended_end, final_segment, final_clean
    
    # Fallback
    print(f"  ⚠ Using base length fallback")
    segment_slice = original_segment[:base_length]
    segment_clean = clean_text_for_comparison(segment_slice)
    return base_length, segment_slice, segment_clean

def parse_srt_file(srt_path):
    """Parse SRT file and return list of subtitle entries"""
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newlines to separate subtitle blocks
    blocks = re.split(r'\n\s*\n', content.strip())
    subtitles = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            index = lines[0]
            timestamp = lines[1]
            text = '\n'.join(lines[2:])
            subtitles.append({
                'index': int(index),
                'timestamp': timestamp,
                'text': text
            })
    
    return subtitles

def correct_srt_with_advanced_matching(srt_path, original_transcript_path, output_path, similarity_threshold=0.40):
    """Advanced SRT correction with improved character boundary matching and lower threshold"""
    
    # Read original transcript
    with open(original_transcript_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Extract dialogue only from original transcript
    original_dialogue = extract_dialogue_from_original(original_content)
    
    # Parse SRT file
    subtitles = parse_srt_file(srt_path)
    
    print(f"Found {len(subtitles)} subtitle entries")
    print(f"Original dialogue length: {len(original_dialogue)} characters")
    print(f"Using similarity threshold: {similarity_threshold}")
    print("-" * 50)
    
    corrected_subtitles = []
    original_position = 0
    
    for i, subtitle in enumerate(subtitles):
        srt_text = subtitle['text']
        srt_clean = clean_text_for_comparison(srt_text)
        base_char_count = len(srt_clean)
        
        print(f"\nProcessing subtitle {subtitle['index']}")
        print(f"SRT text: {srt_text}")
        print(f"SRT clean: {srt_clean} (length: {base_char_count})")
        
        if original_position >= len(original_dialogue):
            print("Reached end of original transcript")
            corrected_subtitles.append(subtitle)
            continue
        
        if base_char_count == 0:
            print("Empty SRT text, skipping")
            corrected_subtitles.append(subtitle)
            continue
        
        # Get a larger segment for advanced matching
        search_buffer = max(30, base_char_count + 20)  # Dynamic buffer size
        max_segment_end = min(original_position + search_buffer, len(original_dialogue))
        original_segment = original_dialogue[original_position:max_segment_end]
        
        print(f"Search segment: {original_segment[:50]}..." if len(original_segment) > 50 else f"Search segment: {original_segment}")
        
        # Advanced character boundary matching
        actual_end_pos, matched_segment, matched_clean = find_last_character_match_advanced(
            srt_clean, original_segment, base_char_count
        )
        
        print(f"Matched segment: {matched_segment}")
        print(f"Matched clean: {matched_clean} (length: {len(matched_clean)})")
        
        # Calculate base similarity
        similarity = similarity_ratio(srt_clean, matched_clean)
        
        # Calculate additional scoring factors
        bonus_score = 0
        
        # Length similarity bonus (prefer segments with similar length)
        if len(matched_clean) > 0 and len(srt_clean) > 0:
            length_ratio = min(len(matched_clean), len(srt_clean)) / max(len(matched_clean), len(srt_clean))
            if length_ratio > 0.8:
                bonus_score += 0.15
            elif length_ratio > 0.6:
                bonus_score += 0.10
        
        # Character overlap bonus (count matching characters)
        if len(matched_clean) > 0 and len(srt_clean) > 0:
            matching_chars = sum(1 for a, b in zip(srt_clean, matched_clean) if a == b)
            char_overlap_ratio = matching_chars / max(len(srt_clean), len(matched_clean))
            bonus_score += char_overlap_ratio * 0.20
        
        # Contextual bonus (if we're in a continuous sequence)
        if i > 0 and corrected_subtitles and corrected_subtitles[-1]['text'] != subtitles[i-1]['text']:
            bonus_score += 0.05  # Small bonus for maintaining flow
        
        final_score = similarity + bonus_score
        print(f"Similarity: {similarity:.2%} + Bonus: {bonus_score:.2%} = Final: {final_score:.2%}")
        
        # Decision logic with multiple criteria
        should_replace = False
        
        if final_score >= similarity_threshold:
            should_replace = True
            reason = f"score above threshold ({final_score:.2%})"
        elif similarity >= 0.30 and bonus_score >= 0.20:
            should_replace = True 
            reason = f"good base similarity with high bonus ({similarity:.2%} + {bonus_score:.2%})"
        elif len(matched_clean) > 5 and similarity >= 0.25 and length_ratio > 0.7:
            should_replace = True
            reason = f"decent match with good length ratio"
        
        if should_replace:
            print(f"✓ Replacing: {reason}")
            corrected_subtitles.append({
                'index': subtitle['index'],
                'timestamp': subtitle['timestamp'],
                'text': matched_segment
            })
            original_position += actual_end_pos
        else:
            print(f"✗ Keeping SRT text (final score: {final_score:.2%})")
            corrected_subtitles.append(subtitle)
            # Conservative position advancement
            advance_amount = min(base_char_count, len(original_dialogue) - original_position)
            original_position += max(1, advance_amount // 2)  # Move forward more conservatively
        
        print(f"Next start position: {original_position}")
    
    # Write corrected SRT file
    with open(output_path, 'w', encoding='utf-8') as f:
        for subtitle in corrected_subtitles:
            f.write(f"{subtitle['index']}\n")
            f.write(f"{subtitle['timestamp']}\n")
            f.write(f"{subtitle['text']}\n\n")
    
    print(f"\n✓ Advanced corrected SRT file saved to: {output_path}")
    
    # Print summary statistics
    replaced_count = sum(1 for i, sub in enumerate(corrected_subtitles) if sub['text'] != subtitles[i]['text'])
    print(f"📊 Summary: {replaced_count}/{len(subtitles)} subtitles were corrected ({replaced_count/len(subtitles)*100:.1f}%)")

if __name__ == "__main__":
    # File paths
    srt_file = "combined_video_20250914_233322.srt"
    transcript_file = "transcript.txt"
    output_file = "corrected_combined_v4.srt"
    
    # Run advanced correction with lower threshold and better scoring
    correct_srt_with_advanced_matching(srt_file, transcript_file, output_file, similarity_threshold=0.40)
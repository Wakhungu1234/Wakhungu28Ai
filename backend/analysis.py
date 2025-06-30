from typing import List, Dict, Any
from collections import Counter
import statistics
from datetime import datetime

def analyze_ticks(ticks: List[Dict]) -> Dict[str, Any]:
    """
    Enhanced analysis with detailed digit-by-digit breakdown and precise predictions
    """
    if not ticks:
        return {}
    
    # Extract last digits
    last_digits = [tick['last_digit'] for tick in ticks]
    
    # Count frequency of each digit (0-9)
    digit_counts = Counter(last_digits)
    total_ticks = len(ticks)
    
    # Calculate detailed digit frequency with expected vs actual
    digit_frequency = []
    expected_percentage = 10.0  # Each digit should appear ~10% if random
    
    for digit in range(10):
        count = digit_counts.get(digit, 0)
        percentage = (count / total_ticks * 100) if total_ticks > 0 else 0
        deviation = percentage - expected_percentage
        
        digit_frequency.append({
            'digit': digit,
            'count': count,
            'percentage': round(percentage, 2),
            'expected': expected_percentage,
            'deviation': round(deviation, 2),
            'is_hot': percentage > expected_percentage + 2,  # Significantly above average
            'is_cold': percentage < expected_percentage - 2   # Significantly below average
        })
    
    # Enhanced Even/Odd Analysis with precise digit breakdown
    even_digits = [0, 2, 4, 6, 8]
    odd_digits = [1, 3, 5, 7, 9]
    
    even_total_count = sum(digit_counts.get(d, 0) for d in even_digits)
    odd_total_count = sum(digit_counts.get(d, 0) for d in odd_digits)
    
    even_percentage = (even_total_count / total_ticks * 100) if total_ticks > 0 else 0
    odd_percentage = (odd_total_count / total_ticks * 100) if total_ticks > 0 else 0
    
    even_odd_analysis = {
        'even': {
            'digits': even_digits,
            'count': even_total_count,
            'percentage': round(even_percentage, 2),
            'digit_breakdown': {str(d): {'count': digit_counts.get(d, 0), 'percentage': round((digit_counts.get(d, 0) / total_ticks * 100), 2)} for d in even_digits}
        },
        'odd': {
            'digits': odd_digits,
            'count': odd_total_count,
            'percentage': round(odd_percentage, 2),
            'digit_breakdown': {str(d): {'count': digit_counts.get(d, 0), 'percentage': round((digit_counts.get(d, 0) / total_ticks * 100), 2)} for d in odd_digits}
        }
    }
    
    # Enhanced Over/Under 5 Analysis with precise digit breakdown
    over_5_digits = [6, 7, 8, 9]
    under_5_digits = [0, 1, 2, 3, 4]
    equal_5_digits = [5]
    
    over_5_count = sum(digit_counts.get(d, 0) for d in over_5_digits)
    under_5_count = sum(digit_counts.get(d, 0) for d in under_5_digits)
    equal_5_count = digit_counts.get(5, 0)
    
    over_5_percentage = (over_5_count / total_ticks * 100) if total_ticks > 0 else 0
    under_5_percentage = (under_5_count / total_ticks * 100) if total_ticks > 0 else 0
    equal_5_percentage = (equal_5_count / total_ticks * 100) if total_ticks > 0 else 0
    
    over_under_analysis = {
        'over_5': {
            'digits': over_5_digits,
            'count': over_5_count,
            'percentage': round(over_5_percentage, 2),
            'digit_breakdown': {str(d): {'count': digit_counts.get(d, 0), 'percentage': round((digit_counts.get(d, 0) / total_ticks * 100), 2)} for d in over_5_digits}
        },
        'under_5': {
            'digits': under_5_digits,
            'count': under_5_count,
            'percentage': round(under_5_percentage, 2),
            'digit_breakdown': {str(d): {'count': digit_counts.get(d, 0), 'percentage': round((digit_counts.get(d, 0) / total_ticks * 100), 2)} for d in under_5_digits}
        },
        'equal_5': {
            'digits': equal_5_digits,
            'count': equal_5_count,
            'percentage': round(equal_5_percentage, 2),
            'digit_breakdown': {'5': {'count': equal_5_count, 'percentage': round(equal_5_percentage, 2)}}
        }
    }
    
    # Enhanced Match/Differ Analysis
    most_frequent_digit = max(digit_counts.items(), key=lambda x: x[1])[0] if digit_counts else 0
    least_frequent_digit = min(digit_counts.items(), key=lambda x: x[1])[0] if digit_counts else 0
    
    most_freq_data = next(d for d in digit_frequency if d['digit'] == most_frequent_digit)
    least_freq_data = next(d for d in digit_frequency if d['digit'] == least_frequent_digit)
    
    # Generate Enhanced Predictions with detailed reasoning
    predictions = {
        # Even/Odd precise prediction
        'even_odd_recommendation': {
            'trade_type': 'EVEN' if even_percentage > odd_percentage else 'ODD',
            'confidence': max(even_percentage, odd_percentage),
            'winning_digits': even_digits if even_percentage > odd_percentage else odd_digits,
            'reason': f"{'Even' if even_percentage > odd_percentage else 'Odd'} digits (digits {even_digits if even_percentage > odd_percentage else odd_digits}) appear {max(even_percentage, odd_percentage):.1f}% of the time",
            'trade_instruction': f"Trade {'EVEN' if even_percentage > odd_percentage else 'ODD'} digits",
            'detailed_breakdown': {
                'even_analysis': f"Even digits {even_digits}: {even_total_count} times ({even_percentage:.1f}%)",
                'odd_analysis': f"Odd digits {odd_digits}: {odd_total_count} times ({odd_percentage:.1f}%)",
                'digit_details': even_odd_analysis['even']['digit_breakdown'] if even_percentage > odd_percentage else even_odd_analysis['odd']['digit_breakdown']
            }
        },
        
        # Over/Under 5 precise prediction
        'over_under_recommendation': {
            'trade_type': 'OVER 5' if over_5_percentage > under_5_percentage else 'UNDER 5',
            'threshold': 5,
            'confidence': max(over_5_percentage, under_5_percentage),
            'winning_digits': over_5_digits if over_5_percentage > under_5_percentage else under_5_digits,
            'reason': f"Digits {over_5_digits if over_5_percentage > under_5_percentage else under_5_digits} appear {max(over_5_percentage, under_5_percentage):.1f}% of the time",
            'trade_instruction': f"Trade {'OVER 5' if over_5_percentage > under_5_percentage else 'UNDER 5'}",
            'detailed_breakdown': {
                'over_5_analysis': f"Over 5 digits {over_5_digits}: {over_5_count} times ({over_5_percentage:.1f}%)",
                'under_5_analysis': f"Under 5 digits {under_5_digits}: {under_5_count} times ({under_5_percentage:.1f}%)",
                'equal_5_analysis': f"Digit 5: {equal_5_count} times ({equal_5_percentage:.1f}%)",
                'digit_details': over_under_analysis['over_5']['digit_breakdown'] if over_5_percentage > under_5_percentage else over_under_analysis['under_5']['digit_breakdown']
            }
        },
        
        # Match/Differ precise prediction
        'match_differ_recommendation': {
            'match_digit': most_frequent_digit,
            'match_confidence': most_freq_data['percentage'],
            'match_instruction': f"Trade MATCH digit {most_frequent_digit}",
            'match_reason': f"Digit {most_frequent_digit} appears {most_freq_data['percentage']:.1f}% of the time (highest frequency, expected 10%)",
            'match_deviation': most_freq_data['deviation'],
            
            'differ_digit': least_frequent_digit,
            'differ_confidence': 100 - least_freq_data['percentage'],
            'differ_instruction': f"Trade DIFFER from digit {least_frequent_digit}",
            'differ_reason': f"Digit {least_frequent_digit} appears only {least_freq_data['percentage']:.1f}% of the time (lowest frequency, expected 10%)",
            'differ_deviation': least_freq_data['deviation'],
            
            'recommendation': 'MATCH' if most_freq_data['deviation'] > abs(least_freq_data['deviation']) else 'DIFFER',
            'primary_instruction': f"Trade {'MATCH digit ' + str(most_frequent_digit) if most_freq_data['deviation'] > abs(least_freq_data['deviation']) else 'DIFFER from digit ' + str(least_frequent_digit)}"
        },
        
        # Legacy fields for compatibility
        'most_frequent_digit': most_frequent_digit,
        'least_frequent_digit': least_frequent_digit,
        'recommended_even_odd': 'even' if even_percentage > odd_percentage else 'odd',
        'recommended_over_under': 'over 5' if over_5_percentage > under_5_percentage else 'under 5',
        'match_digit': most_frequent_digit,
        'differ_digit': least_frequent_digit,
        'confidence': round(max(even_percentage, odd_percentage, over_5_percentage, under_5_percentage, most_freq_data['percentage']), 2)
    }
    
    # Hot and Cold digits analysis
    hot_digits = [d['digit'] for d in digit_frequency if d['is_hot']]
    cold_digits = [d['digit'] for d in digit_frequency if d['is_cold']]
    
    return {
        'digit_frequency': digit_frequency,
        'even_odd_analysis': even_odd_analysis,
        'over_under_analysis': over_under_analysis,
        'predictions': predictions,
        'hot_digits': hot_digits,
        'cold_digits': cold_digits,
        'total_ticks': total_ticks,
        'analysis_timestamp': datetime.utcnow().isoformat(),
        'summary': {
            'most_active_digit': most_frequent_digit,
            'least_active_digit': least_frequent_digit,
            'even_vs_odd_winner': 'even' if even_percentage > odd_percentage else 'odd',
            'over_under_winner': 'over 5' if over_5_percentage > under_5_percentage else 'under 5'
        }
    }

def find_best_over_under_threshold(last_digits: List[int], total_ticks: int) -> Dict[str, Any]:
    """
    Analyze Over 5 vs Under 5 specifically for Deriv trading
    """
    # Traditional Deriv Over/Under 5 analysis
    over_5_digits = [d for d in last_digits if d > 5]  # 6,7,8,9
    under_5_digits = [d for d in last_digits if d < 5]  # 0,1,2,3,4
    equal_5_digits = [d for d in last_digits if d == 5]  # 5
    
    over_5_count = len(over_5_digits)
    under_5_count = len(under_5_digits)
    equal_5_count = len(equal_5_digits)
    
    over_5_percentage = (over_5_count / total_ticks * 100) if total_ticks > 0 else 0
    under_5_percentage = (under_5_count / total_ticks * 100) if total_ticks > 0 else 0
    equal_5_percentage = (equal_5_count / total_ticks * 100) if total_ticks > 0 else 0
    
    # Determine best recommendation
    if over_5_percentage > under_5_percentage:
        trade_type = "OVER 5"
        confidence = over_5_percentage
        winning_digits = [6, 7, 8, 9]
        reason = f"Digits 6,7,8,9 appear {over_5_percentage:.1f}% of the time"
        instruction = f"Trade OVER 5"
    else:
        trade_type = "UNDER 5"
        confidence = under_5_percentage
        winning_digits = [0, 1, 2, 3, 4]
        reason = f"Digits 0,1,2,3,4 appear {under_5_percentage:.1f}% of the time"
        instruction = f"Trade UNDER 5"
    
    # Create detailed analysis breakdown
    analysis = {
        'over_5': {
            'count': over_5_count,
            'percentage': round(over_5_percentage, 2),
            'digits': [6, 7, 8, 9]
        },
        'under_5': {
            'count': under_5_count,
            'percentage': round(under_5_percentage, 2),
            'digits': [0, 1, 2, 3, 4]
        },
        'equal_5': {
            'count': equal_5_count,
            'percentage': round(equal_5_percentage, 2),
            'digits': [5]
        }
    }
    
    return {
        'trade_type': trade_type,
        'threshold': 5,
        'confidence': round(confidence, 2),
        'winning_digits': winning_digits,
        'analysis': analysis,
        'reason': reason,
        'instruction': instruction,
        'detailed_breakdown': {
            'over_5_analysis': f"Digits 6,7,8,9: {over_5_count} times ({over_5_percentage:.1f}%)",
            'under_5_analysis': f"Digits 0,1,2,3,4: {under_5_count} times ({under_5_percentage:.1f}%)",
            'equal_5_analysis': f"Digit 5: {equal_5_count} times ({equal_5_percentage:.1f}%)"
        }
    }

def analyze_recent_trend(recent_digits: List[int]) -> Dict[str, Any]:
    """
    Analyze recent trend in last 50 ticks for short-term predictions
    """
    if not recent_digits:
        return {}
    
    # Count recent frequencies
    recent_counts = Counter(recent_digits)
    total_recent = len(recent_digits)
    
    # Find trending digits (appearing more than expected)
    expected_frequency = total_recent / 10
    trending_up = []
    trending_down = []
    
    for digit in range(10):
        count = recent_counts.get(digit, 0)
        if count > expected_frequency * 1.5:  # 50% above expected
            trending_up.append(digit)
        elif count < expected_frequency * 0.5:  # 50% below expected
            trending_down.append(digit)
    
    return {
        'trending_up': trending_up,
        'trending_down': trending_down,
        'recent_most_frequent': max(recent_counts.items(), key=lambda x: x[1])[0] if recent_counts else 0,
        'recent_sample_size': total_recent
    }
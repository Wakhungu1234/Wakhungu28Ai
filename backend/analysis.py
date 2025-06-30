from typing import Dict, List, Any
from collections import Counter
import statistics

def analyze_ticks(ticks: List[Dict]) -> Dict[str, Any]:
    """Analyze tick data and provide trading predictions"""
    if not ticks:
        return {"error": "No tick data provided"}
    
    # Extract last digits
    last_digits = [tick["last_digit"] for tick in ticks]
    
    # Digit frequency analysis
    digit_counts = Counter(last_digits)
    total_ticks = len(last_digits)
    
    digit_frequency = []
    for digit in range(10):
        count = digit_counts.get(digit, 0)
        percentage = (count / total_ticks) * 100 if total_ticks > 0 else 0
        digit_frequency.append({
            "digit": digit,
            "count": count,
            "percentage": round(percentage, 2)
        })
    
    # Sort by frequency
    digit_frequency.sort(key=lambda x: x["percentage"], reverse=True)
    
    # Even/Odd analysis
    even_count = sum(1 for digit in last_digits if digit % 2 == 0)
    odd_count = total_ticks - even_count
    even_percentage = (even_count / total_ticks) * 100 if total_ticks > 0 else 0
    odd_percentage = (odd_count / total_ticks) * 100 if total_ticks > 0 else 0
    
    even_odd_analysis = {
        "even": {"count": even_count, "percentage": round(even_percentage, 2)},
        "odd": {"count": odd_count, "percentage": round(odd_percentage, 2)}
    }
    
    # Over/Under 5 analysis
    over_count = sum(1 for digit in last_digits if digit > 5)
    under_count = sum(1 for digit in last_digits if digit < 5)
    five_count = sum(1 for digit in last_digits if digit == 5)
    
    over_percentage = (over_count / total_ticks) * 100 if total_ticks > 0 else 0
    under_percentage = (under_count / total_ticks) * 100 if total_ticks > 0 else 0
    five_percentage = (five_count / total_ticks) * 100 if total_ticks > 0 else 0
    
    over_under_analysis = {
        "over": {"count": over_count, "percentage": round(over_percentage, 2)},
        "under": {"count": under_count, "percentage": round(under_percentage, 2)},
        "five": {"count": five_count, "percentage": round(five_percentage, 2)}
    }
    
    # Generate predictions
    predictions = generate_predictions(digit_frequency, even_odd_analysis, over_under_analysis, last_digits)
    
    return {
        "digit_frequency": digit_frequency,
        "even_odd_analysis": even_odd_analysis,
        "over_under_analysis": over_under_analysis,
        "predictions": predictions,
        "total_ticks": total_ticks,
        "hot_digits": [d["digit"] for d in digit_frequency[:3]],
        "cold_digits": [d["digit"] for d in digit_frequency[-3:]]
    }

def generate_predictions(digit_frequency: List[Dict], even_odd: Dict, over_under: Dict, recent_digits: List[int]) -> Dict[str, Any]:
    """Generate trading predictions based on analysis"""
    
    # Even/Odd prediction
    even_percentage = even_odd["even"]["percentage"]
    odd_percentage = even_odd["odd"]["percentage"]
    
    if even_percentage > odd_percentage + 10:
        even_odd_prediction = {
            "trade_type": "ODD",
            "confidence": min(95, 50 + (even_percentage - odd_percentage) * 0.8),
            "reason": f"Even digits dominating ({even_percentage:.1f}%), expecting correction",
            "winning_digits": [1, 3, 5, 7, 9]
        }
    elif odd_percentage > even_percentage + 10:
        even_odd_prediction = {
            "trade_type": "EVEN",
            "confidence": min(95, 50 + (odd_percentage - even_percentage) * 0.8),
            "reason": f"Odd digits dominating ({odd_percentage:.1f}%), expecting correction",
            "winning_digits": [0, 2, 4, 6, 8]
        }
    else:
        # Look at recent trend
        recent_trend = analyze_recent_trend(recent_digits[-10:], "even_odd")
        if recent_trend["type"] == "EVEN":
            even_odd_prediction = {
                "trade_type": "ODD",
                "confidence": 55,
                "reason": "Recent even trend, expecting odd digits",
                "winning_digits": [1, 3, 5, 7, 9]
            }
        else:
            even_odd_prediction = {
                "trade_type": "EVEN",
                "confidence": 55,
                "reason": "Recent odd trend, expecting even digits",
                "winning_digits": [0, 2, 4, 6, 8]
            }
    
    # Over/Under prediction
    over_percentage = over_under["over"]["percentage"]
    under_percentage = over_under["under"]["percentage"]
    
    if over_percentage > under_percentage + 15:
        over_under_prediction = {
            "trade_type": "UNDER 5",
            "confidence": min(95, 50 + (over_percentage - under_percentage) * 0.6),
            "reason": f"Over 5 dominating ({over_percentage:.1f}%), expecting under 5",
            "winning_digits": [0, 1, 2, 3, 4]
        }
    elif under_percentage > over_percentage + 15:
        over_under_prediction = {
            "trade_type": "OVER 5",
            "confidence": min(95, 50 + (under_percentage - over_percentage) * 0.6),
            "reason": f"Under 5 dominating ({under_percentage:.1f}%), expecting over 5",
            "winning_digits": [6, 7, 8, 9]
        }
    else:
        recent_trend = analyze_recent_trend(recent_digits[-10:], "over_under")
        if recent_trend["type"] == "OVER":
            over_under_prediction = {
                "trade_type": "UNDER 5",
                "confidence": 52,
                "reason": "Recent over 5 trend, expecting under 5",
                "winning_digits": [0, 1, 2, 3, 4]
            }
        else:
            over_under_prediction = {
                "trade_type": "OVER 5",
                "confidence": 52,
                "reason": "Recent under 5 trend, expecting over 5",
                "winning_digits": [6, 7, 8, 9]
            }
    
    # Match/Differ prediction (find most frequent digit)
    most_frequent = digit_frequency[0]
    least_frequent = digit_frequency[-1]
    
    if most_frequent["percentage"] > 15:
        match_differ_prediction = {
            "match_digit": least_frequent["digit"],
            "match_confidence": min(95, 50 + (15 - least_frequent["percentage"]) * 2),
            "match_reason": f"Digit {most_frequent['digit']} overrepresented, expecting {least_frequent['digit']}",
            "differ_confidence": min(95, 50 + most_frequent["percentage"] - 10),
            "differ_reason": f"Digit {most_frequent['digit']} very frequent, unlikely to repeat"
        }
    else:
        # Find hot digit from recent data
        hot_digit = Counter(recent_digits[-20:]).most_common(1)[0][0] if recent_digits else 0
        match_differ_prediction = {
            "match_digit": hot_digit,
            "match_confidence": 58,
            "match_reason": f"Digit {hot_digit} trending in recent ticks",
            "differ_confidence": 52,
            "differ_reason": "Balanced distribution, slight favor to differ"
        }
    
    return {
        "even_odd_recommendation": even_odd_prediction,
        "over_under_recommendation": over_under_prediction,
        "match_differ_recommendation": match_differ_prediction
    }

def analyze_recent_trend(recent_digits: List[int], analysis_type: str) -> Dict[str, Any]:
    """Analyze recent trend in digits"""
    if not recent_digits:
        return {"type": "NEUTRAL", "strength": 0}
    
    if analysis_type == "even_odd":
        even_count = sum(1 for d in recent_digits if d % 2 == 0)
        odd_count = len(recent_digits) - even_count
        
        if even_count > odd_count:
            return {"type": "EVEN", "strength": even_count - odd_count}
        else:
            return {"type": "ODD", "strength": odd_count - even_count}
    
    elif analysis_type == "over_under":
        over_count = sum(1 for d in recent_digits if d > 5)
        under_count = sum(1 for d in recent_digits if d < 5)
        
        if over_count > under_count:
            return {"type": "OVER", "strength": over_count - under_count}
        else:
            return {"type": "UNDER", "strength": under_count - over_count}
    
    return {"type": "NEUTRAL", "strength": 0}
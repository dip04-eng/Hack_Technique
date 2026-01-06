"""
Example usage of the File Analyzer
This demonstrates how to use the file analyzer for different commands
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import (
    FileAnalysisRequest,
    AnalysisCommand,
    OptimizationType,
    ExplanationLevel,
)
from agents.file_analyzer import analyze_file


async def example_optimization():
    """Example: Optimize Python code"""
    print("=== OPTIMIZATION EXAMPLE ===")

    sample_code = """
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        total = total + str(numbers[i])
    return total

def process_data(data_list):
    results = []
    for item in data_list:
        if item is not None:
            if item > 0:
                results.append(item * 2)
    return results

# Usage
nums = [1, 2, 3, 4, 5]
result = calculate_sum(nums)
processed = process_data(nums)
    """

    request = FileAnalysisRequest(
        file_name="example.py",
        file_content=sample_code,
        selected_code=sample_code,  # Analyze the whole code
        command=AnalysisCommand.OPTIMIZE,
        optimization_type=OptimizationType.PERFORMANCE,
    )

    result = await analyze_file(request)

    print(f"Success: {result.success}")
    print(f"Language: {result.language}")

    if result.success:
        print("\nOptimization Result:")
        if "optimized_code" in result.result:
            print("Optimized Code:")
            print(result.result["optimized_code"])
        if "changes_made" in result.result:
            print("\nChanges Made:")
            for change in result.result["changes_made"]:
                print(f"- {change}")
        if "suggestions" in result.result:
            print("\nSuggestions:")
            for suggestion in result.result["suggestions"]:
                print(f"- {suggestion}")
    else:
        print(f"Error: {result.error_message}")


async def example_explanation():
    """Example: Explain JavaScript code"""
    print("\n=== EXPLANATION EXAMPLE ===")

    sample_code = """
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

const handleSearch = debounce((query) => {
    fetch(`/api/search?q=${query}`)
        .then(response => response.json())
        .then(data => console.log(data));
}, 300);
    """

    request = FileAnalysisRequest(
        file_name="utils.js",
        file_content=sample_code,
        selected_code=sample_code,
        command=AnalysisCommand.EXPLAIN,
        explanation_level=ExplanationLevel.INTERMEDIATE,
    )

    result = await analyze_file(request)

    print(f"Success: {result.success}")
    print(f"Language: {result.language}")

    if result.success:
        print("\nExplanation Result:")
        if "overview" in result.result:
            print("Overview:")
            print(result.result["overview"])
        if "breakdown" in result.result:
            print("\nDetailed Breakdown:")
            print(result.result["breakdown"])
        if "key_concepts" in result.result:
            print("\nKey Concepts:")
            for concept in result.result["key_concepts"]:
                print(f"- {concept}")
        if "explanation" in result.result:
            print("\nExplanation:")
            print(result.result["explanation"])
    else:
        print(f"Error: {result.error_message}")


async def example_selected_code():
    """Example: Analyze only selected portion of code"""
    print("\n=== SELECTED CODE EXAMPLE ===")

    full_file = """
import os
import json
from typing import List, Dict

def load_config(file_path: str) -> Dict:
    with open(file_path, 'r') as f:
        return json.load(f)

def process_items(items: List[str]) -> List[str]:
    results = []
    for item in items:
        if item.strip():
            results.append(item.upper())
    return results

def main():
    config = load_config('config.json')
    items = config.get('items', [])
    processed = process_items(items)
    print(processed)

if __name__ == '__main__':
    main()
    """

    # Only analyze the process_items function
    selected_portion = """
def process_items(items: List[str]) -> List[str]:
    results = []
    for item in items:
        if item.strip():
            results.append(item.upper())
    return results
    """

    request = FileAnalysisRequest(
        file_name="main.py",
        file_content=full_file,
        selected_code=selected_portion,
        command=AnalysisCommand.OPTIMIZE,
        optimization_type=OptimizationType.READABILITY,
    )

    result = await analyze_file(request)

    print(f"Success: {result.success}")
    print(f"Language: {result.language}")
    print(f"Analyzing selected code only: {len(selected_portion)} characters")

    if result.success:
        print("\nOptimization for selected code:")
        if "optimized_code" in result.result:
            print("Optimized Code:")
            print(result.result["optimized_code"])
        if "analysis" in result.result:
            print("\nAnalysis:")
            print(result.result["analysis"])
    else:
        print(f"Error: {result.error_message}")


async def example_code_review():
    """Example: Perform code review"""
    print("\n=== CODE REVIEW EXAMPLE ===")

    sample_code = """
def authenticate_user(username, password):
    users = load_users_from_database()
    for user in users:
        if user['username'] == username and user['password'] == password:
            return True
    return False

def load_users_from_database():
    # This is a security issue - hardcoded credentials
    return [
        {'username': 'admin', 'password': 'admin123'},
        {'username': 'user', 'password': 'password'}
    ]
    """

    request = FileAnalysisRequest(
        file_name="auth.py",
        file_content=sample_code,
        selected_code=sample_code,
        command=AnalysisCommand.REVIEW,
    )

    result = await analyze_file(request)

    print(f"Success: {result.success}")
    print(f"Language: {result.language}")

    if result.success:
        print("\nCode Review Result:")
        if "quality_score" in result.result:
            print(f"Quality Score: {result.result['quality_score']}/10")
        if "security_concerns" in result.result:
            print("Security Concerns:")
            print(result.result["security_concerns"])
        if "recommendations" in result.result:
            print("\nRecommendations:")
            for rec in result.result["recommendations"]:
                print(f"- {rec}")
        if "review" in result.result:
            print("\nDetailed Review:")
            print(result.result["review"])
    else:
        print(f"Error: {result.error_message}")


async def main():
    """Run all examples"""
    print("File Analyzer Examples")
    print("=" * 50)

    try:
        await example_optimization()
        await example_explanation()
        await example_selected_code()
        await example_code_review()

        print("\n" + "=" * 50)
        print("All examples completed!")

    except Exception as e:
        print(f"Error running examples: {e}")


if __name__ == "__main__":
    asyncio.run(main())

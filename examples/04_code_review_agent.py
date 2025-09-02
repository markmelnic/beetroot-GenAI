#!/usr/bin/env python3
"""
Example 4: Code Review Agent

This example demonstrates an AI agent specialized for code review:
1. Perceive: Receive code for review
2. Think: Analyze code quality, security, and best practices
3. Act: Generate comprehensive review feedback
4. Learn: Remember review patterns and improve over time

What you'll learn:
- Specialized agent design for specific domains
- Code quality analysis and recommendations
- Security vulnerability detection
- Best practice enforcement
- Review history and learning

Prerequisites:
- Ollama installed and running
- Mistral model pulled: ollama pull mistral
"""

import sys
import os
import time
import json
import ast
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from agents.memory import Memory
from tools.code_tools import analyze_code, lint_code, check_security, extract_functions
from config.settings import get_config


class CodeReviewAgent(BaseAgent):
    """
    An AI agent specialized for code review and analysis.
    
    This agent demonstrates:
    - Code quality assessment
    - Security vulnerability detection
    - Best practice recommendations
    - Review history tracking
    - Learning from previous reviews
    """
    
    def __init__(self, model: str = None):
        """Initialize the code review agent."""
        # Define code analysis tools
        tools = [
            analyze_code,
            lint_code,
            check_security,
            extract_functions
        ]
        
        super().__init__(model=model, tools=tools)
        
        # Initialize memory for review history
        self.memory = Memory()
        
        # Load review templates and best practices
        self.review_templates = self._load_review_templates()
        self.best_practices = self._load_best_practices()
        
        print(f"🔍 Code Review Agent initialized with model: {self.model}")
        print(f"🔧 Available tools: {len(self.tools)}")
        print(f"💾 Review history: {self.memory.get_stats()['total_items']} items")
        print()
        print("💡 This agent specializes in code review, analysis, and improvement suggestions.")
        print()
    
    def _load_review_templates(self):
        """Load review templates for different types of feedback."""
        return {
            "general": {
                "structure": "Code structure and organization",
                "readability": "Code readability and clarity",
                "efficiency": "Performance and efficiency considerations",
                "maintainability": "Code maintainability and extensibility"
            },
            "python": {
                "pep8": "PEP 8 style guide compliance",
                "pythonic": "Pythonic code patterns",
                "documentation": "Docstrings and comments",
                "error_handling": "Exception handling and error management"
            },
            "security": {
                "vulnerabilities": "Security vulnerabilities and risks",
                "input_validation": "Input validation and sanitization",
                "authentication": "Authentication and authorization",
                "data_protection": "Data protection and privacy"
            }
        }
    
    def _load_best_practices(self):
        """Load best practices for different programming concepts."""
        return {
            "functions": [
                "Keep functions small and focused (single responsibility)",
                "Use descriptive function names",
                "Limit function parameters (max 3-4)",
                "Return early to reduce nesting",
                "Use type hints for better documentation"
            ],
            "classes": [
                "Follow single responsibility principle",
                "Use composition over inheritance",
                "Keep methods focused and cohesive",
                "Use properties for computed attributes",
                "Implement proper __str__ and __repr__ methods"
            ],
            "error_handling": [
                "Use specific exception types",
                "Don't catch generic exceptions",
                "Provide meaningful error messages",
                "Log errors appropriately",
                "Use context managers (with statements)"
            ],
            "performance": [
                "Avoid premature optimization",
                "Use appropriate data structures",
                "Minimize function calls in loops",
                "Use list comprehensions when appropriate",
                "Profile code before optimizing"
            ]
        }
    
    def review_code(self, code: str, language: str = "python", 
                   focus_areas: list = None) -> dict:
        """
        Perform comprehensive code review.
        
        Args:
            code: Source code to review
            language: Programming language
            focus_areas: Specific areas to focus on
            
        Returns:
            Comprehensive review results
        """
        print(f"🔍 Starting code review for {language} code...")
        start_time = time.time()
        
        # Store the code in memory
        memory_id = self.memory.store(
            content=code,
            item_type="code_review",
            importance=0.8,
            metadata={
                "language": language,
                "focus_areas": focus_areas,
                "timestamp": time.time()
            }
        )
        
        # Perform various analyses
        review_results = {
            "code_info": self._analyze_code_structure(code, language),
            "quality_analysis": self._analyze_code_quality(code, language),
            "security_analysis": self._analyze_security(code, language),
            "best_practices": self._analyze_best_practices(code, language),
            "recommendations": [],
            "overall_score": 0.0,
            "priority_issues": []
        }
        
        # Generate recommendations
        review_results["recommendations"] = self._generate_recommendations(review_results)
        
        # Calculate overall score
        review_results["overall_score"] = self._calculate_overall_score(review_results)
        
        # Identify priority issues
        review_results["priority_issues"] = self._identify_priority_issues(review_results)
        
        # Store review results in memory
        self.memory.store(
            content=review_results,
            item_type="review_result",
            importance=0.9,
            metadata={
                "code_id": memory_id,
                "language": language,
                "score": review_results["overall_score"],
                "timestamp": time.time()
            }
        )
        
        end_time = time.time()
        review_results["review_time"] = end_time - start_time
        
        print(f"✅ Code review completed in {review_results['review_time']:.2f} seconds")
        
        return review_results
    
    def _analyze_code_structure(self, code: str, language: str) -> dict:
        """Analyze the structure and organization of the code."""
        try:
            analysis = analyze_code(code, language)
            
            if "error" not in analysis:
                return {
                    "metrics": analysis.get("metrics", {}),
                    "structure": {
                        "total_lines": analysis.get("metrics", {}).get("total_lines", 0),
                        "code_lines": analysis.get("metrics", {}).get("code_lines", 0),
                        "functions": analysis.get("metrics", {}).get("functions", 0),
                        "classes": analysis.get("metrics", {}).get("classes", 0),
                        "complexity": analysis.get("metrics", {}).get("complexity", 0)
                    },
                    "issues": analysis.get("issues", []),
                    "suggestions": analysis.get("suggestions", [])
                }
            else:
                return {"error": analysis["error"]}
                
        except Exception as e:
            return {"error": f"Structure analysis failed: {str(e)}"}
    
    def _analyze_code_quality(self, code: str, language: str) -> dict:
        """Analyze code quality and style."""
        try:
            lint_results = lint_code(code, language)
            
            if "error" not in lint_results:
                return {
                    "linting": lint_results,
                    "style_issues": lint_results.get("issues", []),
                    "warnings": lint_results.get("warnings", []),
                    "severity": lint_results.get("severity", "unknown")
                }
            else:
                return {"error": lint_results["error"]}
                
        except Exception as e:
            return {"error": f"Quality analysis failed: {str(e)}"}
    
    def _analyze_security(self, code: str, language: str) -> dict:
        """Analyze code for security vulnerabilities."""
        try:
            security_results = check_security(code, language)
            
            if "error" not in security_results:
                return {
                    "vulnerabilities": security_results.get("vulnerabilities", []),
                    "warnings": security_results.get("warnings", []),
                    "risk_level": security_results.get("risk_level", "unknown"),
                    "recommendations": security_results.get("recommendations", [])
                }
            else:
                return {"error": security_results["error"]}
                
        except Exception as e:
            return {"error": f"Security analysis failed: {str(e)}"}
    
    def _analyze_best_practices(self, code: str, language: str) -> dict:
        """Analyze code against best practices."""
        try:
            if language.lower() == "python":
                return self._analyze_python_best_practices(code)
            else:
                return {"error": f"Best practices analysis not implemented for {language}"}
                
        except Exception as e:
            return {"error": f"Best practices analysis failed: {str(e)}"}
    
    def _analyze_python_best_practices(self, code: str) -> dict:
        """Analyze Python code against best practices."""
        try:
            tree = ast.parse(code)
            
            analysis = {
                "functions": [],
                "classes": [],
                "error_handling": [],
                "performance": [],
                "documentation": []
            }
            
            # Analyze functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_analysis = self._analyze_function(node, code)
                    analysis["functions"].append(func_analysis)
                
                elif isinstance(node, ast.ClassDef):
                    class_analysis = self._analyze_class(node, code)
                    analysis["classes"].append(class_analysis)
                
                elif isinstance(node, ast.Try):
                    error_analysis = self._analyze_error_handling(node)
                    analysis["error_handling"].append(error_analysis)
            
            # Analyze documentation
            analysis["documentation"] = self._analyze_documentation(code)
            
            return analysis
            
        except SyntaxError as e:
            return {"error": f"Python syntax error: {str(e)}"}
        except Exception as e:
            return {"error": f"Best practices analysis failed: {str(e)}"}
    
    def _analyze_function(self, func_node, code: str) -> dict:
        """Analyze a function against best practices."""
        func_lines = code.split('\n')[func_node.lineno-1:func_node.end_lineno]
        func_code = '\n'.join(func_lines)
        
        analysis = {
            "name": func_node.name,
            "line_number": func_node.lineno,
            "issues": [],
            "suggestions": []
        }
        
        # Check function length
        if len(func_lines) > 20:
            analysis["issues"].append("Function is too long (>20 lines)")
            analysis["suggestions"].append("Consider breaking into smaller functions")
        
        # Check number of arguments
        if len(func_node.args.args) > 4:
            analysis["issues"].append("Too many parameters (>4)")
            analysis["suggestions"].append("Consider using a data class or dictionary")
        
        # Check for docstring
        if not ast.get_docstring(func_node):
            analysis["issues"].append("Missing docstring")
            analysis["suggestions"].append("Add a descriptive docstring")
        
        # Check for early returns
        has_early_return = any(isinstance(n, ast.Return) for n in ast.walk(func_node))
        if not has_early_return and len(func_lines) > 10:
            analysis["suggestions"].append("Consider using early returns to reduce nesting")
        
        return analysis
    
    def _analyze_class(self, class_node, code: str) -> dict:
        """Analyze a class against best practices."""
        analysis = {
            "name": class_node.name,
            "line_number": class_node.lineno,
            "methods": len([n for n in class_node.body if isinstance(n, ast.FunctionDef)]),
            "issues": [],
            "suggestions": []
        }
        
        # Check for __init__ method
        has_init = any(m.name == "__init__" for m in class_node.body if isinstance(m, ast.FunctionDef))
        if not has_init:
            analysis["suggestions"].append("Consider adding an __init__ method")
        
        # Check for __str__ or __repr__ methods
        has_str_repr = any(m.name in ["__str__", "__repr__"] for m in class_node.body if isinstance(m, ast.FunctionDef))
        if not has_str_repr:
            analysis["suggestions"].append("Consider adding __str__ or __repr__ methods")
        
        return analysis
    
    def _analyze_error_handling(self, try_node) -> dict:
        """Analyze error handling patterns."""
        analysis = {
            "line_number": try_node.lineno,
            "issues": [],
            "suggestions": []
        }
        
        # Check for bare except clauses
        for handler in try_node.handlers:
            if handler.type is None:
                analysis["issues"].append("Bare except clause detected")
                analysis["suggestions"].append("Specify exception types to catch")
        
        return analysis
    
    def _analyze_documentation(self, code: str) -> dict:
        """Analyze code documentation."""
        lines = code.split('\n')
        
        analysis = {
            "total_lines": len(lines),
            "comment_lines": 0,
            "docstring_lines": 0,
            "issues": [],
            "suggestions": []
        }
        
        in_docstring = False
        docstring_delimiter = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Count comment lines
            if stripped.startswith('#'):
                analysis["comment_lines"] += 1
            
            # Count docstring lines
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                    docstring_delimiter = '"""' if '"""' in line else "'''"
                else:
                    if docstring_delimiter in line:
                        in_docstring = False
            
            if in_docstring:
                analysis["docstring_lines"] += 1
        
        # Calculate documentation ratio
        total_doc = analysis["comment_lines"] + analysis["docstring_lines"]
        doc_ratio = total_doc / analysis["total_lines"] if analysis["total_lines"] > 0 else 0
        
        if doc_ratio < 0.1:
            analysis["issues"].append("Low documentation ratio (<10%)")
            analysis["suggestions"].append("Consider adding more comments and docstrings")
        
        return analysis
    
    def _generate_recommendations(self, review_results: dict) -> list:
        """Generate actionable recommendations based on review results."""
        recommendations = []
        
        # Structure recommendations
        if "code_info" in review_results and "error" not in review_results["code_info"]:
            code_info = review_results["code_info"]
            
            if code_info.get("structure", {}).get("complexity", 0) > 10:
                recommendations.append({
                    "category": "complexity",
                    "priority": "high",
                    "message": "High cyclomatic complexity detected",
                    "suggestion": "Consider simplifying control flow by extracting methods"
                })
            
            if code_info.get("structure", {}).get("functions", 0) > 20:
                recommendations.append({
                    "category": "organization",
                    "priority": "medium",
                    "message": "Large number of functions in single file",
                    "suggestion": "Consider splitting into multiple modules"
                })
        
        # Quality recommendations
        if "quality_analysis" in review_results and "error" not in review_results["quality_analysis"]:
            quality = review_results["quality_analysis"]
            
            if quality.get("linting", {}).get("total_issues", 0) > 0:
                recommendations.append({
                    "category": "style",
                    "priority": "medium",
                    "message": f"Found {quality['linting']['total_issues']} style issues",
                    "suggestion": "Run a code formatter like black or autopep8"
                })
        
        # Security recommendations
        if "security_analysis" in review_results and "error" not in review_results["security_analysis"]:
            security = review_results["security_analysis"]
            
            if security.get("vulnerabilities"):
                recommendations.append({
                    "category": "security",
                    "priority": "critical",
                    "message": f"Found {len(security['vulnerabilities'])} security vulnerabilities",
                    "suggestion": "Address security issues before deployment"
                })
            
            if security.get("risk_level") == "high":
                recommendations.append({
                    "category": "security",
                    "priority": "high",
                    "message": "High security risk detected",
                    "suggestion": "Conduct security review with security team"
                })
        
        # Best practices recommendations
        if "best_practices" in review_results and "error" not in review_results["best_practices"]:
            best_practices = review_results["best_practices"]
            
            for func_analysis in best_practices.get("functions", []):
                for issue in func_analysis.get("issues", []):
                    recommendations.append({
                        "category": "best_practices",
                        "priority": "medium",
                        "message": f"Function '{func_analysis['name']}': {issue}",
                        "suggestion": func_analysis.get("suggestions", ["Review and improve"])[0]
                    })
        
        return recommendations
    
    def _calculate_overall_score(self, review_results: dict) -> float:
        """Calculate overall code quality score (0.0 to 1.0)."""
        score = 1.0
        
        # Deduct points for issues
        if "code_info" in review_results and "error" not in review_results["code_info"]:
            code_info = review_results["code_info"]
            
            # Deduct for complexity
            complexity = code_info.get("structure", {}).get("complexity", 0)
            if complexity > 10:
                score -= min(0.2, (complexity - 10) * 0.02)
            
            # Deduct for long functions
            issues = code_info.get("issues", [])
            score -= min(0.1, len(issues) * 0.02)
        
        # Deduct for quality issues
        if "quality_analysis" in review_results and "error" not in review_results["quality_analysis"]:
            quality = review_results["quality_analysis"]
            issues = quality.get("linting", {}).get("total_issues", 0)
            score -= min(0.15, issues * 0.01)
        
        # Deduct for security issues
        if "security_analysis" in review_results and "error" not in review_results["security_analysis"]:
            security = review_results["security_analysis"]
            
            vulnerabilities = len(security.get("vulnerabilities", []))
            score -= min(0.3, vulnerabilities * 0.1)
            
            if security.get("risk_level") == "high":
                score -= 0.2
            elif security.get("risk_level") == "medium":
                score -= 0.1
        
        # Deduct for best practice violations
        if "best_practices" in review_results and "error" not in review_results["best_practices"]:
            best_practices = review_results["best_practices"]
            
            total_issues = sum(
                len(func.get("issues", [])) for func in best_practices.get("functions", [])
            )
            score -= min(0.1, total_issues * 0.01)
        
        return max(0.0, score)
    
    def _identify_priority_issues(self, review_results: dict) -> list:
        """Identify high-priority issues that need immediate attention."""
        priority_issues = []
        
        # Security vulnerabilities are always high priority
        if "security_analysis" in review_results and "error" not in review_results["security_analysis"]:
            security = review_results["security_analysis"]
            
            for vuln in security.get("vulnerabilities", []):
                priority_issues.append({
                    "type": "security",
                    "priority": "critical",
                    "message": vuln,
                    "action": "Fix immediately before deployment"
                })
        
        # High complexity issues
        if "code_info" in review_results and "error" not in review_results["code_info"]:
            code_info = review_results["code_info"]
            complexity = code_info.get("structure", {}).get("complexity", 0)
            
            if complexity > 15:
                priority_issues.append({
                    "type": "complexity",
                    "priority": "high",
                    "message": f"Very high complexity ({complexity})",
                    "action": "Refactor to reduce complexity"
                })
        
        # Critical quality issues
        if "quality_analysis" in review_results and "error" not in review_results["quality_analysis"]:
            quality = review_results["quality_analysis"]
            
            if quality.get("linting", {}).get("severity") == "error":
                priority_issues.append({
                    "type": "quality",
                    "priority": "high",
                    "message": "Critical quality issues detected",
                    "action": "Fix all errors before proceeding"
                })
        
        return priority_issues
    
    def get_review_history(self, limit: int = 10) -> list:
        """Get recent code review history."""
        reviews = self.memory.retrieve(
            item_type="review_result",
            limit=limit,
            min_importance=0.7
        )
        
        return [
            {
                "timestamp": review.metadata.get("timestamp", 0),
                "language": review.metadata.get("language", "unknown"),
                "score": review.metadata.get("score", 0.0),
                "content": review.content
            }
            for review in reviews
        ]
    
    def demonstrate_code_review(self):
        """Demonstrate code review capabilities."""
        print("🔍 Demonstrating Code Review Capabilities")
        print("=" * 60)
        
        # Sample code with various issues
        sample_code = '''
def process_user_data(user_input, config=None):
    if config is None:
        config = {}
    
    result = []
    for i in range(len(user_input)):
        item = user_input[i]
        if item > 0:
            processed = item * 2
            result.append(processed)
    
    return result

class DataProcessor:
    def __init__(self, data):
        self.data = data
        self.cache = {}
    
    def process(self):
        if len(self.data) == 0:
            return []
        
        result = []
        for item in self.data:
            if item in self.cache:
                result.append(self.cache[item])
            else:
                processed = self._process_item(item)
                self.cache[item] = processed
                result.append(processed)
        
        return result
    
    def _process_item(self, item):
        # This is a very long function that does too many things
        # and should probably be broken down into smaller functions
        if isinstance(item, str):
            if item.isdigit():
                return int(item)
            elif item.lower() in ['true', 'false']:
                return item.lower() == 'true'
            else:
                return item.upper()
        elif isinstance(item, (int, float)):
            if item < 0:
                return abs(item)
            elif item > 1000:
                return item / 1000
            else:
                return item
        else:
            return str(item)

def main():
    data = [1, 2, 3, "hello", "123", True, -5, 1500]
    processor = DataProcessor(data)
    result = processor.process()
    print(result)

if __name__ == "__main__":
    main()
'''
        
        print("📝 Sample code for review:")
        print(sample_code)
        print()
        
        # Perform code review
        print("🔍 Performing comprehensive code review...")
        review_results = self.review_code(sample_code, "python")
        
        if "error" not in review_results:
            self._display_review_results(review_results)
        else:
            print(f"❌ Review failed: {review_results['error']}")
        
        print()
    
    def _display_review_results(self, review_results: dict):
        """Display code review results in a formatted way."""
        print("✅ Code Review Results")
        print("=" * 40)
        
        # Overall score
        score = review_results.get("overall_score", 0.0)
        score_percentage = score * 100
        score_emoji = "🟢" if score >= 0.8 else "🟡" if score >= 0.6 else "🔴"
        
        print(f"{score_emoji} Overall Score: {score_percentage:.1f}%")
        print()
        
        # Priority issues
        priority_issues = review_results.get("priority_issues", [])
        if priority_issues:
            print("🚨 Priority Issues:")
            for issue in priority_issues:
                priority_emoji = "🔴" if issue["priority"] == "critical" else "🟡"
                print(f"  {priority_emoji} {issue['message']}")
                print(f"     Action: {issue['action']}")
            print()
        
        # Code structure
        if "code_info" in review_results and "error" not in review_results["code_info"]:
            code_info = review_results["code_info"]
            structure = code_info.get("structure", {})
            
            print("📊 Code Structure:")
            print(f"  📝 Total lines: {structure.get('total_lines', 'N/A')}")
            print(f"  ⚙️  Functions: {structure.get('functions', 'N/A')}")
            print(f"  🏗️  Classes: {structure.get('classes', 'N/A')}")
            print(f"  🔀 Complexity: {structure.get('complexity', 'N/A')}")
            print()
        
        # Quality analysis
        if "quality_analysis" in review_results and "error" not in review_results["quality_analysis"]:
            quality = review_results["quality_analysis"]
            linting = quality.get("linting", {})
            
            print("🧹 Code Quality:")
            print(f"  📊 Total issues: {linting.get('total_issues', 0)}")
            print(f"  ⚠️  Warnings: {linting.get('total_warnings', 0)}")
            print(f"  🎯 Severity: {linting.get('severity', 'unknown')}")
            print()
        
        # Security analysis
        if "security_analysis" in review_results and "error" not in review_results["security_analysis"]:
            security = review_results["security_analysis"]
            
            print("🔒 Security Analysis:")
            print(f"  🚨 Vulnerabilities: {len(security.get('vulnerabilities', []))}")
            print(f"  ⚠️  Warnings: {len(security.get('warnings', []))}")
            print(f"  🎯 Risk Level: {security.get('risk_level', 'unknown')}")
            print()
        
        # Recommendations
        recommendations = review_results.get("recommendations", [])
        if recommendations:
            print("💡 Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
                priority_emoji = "🔴" if rec["priority"] == "critical" else "🟡" if rec["priority"] == "high" else "🟢"
                print(f"  {i}. {priority_emoji} {rec['message']}")
                print(f"     💡 {rec['suggestion']}")
            print()
        
        # Review time
        review_time = review_results.get("review_time", 0)
        print(f"⏱️  Review completed in {review_time:.2f} seconds")
    
    def run_interactive(self):
        """Run the agent in interactive mode."""
        print("🎯 Code Review Agent is ready! Type 'quit' to exit.")
        print("Available commands:")
        print("  - 'demo': Demonstrate code review capabilities")
        print("  - 'review <code>': Review the provided code")
        print("  - 'history': Show recent review history")
        print("  - 'analyze <file>': Analyze a code file")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye! Thanks for trying the Code Review Agent.")
                    break
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() == 'demo':
                    self.demonstrate_code_review()
                    continue
                
                elif user_input.lower() == 'history':
                    print("📚 Recent Review History:")
                    history = self.get_review_history(5)
                    
                    if history:
                        for i, review in enumerate(history, 1):
                            timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime(review["timestamp"]))
                            print(f"  {i}. {timestamp} - {review['language']} (Score: {review['score']:.1f})")
                    else:
                        print("  No review history found")
                    continue
                
                elif user_input.lower().startswith('review '):
                    code = user_input[7:]  # Remove 'review ' prefix
                    print(f"🔍 Reviewing code: {code[:50]}...")
                    
                    review_results = self.review_code(code, "python")
                    
                    if "error" not in review_results:
                        self._display_review_results(review_results)
                    else:
                        print(f"❌ Review failed: {review_results['error']}")
                    continue
                
                elif user_input.lower().startswith('analyze '):
                    file_path = user_input[8:]  # Remove 'analyze ' prefix
                    
                    try:
                        with open(file_path, 'r') as f:
                            code = f.read()
                        
                        print(f"🔍 Analyzing file: {file_path}")
                        review_results = self.review_code(code, "python")
                        
                        if "error" not in review_results:
                            self._display_review_results(review_results)
                        else:
                            print(f"❌ Analysis failed: {review_results['error']}")
                    
                    except FileNotFoundError:
                        print(f"❌ File not found: {file_path}")
                    except Exception as e:
                        print(f"❌ Error reading file: {e}")
                    continue
                
                # Default: treat as code to review
                print(f"🔍 Treating input as code to review...")
                
                review_results = self.review_code(user_input, "python")
                
                if "error" not in review_results:
                    self._display_review_results(review_results)
                else:
                    print(f"❌ Review failed: {review_results['error']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("🔄 Continuing...")


def main():
    """Main function to run the example."""
    print("🧠 AI Agent Demonstration - Example 4: Code Review Agent")
    print("=" * 60)
    print()
    
    # Check configuration
    config = get_config()
    print(f"🔧 Configuration:")
    print(f"  Ollama URL: {config['ollama_base_url']}")
    print(f"  Default Model: {config['default_model']}")
    print(f"  Agent Timeout: {config['agent_timeout']} seconds")
    print()
    
    # Check if user wants to run demo or interactive mode
    print("Choose an option:")
    print("1. Run code review demonstration")
    print("2. Interactive mode (review code manually)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                agent = CodeReviewAgent()
                agent.demonstrate_code_review()
                break
            elif choice == "2":
                agent = CodeReviewAgent()
                agent.run_interactive()
                break
            elif choice == "3":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Please try again.")


if __name__ == "__main__":
    main()

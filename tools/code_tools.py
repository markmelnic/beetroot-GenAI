"""
Code analysis and manipulation tools for AI agents.
Provides functions for analyzing, formatting, and improving code.
"""

import ast
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def analyze_code(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Analyze code for various metrics and insights.
    
    Args:
        code: Source code to analyze
        language: Programming language (currently supports Python)
        
    Returns:
        Dictionary containing analysis results
    """
    if language.lower() == "python":
        return _analyze_python_code(code)
    else:
        return {"error": f"Language {language} not supported yet"}
    
    return {"error": "Analysis failed"}


def format_code(code: str, language: str = "python", style: str = "pep8") -> Dict[str, Any]:
    """
    Format code according to specified style guidelines.
    
    Args:
        code: Source code to format
        language: Programming language
        style: Style guide to follow
        
    Returns:
        Dictionary containing formatted code and metadata
    """
    try:
        if language.lower() == "python":
            return _format_python_code(code, style)
        else:
            return {"error": f"Language {language} not supported yet"}
    except Exception as e:
        return {"error": f"Formatting failed: {str(e)}"}


def lint_code(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Lint code for potential issues and style violations.
    
    Args:
        code: Source code to lint
        language: Programming language
        
    Returns:
        Dictionary containing linting results
    """
    try:
        if language.lower() == "python":
            return _lint_python_code(code)
        else:
            return {"error": f"Language {language} not supported yet"}
    except Exception as e:
        return {"error": f"Linting failed: {str(e)}"}


def extract_functions(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Extract function definitions from code.
    
    Args:
        code: Source code to analyze
        language: Programming language
        
    Returns:
        Dictionary containing extracted functions
    """
    try:
        if language.lower() == "python":
            return _extract_python_functions(code)
        else:
            return {"error": f"Language {language} not supported yet"}
    except Exception as e:
        return {"error": f"Function extraction failed: {str(e)}"}


def check_security(code: str, language: str = "python") -> Dict[str, Any]:
    """
    Check code for potential security vulnerabilities.
    
    Args:
        code: Source code to analyze
        language: Programming language
        
    Returns:
        Dictionary containing security analysis results
    """
    try:
        if language.lower() == "python":
            return _check_python_security(code)
        else:
            return {"error": f"Language {language} not supported yet"}
    except Exception as e:
        return {"error": f"Security check failed: {str(e)}"}


def _analyze_python_code(code: str) -> Dict[str, Any]:
    """Analyze Python code for metrics and insights."""
    try:
        tree = ast.parse(code)
        
        # Count different elements
        class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
        function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        import_count = len([node for node in ast.walk(tree) if isinstance(node, ast.Import)])
        import_from_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)])
        
        # Count lines and characters
        lines = code.split('\n')
        total_lines = len(lines)
        empty_lines = len([line for line in lines if line.strip() == ''])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        code_lines = total_lines - empty_lines - comment_lines
        
        # Calculate complexity (simplified)
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
        
        # Find potential issues
        issues = []
        
        # Check for long functions (more than 20 lines)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = len(code.split('\n')[node.lineno-1:node.end_lineno])
                if func_lines > 20:
                    issues.append(f"Function '{node.name}' is {func_lines} lines long (consider breaking it down)")
        
        # Check for unused imports (basic check)
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_names.add(node.module)
        
        # Check for magic numbers
        magic_numbers = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Num) and isinstance(node.n, (int, float)):
                if node.n > 1000 or (isinstance(node.n, float) and node.n < 0.01):
                    magic_numbers.append(f"Magic number: {node.n}")
        
        analysis = {
            "language": "python",
            "metrics": {
                "total_lines": total_lines,
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "empty_lines": empty_lines,
                "classes": class_count,
                "functions": function_count,
                "imports": import_count + import_from_count,
                "complexity": complexity
            },
            "issues": issues,
            "magic_numbers": magic_numbers,
            "suggestions": _generate_suggestions(class_count, function_count, complexity, code_lines)
        }
        
        return analysis
        
    except SyntaxError as e:
        return {"error": f"Syntax error: {str(e)}"}
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}


def _format_python_code(code: str, style: str) -> Dict[str, Any]:
    """Format Python code according to style guidelines."""
    try:
        # Basic formatting (in a real implementation, you'd use black, autopep8, etc.)
        formatted_lines = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            # Remove trailing whitespace
            line = line.rstrip()
            
            # Basic indentation fix (very basic)
            if line.strip() and not line.startswith(' '):
                # This is a very simplified approach
                pass
            
            formatted_lines.append(line)
        
        formatted_code = '\n'.join(formatted_lines)
        
        return {
            "original_code": code,
            "formatted_code": formatted_code,
            "style": style,
            "changes_made": len([1 for i, (orig, fmt) in enumerate(zip(lines, formatted_lines)) if orig != fmt]),
            "note": "This is a basic formatter. For production use, consider using black, autopep8, or yapf."
        }
        
    except Exception as e:
        return {"error": f"Formatting failed: {str(e)}"}


def _lint_python_code(code: str) -> Dict[str, Any]:
    """Lint Python code for potential issues."""
    try:
        issues = []
        warnings = []
        
        lines = code.split('\n')
        
        # Check line length
        for i, line in enumerate(lines, 1):
            if len(line) > 79:
                issues.append(f"Line {i}: Line too long ({len(line)} characters)")
        
        # Check for common issues
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for unused variables (basic check)
            if '=' in stripped and stripped.endswith('='):
                warnings.append(f"Line {i}: Possible unused assignment")
            
            # Check for missing spaces around operators
            if re.search(r'[a-zA-Z0-9_][=+\-*/][a-zA-Z0-9_]', stripped):
                if not re.search(r'[a-zA-Z0-9_] [=+\-*/] [a-zA-Z0-9_]', stripped):
                    warnings.append(f"Line {i}: Missing spaces around operator")
        
        # Check for potential syntax issues
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(f"Syntax error: {str(e)}")
        
        return {
            "issues": issues,
            "warnings": warnings,
            "total_issues": len(issues),
            "total_warnings": len(warnings),
            "severity": "error" if issues else "warning" if warnings else "clean"
        }
        
    except Exception as e:
        return {"error": f"Linting failed: {str(e)}"}


def _extract_python_functions(code: str) -> Dict[str, Any]:
    """Extract function definitions from Python code."""
    try:
        tree = ast.parse(code)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Get function signature
                args = []
                for arg in node.args.args:
                    args.append(arg.arg)
                
                # Get docstring
                docstring = ast.get_docstring(node) or "No docstring"
                
                # Get function body (first few lines)
                body_lines = code.split('\n')[node.lineno-1:node.end_lineno]
                body = '\n'.join(body_lines)
                
                functions.append({
                    "name": node.name,
                    "args": args,
                    "docstring": docstring,
                    "line_number": node.lineno,
                    "body": body,
                    "decorators": [d.id for d in node.decorator_list if hasattr(d, 'id')]
                })
        
        return {
            "functions": functions,
            "total_functions": len(functions),
            "function_names": [f["name"] for f in functions]
        }
        
    except SyntaxError as e:
        return {"error": f"Syntax error: {str(e)}"}
    except Exception as e:
        return {"error": f"Function extraction failed: {str(e)}"}


def _check_python_security(code: str) -> Dict[str, Any]:
    """Check Python code for potential security vulnerabilities."""
    try:
        vulnerabilities = []
        warnings = []
        
        # Check for dangerous functions
        dangerous_functions = [
            'eval', 'exec', 'os.system', 'subprocess.call', 'subprocess.Popen',
            'pickle.loads', 'yaml.load', 'marshal.loads'
        ]
        
        for func in dangerous_functions:
            if func in code:
                vulnerabilities.append(f"Use of dangerous function: {func}")
        
        # Check for SQL injection patterns
        sql_patterns = [
            r'f".*SELECT.*{.*}.*"',
            r'f".*INSERT.*{.*}.*"',
            r'f".*UPDATE.*{.*}.*"',
            r'f".*DELETE.*{.*}.*"'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                warnings.append("Potential SQL injection: f-string with SQL query")
        
        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                warnings.append("Potential hardcoded secret detected")
        
        # Check for file operations without proper validation
        file_ops = ['open(', 'file(']
        for op in file_ops:
            if op in code:
                warnings.append(f"File operation detected: {op} - ensure proper path validation")
        
        return {
            "vulnerabilities": vulnerabilities,
            "warnings": warnings,
            "total_vulnerabilities": len(vulnerabilities),
            "total_warnings": len(warnings),
            "risk_level": "high" if vulnerabilities else "medium" if warnings else "low",
            "recommendations": _generate_security_recommendations(vulnerabilities, warnings)
        }
        
    except Exception as e:
        return {"error": f"Security check failed: {str(e)}"}


def _generate_suggestions(class_count: int, function_count: int, complexity: int, code_lines: int) -> List[str]:
    """Generate improvement suggestions based on code analysis."""
    suggestions = []
    
    if class_count == 0 and function_count > 5:
        suggestions.append("Consider organizing code into classes for better structure")
    
    if function_count > 20:
        suggestions.append("Consider breaking down large files into smaller modules")
    
    if complexity > 10:
        suggestions.append("High cyclomatic complexity detected. Consider simplifying control flow")
    
    if code_lines > 500:
        suggestions.append("Large file detected. Consider splitting into smaller files")
    
    if function_count > 0 and class_count == 0:
        suggestions.append("Consider using object-oriented design for better code organization")
    
    return suggestions


def _generate_security_recommendations(vulnerabilities: List[str], warnings: List[str]) -> List[str]:
    """Generate security improvement recommendations."""
    recommendations = []
    
    if any('eval' in v for v in vulnerabilities):
        recommendations.append("Replace eval() with safer alternatives like ast.literal_eval()")
    
    if any('os.system' in v for v in vulnerabilities):
        recommendations.append("Use subprocess.run() with proper argument handling instead of os.system()")
    
    if any('pickle' in v for v in vulnerabilities):
        recommendations.append("Avoid pickle for untrusted data. Use JSON or other safe serialization")
    
    if any('SQL injection' in w for w in warnings):
        recommendations.append("Use parameterized queries or ORM to prevent SQL injection")
    
    if any('hardcoded secret' in w for w in warnings):
        recommendations.append("Use environment variables or secure configuration management for secrets")
    
    if any('file operation' in w for w in warnings):
        recommendations.append("Validate file paths and use pathlib for safer file operations")
    
    return recommendations

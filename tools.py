"""Tools for the APE Agent - Hash operations and other utilities."""

import hashlib
from typing import Dict, Any, List
from langchain_core.tools import tool


@tool
def sha512_hash(text: str) -> str:
    """
    Compute the SHA-512 hash of the given text.
    
    Args:
        text: The input text to hash
        
    Returns:
        The SHA-512 hash as a hexadecimal string
    """
    return hashlib.sha512(text.encode()).hexdigest()


@tool
def md5_hash(text: str) -> str:
    """
    Compute the MD5 hash of the given text.
    
    Args:
        text: The input text to hash
        
    Returns:
        The MD5 hash as a hexadecimal string
    """
    return hashlib.md5(text.encode()).hexdigest()


class HashToolExecutor:
    """Executor for hash operations that can chain multiple hash functions."""
    
    def __init__(self):
        self.tools = {
            'sha512': sha512_hash,
            'md5': md5_hash,
        }
    
    def execute_sequence(self, initial_text: str, operations: List[str]) -> Dict[str, Any]:
        """
        Execute a sequence of hash operations.
        
        Args:
            initial_text: The starting text
            operations: List of operations to perform (e.g., ['sha512', 'sha512', 'md5'])
            
        Returns:
            Dictionary with intermediate steps and final result
        """
        result = initial_text
        steps = [f"Initial: {initial_text}"]
        
        for i, op in enumerate(operations, 1):
            if op.lower() in self.tools:
                tool_func = self.tools[op.lower()]
                result = tool_func.invoke(result)
                steps.append(f"Step {i} ({op}): {result[:16]}...{result[-16:]}" if len(result) > 32 else f"Step {i} ({op}): {result}")
            else:
                raise ValueError(f"Unknown operation: {op}")
        
        return {
            'steps': steps,
            'final_result': result,
            'operations_performed': operations
        }
    
    def parse_and_execute(self, instruction: str) -> str:
        """
        Parse an instruction string and execute the hash operations.
        
        Args:
            instruction: Natural language instruction for hash operations
            
        Returns:
            The final hash result
        """
        # Extract the initial string to hash
        import re
        
        # Look for quoted strings
        string_match = re.search(r'"([^"]+)"', instruction)
        if not string_match:
            string_match = re.search(r"'([^']+)'", instruction)
        
        if not string_match:
            return "Error: Could not find the string to hash. Please provide it in quotes."
        
        initial_text = string_match.group(1)
        
        # Extract the sequence of operations
        operations = []
        
        # Look for numbered operations (more specific pattern)
        # Match patterns like "1. sha512" or "1. sha512," or "1. sha512."
        operation_patterns = [
            r'1\.\s*(sha512|md5|sha256|sha1)',
            r'2\.\s*(sha512|md5|sha256|sha1)',
            r'3\.\s*(sha512|md5|sha256|sha1)',
            r'4\.\s*(sha512|md5|sha256|sha1)',
            r'5\.\s*(sha512|md5|sha256|sha1)',
            r'6\.\s*(sha512|md5|sha256|sha1)',
            r'7\.\s*(sha512|md5|sha256|sha1)',
            r'8\.\s*(sha512|md5|sha256|sha1)',
        ]
        
        for pattern in operation_patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                operations.append(match.group(1).lower())
        
        # If no numbered operations found, look for operations in sequence
        if not operations:
            # Try to find operations mentioned after "operations:" or "sequence:"
            parts = instruction.lower()
            hash_ops = re.findall(r'\b(sha512|md5|sha256|sha1)\b', parts)
            if hash_ops:
                # Filter out duplicates that might be from the instruction text
                operations = hash_ops
        
        if not operations:
            return "Error: Could not identify the hash operations to perform."
        
        try:
            result = self.execute_sequence(initial_text, operations)
            return result['final_result']
        except Exception as e:
            return f"Error executing hash operations: {str(e)}"
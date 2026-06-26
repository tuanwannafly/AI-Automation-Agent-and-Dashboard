from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    name: str = "base_tool"
    description: str = "Base tool"
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool"""
        pass

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for information"
    
    async def execute(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        import requests
        from bs4 import BeautifulSoup
        
        try:
            search_url = f"https://www.google.com/search?q={query}&num={num_results}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(search_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            results = []
            for g in soup.find_all("div", class_="g", limit=num_results):
                title_elem = g.find("h3")
                link_elem = g.find("a")
                snippet_elem = g.find("div", class_=["VwiC3b", "yXK7lf"], string=True)
                
                if title_elem and link_elem:
                    results.append({
                        "title": title_elem.text,
                        "link": link_elem.get("href"),
                        "snippet": str(snippet_elem) if snippet_elem else ""
                    })
            
            return {"success": True, "results": results, "query": query}
        except Exception as e:
            return {"success": False, "error": str(e), "query": query}

class CodeExecutorTool(BaseTool):
    name = "code_executor"
    description = "Execute Python code safely"
    
    async def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        import ast
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        
        allowed_modules = {"math", "random", "statistics", "datetime", "collections", "itertools", "functools", "re", "json"}
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name not in allowed_modules:
                            return {"success": False, "error": f"Import not allowed: {alias.name}"}
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.split(".")[0] not in allowed_modules:
                        return {"success": False, "error": f"Import not allowed: {node.module}"}
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ["system", "popen", "exec", "eval", "__import__"]:
                            return {"success": False, "error": f"Dangerous function call: {node.func.attr}"}
            
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            
            local_scope = {}
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                exec(code, {"__builtins__": __builtins__}, local_scope)
            
            stdout = output_buffer.getvalue()
            stderr = error_buffer.getvalue()
            
            result = local_scope.get("result", local_scope.get("answer", None))
            
            return {
                "success": True,
                "stdout": stdout,
                "stderr": stderr,
                "result": result,
                "variables": {k: v for k, v in local_scope.items() if not k.startswith("_")}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Perform mathematical calculations"
    
    async def execute(self, expression: str) -> Dict[str, Any]:
        import ast
        import operator
        
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        
        try:
            tree = ast.parse(expression, mode="eval")
            
            def eval_node(node):
                if isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    left = eval_node(node.left)
                    right = eval_node(node.right)
                    return operators[type(node.op)](left, right)
                elif isinstance(node, ast.UnaryOp):
                    operand = eval_node(node.operand)
                    return operators[type(node.op)](operand)
                else:
                    raise ValueError(f"Unsupported node: {type(node)}")
            
            result = eval_node(tree.body)
            return {"success": True, "result": result, "expression": expression}
        except Exception as e:
            return {"success": False, "error": str(e), "expression": expression}

def get_available_tools() -> Dict[str, BaseTool]:
    return {
        "web_search": WebSearchTool(),
        "code_executor": CodeExecutorTool(),
        "calculator": CalculatorTool(),
    }
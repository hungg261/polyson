import re

def evaluate_expression(expr, ctx):
    for var_name, var_val in ctx.items():
        expr = re.sub(r'\b' + var_name + r'\b', str(var_val), expr)
    try:
        cleaned = re.sub(r'[^0-9\+\-\*\/\(\)\s]', '', expr)
        return int(eval(cleaned))
    except:
        return expr.strip()

def parse_freemarker_polygon(ftl_content):
    ftl_content = re.sub(r"<#--.*?-->", "", ftl_content, flags=re.DOTALL)
    
    context = {}
    assign_pattern = r"<#assign\s+(\w+)\s*=\s*([^>]+)>"
    
    for var_name, expr in re.findall(assign_pattern, ftl_content):
        context[var_name] = evaluate_expression(expr, context)
    
    ftl_content = re.sub(assign_pattern, "", ftl_content)
    list_pattern = r"<#list\s+([^.]+)\.\.([^\s>]+)(?:\s+b([^\s>]+))?\s+as\s+(\w+)>(.*?)</#list>"
    matches = re.findall(list_pattern, ftl_content, re.DOTALL)
    commands = []
    
    if not matches:
        lines = [line.strip() for line in ftl_content.split('\n') if line.strip()]
        for line in lines:
            replaced_line = line
            for var_name, var_val in context.items():
                replaced_line = re.sub(r'\$\{' + var_name + r'\}', str(var_val), replaced_line)
            commands.append(replaced_line)
        return commands

    for start_expr, end_expr, step_expr, var_name, loop_body in matches:
        start = int(evaluate_expression(start_expr, context))
        end = int(evaluate_expression(end_expr, context))
        step = int(evaluate_expression(step_expr, context)) if step_expr else 1
        
        for i in range(start, end + 1, step):
            local_context = context.copy()
            local_context[var_name] = i
            for line in loop_body.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                def replace_expr_match(match):
                    expr_inside = match.group(1)
                    return str(evaluate_expression(expr_inside, local_context))
                replaced_line = re.sub(r"\$\{([^}]+)\}", replace_expr_match, line)
                commands.append(replaced_line)
                
    return commands

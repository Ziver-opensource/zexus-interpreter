    # Evaluate target and policy
    target_value = eval_node(node.target, env)
    if isinstance(target_value, (EvaluationError, ObjectEvaluationError)):
        return target_value

    policy_value = eval_node(node.policy, env)
    if isinstance(policy_value, (EvaluationError, ObjectEvaluationError)):
        return policy_value

    # Extract policy settings from map
    ttl = 3600  # Default 1 hour
    invalidate_on = []

    if isinstance(policy_value, Map):
        for key, value in policy_value.pairs.items():
            key_str = key.value if isinstance(key, String) else str(key)
            if key_str == "ttl" and isinstance(value, Integer):
                ttl = value.value
            elif key_str == "invalidate_on" and isinstance(value, List):
                invalidate_on = [item.value if hasattr(item, 'value') else str(item) for item in value.elements]

    # Create cache policy
    cache_policy = CachePolicy(ttl=ttl, invalidate_on=invalidate_on)

    # Register in security context
    ctx = get_security_context()
    ctx.cache_policies = getattr(ctx, 'cache_policies', {})
    ctx.cache_policies[str(node.target)] = cache_policy

    return NULL


def eval_seal_statement(node, env, stack_trace=None):
    """Evaluate seal statement - mark a variable as sealed (immutable)

    Only identifier targets are supported for simple sealing (e.g. `seal myVar`).
    """
    from .security import SealedObject

    # Only support sealing identifiers for now
    target = node.target
    if target is None:
        return EvaluationError("seal: missing target")

    # If target is an Identifier, seal that variable in the environment
    if isinstance(target, Identifier):
        name = target.value
        current = env.get(name)
        if current is None:
            return EvaluationError(f"seal: identifier '{name}' not found")
        sealed = SealedObject(current)
        env.set(name, sealed)
        debug_log("  Sealed identifier", name)
        return sealed

    # If target is a property access, attempt to seal the referenced value
    if hasattr(target, 'object') and hasattr(target, 'property'):
        obj = eval_node(target.object, env, stack_trace)
        if is_error(obj):
            return obj
        prop_name = target.property.value
        # Try maps and entity instances
        try:
            # Map-like
            if isinstance(obj, Map):
                val = obj.pairs.get(prop_name)
                if val is None:
                    return EvaluationError(f"seal: property '{prop_name}' not found")
                obj.pairs[prop_name] = SealedObject(val)
                debug_log("  Sealed map property", prop_name)
                return obj.pairs[prop_name]
            # EntityInstance-like: try to set via set() API
            if hasattr(obj, 'set') and hasattr(obj, 'get'):
                val = obj.get(prop_name)
                if val is None:
                    return EvaluationError(f"seal: property '{prop_name}' not found on object")
                obj.set(prop_name, SealedObject(val))
                debug_log("  Sealed object property", prop_name)
                return SealedObject(val)
        except Exception as e:
            return EvaluationError(f"seal error: {str(e)}")

    return EvaluationError("seal: unsupported target; use an identifier or property access")

# Production evaluation with enhanced debugging
def evaluate(program, env, debug_mode=False):
    """Production evaluation with enhanced error handling and debugging"""
    if debug_mode:
        env.enable_debug()
        print("🔧 Debug mode enabled")

    result = eval_node(program, env)
    # Resolve awaitables at the top level when possible
    result = _resolve_awaitable(result)

    if debug_mode:
        env.disable_debug()

    # When debug mode is off, print a concise 5-line summary only
    if not debug_mode:
        try:
            print(f"Summary: statements parsed={EVAL_SUMMARY.get('parsed_statements',0)}")
            print(f"Summary: statements evaluated={EVAL_SUMMARY.get('evaluated_statements',0)}")
            print(f"Summary: errors={EVAL_SUMMARY.get('errors',0)}")
            print(f"Summary: async_tasks_run={EVAL_SUMMARY.get('async_tasks_run',0)}")
            print(f"Summary: max_statements_in_block={EVAL_SUMMARY.get('max_statements_in_block',0)}")
        except Exception:
            # If summary printing fails, ignore and continue
            pass

    if isinstance(result, (EvaluationError, ObjectEvaluationError)):
        return str(result)

    return result

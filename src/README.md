# Zexus — Developer Guide (Interpreter & Compiler)

This document describes the source layout, responsibilities of each module under `src/zexus`, the language syntax accepted by the system (both interpreter and compiler), examples, built-ins, and developer workflows for testing and extending the project.

Use this as the canonical reference for contributors and maintainers.

---

## Quick commands

- Run quick integration tests:
  - `python3 scripts/verify_integration.py`
- Run compiler investigation script:
  - `python3 investigate_compiler.py`
- Run unit tests (if present):
  - `pytest tests/`
- Start interactive experimentation (REPL not included by default):
  - Use the interpreter pipeline in python REPL by importing modules.

---

## High-level architecture

- **Lexer**: tokenizes source text into a token stream.
- **Parser(s)**: Convert tokens into AST nodes.
  - Interpreter parser (tolerant): robust parsing that recovers from mixed syntax styles and common mistakes.
  - Compiler parser (production): cleaner AST for semantic checks and bytecode generation; made tolerant for common surface differences.
- **Structural/context strategies**: helpers used by the tolerant interpreter parser to split token streams into blocks and map blocks to AST.
- **AST**: two parallel AST definitions:
  - Interpreter AST (`src/zexus/zexus_ast.py`) — richer node set used by the evaluator.
  - Compiler AST (`src/zexus/compiler/zexus_ast.py`) — cleaner nodes optimized for semantic analysis and code generation.
- **Evaluator**: Walks the interpreter AST and produces runtime objects; includes builtins and error handling.
- **Object model**: Runtime `Object` classes (Integer, String, List, Map, Environment, Builtin, Action, etc.).
- **Compiler front-end**: Production lexer/parser, semantic analyzer, bytecode generator.
- **Renderer System**: Advanced UI/graphics system with screens, components, themes, and canvas drawing.
- **Virtual Machine**: **NEW** - Advanced stack-based VM with async/await, events, modules, and closure support.
- **Utilities**: syntax validator, recovery engine, config flags, developer scripts.

---

## File map (src/zexus) — what each file does

### Core Language
- `zexus_token.py`
  - Defines token constants and Token class.
  - **NEW**: Async/events tokens (`ASYNC`, `AWAIT`, `EVENT`, `EMIT`, `ENUM`, `PROTOCOL`, `IMPORT`)

- `lexer.py`
  - Implements lexical analysis (character scanning → tokens).

- `zexus_ast.py` (interpreter)
  - Interpreter AST node classes.
  - **NEW**: `AsyncActionStatement`, `AwaitExpression`, `EventStatement`, `EmitStatement`, `EnumStatement`, `ProtocolStatement`, `ImportStatement`

- `evaluator.py`
  - Evaluator walks interpreter AST and returns runtime objects.
  - **NEW**: Async/event builtins and runtime support.

### Compiler System
- `compiler/__init__.py`
  - Exposes `ZexusCompiler`, re-exports interpreter `builtins` as `BUILTINS`.

- `compiler/parser.py` (ProductionParser)
  - **NEW**: Supports async actions, await expressions, events, enums, protocols, imports.

- `compiler/zexus_ast.py` (compiler)
  - **NEW**: Async/events AST nodes for compiler pipeline.

- `compiler/semantic.py`
  - **NEW**: Semantic checks for async usage, event signatures, protocol conformance.

- `compiler/bytecode.py`
  - **NEW**: Bytecode generation for async/await, events, modules, closures.

### Virtual Machine (NEW - Major Update)
- `vm/vm.py`
  - **COMPLETELY REWRITTEN**: Advanced stack-based VM with:
    - **Low-level ops**: `LOAD_CONST`, `LOAD`, `STORE`, `CALL`, `JUMP`, `RETURN`
    - **Async primitives**: `SPAWN`, `AWAIT` - real coroutine support
    - **Event system**: `REGISTER_EVENT`, `EMIT_EVENT` - reactive programming
    - **Module system**: `IMPORT` - Python module integration
    - **Type system**: `DEFINE_ENUM`, `ASSERT_PROTOCOL` - advanced types
    - **Function calls**: `CALL_NAME`, `CALL_FUNC_CONST`, `CALL_TOP` - multiple calling conventions
    - **Closure support**: `STORE_FUNC` with lexical closure capture

- `vm/bytecode.py`
  - **NEW**: Complete bytecode instruction set and VM operations.

### Renderer System
- `renderer/` - Advanced UI/Graphics System
  - `backend.py` - Unified backend for interpreter and VM
  - `color_system.py` - Color mixing, themes, gradients
  - `layout.py` - Screen components and inheritance
  - `painter.py` - Terminal graphics with styling
  - `canvas.py` - Drawing primitives
  - `graphics.py` - Clocks, animations, visualizations

---

## Language syntax overview

### NEW: Advanced Language Features

#### Async/Await System
```zexus
// Real async/await with proper concurrency
action async broadcast_transaction(tx: Transaction) {
    let peers = get_connected_peers()
    for each p in peers {
        let response = await p.send(tx)  // 🚀 Real async I/O
        if response.success {
            print("Propagated to " + p.address)
        }
    }
}

action async mine_block() {
    let block = await create_new_block()
    let result = await broadcast_block(block)
    return result
}
```

Event System

```zexus
// Reactive event-driven programming
event TransactionMined {
    hash: string,
    block_number: integer,
    from: Address,
    to: Address
}

// Register event handlers
register_event("tx_mined", action(tx) {
    update_wallet_balance(tx.from, -tx.amount)
    update_wallet_balance(tx.to, tx.amount)
    notify_subscribers(tx)
})

// Emit events
action confirm_transaction(tx: Transaction) {
    // ... validation logic
    emit TransactionMined {
        hash: tx.hash,
        block_number: current_block,
        from: tx.from,
        to: tx.to
    }
}
```

Module System

```zexus
// Import external modules
use "crypto" as crypto
use "network" as p2p
use "blockchain" as chain

action create_wallet() {
    let keypair = crypto.generate_keypair()
    let address = crypto.derive_address(keypair.public_key)
    return Wallet { keypair: keypair, address: address }
}
```

Enums & Protocols

```zexus
// Advanced type system
enum ChainType {
    ZIVER,
    ETHEREUM, 
    BSC,
    TON,
    POLYGON
}

protocol Wallet {
    action transfer(to: Address, amount: integer) -> boolean
    action get_balance() -> integer
    action get_address() -> Address
}

// Protocol implementation
contract MyWallet implements Wallet {
    action transfer(to: Address, amount: integer) -> boolean {
        // implementation
        return true
    }
    
    action get_balance() -> integer {
        return this.balance
    }
    
    action get_address() -> Address {
        return this.address
    }
}
```

Closure System

```zexus
// Proper lexical closures
action create_counter() {
    let count = 0
    
    action increment() {
        count = count + 1
        return count
    }
    
    action get_count() {
        return count
    }
    
    return [increment, get_count]
}

// Usage - maintains proper closure semantics
let counter_ops = create_counter()
let increment = counter_ops[0]
let get_count = counter_ops[1]

print(increment())  // 1
print(increment())  // 2  
print(get_count())  // 2 - Correct closure behavior!
```

Existing Features (Enhanced)

Renderer System

```zexus
// Now works in both interpreter and compiled modes
Screen blockchain_dashboard {
    height: 30,
    width: 100,
    theme: "dark_theme"
}

Component mining_visualization {
    type: "mining_viz",
    x: 10,
    y: 5,
    width: 80,
    height: 20
}

action async update_dashboard() {
    define_screen("blockchain_dashboard")
    define_component("mining_visualization") 
    add_to_screen("blockchain_dashboard", "mining_visualization")
    
    while true {
        let output = render_screen("blockchain_dashboard")
        print(output)
        await sleep(1)  // Async rendering loop
    }
}
```

Smart Contract Ready

```zexus
contract Token {
    persistent storage balances: Map<Address, integer>
    persistent storage total_supply: integer
    
    action transfer(to: Address, amount: integer) -> boolean {
        let sender = msg.sender
        let sender_balance = balances.get(sender, 0)
        
        require(sender_balance >= amount, "Insufficient balance")
        require(amount > 0, "Amount must be positive")
        
        balances[sender] = sender_balance - amount
        balances[to] = balances.get(to, 0) + amount
        
        emit Transfer { from: sender, to: to, amount: amount }
        return true
    }
}
```

---

Virtual Machine Architecture (NEW)

Stack-Based Execution

```
[VM Stack Machine]
├── Value Stack: [val1, val2, val3, ...]
├── Call Stack: [frame1, frame2, ...]  
├── Environment: {vars, closures, builtins}
└── Event Registry: {event_name: [handlers]}
```

Bytecode Operations

```python
# Low-level ops (stack machine)
LOAD_CONST 0      # Push constant
STORE "x"         # Pop and store variable  
LOAD "x"          # Push variable value
CALL_NAME "print" # Call function
SPAWN             # Create async task
AWAIT             # Await coroutine
JUMP 15           # Jump to instruction
```

Closure Implementation

```python
# Closure capture uses Cell objects
def STORE_FUNC(name, func_descriptor):
    # Capture current environment as closure cells
    closure = {k: Cell(v) for k, v in current_env.items()}
    func_descriptor.closure = closure
    current_env[name] = func_descriptor
```

---

Execution Modes

1. Interpreter Mode

· Direct AST evaluation
· Good for development/debugging
· Full language support

2. Compiler Mode

· Source → Bytecode → VM execution
· Better performance
· NEW: Full async/events/closure support

3. Auto Mode

· Attempt compilation, fallback to interpreter
· Best of both worlds

Unified Renderer Backend

· Renderer works identically in all modes
· Single backend API for both interpreter and VM

---

Built-in functions (Enhanced)

Core Builtins

· string(x), len(x), first(list), rest(list)
· map(), filter(), reduce()
· datetime_now(), random(), sqrt()

NEW: Async & Network

· sleep(seconds) - Async sleep
· spawn(coroutine) - Create async task
· fetch(url) - HTTP requests
· connect_peer(address) - P2P networking

NEW: Crypto & Blockchain

· keccak256(data) - Hashing
· secp256k1_sign(msg, key) - Signing
· verify_signature(msg, sig, pubkey) - Verification
· create_address(pubkey) - Address derivation

Renderer Builtins

· define_screen(), define_component(), render_screen()
· mix(), create_canvas(), draw_line(), draw_circle()

---

Developer workflows

Adding New Syntax

1. Add tokens in zexus_token.py
2. Update lexer in lexer.py
3. Add AST nodes in both zexus_ast.py and compiler/zexus_ast.py
4. Implement parsing in both parsers
5. Add bytecode generation in compiler/bytecode.py
6. Implement VM support in vm/vm.py
7. Add semantic checks in compiler/semantic.py
8. Create tests and update verification scripts

Async/Event Development

```zexus
// 1. Define async action
action async network_operation() {
    let data = await fetch("https://api.example.com/data")
    return process(data)
}

// 2. Define events
event DataReceived {
    url: string,
    data: any,
    timestamp: integer
}

// 3. Register handlers
register_event("data_received", action(event) {
    print("Received data from " + event.url)
    cache_data(event.data)
})

// 4. Emit events
emit DataReceived {
    url: "https://api.example.com/data",
    data: response_data,
    timestamp: datetime_now().timestamp()
}
```

---

Testing & Verification

Comprehensive Testing

```bash
# Run full test suite
python3 scripts/verify_integration.py

# Test specific features
python3 -c "
from zexus.compiler import ZexusCompiler

# Test async/await
code = '''
action async test_async() {
    let result = await some_operation()
    return result
}
'''

compiler = ZexusCompiler(code)
bytecode = compiler.compile()
if compiler.errors:
    print('Errors:', compiler.errors)
else:
    result = compiler.run_bytecode(debug=True)
    print('Result:', result)
"
```

VM Inspection

```python
from zexus.vm.vm import VM

# Create VM with custom environment
vm = VM(builtins=my_builtins, env=initial_env)

# Execute and inspect
result = vm.execute(bytecode, debug=True)
print("VM Stack:", vm.stack)
print("VM Environment:", vm.env)
```

---

Performance Characteristics

Interpreter Mode

· Pros: Fast startup, easy debugging
· Cons: Slower execution, no optimizations

Compiler + VM Mode

· Pros: Better performance, async optimization
· Cons: Slower startup, more complex

Memory Management

· Stack-based: Efficient value passing
· Closure cells: Proper memory handling
· Async tasks: Automatic cleanup

---

Production Readiness

✅ Implemented

· Complete language syntax
· Advanced type system
· Async/await concurrency
· Event-driven architecture
· Module system
· Closure semantics
· Virtual machine
· Renderer system

🚀 Blockchain Ready

· Smart contract runtime
· P2P networking primitives
· Crypto operations
· State management
· Gas tracking (conceptual)

🔧 Next Steps

· Enhanced optimizer
· JIT compilation
· Production deployment
· Standard library expansion

---

Contribution Guidelines

Code Standards

· Maintain dual AST compatibility
· Test both interpreter and compiler paths
· Ensure renderer backend consistency
· Document new VM operations

Testing Requirements

· Add integration tests for new features
· Verify async/event behavior
· Test closure semantics
· Ensure cross-mode compatibility

Documentation

· Update this README for new features
· Add examples for complex features
· Document VM bytecode operations
· Create architecture diagrams

---

Architecture Diagrams Available

· Language compilation pipeline
· VM stack machine operation
· Async/event system flow
· Closure memory model
· Renderer component architecture

Contact maintainers for detailed architecture diagrams.

---

Zexus is now a production-ready language system capable of building sophisticated applications including blockchain platforms, reactive UIs, and distributed systems.
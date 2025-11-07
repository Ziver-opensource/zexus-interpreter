# Zexus — Developer Guide (Interpreter & Compiler)

This document describes the source layout, responsibilities of each module under `src/zexus`, the language syntax accepted by the system (both interpreter and compiler), examples, built-ins, and developer workflows for testing and extending the project.

Use this as the canonical reference for contributors and maintainers.

---

## Quick commands

- Run quick integration tests:
  - python3 scripts/verify_integration.py
- Run compiler investigation script:
  - python3 investigate_compiler.py
- Run unit tests (if present):
  - pytest tests/
- Start interactive experimentation (REPL not included by default):
  - Use the interpreter pipeline in python REPL by importing modules.

---

## High-level architecture

- Lexer: tokenizes source text into a token stream.
- Parser(s): Convert tokens into AST nodes.
  - Interpreter parser (tolerant): robust parsing that recovers from mixed syntax styles and common mistakes.
  - Compiler parser (production): cleaner AST for semantic checks and bytecode generation; made tolerant for common surface differences.
- Structural/context strategies: helpers used by the tolerant interpreter parser to split token streams into blocks and map blocks to AST.
- AST: two parallel AST definitions:
  - Interpreter AST (`src/zexus/zexus_ast.py`) — richer node set used by the evaluator.
  - Compiler AST (`src/zexus/compiler/zexus_ast.py`) — cleaner nodes optimized for semantic analysis and code generation.
- Evaluator: Walks the interpreter AST and produces runtime objects; includes builtins and error handling.
- Object model: Runtime `Object` classes (Integer, String, List, Map, Environment, Builtin, Action, etc.).
- Compiler front-end: Production lexer/parser, semantic analyzer, bytecode generator.
- **Renderer System**: Advanced UI/graphics system with screens, components, themes, and canvas drawing.
- **Virtual Machine**: Executes compiled bytecode with renderer support.
- Utilities: syntax validator, recovery engine, config flags, developer scripts.

---

## File map (src/zexus) — what each file does

- zexus_token.py
  - Defines token constants and possibly a Token class.
  - Tokens: keywords (LET, IF, ELSE, TRY, CATCH, ACTION, EXTERNAL, EXPORT, USE, DEBUG...), punctuation (LBRACE, RBRACE, LPAREN, RPAREN, SEMICOLON, COMMA, COLON), operators, literal token types (INT, FLOAT, STRING, IDENT), and EOF.
  - **NEW**: Renderer tokens (SCREEN, COMPONENT, THEME, COLOR, GRAPHICS, CANVAS, ANIMATION, CLOCK, MIX, RENDER, ADD_TO, SET_THEME, CREATE_CANVAS, DRAW, WIDTH, HEIGHT, X, Y, TEXT, BACKGROUND, BORDER, STYLE, RADIUS, FILL).

- lexer.py
  - Implements lexical analysis (character scanning → tokens).
  - Handles numbers, strings (escape sequences), identifiers/keywords, comments, and punctuation.
  - Exposes `next_token()` and helper methods for tests (e.g. `tokenize()`).

- zexus_ast.py (interpreter)
  - Interpreter AST node classes:
    - Program, Statement / Expression base classes.
    - Statement nodes: LetStatement, ReturnStatement, ExpressionStatement, BlockStatement, PrintStatement, ForEachStatement, EmbeddedCodeStatement, UseStatement, IfStatement, WhileStatement, **ScreenStatement, ComponentStatement, ThemeStatement**, ActionStatement, ExactlyStatement, ExportStatement, DebugStatement, TryCatchStatement, ExternalDeclaration.
    - Expression nodes: Identifier, IntegerLiteral, FloatLiteral, StringLiteral, Boolean, ListLiteral, MapLiteral, ActionLiteral, LambdaExpression, CallExpression, MethodCallExpression, PropertyAccessExpression, AssignmentExpression, EmbeddedLiteral, PrefixExpression, InfixExpression, IfExpression.
  - These nodes are designed to be directly evaluated by the interpreter evaluator.

- syntax_validator.py
  - Static analysis to suggest style/fixups.
  - Supports two styles:
    - "universal": requires parens/braces (if(...){...}), stricter.
    - "tolerable": allows colon blocks, leading `debug ` style, and other legacy forms.
  - Offers `validate_code`, `auto_fix`, and `suggest_syntax_style`.

- strategy_structural.py
  - StructuralAnalyzer: scans the token stream and segments it into top-level blocks.
  - Brace-aware collection, special handling for try/catch blocks and map literals.
  - Produces a block map consumed by the context parser.

- strategy_context.py
  - ContextStackParser: maps structural blocks to interpreter AST nodes with awareness of current parsing context.
  - Contains direct parsers for statements often found inside blocks (let, print, assignment, function call, try-catch).
  - Converts token sequences into AST nodes, using heuristics for tolerant parsing.

- strategy_recovery.py
  - ErrorRecoveryEngine: heuristics to skip tokens and continue parsing after errors (used by the tolerant parser).

- parser.py (interpreter) — UltimateParser
  - Entry point for interpreter parsing.
  - Multi-strategy:
    - Uses StructuralAnalyzer and ContextStackParser to handle messy inputs.
    - Falls back to traditional recursive-descent.
  - Supports both universal and tolerable styles via config flags.
  - Produces interpreter AST nodes (zexus_ast.py).

- evaluator.py
  - Evaluator walks interpreter AST and returns runtime objects.
  - Implements:
    - eval_program, eval_node (multi-dispatch on node types), expression evaluation, function application.
    - Enhanced error types (EvaluationError, FixedEvaluationError) and debug logging helpers.
    - try/catch evaluation with proper isolation: if try-block raises, the catch block runs with an environment containing the error variable.
  - Builtins: provided as Python functions wrapped as Builtin objects. Examples:
    - string(x), len(x), first/rest/push, map/filter/reduce, datetime_now, random, sqrt, to_hex/from_hex, file_read_text, file_write_text, file_read_json, file_write_json, debug_log, debug_trace.
    - **NEW RENDERER BUILTINS**: define_screen, define_component, render_screen, add_to_screen, set_theme, mix (color mixing), create_canvas, draw_line, draw_circle, draw_rectangle, draw_text, create_animation, start_animation.
  - Exposes `evaluate(program, env, debug_mode=False)`.

- object.py
  - Definitions for runtime objects and Environment API:
    - Integer, Float, String, List, Map, Null, Boolean, Builtin, Action, ReturnValue, LambdaFunction, DateTime, Math, File, Debug.
  - Environment provides scoping, `get`, `set`, `get_exports`, `export`.

- config.py
  - Global runtime/config flags:
    - syntax_style (default "universal" or "tolerable")
    - enable_advanced_parsing
    - enable_debug_logs, etc.

- compiler/ (subpackage)
  - __init__.py
    - Exposes `ZexusCompiler`, aliases `Parser` for backward compatibility, and re-exports interpreter `builtins` as `BUILTINS` when available (fallback to {}).
  - lexer.py (compiler-specific)
    - A lexer variant used by the compiler front-end (may be similar to interpreter lexer).
  - parser.py (ProductionParser)
    - Cleaner parser that produces `src/zexus/compiler/zexus_ast.py` nodes.
    - Historically stricter; recent changes introduced tolerant behaviors for:
      - stray semicolons
      - map literal separators (accept `,` and `;`)
      - try/catch parenthesis variants
  - zexus_ast.py (compiler)
    - Cleaner AST node classes optimized for semantic analysis and bytecode generation.
    - Includes TryCatchStatement and ExternalDeclaration so the compiler can represent try/catch and "external action" declarations.
    - **NEW**: Screen, Component, Theme AST nodes for renderer support.
  - semantic.py
    - Semantic analyzer: name resolution, builtin wiring, type checks, export permissions.
    - Should consult `compiler.__init__.BUILTINS` for builtin function definitions to avoid duplication.
  - bytecode.py
    - Bytecode generator that walks compiler AST and emits instructions for the VM or for downstream stages.
    - **NEW**: Renderer operation bytecodes.

- vm/ (Virtual Machine subpackage)
  - __init__.py - VM package exports
  - vm.py - **NEW**: Small VM that executes compiler bytecode and delegates renderer operations to backend
  - bytecode.py - VM bytecode definitions and operations
  - jit.py - (Future) Just-In-Time compilation optimizations

- renderer/ (Advanced UI/Graphics System) - **NEW**
  - __init__.py - Renderer package exports and backend facade
  - backend.py - Unified backend used by both interpreter and VM
  - color_system.py - Advanced color mixing, themes, gradients, RGB/HSV conversion
  - layout.py - Screen components, inheritance system, UI layout management
  - painter.py - Modern terminal painter with colors, styles, rounded corners
  - canvas.py - Drawing primitives (lines, circles, polygons, arcs), graphics system
  - graphics.py - Advanced components (clocks, progress meters, animations, mining visualizations)

- scripts/
  - verify_integration.py
    - Runs representative code snippets through both the interpreter and the compiler and prints pass/fail diagnostics.
  - investigate_compiler.py
    - Helper script that executes the CLI `zx` in different modes to exercise compiler/integrated runtime.

- debug_parser.py
  - Developer script to dump tokens and AST from the parser for a small hard-coded sample.

---

## Language syntax overview (what both parsers accept)

Both parser variants support a largely overlapping language; the interpreter parser is more tolerant and accepts several stylistic variations.

General tokens/keywords:
- let, return, print, for, each, in, action, if, else, while, try, catch, debug, external, from, use, export, screen, exactly, lambda
- **NEW RENDERER**: screen, component, theme, color, graphics, canvas, animation, clock, mix, render, add_to, set_theme, create_canvas, draw

Literals:
- Integers: 42
- Floats: 3.14
- Strings: "hello world"
- Booleans: true, false
- Lists: [1, 2, "a"]
- Maps/objects: { "a": 1, b: 2 } — keys can be string literals or bare identifiers

Operators:
- Arithmetic: +, -, *, /, %
- Comparison: ==, !=, <, >, <=, >=
- Logical: &&, ||
- Assignment: =

Function and method calls:
- Function: fn(arg1, arg2)
- Method: obj.method(arg1)
- Lambda: lambda(x) -> x + 1  OR lambda x -> x + 1  (tolerant parser)
- Action literal (block function): action(param1, param2) { ... } or action(param1): ... (tolerant)

**NEW RENDERER SYNTAX:**
```zexus
// Screen definitions
Screen login_page {
    height: 20,
    width: 60,
    theme: "dark_theme",
    title: "Login System"
}

// Component definitions  
Component login_button {
    type: "button",
    text: "Login",
    color: mix("blue", "white", 0.2),
    x: 24,
    y: 10,
    width: 12,
    height: 3
}

// Theme definitions
Theme dark_theme {
    primary: "blue",
    accent: "mint", 
    background: "black",
    text: "white"
}

// Color mixing
Color primary = mix("blue", "purple", 0.3)

// Graphics operations
let canvas = create_canvas(80, 25)
draw_line(canvas, 10, 10, 50, 10, color: "red")
draw_circle(canvas, 40, 12, 8, fill: true)

// Screen assembly and rendering
add_to_screen("login_page", "login_button")
let output = render_screen("login_page")
print(output)
```

Blocks and block styles:

· Universal style (preferred):
  · if (cond) { ... }
  · while (cond) { ... }
  · try { ... } catch(error) { ... }
· Tolerable style (older/alternative):
  · if cond:
    ...
  · action name(param):
    ...
· Semicolons:
  · Interpreter: semicolons optional (tolerant).
  · Compiler: semicolons recognized as separators; parser now skips stray semicolons at top-level and inside blocks.

Try/Catch forms accepted (tolerant):

· try { ... } catch(error) { ... }
· try { ... } catch error { ... }
· try { ... } catch((error)) { ... }  (extra parens allowed; parser normalizes)

Map/object separators:

· Standard: comma ,
· Tolerant: semicolon ; is also accepted as a separator (compiler parser was updated for tolerance)
· Trailing separators are tolerated by the parsers

Embedded code:

· Embedded blocks are represented as EmbeddedLiteral/EmbeddedCode with a language name on the first line
· Example:
  ```
  {|
  python
  print("hello from embedded")
  |}
  ```
  (exact marker depends on lexer/embedded tokenization)

---

Key examples

1. Simple print and builtin string:

```zexus
print(string(42));
```

1. Let + arithmetic:

```zexus
let x = 10 + 5
print(x)
```

1. Map literal:

```zexus
let m = { "a": 1, b: 2; c: 3, }
print(string(m))
```

1. Try/catch tolerant variants:

```zexus
try {
  let x = 10 / 0
} catch((err)) {
  print("error: " + string(err))
}
```

or

```zexus
try {
  let x = 10 / 0
} catch err {
  print("error: " + string(err))
}
```

1. Lambda and map:

```zexus
let nums = [1,2,3,4]
let doubled = nums.map(lambda(n) -> n * 2)
print(string(doubled))
```

1. NEW: Advanced renderer example - Mining Dashboard with Clock:

```zexus
Theme mining_theme {
    primary: "blue",
    accent: "orange",
    background: "black",
    text: "white"
}

Screen mining_dashboard {
    height: 25,
    width: 80,
    theme: "mining_theme",
    title: "⛏️ Blockchain Mining Operation"
}

Component hash_display {
    type: "textbox",
    text: "Hash Rate: 45.6 MH/s",
    x: 10,
    y: 5,
    width: 30,
    height: 3
}

Component mining_clock {
    type: "clock",
    x: 50,
    y: 5,
    radius: 8,
    style: "modern",
    show_seconds: true
}

action main() {
    set_theme("mining_theme")
    define_screen("mining_dashboard")
    define_component("hash_display")
    define_component("mining_clock")
    add_to_screen("mining_dashboard", "hash_display")
    add_to_screen("mining_dashboard", "mining_clock")
    
    // Real-time rendering loop
    while true {
        let dashboard_output = render_screen("mining_dashboard")
        print(dashboard_output)
        sleep(1)  // Update every second
    }
}
```

---

Built-in functions (common subset)

· string(x): convert to readable string
· len(x): length for strings/lists
· first(list), rest(list), push(list, value)
· map(list, lambda), filter(list, lambda), reduce(list, lambda [, initial])
· date/time: datetime_now(), timestamp()
· math: random(), sqrt(), to_hex(), from_hex()
· file I/O: file_read_text(path), file_write_text(path, data), file_read_json(path), file_write_json(path, data), file_list_dir(path)
· debug: debug_log(msg, value?), debug_trace(string)

NEW RENDERER BUILTINS:

· define_screen(name, properties): Define a screen template
· define_component(name, type, properties): Define a reusable component
· render_screen(screen_name): Render screen to terminal output
· add_to_screen(screen_name, component_name): Add component to screen
· set_theme(theme_name): Set active color theme
· mix(color1, color2, ratio): Mix two colors (returns new color)
· create_canvas(width, height): Create drawing canvas
· draw_line(canvas, x1, y1, x2, y2, color, thickness): Draw line on canvas
· draw_circle(canvas, x, y, radius, color, fill): Draw circle on canvas
· draw_rectangle(canvas, x, y, width, height, color, fill): Draw rectangle
· draw_text(canvas, x, y, text, color): Draw text on canvas
· create_animation(name, duration, update_callback, draw_callback): Create animation
· start_animation(name): Start named animation

Builtins are defined in evaluator.py as Python callables wrapped by Builtin objects. The compiler exposes the same set via src/zexus/compiler.__init__.BUILTINS when possible.

---

Developer workflows

· Add new syntax:
  1. Add token(s) in zexus_token.py.
  2. Update lexer.py to emit new tokens.
  3. Update both parsers:
     · Interpreter parser.py (UltimateParser / ContextStackParser) for tolerant acceptance.
     · Compiler compiler/parser.py (ProductionParser) for canonical AST emission.
  4. Add AST node in zexus_ast.py and compiler/zexus_ast.py as appropriate.
  5. Implement evaluation in evaluator.py (interpreter) and semantic/bytecode support in compiler modules.
  6. Add unit/integration tests and update scripts/verify_integration.py tests.
· Adding renderer features:
  1. Extend renderer backend in renderer/backend.py
  2. Add builtin wrapper in evaluator.py
  3. Update compiler bytecode generator in compiler/bytecode.py
  4. Add VM support in vm/vm.py
  5. Test in both interpreter and compiler modes
· Debugging parsing differences:
  · Use debug_parser.py and scripts/verify_integration.py to dump tokens and AST and compare interpreter vs compiler outputs.
· Ensuring builtin parity:
  · Keep builtin definitions in evaluator.py.
  · Expose them to compiler via compiler.__init__.BUILTINS so the semantic analyzer can map builtin names to behaviors during compilation.

---

Execution Modes

Zexus now supports multiple execution modes:

1. Interpreter Mode: Direct AST evaluation (original method)
2. Compiler Mode: Source → Bytecode → VM execution
3. Auto Mode: Attempt compilation, fall back to interpreter on failure

Renderer System Works in All Modes:

· Interpreter: Direct calls to renderer backend via builtins
· Compiler: Bytecode operations delegate to same renderer backend
· Unified results across all execution paths

---

Troubleshooting & common issues

· "Unexpected token ';'" — older compiler parser was strict; compiler/parser.py now tolerates stray semicolons and uses them as separators.
· "Identifier not found" at compile time — ensure semantic analyzer maps builtin names into its environment or compiler.__init__.BUILTINS is present.
· Try/catch parsing errors — tolerant parsing supports multiple catch syntaxes, but consistent source style (catch(error)) is recommended.
· Map/object parsing — ensure separators are either commas or semicolons; trailing separators are tolerated.
· Renderer not working — ensure renderer backend is properly imported and all renderer builtins are registered in environment.

---

Verification

Run:

```bash
python3 scripts/verify_integration.py
```

This will:

· Run representative snippets through both interpreter and compiler.
· Print parse/eval results and any compiler errors.
· NEW: Test renderer functionality in both modes.

Use investigate_compiler.py to execute the project CLI zx in different execution modes if you have the CLI installed.

Test renderer specifically:

```bash
echo 'Screen test { height: 10, width: 40 }; print(render_screen("test"))' | zx run --execution-mode compiler -
```

---

Contribution notes

· Follow the parse → AST → evaluate/compile flow.
· Tests are critical when changing parsing heuristics: add examples for both correct inputs and common malformed variants to ensure tolerant parser behavior remains stable.
· Keep both AST definitions aligned by name where nodes represent the same semantic construct (TryCatchStatement, ExternalDeclaration, DebugStatement, etc.).
· Renderer features should work identically in interpreter and compiler modes via the unified backend system.

---

If you want, I can:

· Generate a compact cheat-sheet (one-page PDF) showing syntax and examples.
· Add a pytest-based test-suite with canonical examples ensuring parity between interpreter and compiler.
· Produce a UML-style diagram of module relationships.
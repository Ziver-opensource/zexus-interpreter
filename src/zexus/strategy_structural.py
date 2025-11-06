# strategy_structural.py (FIXED VERSION - with improved try-catch parsing)
from .zexus_token import *
from typing import List, Dict

class StructuralAnalyzer:
    """Lightweight structural analyzer that splits token stream into top-level blocks.
    Special handling for try/catch to avoid merging statements inside try blocks.
    """

    def __init__(self):
        # blocks: id -> block_info
        self.blocks = {}

    def analyze(self, tokens: List):
        """Analyze tokens and produce a block map used by the context parser.

        block_info keys:
            - id: unique id
            - type/subtype: block type (e.g. 'try', 'let', 'print', 'block')
            - tokens: list of tokens that belong to the block
            - start_token: token object where block starts
            - start_index / end_index: indices in original token stream
            - parent: optional parent block id
        """
        self.blocks = {}
        i = 0
        block_id = 0
        n = len(tokens)

        # helper sets for stopping heuristics (mirrors context parser)
        stop_types = {SEMICOLON, RBRACE}
        statement_starters = {LET, PRINT, FOR, IF, WHILE, RETURN, ACTION, TRY, EXTERNAL, SCREEN, EXPORT, USE, DEBUG}

        while i < n:
            t = tokens[i]
            # skip EOF tokens
            if t.type == EOF:
                i += 1
                continue

            # Try-catch: collect the try block and catch block separately
            if t.type == TRY:
                start_idx = i
                # collect try token + following block tokens (brace-aware)
                try_block_tokens, next_idx = self._collect_brace_block(tokens, i + 1)
                # include the 'try' token as part of the block for context
                full_try_tokens = [t] + try_block_tokens
                self.blocks[block_id] = {
                    'id': block_id,
                    'type': 'try_catch',
                    'subtype': 'try',
                    'tokens': full_try_tokens,
                    'start_token': t,
                    'start_index': start_idx,
                    'end_index': next_idx - 1,
                    'parent': None
                }
                block_id += 1
                i = next_idx

                # Look for catch token after try block
                if i < n and tokens[i].type == CATCH:
                    catch_token = tokens[i]
                    catch_block_tokens, after_catch_idx = self._collect_brace_block(tokens, i + 1)
                    full_catch_tokens = [catch_token] + catch_block_tokens
                    self.blocks[block_id] = {
                        'id': block_id,
                        'type': 'try_catch',
                        'subtype': 'catch',
                        'tokens': full_catch_tokens,
                        'start_token': catch_token,
                        'start_index': i,
                        'end_index': after_catch_idx - 1,
                        'parent': None
                    }
                    block_id += 1
                    i = after_catch_idx
                continue

            # Brace-delimited top-level block
            if t.type == LBRACE:
                block_tokens, next_idx = self._collect_brace_block(tokens, i)
                self.blocks[block_id] = {
                    'id': block_id,
                    'type': 'block',
                    'subtype': 'brace_block',
                    'tokens': block_tokens,
                    'start_token': tokens[i],
                    'start_index': i,
                    'end_index': next_idx - 1,
                    'parent': None
                }
                block_id += 1
                i = next_idx
                continue

            # Statement-like tokens: try to collect tokens up to a statement boundary
            if t.type in statement_starters or t.type == LET or t.type == PRINT:
                start_idx = i
                stmt_tokens = [t]
                j = i + 1
                while j < n:
                    tj = tokens[j]
                    # stop at explicit terminator or when next token starts a new statement
                    if tj.type in stop_types:
                        break
                    if tj.type in statement_starters:
                        break
                    # also stop if we encounter a top-level block start
                    if tj.type == LBRACE:
                        break
                    stmt_tokens.append(tj)
                    j += 1
                self.blocks[block_id] = {
                    'id': block_id,
                    'type': 'statement',
                    'subtype': t.type,
                    'tokens': stmt_tokens,
                    'start_token': tokens[start_idx],
                    'start_index': start_idx,
                    'end_index': j,
                    'parent': None
                }
                block_id += 1
                i = j
                continue

            # Fallback: consume single token as a minimal block
            self.blocks[block_id] = {
                'id': block_id,
                'type': 'token',
                'subtype': t.type,
                'tokens': [t],
                'start_token': t,
                'start_index': i,
                'end_index': i,
                'parent': None
            }
            block_id += 1
            i += 1

        return self.blocks

    def _collect_brace_block(self, tokens: List, start_index: int):
        """Collect tokens comprising a brace-delimited block.
        start_index should point at the token immediately after the 'try' or at a LBRACE.
        Returns (collected_tokens_including_braces, next_index_after_block)
        """
        n = len(tokens)
        # find the opening brace if start_index points to something else
        i = start_index
        # if the next token is not a LBRACE, try to find it
        if i < n and tokens[i].type != LBRACE:
            # scan forward to first LBRACE or EOF
            while i < n and tokens[i].type != LBRACE and tokens[i].type != EOF:
                i += 1
            if i >= n or tokens[i].type != LBRACE:
                # no brace, return empty block
                return [], start_index

        # i points to LBRACE
        depth = 0
        collected = []
        while i < n:
            tok = tokens[i]
            collected.append(tok)
            if tok.type == LBRACE:
                depth += 1
            elif tok.type == RBRACE:
                depth -= 1
                if depth == 0:
                    return collected, i + 1
            i += 1

        # Reached EOF without closing brace - return what we have (tolerant)
        return collected, i

    def print_structure(self):
        print("🔎 Structural Analyzer - Blocks:")
        for bid, info in self.blocks.items():
            start = info.get('start_index')
            end = info.get('end_index')
            ttype = info.get('type')
            subtype = info.get('subtype')
            token_literals = [t.literal for t in info.get('tokens', []) if getattr(t, 'literal', None)]
            print(f"  [{bid}] {ttype}/{subtype} @ {start}-{end}: {token_literals}")
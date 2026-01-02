# D&D Campaign Management System

A parallel agents architecture for running D&D campaigns with strict separation between code (Git-tracked) and campaign data (not Git-tracked).

## Project Structure

```
C:\DnD\
├── DnD_Cursor\              # CODE REPO (Git-tracked)
│   ├── config\             # Configuration files
│   ├── scripts\            # PowerShell scripts
│   ├── docs\               # Documentation
│   └── .cursor\            # Cursor configuration
├── Sourcebooks\            # BUILD-ONLY: Raw sourcebook text (.txt)
├── Campaigns\
│   └── Phandelver\        # CAMPAIGN DATA (NOT Git)
│       ├── chapters\      # BUILD-ONLY: Raw chapter text dumps (.txt)
│       └── packs\         # PLAY-ONLY: Generated JSON packs (runtime interface)
├── .coord-<session-id>\    # Coordination outputs (outside repo)
└── workspaces\
    └── ksist-dnde.code-workspace
```

### BUILD vs PLAY Separation

**BUILD inputs (compile-time only):**
- Raw `.txt` files in `C:\DnD\Sourcebooks\` (rules reference)
- Raw `.txt` files in `C:\DnD\Campaigns\Phandelver\chapters\` (module text dumps)
- These are processed by build scripts to generate JSON packs

**PLAY inputs (runtime only):**
- JSON packs in `C:\DnD\Campaigns\Phandelver\packs\` (generated from BUILD inputs)
- Agents during PLAY **must not** read raw `.txt` files - only the compiled packs
- This prevents agents from scanning 200+ pages mid-turn and causing drift/hangs

## Safety Rules

- **Campaign data is NEVER Git-tracked** - All campaign files in `C:\DnD\Campaigns\Phandelver` are excluded from Git
- **No destructive Git commands** - Never run `git clean`, `reset --hard`, or `rebase` unless explicitly instructed
- **Secrets protection** - `.env`, `OpenAI_Key.txt`, `google_credentials.json`, `*.key`, `*.pem`, `*.pfx` are never committed
- **Worktrees only in repo** - All agent worktrees operate only in `C:\DnD\DnD_Cursor`
- **Coordination outputs outside repo** - All parallel agent outputs go to `C:\DnD\.coord-<session-id>\`

## Parallel Agents Runbook

### Overview

The system uses 5 specialized agents that work in parallel to process D&D turns:

1. **REFEREE** - Mechanics, rolls, DCs only
2. **NARRATOR** - Narration only
3. **STATE_PATCHER** - State updates (PATCH deltas) only
4. **QA_COMPLIANCE** - Output format + guardrails validation
5. **MERGE** - Composes final 3-block response

### Starting a Session

#### Step 1: Bootstrap Session

Run the bootstrap script to create a coordination directory:

```powershell
cd C:\DnD\DnD_Cursor
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_agents.ps1
```

Or with a specific session ID:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_agents.ps1 -SessionId "my-session-001"
```

This will:
- Generate or use provided session ID
- Create coordination directory: `C:\DnD\.coord-<session-id>\`
- Run safety checks
- Verify required files exist

#### Step 2: Run Parallel Agents

Use the `/dnd_turn_parallel` command in Cursor:

```
/dnd_turn_parallel <session-id>
```

Or manually dispatch agents by following the instructions in `.cursor\commands\dnd_turn_parallel.md`.

This dispatches 4 worker agents in parallel:
- REFEREE
- NARRATOR
- STATE_PATCHER
- QA_COMPLIANCE

Each agent writes its output to:
- `C:\DnD\.coord-<session-id>\dnd_out_REFEREE.json`
- `C:\DnD\.coord-<session-id>\dnd_out_NARRATOR.json`
- `C:\DnD\.coord-<session-id>\dnd_out_STATE_PATCHER.json`
- `C:\DnD\.coord-<session-id>\dnd_out_QA_COMPLIANCE.json`

#### Step 3: Merge Outputs

After all 4 agents complete, run the merge script:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\merge_outputs.ps1 -SessionId <session-id>
```

Or use the `/dnd_turn_merge` command in Cursor:

```
/dnd_turn_merge <session-id>
```

This will:
- Read all 4 agent outputs
- Apply merge rules
- Generate final 3-block output
- Write to `C:\DnD\.coord-<session-id>\dnd_out_MERGE.json`

### Expected Output Format

The final output will be exactly these 3 blocks:

```
NARRATION:
<narration text from NARRATOR>

ASK:
<ask text - requests roll if REFEREE says required=true>

PATCH:
<JSON array from STATE_PATCHER - empty [] if roll pending>
```

If any agent is blocked or validation fails, output will be:

```
BLOCKED: Pack missing required data: <description>
```

### Validation

#### Validate Packs

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_packs.ps1
```

Validates all JSON pack files in `packs\` directory.

#### Validate Agent Outputs

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_agent_outputs.ps1 -SessionId <session-id>
```

Validates:
- All agent output files exist
- Files are in coordination directory (not campaign folder)
- JSON schemas match expected structure
- Required fields are present

### Coordination Directory Structure

After a complete run, you'll find:

```
C:\DnD\.coord-<session-id>\
├── .session-id                    # Session ID reference
├── dnd_out_REFEREE.json          # REFEREE output
├── dnd_out_NARRATOR.json         # NARRATOR output
├── dnd_out_STATE_PATCHER.json    # STATE_PATCHER output
├── dnd_out_QA_COMPLIANCE.json    # QA_COMPLIANCE output
└── dnd_out_MERGE.json           # Final merged output
```

### Quick Test Run

Here's a complete test workflow:

```powershell
# 1. Bootstrap
cd C:\DnD\DnD_Cursor
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_agents.ps1

# Note the session ID from output (e.g., dnd-20241215-143022)

# 2. In Cursor, run:
# /dnd_turn_parallel dnd-20241215-143022
# (Wait for all agents to complete)

# 3. Merge
powershell -ExecutionPolicy Bypass -File .\scripts\merge_outputs.ps1 -SessionId dnd-20241215-143022

# 4. Validate
powershell -ExecutionPolicy Bypass -File .\scripts\validate_agent_outputs.ps1 -SessionId dnd-20241215-143022
```

## Documentation

- **Parallel Agents Architecture**: `docs\PARALLEL_AGENTS.md`
- **PACK Schema**: `docs\PACK_SCHEMA.md`
- **Command Documentation**: `.cursor\commands\*.md`

## Scripts

- `scripts\bootstrap_agents.ps1` - Initialize session
- `scripts\merge_outputs.ps1` - Merge agent outputs
- `scripts\validate_packs.ps1` - Validate pack JSON files
- `scripts\validate_agent_outputs.ps1` - Validate agent outputs
- `scripts\build_session_preload.ps1` - Build session preload pack
- `scripts\build_chapter_pack.ps1` - Build chapter pack from raw .txt
- `scripts\build_encounter_pack.ps1` - Build encounter pack

### Running Build Scripts

Build scripts are written in Python for efficient handling of large text files:

```powershell
python scripts\build_chapter_pack.py --chapter 1
```

For very large chapters, you can skip embedding raw text:

```powershell
python scripts\build_chapter_pack.py --chapter 1 --skip-raw-text
```

## Configuration

- `.cursor\worktrees.json` - Agent roles and output paths
- `.cursorrules` - Cursor rules and safety guardrails
- `.gitignore` - Git ignore rules (protects secrets and campaign data)

## Troubleshooting

### Agent outputs not found
- Verify session ID is correct
- Check coordination directory exists: `C:\DnD\.coord-<session-id>\`
- Run bootstrap script again if needed

### Validation fails
- Check agent output JSON files are valid
- Verify all required fields are present
- Review `docs\PARALLEL_AGENTS.md` for schema requirements

### Blocked output
- Check which agent has `blocked: true`
- Review agent output files for error details
- Verify required data (packs, campaign files) are available

## Contributing

When adding new features:
1. Never modify campaign data directly
2. All outputs go to coordination directory
3. Follow agent role separation strictly
4. Update documentation for any schema changes
5. Run validation scripts before committing

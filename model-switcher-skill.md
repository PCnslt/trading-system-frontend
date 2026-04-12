# Model Switcher Skill

## Purpose
Automatically analyze prompt context and switch between DeepSeek Reasoner (for coding/complex tasks) and DeepSeek Chat (for regular conversations).

## Detection Logic

### Switch to DeepSeek Reasoner when prompt contains:
- **Coding keywords**: `code`, `coding`, `program`, `develop`, `build`, `fix`, `error`, `bug`, `TypeScript`, `Angular`, `compile`, `syntax`, `function`, `class`, `interface`, `component`, `service`, `module`, `import`, `export`, `debug`, `test`, `implement`, `algorithm`, `logic`
- **Complex tasks**: `complex`, `analysis`, `design`, `architecture`, `refactor`, `optimize`, `performance`, `memory`, `storage`, `database`, `API`, `endpoint`, `backend`, `frontend`, `infrastructure`, `docker`, `container`, `port`, `configuration`, `setup`, `install`, `dependency`
- **System tasks**: `package.json`, `tsconfig`, `angular.json`, `build`, `deploy`, `CI/CD`, `git`, `commit`, `push`, `merge`, `branch`, `repository`
- **Debugging**: `error`, `bug`, `fix`, `debug`, `troubleshoot`, `issue`, `problem`
- **Analysis**: `analyze`, `review`, `audit`, `evaluate`, `assess`

### Switch to DeepSeek Chat when:
- **Simple conversations**: `hi`, `hello`, `thanks`, `ok`, `yes`, `no`, `maybe`
- **Status updates**: `status`, `progress`, `update`, `report`, `check`
- **Brief questions**: `what`, `when`, `where`, `how`, `why` (short form)
- **General chat**: casual conversation, social interaction

## Implementation

### Manual Switching Commands:
- "Switch to Reasoner for this coding task"
- "Use DeepSeek Chat for faster responses"  
- "Enable reasoning mode"
- "Use the faster model"

### Automatic Detection:
1. Analyze prompt for keywords
2. If coding/complex keywords > 2, switch to Reasoner
3. If prompt length < 50 chars and no complex keywords, use Chat
4. For tool usage (exec, edit, write, etc.), use Reasoner

### Example Workflow:
```
User: "Fix the Angular compilation errors"
Assistant: (detects "Angular", "compilation", "errors" → switches to Reasoner)
"I'll use DeepSeek Reasoner for this coding task..."

[After fix]
Assistant: (switches back to Chat)
"Errors fixed! Back to faster responses."
```

## Current Configuration
- **Primary**: `deepseek/deepseek-chat` (faster conversations)
- **Fallback**: `deepseek/deepseek-reasoner` (complex tasks)
- **Manual switch**: `session_status({model: "deepseek/deepseek-reasoner"})`

## Usage
Apply this logic before responding to any prompt. Check for coding/complex keywords and switch models accordingly.
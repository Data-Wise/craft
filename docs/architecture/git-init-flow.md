# /craft:git:init - Architecture & Flow Diagrams

## Command Execution Flow

```mermaid
flowchart TD
    Start([User invokes /craft:git:init]) --> ParseArgs[Parse Arguments]
    ParseArgs --> DryRun{Dry-run mode?}

    DryRun -->|Yes| Preview[Generate Preview]
    Preview --> ShowPreview[Display Dry-run Output]
    ShowPreview --> End([Exit])

    DryRun -->|No| CheckGit{.git exists?}

    CheckGit -->|Yes| AskAction[Ask: What to do?]
    AskAction --> ActionChoice{User Choice}
    ActionChoice -->|Add dev+protection| Step3
    ActionChoice -->|Fix/sync dev| SyncDev[Sync dev with main]
    ActionChoice -->|Re-init| ForceCheck{--force flag?}
    ActionChoice -->|Cancel| End

    ForceCheck -->|No| Error1[Error: Requires --force]
    Error1 --> End
    ForceCheck -->|Yes| RemoveGit[Remove .git]
    RemoveGit --> InitRepo

    CheckGit -->|No| InitRepo[Initialize Git Repository]

    SyncDev --> Step3
    InitRepo --> Step2[Step 2: Remote Setup]

    Step2 --> RemoteChoice{Remote option?}
    RemoteChoice -->|Local only| Step3[Step 3: Branch Structure]
    RemoteChoice -->|Connect existing| AddRemote[git remote add]
    RemoteChoice -->|Create new| CreateRepo[gh repo create]

    AddRemote --> Step3
    CreateRepo --> ConfigureRepo[Set visibility, description, topics]
    ConfigureRepo --> AddRemote

    Step3 --> WorkflowType{Workflow pattern}
    WorkflowType -->|main-dev| CreateMainDev[Create main + dev]
    WorkflowType -->|simple| CreateMain[Create main only]
    WorkflowType -->|gitflow| CreateGitFlow[Create main + develop]

    CreateMainDev --> Step4[Step 4: Branch Protection]
    CreateMain --> Step4
    CreateGitFlow --> Step4

    Step4 --> ProtectChoice{Enable protection?}
    ProtectChoice -->|Yes| SetProtection[Configure GitHub protection rules]
    ProtectChoice -->|No| Step5[Step 5: CI Workflow]

    SetProtection --> Step5

    Step5 --> CIChoice{Generate CI?}
    CIChoice -->|Yes| DetectType[Auto-detect project type]
    CIChoice -->|No| Step6[Step 6: Project Files]

    DetectType --> SelectTemplate[User selects CI template]
    SelectTemplate --> GenerateCI[Generate .github/workflows/ci.yml]
    GenerateCI --> Step6

    Step6 --> FilesChoice{Create files?}
    FilesChoice -->|Yes| CreateFiles[Create .STATUS, CLAUDE.md, PR template]
    FilesChoice -->|No| Step7[Step 7: Initial Commit]

    CreateFiles --> Step7

    Step7 --> CommitChoice{Create commit?}
    CommitChoice -->|Yes| StageFiles[git add -A]
    CommitChoice -->|No| Step8[Step 8: Push to Remote]

    StageFiles --> CreateCommit[git commit with conventional message]
    CreateCommit --> Step8

    Step8 --> PushChoice{Push to GitHub?}
    PushChoice -->|Yes| Push[git push origin main dev]
    PushChoice -->|No| Step9[Step 9: Validation]

    Push --> Step9

    Step9 --> ValidateChoice{Run /craft:check?}
    ValidateChoice -->|Yes| RunCheck[Execute /craft:check]
    ValidateChoice -->|No| Success

    RunCheck --> CheckResult{Validation pass?}
    CheckResult -->|Yes| Success[✓ Success Summary]
    CheckResult -->|No| Warning[⚠ Warnings Displayed]

    Success --> End
    Warning --> End

    %% Error handling paths
    InitRepo -.->|Error| Rollback1[Rollback: Remove .git]
    CreateRepo -.->|Error| Rollback2[Rollback: Offer to delete repo]
    SetProtection -.->|Error| Rollback3[Rollback: Disable protection]
    GenerateCI -.->|Error| Rollback4[Rollback: Delete CI file]
    CreateFiles -.->|Error| Rollback5[Rollback: Delete created files]
    CreateCommit -.->|Error| Rollback6[Rollback: Reset HEAD]

    Rollback1 --> ErrorEnd([Exit with error])
    Rollback2 --> ErrorEnd
    Rollback3 --> ErrorEnd
    Rollback4 --> ErrorEnd
    Rollback5 --> ErrorEnd
    Rollback6 --> ErrorEnd

    style Start fill:#e1f5e1
    style End fill:#e1f5e1
    style Success fill:#c8e6c9
    style ErrorEnd fill:#ffcdd2
    style Error1 fill:#ffcdd2
    style Warning fill:#fff9c4
```

## Workflow Patterns Architecture

### Pattern 1: Main + Dev (Default)

```mermaid
gitGraph
    commit id: "Initial commit"
    branch dev
    checkout dev
    commit id: "Setup dev branch"
    branch feature/auth
    checkout feature/auth
    commit id: "Add login"
    commit id: "Add signup"
    checkout dev
    merge feature/auth tag: "PR #1"
    branch feature/api
    checkout feature/api
    commit id: "Add API endpoints"
    checkout dev
    merge feature/api tag: "PR #2"
    checkout main
    merge dev tag: "Release v1.0"
```

**Branch Flow:**
```mermaid
graph LR
    Feature[feature/*] -->|PR| Dev[dev]
    Dev -->|PR| Main[main]
    Main -->|Deploy| Production[Production]

    style Main fill:#ff6b6b
    style Dev fill:#4ecdc4
    style Feature fill:#95e1d3
    style Production fill:#f38181
```

### Pattern 2: Simple

```mermaid
gitGraph
    commit id: "Initial commit"
    commit id: "Add feature A"
    commit id: "Add feature B"
    commit id: "Fix bug"
    commit id: "Release v1.0" tag: "v1.0"
```

**Branch Flow:**
```mermaid
graph LR
    Main[main] -->|Direct commits| Main
    Main -->|Deploy| Production[Production]

    style Main fill:#ff6b6b
    style Production fill:#f38181
```

### Pattern 3: GitFlow

```mermaid
gitGraph
    commit id: "Initial"
    branch develop
    checkout develop
    commit id: "Setup develop"
    branch feature/user-auth
    checkout feature/user-auth
    commit id: "Add auth"
    checkout develop
    merge feature/user-auth
    branch release/v1.0
    checkout release/v1.0
    commit id: "Bump version"
    commit id: "Update docs"
    checkout main
    merge release/v1.0 tag: "v1.0"
    checkout develop
    merge release/v1.0
    branch hotfix/critical-bug
    checkout hotfix/critical-bug
    commit id: "Fix bug"
    checkout main
    merge hotfix/critical-bug tag: "v1.0.1"
    checkout develop
    merge hotfix/critical-bug
```

**Branch Flow:**
```mermaid
graph TB
    Feature[feature/*] -->|PR| Develop[develop]
    Develop -->|PR| Release[release/*]
    Release -->|PR| Main[main]
    Main -->|Tag| Version[v1.0.0]
    Release -->|Merge back| Develop
    Main -->|Hotfix| Hotfix[hotfix/*]
    Hotfix -->|PR| Main
    Hotfix -->|Merge back| Develop

    style Main fill:#ff6b6b
    style Develop fill:#4ecdc4
    style Feature fill:#95e1d3
    style Release fill:#ffd93d
    style Hotfix fill:#ff8787
```

## Component Architecture

```mermaid
graph TB
    subgraph "User Interface"
        CLI["/craft:git:init CLI"]
        SmartRouter["/craft:do Smart Router"]
    end

    subgraph "Wizard Engine"
        StepController[Step Controller]
        AskQuestion[AskUserQuestion]
        ProgressTracker[Progress Tracker]
    end

    subgraph "Core Operations"
        GitOps[Git Operations]
        GHOps[GitHub Operations]
        FileOps[File Operations]
        CIOps[CI Generation]
    end

    subgraph "Templates"
        StatusTemplate[.STATUS Template]
        ClaudeTemplate[CLAUDE.md Template]
        PRTemplate[PR Template]
        CITemplates[CI Templates]
    end

    subgraph "Validation"
        DryRun[Dry-run Validator]
        Check[/craft:check Integration]
        Rollback[Rollback Engine]
    end

    CLI --> StepController
    SmartRouter --> StepController
    StepController --> AskQuestion
    StepController --> ProgressTracker
    StepController --> GitOps
    StepController --> GHOps
    StepController --> FileOps
    StepController --> CIOps

    GitOps --> DryRun
    GHOps --> DryRun
    FileOps --> Templates
    CIOps --> CITemplates

    GitOps -.->|Error| Rollback
    GHOps -.->|Error| Rollback
    FileOps -.->|Error| Rollback

    StepController --> Check

    style CLI fill:#e3f2fd
    style SmartRouter fill:#e3f2fd
    style StepController fill:#fff3e0
    style Rollback fill:#ffebee
    style Check fill:#e8f5e9
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Wizard
    participant Git
    participant GitHub
    participant Templates
    participant CI

    User->>Wizard: /craft:git:init
    Wizard->>User: Check .git exists?

    alt Repository exists
        Wizard->>User: Ask action (add dev/sync/reinit)
        User->>Wizard: Select action
    else New repository
        Wizard->>Git: git init
        Git-->>Wizard: Repository created
    end

    Wizard->>User: Ask remote setup
    User->>Wizard: Create new GitHub repo

    Wizard->>GitHub: gh repo create
    GitHub-->>Wizard: Repository URL
    Wizard->>Git: git remote add origin

    Wizard->>User: Select workflow pattern
    User->>Wizard: main-dev

    Wizard->>Git: Create main + dev branches
    Git-->>Wizard: Branches created

    Wizard->>User: Enable branch protection?
    User->>Wizard: Yes

    Wizard->>GitHub: Configure protection rules
    GitHub-->>Wizard: Protection enabled

    Wizard->>User: Generate CI workflow?
    User->>Wizard: Yes (auto-detect)

    Wizard->>CI: Detect project type
    CI-->>Wizard: Python UV detected
    Wizard->>User: Confirm template?
    User->>Wizard: Confirmed

    Wizard->>CI: Generate workflow file
    CI-->>Wizard: .github/workflows/ci.yml

    Wizard->>User: Create project files?
    User->>Wizard: Yes (all)

    Wizard->>Templates: Render templates
    Templates-->>Wizard: .STATUS, CLAUDE.md, PR template

    Wizard->>User: Create initial commit?
    User->>Wizard: Yes

    Wizard->>Git: git add -A
    Wizard->>Git: git commit
    Git-->>Wizard: Commit created

    Wizard->>User: Push to GitHub?
    User->>Wizard: Yes

    Wizard->>Git: git push origin main dev
    Git->>GitHub: Push branches
    GitHub-->>Wizard: Push successful

    Wizard->>User: Run validation?
    User->>Wizard: Yes

    Wizard->>CI: Execute /craft:check
    CI-->>Wizard: Validation results

    Wizard->>User: ✓ Setup complete!
```

## Error Handling Flow

```mermaid
flowchart TD
    Operation[Execute Operation] --> Success{Success?}

    Success -->|Yes| RecordState[Record State]
    RecordState --> NextOp[Next Operation]

    Success -->|No| CaptureError[Capture Error Details]
    CaptureError --> DetermineRollback[Determine Rollback Steps]

    DetermineRollback --> RollbackType{Rollback Type}

    RollbackType -->|Git Init| RemoveGit[Remove .git directory]
    RollbackType -->|Branches| DeleteBranches[Delete created branches]
    RollbackType -->|Remote| RemoveRemote[Remove remote config]
    RollbackType -->|GitHub Repo| OfferDelete[Offer to delete repo]
    RollbackType -->|Protection| DisableProtection[Disable protection]
    RollbackType -->|Files| DeleteFiles[Delete created files]
    RollbackType -->|Commits| ResetHead[git reset HEAD~1]

    RemoveGit --> NotifyUser[Notify User]
    DeleteBranches --> NotifyUser
    RemoveRemote --> NotifyUser
    OfferDelete --> UserConfirm{User confirms?}
    UserConfirm -->|Yes| DeleteRepo[gh repo delete]
    UserConfirm -->|No| KeepRepo[Keep repository]
    DeleteRepo --> NotifyUser
    KeepRepo --> NotifyUser
    DisableProtection --> NotifyUser
    DeleteFiles --> NotifyUser
    ResetHead --> NotifyUser

    NotifyUser --> LogError[Log Error Details]
    LogError --> SuggestFix[Suggest Fix]
    SuggestFix --> Exit([Exit with error code])

    style Operation fill:#e3f2fd
    style Success fill:#fff3e0
    style NotifyUser fill:#ffebee
    style Exit fill:#ffcdd2
```

## Template Processing

```mermaid
flowchart LR
    subgraph "Input"
        Repo[Repository Info]
        User[User Data]
        Workflow[Workflow Type]
    end

    subgraph "Template Engine"
        Load[Load Template]
        Parse[Parse Placeholders]
        Replace[Replace Variables]
        Validate[Validate Output]
    end

    subgraph "Templates"
        STATUS[STATUS-template.yaml]
        CLAUDE[CLAUDE-template.md]
        PR[pull_request_template.md]
    end

    subgraph "Output"
        StatusFile[.STATUS]
        ClaudeFile[CLAUDE.md]
        PRFile[.github/pull_request_template.md]
    end

    Repo --> Parse
    User --> Parse
    Workflow --> Parse

    STATUS --> Load
    CLAUDE --> Load
    PR --> Load

    Load --> Parse
    Parse --> Replace
    Replace --> Validate

    Validate --> StatusFile
    Validate --> ClaudeFile
    Validate --> PRFile

    style Load fill:#e3f2fd
    style Parse fill:#fff3e0
    style Replace fill:#e8f5e9
    style Validate fill:#fff9c4
```

## Integration Points

```mermaid
graph TB
    subgraph "Command Entry"
        DirectCall["/craft:git:init"]
        SmartDo["/craft:do 'initialize project'"]
        Hub["/craft:hub git"]
    end

    subgraph "Core Command"
        GitInit["/craft:git:init Engine"]
    end

    subgraph "Related Commands"
        Worktree["/craft:git:worktree"]
        Branch["/craft:git:branch"]
        Check["/craft:check"]
        CIGen["/craft:ci:generate"]
        Clean["/craft:git:clean"]
    end

    subgraph "External Tools"
        Git[Git CLI]
        GH[GitHub CLI]
        Python[Python CI Detection]
    end

    DirectCall --> GitInit
    SmartDo --> GitInit
    Hub -.->|Discovery| DirectCall

    GitInit -->|Uses| Git
    GitInit -->|Uses| GH
    GitInit -->|Calls| CIGen
    GitInit -->|Calls| Check

    GitInit -.->|Suggests| Worktree
    GitInit -.->|Related| Branch
    GitInit -.->|Related| Clean

    CIGen --> Python

    style GitInit fill:#fff3e0
    style DirectCall fill:#e3f2fd
    style Check fill:#e8f5e9
    style Git fill:#ffebee
    style GH fill:#ffebee
```

## State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> CheckingRepo: Command invoked
    CheckingRepo --> InitializingNew: No .git found
    CheckingRepo --> UpdatingExisting: .git exists
    CheckingRepo --> Cancelled: User cancels

    InitializingNew --> SettingUpRemote
    UpdatingExisting --> SettingUpRemote

    SettingUpRemote --> CreatingBranches: Remote configured
    SettingUpRemote --> CreatingBranches: Local only

    CreatingBranches --> ConfiguringProtection
    ConfiguringProtection --> GeneratingCI
    GeneratingCI --> CreatingFiles
    CreatingFiles --> Committing
    Committing --> Pushing: Remote exists
    Committing --> Validating: Local only
    Pushing --> Validating
    Validating --> Success
    Validating --> SuccessWithWarnings: Warnings present

    Success --> [*]
    SuccessWithWarnings --> [*]
    Cancelled --> [*]

    note right of CheckingRepo
        Checks for .git directory
        Asks user for action
    end note

    note right of SettingUpRemote
        GitHub integration
        Remote configuration
    end note

    note right of ConfiguringProtection
        Branch protection rules
        Requires GitHub admin
    end note

    note right of Validating
        Runs /craft:check
        Reports status
    end note
```

## File System Operations

```mermaid
graph TB
    Start[Start] --> CheckCWD{Current dir writable?}

    CheckCWD -->|No| Error[Error: Permission denied]
    CheckCWD -->|Yes| CreateGit[Create .git/]

    CreateGit --> CreateBranches[Create branches]
    CreateBranches --> CreateGitHub[Create .github/]

    CreateGitHub --> CreateWorkflows[Create workflows/]
    CreateWorkflows --> GenerateCI[Generate ci.yml]

    GenerateCI --> CreateTemplates[Create templates directory]
    CreateTemplates --> RenderStatus[Render .STATUS]
    RenderStatus --> RenderClaude[Render CLAUDE.md]
    RenderClaude --> RenderPR[Render PR template]

    RenderPR --> Stage[git add -A]
    Stage --> Commit[git commit]
    Commit --> Success[✓ Files created]

    Error --> End[Exit]
    Success --> End

    style Start fill:#e3f2fd
    style Success fill:#e8f5e9
    style Error fill:#ffebee
    style End fill:#fff3e0
```

---

**Document Version:** 1.0
**Generated:** 2025-01-15
**Architecture:** /craft:git:init command

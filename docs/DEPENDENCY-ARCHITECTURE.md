# Architecture - Dependency Management System

Visual architecture diagrams and system design documentation.

---

## Table of Contents

- [System Overview](#system-overview)
- [Component Diagrams](#component-diagrams)
- [Sequence Diagrams](#sequence-diagrams)
- [Data Flow](#data-flow)
- [Decision Trees](#decision-trees)

---

## System Overview

```mermaid
graph TB
    subgraph "User Interface"
        CMD[/craft:docs:demo]
        CLI["CLI Flags<br/>--check, --fix, --convert, --batch"]
    end

    subgraph "Phase 1: Detection"
        DM[dependency-manager.sh]
        TD[tool-detector.sh]
        SC[session-cache.sh]
    end

    subgraph "Phase 2: Installation"
        DI[dependency-installer.sh]
        CP[consent-prompt.sh]
        BREW[Homebrew]
        CARGO[Cargo]
        BINARY[Binary Download]
    end

    subgraph "Phase 3: Conversion"
        CC[convert-cast.sh]
        BC[batch-convert.sh]
        AGG[agg converter]
        GIF[gifsicle optimizer]
    end

    subgraph "Phase 4: Advanced"
        HC[health-check.sh]
        VC[version-check.sh]
        RT[repair-tools.sh]
    end

    subgraph "Storage"
        CACHE[(Session Cache)]
        YAML[(YAML Frontmatter)]
    end

    CMD --> CLI
    CLI --> DM
    DM --> TD
    DM --> SC
    SC <--> CACHE
    TD --> YAML

    DM --> DI
    DI --> CP
    DI --> BREW
    DI --> CARGO
    DI --> BINARY

    DM --> HC
    DM --> VC
    HC --> RT
    VC --> RT

    CLI --> CC
    CLI --> BC
    CC --> AGG
    AGG --> GIF

    style CMD fill:#4CAF50
    style DM fill:#2196F3
    style DI fill:#FF9800
    style CC fill:#9C27B0
    style HC fill:#F44336
```

---

## Component Diagrams

### Phase 1: Dependency Detection

```mermaid
graph LR
    subgraph "Input"
        YAML[YAML Frontmatter<br/>Tool Specs]
    end

    subgraph "Core Logic"
        PM[parse_frontmatter]
        CD[check_dependencies]
        DT[detect_tool]
    end

    subgraph "Caching"
        GC[get_cached_status]
        SC[store_cache]
        CACHE[(Cache File)]
    end

    subgraph "Output"
        JSON{JSON Status}
        TABLE[Status Table]
    end

    YAML --> PM
    PM --> CD
    CD --> GC
    GC --> CACHE
    CACHE --> GC
    GC -.cache miss.-> DT
    DT --> CD
    CD --> SC
    SC --> CACHE
    CD --> JSON
    JSON --> TABLE

    style PM fill:#E3F2FD
    style CD fill:#BBDEFB
    style JSON fill:#90CAF9
```

### Phase 2: Installation Pipeline

```mermaid
graph TD
    START[Missing Tool Detected]
    CONSENT{User<br/>Consent?}
    STRATEGY{Installation<br/>Strategy}

    BREW[brew install]
    CARGO[cargo install]
    BINARY[Binary Download]
    APT[apt install]
    YUM[yum install]

    VERIFY{Verify<br/>Install?}
    SUCCESS[Installation Success]
    FAIL[Installation Failed]

    START --> CONSENT
    CONSENT -->|Yes| STRATEGY
    CONSENT -->|No| FAIL

    STRATEGY --> BREW
    STRATEGY -.fallback.-> CARGO
    CARGO -.fallback.-> BINARY
    BINARY -.fallback.-> APT
    APT -.fallback.-> YUM

    BREW --> VERIFY
    CARGO --> VERIFY
    BINARY --> VERIFY
    APT --> VERIFY
    YUM --> VERIFY

    VERIFY -->|Success| SUCCESS
    VERIFY -->|Fail| FAIL

    style SUCCESS fill:#4CAF50
    style FAIL fill:#F44336
    style CONSENT fill:#FF9800
```

### Phase 3: Conversion Workflow

```mermaid
graph LR
    subgraph "Input"
        CAST1[demo1.cast]
        CAST2[demo2.cast]
        CASTN[demoN.cast]
    end

    subgraph "Batch Processor"
        FIND[Find .cast Files]
        FILTER[Filter Existing]
        QUEUE[Conversion Queue]
    end

    subgraph "Conversion"
        AGG[agg Converter<br/>font-size: 16<br/>theme: monokai]
        OPT[gifsicle Optimizer<br/>-O3 --colors 256]
    end

    subgraph "Output"
        GIF1[demo1.gif]
        GIF2[demo2.gif]
        GIFN[demoN.gif]
        STATS[Summary Stats<br/>Time, Size]
    end

    CAST1 --> FIND
    CAST2 --> FIND
    CASTN --> FIND

    FIND --> FILTER
    FILTER --> QUEUE
    QUEUE --> AGG
    AGG --> OPT

    OPT --> GIF1
    OPT --> GIF2
    OPT --> GIFN
    OPT --> STATS

    style AGG fill:#9C27B0
    style OPT fill:#673AB7
```

### Phase 4: Health & Repair System

```mermaid
graph TB
    subgraph "Health Checks"
        RHC[run_health_check]
        VAH[validate_all_health]
    end

    subgraph "Version Checks"
        EV[extract_version]
        CV[compare_versions]
        CVR[check_version_requirement]
    end

    subgraph "Repair Logic"
        DRC[detect_repair_candidates]
        RT[repair_tool]
    end

    subgraph "Issues Database"
        MISSING[Not Installed]
        BROKEN[Health Check Failed]
        OUTDATED[Version Too Old]
    end

    RHC --> VAH
    VAH --> DRC

    EV --> CV
    CV --> CVR
    CVR --> DRC

    DRC --> MISSING
    DRC --> BROKEN
    DRC --> OUTDATED

    MISSING --> RT
    BROKEN --> RT
    OUTDATED --> RT

    style MISSING fill:#F44336
    style BROKEN fill:#FF9800
    style OUTDATED fill:#FFC107
```

---

## Sequence Diagrams

### Full Dependency Check Workflow

```mermaid
sequenceDiagram
    actor User
    participant CLI as /craft:docs:demo
    participant DM as dependency-manager
    participant Cache as session-cache
    participant TD as tool-detector
    participant HC as health-check
    participant VC as version-check

    User->>CLI: /craft:docs:demo --check
    CLI->>DM: check_dependencies("asciinema")

    DM->>Cache: get_cached_status()
    alt Cache Hit
        Cache-->>DM: return cached JSON
    else Cache Miss
        DM->>TD: detect_tool("asciinema")
        TD-->>DM: /usr/local/bin/asciinema

        DM->>HC: run_health_check("asciinema")
        HC-->>DM: {"health": "ok"}

        DM->>VC: extract_version("asciinema")
        VC-->>DM: "2.3.0"

        DM->>VC: compare_versions("2.3.0", "2.0.0")
        VC-->>DM: 1 (newer)

        DM->>Cache: store_cache(status)
    end

    DM-->>CLI: status JSON
    CLI->>User: Display table
```

### Installation Workflow

```mermaid
sequenceDiagram
    actor User
    participant CLI as /craft:docs:demo
    participant DM as dependency-manager
    participant DI as dependency-installer
    participant CP as consent-prompt
    participant PKG as Package Manager

    User->>CLI: /craft:docs:demo --fix
    CLI->>DM: check_dependencies()
    DM-->>CLI: {"status": "issues"}

    CLI->>DI: install_tool("agg")
    DI->>CP: prompt_consent("agg", "cargo install agg")
    CP->>User: "Install agg via cargo? (y/n)"
    User-->>CP: y

    DI->>PKG: cargo install agg
    PKG-->>DI: exit 0

    DI->>DM: verify installation
    DM-->>DI: {"installed": true}
    DI-->>CLI: success

    CLI->>User: "agg installed successfully"
```

### Batch Conversion Flow

```mermaid
sequenceDiagram
    actor User
    participant CLI as /craft:docs:demo
    participant BC as batch-convert
    participant CC as convert-cast
    participant AGG as agg
    participant GIF as gifsicle

    User->>CLI: /craft:docs:demo --batch
    CLI->>BC: batch_convert()

    BC->>BC: find_cast_files("docs/")
    BC->>BC: filter_existing()

    loop For Each File
        BC->>CC: convert_single(demo.cast)
        CC->>AGG: agg demo.cast temp.gif
        AGG-->>CC: exit 0
        CC->>GIF: gifsicle -O3 temp.gif -o demo.gif
        GIF-->>CC: exit 0
        CC-->>BC: success
        BC->>User: ✓ demo.cast → demo.gif (2.1s, 145KB)
    end

    BC->>User: Summary: 5/5 converted, 567KB total
```

### Repair Workflow

```mermaid
sequenceDiagram
    actor User
    participant RT as repair-tools
    participant DM as dependency-manager
    participant HC as health-check
    participant VC as version-check
    participant DI as dependency-installer

    User->>RT: detect_repair_candidates("asciinema")

    RT->>DM: check_dependencies()
    DM->>HC: validate_all_health()
    HC-->>DM: {"agg": "broken"}
    DM->>VC: validate_all_versions()
    VC-->>DM: {"gifsicle": "outdated"}
    DM-->>RT: status JSON

    RT->>RT: analyze issues
    RT-->>User: {"candidates": ["agg", "gifsicle"]}

    User->>RT: repair_tool("agg")
    RT->>DI: uninstall("agg")
    DI-->>RT: success
    RT->>DI: install_tool("agg")
    DI-->>RT: success
    RT->>HC: run_health_check("agg")
    HC-->>RT: {"health": "ok"}
    RT-->>User: Repair successful
```

---

## Data Flow

### Dependency Check Data Flow

```mermaid
flowchart TD
    START([User runs --check])
    PARSE[Parse YAML Frontmatter]
    CACHE{Check<br/>Cache}
    DETECT[Detect Tools]
    HEALTH[Health Checks]
    VERSION[Version Checks]
    AGGREGATE[Aggregate Results]
    STORE[Store in Cache]
    OUTPUT[Display Status]
    END([Complete])

    START --> PARSE
    PARSE --> CACHE
    CACHE -->|Hit| OUTPUT
    CACHE -->|Miss| DETECT
    DETECT --> HEALTH
    HEALTH --> VERSION
    VERSION --> AGGREGATE
    AGGREGATE --> STORE
    STORE --> OUTPUT
    OUTPUT --> END

    style START fill:#4CAF50
    style END fill:#4CAF50
    style CACHE fill:#FF9800
```

### Installation Data Flow

```mermaid
flowchart TD
    START([Missing Tool])
    SPEC[Get Install Spec]
    CONSENT{User<br/>Consent?}
    STRAT1[Try Strategy 1]
    SUCCESS1{Success?}
    STRAT2[Try Strategy 2]
    SUCCESS2{Success?}
    STRAT3[Try Strategy 3]
    SUCCESS3{Success?}
    VERIFY[Verify Install]
    COMPLETE([Installed])
    FAIL([Failed])

    START --> SPEC
    SPEC --> CONSENT
    CONSENT -->|No| FAIL
    CONSENT -->|Yes| STRAT1
    STRAT1 --> SUCCESS1
    SUCCESS1 -->|Yes| VERIFY
    SUCCESS1 -->|No| STRAT2
    STRAT2 --> SUCCESS2
    SUCCESS2 -->|Yes| VERIFY
    SUCCESS2 -->|No| STRAT3
    STRAT3 --> SUCCESS3
    SUCCESS3 -->|Yes| VERIFY
    SUCCESS3 -->|No| FAIL
    VERIFY --> COMPLETE

    style COMPLETE fill:#4CAF50
    style FAIL fill:#F44336
```

---

## Decision Trees

### Dependency Status Decision

```mermaid
graph TD
    START{Tool<br/>Installed?}
    HEALTH{Health<br/>Check?}
    VERSION{Version<br/>OK?}

    STATUS_OK[Status: OK ✅]
    STATUS_BROKEN[Status: Broken ⚠️]
    STATUS_OUTDATED[Status: Outdated ⚠️]
    STATUS_MISSING[Status: Missing ❌]

    START -->|Yes| HEALTH
    START -->|No| STATUS_MISSING

    HEALTH -->|Pass| VERSION
    HEALTH -->|Fail| STATUS_BROKEN

    VERSION -->|>= min| STATUS_OK
    VERSION -->|< min| STATUS_OUTDATED

    style STATUS_OK fill:#4CAF50
    style STATUS_BROKEN fill:#FF9800
    style STATUS_OUTDATED fill:#FFC107
    style STATUS_MISSING fill:#F44336
```

### Installation Strategy Selection

```mermaid
graph TD
    START{Platform?}
    PKG_MGR{Package<br/>Manager?}

    MACOS[macOS]
    LINUX[Linux]

    HAS_BREW{Homebrew<br/>Available?}
    HAS_CARGO{Cargo<br/>Available?}
    HAS_APT{APT<br/>Available?}
    HAS_YUM{YUM<br/>Available?}

    USE_BREW[Use: brew install]
    USE_CARGO[Use: cargo install]
    USE_BINARY[Use: Binary download]
    USE_APT[Use: apt install]
    USE_YUM[Use: yum install]

    START --> MACOS
    START --> LINUX

    MACOS --> HAS_BREW
    HAS_BREW -->|Yes| USE_BREW
    HAS_BREW -->|No| HAS_CARGO

    HAS_CARGO -->|Yes| USE_CARGO
    HAS_CARGO -->|No| USE_BINARY

    LINUX --> PKG_MGR
    PKG_MGR --> HAS_APT
    PKG_MGR --> HAS_YUM

    HAS_APT -->|Yes| USE_APT
    HAS_APT -->|No| HAS_CARGO

    HAS_YUM -->|Yes| USE_YUM
    HAS_YUM -->|No| HAS_CARGO

    style USE_BREW fill:#4CAF50
    style USE_CARGO fill:#4CAF50
    style USE_BINARY fill:#4CAF50
    style USE_APT fill:#4CAF50
    style USE_YUM fill:#4CAF50
```

### Batch Conversion Decision

```mermaid
graph TD
    START[.cast File Found]
    EXISTS{.gif<br/>Exists?}
    FORCE{--force<br/>Flag?}
    VALID{.cast<br/>Valid?}

    SKIP[Skip File]
    CONVERT[Convert File]
    ERROR[Report Error]

    START --> EXISTS
    EXISTS -->|No| VALID
    EXISTS -->|Yes| FORCE

    FORCE -->|Yes| VALID
    FORCE -->|No| SKIP

    VALID -->|Yes| CONVERT
    VALID -->|No| ERROR

    style CONVERT fill:#4CAF50
    style SKIP fill:#FFC107
    style ERROR fill:#F44336
```

---

## System Integration Points

### CI/CD Integration Architecture

```mermaid
graph TB
    subgraph "GitHub Actions"
        TRIGGER[Push/PR Event]
        CHECKOUT[Checkout Code]
        INSTALL_JQ[Install jq]
    end

    subgraph "Dependency Validation"
        CHECK_ASC[Check asciinema]
        CHECK_VHS[Check VHS]
        JSON_ASC[(asciinema.json)]
        JSON_VHS[(vhs.json)]
    end

    subgraph "Validation Logic"
        PARSE[Parse JSON]
        STATUS{Status?}
        EXTRACT[Extract Issues]
    end

    subgraph "Reporting"
        ARTIFACT[Upload Artifacts]
        SUMMARY[Job Summary]
        PASS[✅ Success]
        FAIL[❌ Failure]
    end

    TRIGGER --> CHECKOUT
    CHECKOUT --> INSTALL_JQ
    INSTALL_JQ --> CHECK_ASC
    INSTALL_JQ --> CHECK_VHS

    CHECK_ASC --> JSON_ASC
    CHECK_VHS --> JSON_VHS

    JSON_ASC --> PARSE
    JSON_VHS --> PARSE

    PARSE --> STATUS
    STATUS -->|ok| PASS
    STATUS -->|issues| EXTRACT
    EXTRACT --> FAIL

    PASS --> ARTIFACT
    FAIL --> ARTIFACT
    ARTIFACT --> SUMMARY

    style PASS fill:#4CAF50
    style FAIL fill:#F44336
```

### Command Integration Flow

```mermaid
graph LR
    subgraph "demo.md Frontmatter"
        YAML[YAML Spec<br/>Dependencies]
    end

    subgraph "Command Execution"
        PARSE[Parse Frontmatter]
        FLAGS{CLI Flags}
    end

    subgraph "Script Execution"
        CHECK[--check]
        FIX[--fix]
        CONVERT[--convert]
        BATCH[--batch]
    end

    subgraph "Output"
        TABLE[Status Table]
        INSTALL[Installation]
        SINGLE[Single GIF]
        MULTI[Multiple GIFs]
    end

    YAML --> PARSE
    PARSE --> FLAGS

    FLAGS --> CHECK
    FLAGS --> FIX
    FLAGS --> CONVERT
    FLAGS --> BATCH

    CHECK --> TABLE
    FIX --> INSTALL
    CONVERT --> SINGLE
    BATCH --> MULTI

    style YAML fill:#E3F2FD
    style FLAGS fill:#BBDEFB
```

---

## Performance Characteristics

### Caching Strategy

```mermaid
graph TD
    subgraph "Cache Lifecycle"
        INIT[Session Start]
        CREATE[Create Cache File]
        TTL[60s TTL]
        EXPIRE[Cache Expires]
        CLEANUP[Session End]
    end

    subgraph "Cache Operations"
        READ{Read<br/>Cache}
        VALID{Valid &<br/>Fresh?}
        USE[Use Cached Data]
        MISS[Cache Miss]
        COMPUTE[Compute Fresh]
        WRITE[Write Cache]
    end

    INIT --> CREATE
    CREATE --> READ
    READ --> VALID
    VALID -->|Yes| USE
    VALID -->|No| MISS
    MISS --> COMPUTE
    COMPUTE --> WRITE
    WRITE --> READ

    CREATE --> TTL
    TTL --> EXPIRE
    EXPIRE --> CLEANUP

    style USE fill:#4CAF50
    style MISS fill:#FFC107
```

### Parallel Processing

```mermaid
graph TB
    subgraph "Batch Conversion"
        QUEUE[Conversion Queue]
        T1[Thread 1: file1.cast]
        T2[Thread 2: file2.cast]
        T3[Thread 3: file3.cast]
        TN[Thread N: fileN.cast]
    end

    subgraph "Progress Tracking"
        COUNTER[Completed Counter]
        PROGRESS[Progress Bar]
        ETA[ETA Calculation]
    end

    QUEUE --> T1
    QUEUE --> T2
    QUEUE --> T3
    QUEUE --> TN

    T1 --> COUNTER
    T2 --> COUNTER
    T3 --> COUNTER
    TN --> COUNTER

    COUNTER --> PROGRESS
    PROGRESS --> ETA

    style QUEUE fill:#2196F3
    style PROGRESS fill:#4CAF50
```

---

**Last Updated**: 2026-01-17
**Version**: 1.26.0
**Status**: Production Ready

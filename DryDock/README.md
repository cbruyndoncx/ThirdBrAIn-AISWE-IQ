[![Version](https://img.shields.io/badge/version-1.0.5-blue.svg)](https://github.com/savannah-i-g/DryDock)
[![License](https://img.shields.io/badge/license-GPL3.0-green.svg)](LICENSE)
[![Compatibility](https://img.shields.io/badge/AI-Claude%20Code-orange.svg)](https://github.com/savannah-i-g/DryDock)
[![Functionality](https://img.shields.io/badge/Functionality-Agent%20Construction%20Framework-red.svg)](https://github.com/savannah-i-g/DryDock)
[![Agent](https://img.shields.io/badge/Claude%20Agent%20Suport-Yes-green.svg)](https://github.com/savannah-i-g/DryDock)
![Logo](https://raw.githubusercontent.com/savannah-i-g/ShimazuSystems-resources/main/visuals/DryDock_Transparent_White_Shadow.png)
**Build production-ready AI agents in minutes using modular prompt architecture.**

DryDock is a meta-framework that creates specialized AI agents for business and productivity roles. It acts as an intelligent "shipyard" where agents are designed, configured, validated, and deployed—entirely within Claude Code.

## What Makes DryDock Different

Unlike other agent frameworks that simply provide pre-built agents, **DryDock BUILDS agents**. It's a meta-framework that uses modular prompt architecture to create complete, standalone AI systems tailored to your specific needs.

## Quick Start

### 1. Activate DryDock

Provide the `drydock.activationkey` file to Claude:

```
I want to use the drydock.activationkey file to activate DryDock
```

### 2. Choose Your Path

**Quick Start (2-3 minutes):**
- Select a pre-built template (Project Manager, Developer, QA Engineer, etc.)
- Customize the name and basic settings
- Generate your agent

**Custom Build (10-15 minutes):**
- Define your agent's purpose from scratch
- Select capabilities from the component library
- Configure personality and interface
- Generate a fully customized agent

### 3. Deploy Your Agent

DryDock generates:
- `.activationkey` file - Bootstrap configuration
- Core system file - Complete agent configuration
- Activation instructions
- Usage documentation

Simply provide the generated activation key to Claude, and your agent is ready to work!

## Agent Execution Modes

DryDock agents can operate in two modes, giving you flexibility based on your task needs:

### Interactive Mode (Traditional)
**Best for:** Exploratory tasks, learning, when you want step-by-step control

Activate your generated agent by providing its `.activationkey` file:
```
Provide: output/developer/developer.activationkey
```

The agent presents an interactive menu, asks clarifying questions, and guides you through each step of the workflow.

### Autonomous Mode (Runtime) - NEW
**Best for:** Well-defined tasks, batch operations, autonomous execution to completion

Use the DryDock Runtime subagent to execute agents autonomously:
```
"Use drydock-runtime to review this code for security issues"
```

The runtime:
1. Automatically loads the appropriate DryDock agent (e.g., Developer)
2. Executes its capabilities using workflows, decision logic, and quality gates
3. Runs to completion without requiring user interaction
4. Returns comprehensive, professional results

**Same agent configuration, two execution modes.** Choose based on your task:
- Need guidance and control? → Interactive mode
- Want autonomous execution? → Runtime mode

### Runtime System

Located in `.claude/agents/`, the runtime system enables autonomous execution of DryDock agents:

**Components:**
- **drydock-runtime** - Main autonomous execution engine
- **drydock-selector** - Agent discovery and recommendation helper
- **tool_mappings.library** - Permission-to-tool mapping system

**How it works:**
```
User Request → Runtime Subagent → Loads DryDock Agent Config →
Executes Autonomously → Returns Results
```

**Examples:**
```bash
# Code review with security focus
"Use drydock-runtime to review this authentication code for vulnerabilities"

# Project planning
"Use drydock-runtime to create a project plan for implementing SSO"

# API documentation
"Use drydock-runtime to generate API docs for the user service"

# Discover available agents
"Use drydock-selector to show what agents I have"
```

The runtime preserves all DryDock sophistication - workflows, decision logic, quality gates, and personality - while executing autonomously to completion.

**Learn more:** See `.claude/agents/README.md` for complete runtime documentation.

## Architecture

```
dry_dock/
├── drydock.activationkey          # DryDock bootstrap
├── drydock_core.drydock           # DryDock builder system
├── .claude/                       # Runtime system (autonomous execution)
│   └── agents/
│       ├── drydock-runtime.md     # Autonomous execution engine
│       ├── drydock-selector.md    # Agent discovery helper
│       └── README.md              # Runtime documentation
├── templates/                     # Pre-built agent templates (20 roles)
│   ├── project_manager.template
│   ├── developer.template
│   ├── qa_engineer.template
│   └── [17 more templates]
├── library/                       # Reusable components
│   ├── core_functions.library     # Function definitions
│   ├── personalities.library      # Communication styles
│   ├── workflows.library          # Orchestration patterns
│   ├── security_policies.library  # Security frameworks
│   └── tool_mappings.library      # Permission-to-tool mappings
├── output/                        # Your generated agents
└── CLAUDE.md                      # System orchestration guide

```

## Available Templates

DryDock includes **20 production-ready templates** covering engineering, product, design, business, and specialized roles. Each template includes 10 comprehensive capabilities, personality configuration, security constraints, and detailed workflows.

### Engineering & Development (8 Templates)

| Template | Description | Best For |
|----------|-------------|----------|
| **Software Developer** | Full-stack development with code generation, review, testing, and documentation | Software engineers, full-stack developers |
| **Frontend Developer** | UI/UX implementation with modern frameworks and accessibility standards | Frontend engineers, React/Vue/Angular developers |
| **QA Engineer** | Comprehensive testing and quality assurance | QA engineers, test automation engineers |
| **DevOps Engineer** | Infrastructure automation, CI/CD, deployment management | DevOps engineers, platform engineers |
| **Data Engineer** | Data pipeline design, ETL development, data warehousing | Data engineers, analytics engineers |
| **ML Engineer** | ML model development, training, deployment, monitoring | ML engineers, applied scientists |
| **Security Engineer** | Security architecture, vulnerability assessment, compliance | Security engineers, AppSec specialists |
| **SRE** | System reliability, SLO/SLI management, incident response | Site reliability engineers, production engineers |

### Product & Design (5 Templates)

| Template | Description | Best For |
|----------|-------------|----------|
| **Product Manager** | Product strategy, roadmap planning, feature prioritization | Product managers, product owners |
| **API Product Manager** | API product strategy, OpenAPI specs, developer experience | API product managers, platform PMs |
| **Product Designer** | End-to-end design from wireframes to design systems | Product designers, UX/UI designers |
| **UX Researcher** | User research planning, execution, and synthesis | UX researchers, design researchers |
| **Sales Engineer** | Technical pre-sales, solution design, demos, POCs | Sales engineers, solutions engineers |

### Business & Operations (4 Templates)

| Template | Description | Best For |
|----------|-------------|----------|
| **Project Manager** | Project planning, tracking, coordination, stakeholder management | Project managers, scrum masters |
| **Business Analyst** | Requirements gathering, business process analysis | Business analysts, systems analysts |
| **Customer Success** | Customer onboarding, relationship management, success planning | Customer success managers, account managers |
| **Technical Writer** | Technical documentation, API docs, user guides | Technical writers, documentation specialists |

### Specialized Roles (3 Templates)

| Template | Description | Best For |
|----------|-------------|----------|
| **Financial Analyst** | Financial modeling, forecasting, budgeting, investment analysis | Financial analysts, FP&A analysts |
| **Legal/Compliance** | Contract review, compliance management, policy development | Legal counsel, compliance officers |
| **HR/People Operations** | Recruiting, onboarding, performance management, engagement | HR managers, people operations specialists |

## Component Library

### Core Functions
Essential capabilities that can be added to any agent:
- **context_manager** - State and memory management
- **code_analyzer** - Code quality and pattern analysis
- **report_generator** - Formatted reports and dashboards
- **documentation_generator** - Comprehensive documentation
- **task_decomposer** - Complex task breakdown
- **risk_analyzer** - Risk identification and mitigation
- **workflow_orchestrator** - Multi-step workflow management

### Personalities
Pre-configured communication styles:
- **Professional Executive** - Confident, action-oriented leadership
- **Technical Precise** - Detailed, accurate technical communication
- **Analytical Professional** - Data-driven, evidence-based analysis
- **Detail-Oriented QA** - Meticulous, systematic verification
- **Clear Communicator** - Accessible, user-friendly documentation
- **Supportive Coach** - Encouraging, educational guidance
- **Strategic Advisor** - High-level, forward-thinking consultation
- **Efficient Operator** - Fast-paced, results-focused execution

## How It Works

DryDock operates entirely through conversational interaction within Claude Code:

1. **Activation** - You provide the `drydock.activationkey` to Claude
2. **Menu Interface** - DryDock presents an interactive menu of options
3. **Guided Creation** - Claude asks questions to understand your needs
4. **Configuration Building** - Your responses are assembled into a complete agent config
5. **Validation** - DryDock ensures quality, security, and best practices
6. **Generation** - Complete agent files are generated and presented
7. **Documentation** - Instructions and usage examples provided

## Example Workflow

```
User: I want to build a project management agent

DryDock: Great! I'll help you create a project manager agent.
         Let's start with the Quick Start template.

         What should we call this agent?

User: TaskMaster

DryDock: Perfect! TaskMaster it is.

         The Project Manager template includes these capabilities:
         ✓ Project Planning
         ✓ Task Breakdown
         ✓ Timeline Management
         ✓ Stakeholder Communication
         ✓ Risk Assessment
         ✓ Status Reporting

         Would you like to add any additional capabilities?
         Options: budget_tracking, resource_allocation, quality_assurance

User: Add budget_tracking and resource_allocation

DryDock: Excellent choices! Now for the communication style...
         [continues through personality, interface, etc.]

         Configuration complete! Generating TaskMaster agent files...

         ✓ taskmaster.activationkey created
         ✓ taskmaster_core.taskmaster created
         ✓ Documentation generated

         Your TaskMaster agent is ready!
```

## Key Features

### Template-Based Quick Start
Pre-configured agents for common business roles. Customize and deploy in minutes.

### Full Custom Builder
Complete control over every aspect of your agent. Define unique capabilities and workflows.

### Component Library
Reusable building blocks (functions, personalities, workflows) that can be mixed and matched.

### Validation Engine
Ensures generated agents follow best practices, security standards, and structural requirements.

### Pure Prompt Architecture
No external dependencies. Works entirely within Claude Code using modular prompt framework.

### Production Ready
Generated agents are complete, documented, and ready for immediate use.

## Use Cases

### Business Operations
- Project managers for planning and tracking
- Coordinators for team and resource management
- Analysts for data-driven decision making

### Software Development
- Developers for coding, testing, and review
- QA engineers for quality assurance
- DevOps for infrastructure and deployment
- Technical writers for documentation

### Customer Success
- Support specialists for customer assistance
- Onboarding coaches for new user training
- Success managers for relationship management

### Analysis & Research
- Business analysts for requirements and reporting
- Data analysts for insights and visualization
- Researchers for investigation and synthesis

## Philosophy

DryDock follows the modular prompt architecture philosophy:

1. **Separation of Concerns** - Building agents is separate from being an agent
2. **Configuration Over Code** - Behaviors defined declaratively, not procedurally
3. **Modularity** - Every component is reusable and composable
4. **Validation First** - Quality and security built into every step
5. **Best Practices** - Enforces framework standards automatically
6. **User-Friendly** - Conversational guidance throughout the process

## Technical Details

### File Extensions
- `.drydock` - DryDock system files
- `.activationkey` - Activation keys (bootstrap files)
- `.template` - Agent role templates
- `.library` - Component libraries
- Generated agents use custom extensions (`.projectmanager`, `.developer`, etc.)

### Validation
Every generated agent is validated for:
- Schema compliance (required fields, data types)
- Logical consistency (no conflicting configurations)
- Security standards (proper constraints and permissions)
- Best practices (naming, structure, modularity)
- Completeness (all necessary components present)

### Security
DryDock enforces security at multiple levels:
- Template-level security constraints
- Function-level permission boundaries
- Agent-level operational restrictions
- Validation of all security configurations

## Roadmap

### Current (v1.0) ⚒
- ⚒ Core builder system with conversational interface
- ⚒ Interactive menu interface with splash screen
- ⚒ 20 production-ready templates across 4 categories
- ⚒ Component libraries (functions, personalities, workflows, security policies)
- ⚒ Comprehensive validation engine
- ⚒ Complete file generation system
- ⚒ Security policies library with compliance frameworks (GDPR, HIPAA, PCI DSS, SOC 2)
- ⚒ Workflow orchestration patterns (8 patterns + error handling)
- ⚒ **Runtime System** - Autonomous execution of DryDock agents via Claude Code subagents
- ⚒ Dual execution modes (Interactive & Autonomous)

### Coming Soon
- Template versioning and update system
- Advanced validation with automated improvement suggestions
- Interactive template customization wizard
- Agent capability marketplace
- Performance analytics for generated agents
- Multi-language prompt generation
- Agent testing framework
- Multi-agent runtime coordination (orchestrate multiple DryDock agents autonomously)
- Runtime learning system (improve execution based on history)

### Future
- Multi-agent coordination and orchestration templates
- Agent learning and continuous improvement tracking
- Community marketplace for sharing templates and components
- Advanced workflow patterns (stateful, transactional, distributed)
- Web UI integration for visual agent building
- Out-of-the-Box integration with external LLM providers beyond Claude
- Agent performance benchmarking and optimization tools

## Contributing

Want to add templates or components? The modular architecture makes it easy:

1. **Templates** - Add JSON files to `templates/` following the template schema
2. **Functions** - Add to `library/core_functions.library`
3. **Personalities** - Add to `library/personalities.library`
4. **Workflows** - Add to `library/workflows.library` (coming soon)

## Support

For issues, questions, or feature requests, refer to the project documentation.

## License

**DryDock** is free software licensed under **GPL-3.0** (GNU General Public License v3).

Copyright © 2025 Savannah Goring

### What This Means

- Free to use - Use DryDock for any purpose, personal or commercial
- Free to modify - Adapt and customize to your needs
- Free to distribute - Share with others
- Attribution required - Must credit the original author
- Share modifications - Derivatives must also be GPL-3.0 and open source
- Source code included - If you distribute it, you must share the source

### Why I picked GPL-3.0?

Unlike permissive licenses (MIT, Apache), GPL-3.0 ensures:
- Your contributions and improvements benefit the community
- Credit always goes to the original creator
- Nobody can take this work and make it proprietary without sharing back
- The project remains free and open for everyone

### Full License

See the [LICENSE.txt](LICENSE) file for complete terms and conditions.

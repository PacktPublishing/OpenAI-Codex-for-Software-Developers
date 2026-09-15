# Student pre-work setup

Please complete this checklist before the **Build AI Agents with OpenAI Codex** workshop.
The course uses local Python tools and an authenticated Codex client throughout the day.

## Required

- **A laptop or computer running Windows, macOS, or Linux** where you can install developer tools,
  run terminal commands, and edit local files. A tablet or browser-only environment is not
  sufficient.
- **Python 3.12.x — exactly.** Python 3.13 or newer does not replace this requirement.
  Get Python from the [Python 3.12.10 release page](https://www.python.org/downloads/release/python-31210/).
  Python 3.12.10 is the final 3.12 release with standard Windows and macOS installers.
- **Git.** Get it from [git-scm.com](https://git-scm.com/downloads/).
- **A modern web browser.** You will use it to sign in to Codex and view a Flask application
  running on your laptop.
- **A ChatGPT account with working Codex access.** Sign in at
  [chatgpt.com](https://chatgpt.com/auth/login/) and review
  [Using Codex with your ChatGPT plan](https://help.openai.com/en/articles/11369540).
  Usage limits vary by plan. If you use a company or school workspace, confirm that its
  administrator permits Codex and that the account is suitable for a full workshop day.
- **One authenticated local Codex client:**
  - Recommended: [Visual Studio Code](https://code.visualstudio.com/download) with the
    [Codex IDE extension](https://learn.chatgpt.com/docs/codex/ide).
  - Alternative: [Codex CLI](https://learn.chatgpt.com/docs/codex/cli) plus an editor.

The official IDE guidance also covers Cursor, Windsurf, Xcode, and JetBrains integrations.
If you choose one of those, make sure Codex can open and work with a local folder before class.

## Access to confirm

- Your classroom network, VPN, proxy, and security software allow access to:
  `github.com`, `pypi.org`, `files.pythonhosted.org`, `chatgpt.com`, `openai.com`, and—if
  using VS Code—`marketplace.visualstudio.com`.
- You can install Python packages into a local virtual environment.
- Windows users can run local PowerShell scripts; macOS/Linux users can run `sh` scripts.
- Your browser can open a local address such as `http://127.0.0.1:5000`.
- If the instructor provides a restricted GitHub repository, your GitHub account has access
  and the repository link opens before class.

Managed laptops often restrict one of these capabilities. Please resolve restrictions with
your IT administrator before the workshop.

## Five-minute readiness check

Before class, confirm:

1. Python reports version `3.12.x`.
2. `git --version` succeeds.
3. Your chosen Codex client opens and is signed in with the intended ChatGPT account.
4. Codex can open a local folder and start a chat.
5. Your Codex client is current enough to run subagents and load project agents from
   `.codex/agents/`. Update the client before class if a project agent is not recognized.
6. You know where to find a terminal in your editor or operating system.

CLI users can additionally run:

```text
codex --version
codex login status
codex features list
```

In the feature list, confirm that `multi_agent` is enabled. Project agents are loaded when
Codex starts a session for the repository, so start a new chat after cloning or updating the
workshop files.

## Not required

Do not install Flask, SQLAlchemy, pytest, Ruff, SQLite tools, Docker, Node.js, or a database
server separately. The workshop bootstrap creates a virtual environment and installs the
course packages. The labs do not require an OpenAI API key.

Your instructor will provide the repository URL and workshop bootstrap command separately.

# Day 2: Templates Git Repository and Golden Config Settings

> 📝 **Draft stub.** Day 2's full walkthrough lands in a subsequent commit.

Today we set up the Git repositories Golden Config needs (templates, backup target, intended target) and configure its scope filter to point at the four cEOS Devices that Device Onboarding placed in Nautobot.

## Sections planned

- **Where the templates will live** — decision: scaffold a Jinja-template repo inside this repo's `clab/golden-config-templates/`, point at a public starter repo, or use a file:// URL. Final call captured here.
- **Create the Git repositories in Nautobot** — Extensibility → Git Repositories. One for templates, one for backups, one for intended. Each with the right `provided_contents` flag.
- **Configure Golden Config Settings** — Apps → Golden Config → Settings. Per-Platform settings for `arista_eos`. Wire each repo, set the templates path, set the dynamic-group scope filter to the cEOS Devices.
- **Validate the wiring** — quick sanity-check links from the Settings page back to the Git repos.
